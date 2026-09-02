import requests
from langchain_core.tools import tool

@tool
def search_wikipedia(topic: str) -> str:
    """Search Wikipedia for relevant articles."""

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": topic,
        "srlimit": 5,
    }

    headers = {
        "User-Agent": "ai-research-agent/0.1"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"NO_RESULTS: Wikipedia search failed: {e}"

    results = data.get("query", {}).get("search", [])

    if not results:
        return f"NO_RESULTS: No Wikipedia results found for: {topic}"

    # (expression for item in collection) 
    # [...] → list comprehension → creates a list immediately
    # (...) → generator expression → produces values as needed

    return "\n\n".join(
        f"SOURCE:\n"
        f"Title: {result['title']}\n"
        f"URL: https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"
        for result in results
    )


@tool
def get_wikipedia_article(title: str) -> str:
    """Get the full Wikipedia article for a title."""

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
    }

    headers = {
        "User-Agent": "ai-research-agent/0.1"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"NO_RESULTS: Failed to fetch Wikipedia article: {e}"

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return f"NO_RESULTS: No article content found for: {title}"

    page = next(iter(pages.values()))
    extract = page.get("extract")

    if not extract:
        return f"NO_RESULTS: No article content found for: {title}"

    return (
        f"SOURCE:\n"
        f"Title: {title}\n"
        f"URL: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}\n\n"
        f"CONTENT:\n{extract}"
    )