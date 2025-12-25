# normalizer.py

def normalize_query(query: str) -> str:
    SAFE_TAIL = "across large scale data center infrastructure deployments"
    words = query.split()

    if len(words) < 10:
        words.extend(SAFE_TAIL.split()[: 10 - len(words)])

    if len(words) > 15:
        words = words[:15]

    return " ".join(words)
