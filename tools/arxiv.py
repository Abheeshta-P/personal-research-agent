import requests
import xml.etree.ElementTree as ET

from langchain_core.tools import tool



@tool
def search_arxiv(topic: str) -> str:
    """Search arXiv for research papers on a topic."""

    print(f"Searching arXiv for: '{topic}'...")

    import re

    # Extract meaningful keywords of 3+ letters to verify query relevance
    topic_words = [
        word.lower()
        for word in re.findall(r"\b[a-zA-Z]{3,}\b", topic)
    ]

    url = "https://export.arxiv.org/api/query"

    params = {
        "search_query": f'all:"{topic}"',
        "start": 0,
        "max_results": 5,
    }

    headers = {
        "User-Agent": "ai-research-agent/0.1"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

    except requests.exceptions.Timeout:
        return f"NO_RESULTS: arXiv search timed out for: {topic}"

    except requests.exceptions.RequestException as e:
        return f"NO_RESULTS: arXiv search failed: {e}"

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        return f"NO_RESULTS: Failed to parse arXiv XML response: {e}"

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    entries = root.findall("atom:entry", namespace)
    results = []

    for entry in entries:
        title = entry.find("atom:title", namespace)
        authors = entry.findall("atom:author/atom:name", namespace)
        published = entry.find("atom:published", namespace)
        link = entry.find("atom:id", namespace)
        summary = entry.find("atom:summary", namespace)

        if title is None or published is None or link is None:
            continue

        title_text = (title.text or "").strip().lower()
        summary_text = (summary.text or "").strip().lower() if summary is not None else ""

        # Ensure at least one meaningful topic keyword appears in the title or summary
        relevant = any(
            word in title_text or word in summary_text
            for word in topic_words
        ) if topic_words else True

        if not relevant:
            continue

        results.append(
            f"SOURCE:\n"
            f"Title: {(title.text or '').strip()}\n"
            f"URL: {(link.text or '').strip()}\n"
            f"Authors: {', '.join((author.text or '').strip() for author in authors)}\n"
            f"Published: {(published.text or '')[:10]}"
        )

    if not results:
        return f"NO_RESULTS: No arXiv papers found for: {topic}"

    return "\n\n".join(results)