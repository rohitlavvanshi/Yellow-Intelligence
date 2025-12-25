import json
from pathlib import Path

PROMPT_STORE = Path("prompts_store.json")


def load_prompts() -> dict:
    """
    Load ALL prompts (used by prompt editor UI).
    """
    if not PROMPT_STORE.exists():
        return {}

    with PROMPT_STORE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_prompts(data: dict) -> None:
    """
    Save prompts after user edits.
    """
    with PROMPT_STORE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_dynamic_instructions(key: str) -> str:
    """
    Load a SINGLE protected instruction block
    used internally by the pipeline.
    """
    data = load_prompts()
    return data.get(key, "")
