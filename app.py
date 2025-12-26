from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

import state
from prompt_manager import load_prompts, save_prompts
from query_generator import generate_queries_for_driver
from search_executor import run_search
from deduplicator import deduplicate_search_results
from fetcher import fetch_article
from article_evaluator import evaluate_article

load_dotenv()

SEARCH_FRESHNESS_DAYS = int(os.getenv("SEARCH_FRESHNESS_DAYS", 4))

app = Flask(__name__)
state.load()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html", data=state.data)


# ---------------- CONTEXT ----------------
@app.route("/context", methods=["GET", "POST"])
def context():
    if request.method == "POST":
        state.data["context"] = request.form.get("context", "").strip()
        state.data["metric"] = request.form.get("metric", "").strip()
        drivers = request.form.getlist("drivers[]")

        state.data["drivers"] = [d.strip() for d in drivers if d.strip()]

        # 🔥 Reset downstream cached data
        state.data["queries"] = {}
        state.data["search_results"] = {}

        state.save()
        return redirect(url_for("home"))

    return render_template("context.html", data=state.data)


# ---------------- START SEARCH ----------------
@app.route("/start-search", methods=["POST"])
def start_search():
    context = state.data.get("context")
    metric = state.data.get("metric")
    drivers = state.data.get("drivers", [])

    if not context or not metric or not drivers:
        return jsonify({"error": "Context, metric, or drivers missing"}), 400

    # 🔥 ALWAYS reset old results before running
    state.data["queries"] = {}
    state.data["search_results"] = {}
    state.save()

    # ---------- STEP 1: QUERY GENERATION ----------
    queries_by_driver = {}

    for driver in drivers:
        try:
            queries = generate_queries_for_driver(context, metric, driver)
            queries_by_driver[driver] = queries
        except Exception as e:
            print(f"Query generation failed for driver '{driver}':", e)
            queries_by_driver[driver] = []

    state.data["queries"] = queries_by_driver
    state.save()

    # ---------- STEP 2: BRAVE SEARCH ----------
    raw_search_results = run_search(
        queries_by_driver,
        days=SEARCH_FRESHNESS_DAYS
    )

    # ---------- STEP 3: DEDUPLICATION ----------
    deduped_results = deduplicate_search_results(
        raw_search_results,
        simhash_threshold=5
    )

    # ---------- STEP 4: PARALLEL ARTICLE EVALUATION ----------
    final_results = {}

    tasks = []
    for driver, queries in deduped_results.items():
        for query, results in queries.items():
            for item in results:
                tasks.append((driver, query, item))

    def process_article(driver, query, item):
        try:
            article_text = fetch_article(item.get("url", ""))
            if not article_text:
                return None

            evaluation = evaluate_article(
                article=article_text,
                context=context,
                metric=metric,
                driver=driver,
                query=query
            )

            return {
                "driver": driver,
                "query": query,
                "title": item.get("title"),
                "url": item.get("url"),
                "source": item.get("source"),
                "published": item.get("published"),
                "rank": item.get("rank"),
                "score": evaluation.get("score"),
                "summary": evaluation.get("summary"),
            }

        except Exception as e:
            print("Article processing failed:", e)
            return None

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_article, d, q, i)
            for d, q, i in tasks
        ]

        for future in as_completed(futures):
            result = future.result()
            if not result:
                continue

            d = result.pop("driver")
            q = result.pop("query")

            final_results.setdefault(d, {}).setdefault(q, []).append(result)

    state.data["search_results"] = final_results
    state.save()

    return jsonify({
        "status": "success",
        "drivers": len(drivers),
        "queries_generated": sum(len(v) for v in queries_by_driver.values()),
        "articles_processed": len(tasks),
        "parallel_execution": True
    })


# ---------------- PROMPTS ----------------
@app.route("/prompts", methods=["GET", "POST"])
def manage_prompts():
    if request.method == "POST":
        prompts = load_prompts()

        # Values are STRINGS (as per your fixed structure)
        for key in prompts.keys():
            if key in request.form:
                prompts[key] = request.form.get(key, "").strip()

        save_prompts(prompts)
        return redirect(url_for("home"))

    return render_template(
        "prompts.html",
        prompts=load_prompts()
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
