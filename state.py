import json
from pathlib import Path

STORAGE_FILE = Path("storage.json")

data = {
    "context": "",
    "metric": "",
    "drivers": [],
    "queries": {},
    "search_results": {}   # 👈 NEW
}


def load():
    global data
    if STORAGE_FILE.exists():
        data.update(json.loads(STORAGE_FILE.read_text()))

def save():
    STORAGE_FILE.write_text(json.dumps(data, indent=2))
