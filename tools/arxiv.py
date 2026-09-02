import requests
import xml.etree.ElementTree as ET

from langchain_core.tools import tool



@tool
def search_arxiv(topic:str) -> str:
    """Search arXiv for research papers on a topic."""

    import re

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

    root = ET.fromstring(response.text)

    namespace = {
        "atom":"http://www.w3.org/2005/atom"
    }

    results = []

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    entries = root.findall("atom:entry", namespace)

    results = []

    for i, entry in enumerate(entries, 1):
        title = entry.find("atom:title", namespace)
        authors = entry.findall("atom:author/atom:name", namespace)
        published = entry.find("atom:published", namespace)
        link = entry.find("atom:id", namespace)
        summary = entry.find("atom:summary", namespace)


        # At least one meaningful topic term must appear
        # in the paper title or abstract.
        title_text = title.text.strip().lower()
        summary_text = summary.text.strip().lower()

        relevant = any(
            word in title_text or word in summary_text
            for word in topic_words
        )

        if not relevant:
            continue

        results.append(
            f"SOURCE:\n"
            f"Title: {title.text.strip()}\n"
            f"URL: {link.text.strip()}\n"
            f"Authors: {', '.join(author.text.strip() for author in authors)}\n"
            f"Published: {published.text[:10]}"
        )

    if not results:
        return f"NO_RESULTS: No arXiv papers found for: {topic}"

    return "\n\n".join(results)