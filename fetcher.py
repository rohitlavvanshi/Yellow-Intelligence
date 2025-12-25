# fetcher.py
import requests
from bs4 import BeautifulSoup
from readability import Document

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_article(url: str, timeout: int = 12) -> str:
    """
    Fetch and extract main article text.
    This function is FAIL-SAFE and will NEVER raise.
    """

    if not url:
        return ""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        html = response.text
    except Exception:
        return ""

    if not html or len(html.strip()) < 200:
        return ""

    # ---------- ATTEMPT 1: Readability ----------
    try:
        doc = Document(html)
        summary_html = doc.summary(html_partial=True)

        if summary_html and len(summary_html.strip()) > 200:
            soup = BeautifulSoup(summary_html, "html.parser")
            text = soup.get_text(separator="\n").strip()
            if len(text) > 200:
                return text
    except Exception:
        pass  # fall through safely

    # ---------- ATTEMPT 2: Fallback to <p> extraction ----------
    try:
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.find_all("p")

        texts = [
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 50
        ]

        combined = "\n".join(texts)
        if len(combined) > 200:
            return combined
    except Exception:
        pass

    # ---------- FINAL FALLBACK ----------
    return ""
