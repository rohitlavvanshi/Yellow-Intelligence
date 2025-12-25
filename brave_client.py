# brave_client.py
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

if not BRAVE_API_KEY:
    raise RuntimeError("BRAVE_API_KEY missing in .env")


def _build_freshness(days: int) -> str:
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    return f"{start}to{end}"


def search_brave(query: str, days: int, count: int = 10) -> list[dict]:
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }

    params = {
        "q": query,
        "count": count,
        "search_lang": "en",
        "spellcheck": 1,
        "freshness": _build_freshness(days)
    }

    response = requests.get(
        BRAVE_ENDPOINT,
        headers=headers,
        params=params,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    results = []
    for rank, item in enumerate(data.get("web", {}).get("results", []), start=1):
        results.append({
            "rank": rank,                      # Brave relevance order
            "title": item.get("title"),
            "url": item.get("url"),
            "description": item.get("description"),
            "source": item.get("source"),
            "published": item.get("published")
        })

    return results
