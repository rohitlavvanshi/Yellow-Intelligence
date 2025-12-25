# query_generator.py
from llm import call_llm
from prompts import PROMPT_BUILDER_PROMPT, QUERY_GENERATION_PROMPT_WRAPPER
from prompt_manager import load_dynamic_instructions


def generate_queries_for_driver(context, metric, driver):
    # 1️⃣ Load dynamic but SAFE instructions (user-editable part)
    instructions = load_dynamic_instructions("PROMPT_BUILDER_INSTRUCTIONS")

    # 2️⃣ Ask AI to CREATE a driver-specific query-generation prompt
    builder_prompt = PROMPT_BUILDER_PROMPT.replace(
        "{{DYNAMIC_INSTRUCTIONS}}",
        instructions
    ).format(
        context=context,
        metric=metric,
        driver=driver
    )

    generated_prompt = call_llm(builder_prompt)

    # 3️⃣ FORCE the AI to output EXACTLY 12 queries in STRICT JSON
    final_prompt = QUERY_GENERATION_PROMPT_WRAPPER.format(
        generated_prompt=generated_prompt
    )

    queries_json = call_llm(final_prompt)

    return queries_json
