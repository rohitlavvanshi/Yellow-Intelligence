import json


def finalize_queries(raw_text: str) -> list[str]:
    """
    ALWAYS returns exactly 12 queries.
    Never raises.
    """

    queries = _safe_parse(raw_text)

    # Remove duplicates + empty
    queries = _dedupe_clean(queries)

    # If we already have enough
    if len(queries) >= 12:
        return queries[:12]

    # Pad deterministically if fewer than 12
    return _pad_to_12(queries)


def _safe_parse(raw_text: str) -> list[str]:
    try:
        data = json.loads(raw_text)
        queries = data.get("queries", [])
        if isinstance(queries, list):
            return [q.strip() for q in queries if isinstance(q, str)]
    except Exception:
        pass
    return []


def _dedupe_clean(queries: list[str]) -> list[str]:
    seen = set()
    clean = []
    for q in queries:
        if q and q not in seen:
            seen.add(q)
            clean.append(q)
    return clean


def _pad_to_12(queries: list[str]) -> list[str]:
    """
    Guarantees exactly 12 queries without AI.
    """
    if not queries:
        # absolute last-resort fallback
        return [f"external ecosystem signal query {i+1}" for i in range(12)]

    i = 0
    while len(queries) < 12:
        queries.append(queries[i % len(queries)])
        i += 1

    return queries
