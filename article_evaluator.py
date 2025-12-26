import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompt_manager import load_prompts

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_ARTICLE_CHARS = 8000
MIN_ARTICLE_CHARS = 500


# --------------------------------------------------
# Safe JSON parsing
# --------------------------------------------------
def _safe_json_parse(text: str) -> dict:
    if not text:
        raise ValueError("Empty LLM response")

    text = text.strip()

    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt to extract JSON substring
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        return json.loads(text[start:end + 1])

    raise ValueError("Invalid JSON returned by LLM")


# --------------------------------------------------
# Article Evaluation (LLM)
# --------------------------------------------------
def evaluate_article(
    article: str,
    context: str,
    metric: str,
    driver: str,
    query: str
) -> dict:
    """
    Scores and summarizes an article using OpenAI.
    Always fails gracefully.
    """

    # 🚫 Do NOT waste credits on junk articles
    if not article or len(article) < MIN_ARTICLE_CHARS:
        return {
            "score": 1,
            "summary": "Article content unavailable or insufficient for reliable evaluation."
        }

    prompts = load_prompts()
    user_instruction = prompts.get("ARTICLE_EVALUATION_INSTRUCTIONS", "").strip()

    # 🔒 Hard system envelope (NOT user editable)
    system_prompt = f"""
You are an expert equity research and market intelligence analyst.

You must evaluate the article strictly as an EXTERNAL SIGNAL.

Context:
{context}

Target Metric:
{metric}

Driver:
{driver}

Search Query:
{query}

Article Content:
\"\"\"
{article[:MAX_ARTICLE_CHARS]}
\"\"\"

Evaluation Rules:
- Assign a relevance score from 1 to 5
- Score reflects how strongly the article indicates movement in the metric via the driver
- Generate a concise executive summary (max 3 sentences)
- Do NOT speculate or add external knowledge
- Base judgment ONLY on the article

User Guidance:
{user_instruction}

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "score": <integer 1-5>,
  "summary": "<short summary>"
}}
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0
        )

        content = response.choices[0].message.content
        parsed = _safe_json_parse(content)

        # Hard validation
        score = int(parsed.get("score", 1))
        score = min(max(score, 1), 5)

        summary = parsed.get("summary", "").strip()

        return {
            "score": score,
            "summary": summary or "No summary returned."
        }

    except Exception as e:
        print("Article evaluation failed:", e)

        # ✅ NEVER crash pipeline
        return {
            "score": 1,
            "summary": "Article could not be reliably evaluated."
        }
