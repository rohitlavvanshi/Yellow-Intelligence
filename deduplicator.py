# deduplicator.py
from simhash import Simhash


def _text_fingerprint(item: dict) -> int:
    """
    Create a SimHash fingerprint from title + description.
    """
    text = f"{item.get('title', '')} {item.get('description', '')}"
    tokens = text.lower().split()
    return Simhash(tokens).value


def deduplicate_search_results(
    search_results: dict,
    simhash_threshold: int = 5
) -> dict:
    """
    Deduplicates search results by:
    1. Exact URL match
    2. Near-duplicate content using SimHash

    search_results structure:
    {
      driver: {
        query: [ { result }, ... ]
      }
    }
    """

    deduped = {}

    for driver, queries in search_results.items():
        seen_urls = set()
        seen_hashes = []

        driver_cleaned = {}

        for query, results in queries.items():
            unique_results = []

            for item in results:
                url = item.get("url")
                if not url:
                    continue

                # ---- STEP 1: URL dedup ----
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                # ---- STEP 2: SimHash dedup ----
                fingerprint = _text_fingerprint(item)

                is_duplicate = False
                for existing in seen_hashes:
                    if Simhash.distance(
                        Simhash(fingerprint),
                        Simhash(existing)
                    ) <= simhash_threshold:
                        is_duplicate = True
                        break

                if is_duplicate:
                    continue

                seen_hashes.append(fingerprint)
                unique_results.append(item)

            driver_cleaned[query] = unique_results

        deduped[driver] = driver_cleaned

    return deduped
