import json
from llm import call_llm
from prompts import QUERY_GENERATION_SCHEMA
from prompt_manager import load_prompts

EXPECTED_COUNT = 12


def generate_queries_for_driver(context: str, metric: str, driver: str) -> list[str]:
    prompts = load_prompts()
    instructions = prompts["PROMPT_BUILDER_INSTRUCTIONS"]

    prompt = f"""
{instructions}

You are generating SEARCH QUERIES for an AI search engine (Brave).

Each query MUST describe a REAL-WORLD EXTERNAL EVENT.

✅ GOOD QUERY EXAMPLES (STYLE ONLY — DO NOT COPY):
- AWS hyperscale data center expansion driving high-capacity power infrastructure procurement
- Equinix colocation campus buildouts signaling increased modular UPS and cooling demand
- Semiconductor fabrication facility expansions requiring redundant power distribution systems

❌ BAD QUERIES (NEVER DO THIS):
- external ecosystem signal query 1
- generic infrastructure expansion query
- placeholder query

STRICT RULES:
- Generate EXACTLY {EXPECTED_COUNT} queries
- Each query must be 10–15 words
- Mention REAL companies, operators, facilities, or infrastructure
- Focus on EXTERNAL signals only
- No placeholders
- No numbering
- No explanations
- No generic language

Context:
{context}

Metric:
{metric}

Driver:
{driver}

OUTPUT FORMAT (STRICT JSON ONLY):
{QUERY_GENERATION_SCHEMA}
""".strip()

    raw = call_llm(prompt)

    try:
        data = json.loads(raw)
        queries = data.get("queries", [])
    except Exception:
        raise ValueError("Query generation failed: invalid JSON")

    # Final hard sanity check
    cleaned = []
    for q in queries:
        if not isinstance(q, str):
            continue
        if len(q.split()) < 8:
            continue
        if "external ecosystem signal" in q.lower():
            continue
        cleaned.append(q.strip())

    if len(cleaned) != EXPECTED_COUNT:
        raise ValueError(
            f"Query generation failed: expected {EXPECTED_COUNT}, got {len(cleaned)}"
        )

    return cleaned
