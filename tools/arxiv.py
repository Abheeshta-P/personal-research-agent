import requests
import xml.etree.ElementTree as ET

from langchain_core.tools import tool



@tool
def search_arxiv(topic: str) -> str:
    """Search arXiv for research papers on a topic."""

    print(f"Searching arXiv for: '{topic}'...")

    import re

    # Remove extra quotes and clean the query string
    clean_topic = re.sub(r'["\']', '', topic).strip()

    # Formulate query: combine exact phrase match with top keywords joined by AND
    words = [w for w in re.findall(r"\b\w+\b", clean_topic) if len(w) > 2]
    if len(words) >= 2:
        search_query = f'all:"{clean_topic}" OR ({" AND ".join(f"all:{w}" for w in words[:3])})'
    else:
        search_query = f"all:{clean_topic}"

    url = "https://export.arxiv.org/api/query"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": 5,
    }

    # Set descriptive User-Agent header to avoid request throttling
    headers = {
        "User-Agent": "PersonalResearchAgent/1.0"
    }

    import time
    response = None
    last_error = None

    # Retry loop: allow up to 2 attempts (1 initial + 1 retry) with a 60s timeout for peak server loads
    for attempt in range(2):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            break
        except requests.exceptions.Timeout:
            last_error = f"NO_RESULTS: arXiv search timed out for: {topic}"
            if attempt == 0:
                print("arXiv is taking longer than expected, retrying...")
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            last_error = f"NO_RESULTS: arXiv search failed: {e}"
            if attempt == 0:
                time.sleep(2)

    # Return recorded failure if all attempts fail
    if response is None or not response.ok:
        return last_error or f"NO_RESULTS: arXiv search failed for: {topic}"

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

        results.append(
            f"SOURCE:\n"
            f"Title: {(title.text or '').strip()}\n"
            f"URL: {(link.text or '').strip()}\n"
            f"Authors: {', '.join((author.text or '').strip() for author in authors)}\n"
            f"Published: {(published.text or '')[:10]}\n\n"
            f"CONTENT:\n{(summary.text or '').strip() if summary is not None else ''}"
        )

    if not results:
        return f"NO_RESULTS: No arXiv papers found for: {topic}"

    return "\n\n".join(results)