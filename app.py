from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from prompt_manager import load_prompts, save_prompts

import state
from query_generator import generate_queries_for_driver
from validators import finalize_queries
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
        state.data["context"] = request.form.get("context", "")
        state.data["metric"] = request.form.get("metric", "")

        drivers = request.form.getlist("drivers[]")
        state.data["drivers"] = [d.strip() for d in drivers if d.strip()]

        # Reset downstream data
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

    # ---------- STEP 1: QUERY GENERATION ----------
    queries_by_driver = {}

    for driver in drivers:
        raw_queries = generate_queries_for_driver(context, metric, driver)
        queries_by_driver[driver] = finalize_queries(raw_queries)

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

    # ---------- STEP 4: ARTICLE EVALUATION (LLM) ----------
    final_results = {}

    for driver, queries in deduped_results.items():
        driver_results = {}

        for query, results in queries.items():
            evaluated_results = []

            for item in results:
                article_text = fetch_article(item.get("url", ""))

                evaluation = evaluate_article(
                    article_text=article_text,
                    context=context,
                    metric=metric,
                    driver=driver,
                    query=query
                )

                evaluated_results.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "source": item.get("source"),
                    "published": item.get("published"),
                    "rank": item.get("rank"),
                    "score": evaluation["score"],
                    "summary": evaluation["summary"]
                })

            driver_results[query] = evaluated_results

        final_results[driver] = driver_results

    state.data["search_results"] = final_results
    state.save()

    return jsonify({
        "status": "success",
        "drivers": len(drivers),
        "freshness_days": SEARCH_FRESHNESS_DAYS,
        "evaluation": "llm_based",
        "search_executed": True
    })

@app.route("/prompts", methods=["GET", "POST"])
def manage_prompts():
    if request.method == "POST":
        prompts = load_prompts()

        # prompts is a flat dict: key -> instruction string
        for key in prompts.keys():
            if key in request.form:
                prompts[key] = request.form.get(key, "").strip()

        save_prompts(prompts)

        # Redirect to home after saving
        return redirect(url_for("home"))

    return render_template(
        "prompts.html",
        prompts=load_prompts()
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
