# prompts.py

PROMPT_BUILDER_PROMPT = """
You are an expert AI Search Strategist.

Using the information below, generate a HIGH-QUALITY,
driver-specific search query generation prompt.

The generated prompt MUST:
- Be optimized for the Brave Search API
- Focus on EXTERNAL ecosystem signals only
- Emphasize entity actions, capital expenditure, infrastructure expansion,
  procurement signals, and technology transitions
- Avoid internal Vertiv signals entirely
- Instruct generation of EXACTLY 12 queries
- Enforce 10–15 words per query
- Exclude dates, headers, numbering, and explanations

INPUT:
Company: Vertiv
Metric: {metric}
Driver: {driver}

Company Context:
{context}

OUTPUT:
Return ONLY the generated prompt text.
Do NOT include explanations.
""".strip()


QUERY_GENERATION_PROMPT_WRAPPER = """
{generated_prompt}

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "queries": [
    "<query 1>",
    "<query 2>",
    "<query 3>",
    "<query 4>",
    "<query 5>",
    "<query 6>",
    "<query 7>",
    "<query 8>",
    "<query 9>",
    "<query 10>",
    "<query 11>",
    "<query 12>"
  ]
}}
""".strip()
QUERY_REPAIR_PROMPT = """
You previously generated a list of search queries, but it does not meet the requirements.

Your task:
- Adjust the list so that it contains EXACTLY 12 queries
- You may rewrite, split, merge, or add queries as needed
- All queries must remain relevant to the original driver and metric
- Each query must contain between 10 and 15 words
- Do NOT include dates, headers, or explanations

Original Driver:
{driver}

Original Queries:
{queries}

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "queries": [
    "<query 1>",
    "<query 2>",
    "<query 3>",
    "<query 4>",
    "<query 5>",
    "<query 6>",
    "<query 7>",
    "<query 8>",
    "<query 9>",
    "<query 10>",
    "<query 11>",
    "<query 12>"
  ]
}}
""".strip()
# prompts.py

ARTICLE_EVALUATION_PROMPT = """
You are an expert equity research analyst and market intelligence analyst.

Your task is to evaluate a news article as an EXTERNAL SIGNAL.

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
{article}
\"\"\"

Instructions:
{{DYNAMIC_INSTRUCTIONS}}

JSON Format:
{{
  "score": <integer 1-5>,
  "summary": "<short summary>"
}}
""".strip()

