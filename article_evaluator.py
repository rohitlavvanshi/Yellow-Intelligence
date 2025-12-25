from prompt_manager import load_dynamic_instructions
from llm import call_llm
from prompts import ARTICLE_EVALUATION_PROMPT
import json


def evaluate_article(article_text, context, metric, driver, query):
    instructions = load_dynamic_instructions("ARTICLE_EVALUATION_INSTRUCTIONS")

    prompt = ARTICLE_EVALUATION_PROMPT.replace(
        "{{DYNAMIC_INSTRUCTIONS}}",
        instructions
    ).format(
        context=context,
        metric=metric,
        driver=driver,
        query=query,
        article=article_text[:6000]
    )

    try:
        return json.loads(call_llm(prompt))
    except Exception:
        return {"score": 1, "summary": "Evaluation failed"}
