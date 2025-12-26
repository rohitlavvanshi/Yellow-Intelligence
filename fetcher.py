import requests
from bs4 import BeautifulSoup
from readability import Document
import re
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_article(url: str, timeout=10) -> str:
    if not url:
        return ""

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return ""

        html = resp.text.strip()
        if not html:
            return ""

        # ---------- Attempt 1: Readability ----------
        try:
            doc = Document(html)
            content_html = doc.summary(html_partial=True)
            text = _html_to_text(content_html)
            if _is_valid(text):
                return text
        except Exception:
            pass

        # ---------- Attempt 2: BeautifulSoup ----------
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        ]

        text = "\n".join(paragraphs)
        if _is_valid(text):
            return text

        # ---------- Attempt 3: Meta description ----------
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            return desc["content"].strip()

    except Exception as e:
        print("Fetch failed:", e)

    return ""


# -----------------------------
# Helpers
# -----------------------------
def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def _is_valid(text: str) -> bool:
    if not text:
        return False

    text = re.sub(r"\s+", " ", text).strip()

    # Require minimum content
    return len(text) > 500
