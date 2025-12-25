# search_executor.py
from brave_client import search_brave


def run_search(queries_by_driver: dict, days: int) -> dict:
    all_results = {}

    for driver, queries in queries_by_driver.items():
        driver_results = {}

        for query in queries:
            results = search_brave(query, days)

            # Attach traceability metadata
            for r in results:
                r["query"] = query
                r["driver"] = driver
                r["freshness_window_days"] = days

            driver_results[query] = results

        all_results[driver] = driver_results

    return all_results
