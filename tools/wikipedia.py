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

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    results = data["query"]["search"]

    if not results:
        return f"No Wikipedia results found for: {topic}"

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

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    extract = page.get("extract")

    if not extract:
        return f"No article content found for: {title}"

    return (
        f"SOURCE:\n"
        f"Title: {title}\n"
        f"URL: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}\n\n"
        f"CONTENT:\n{extract}"
    )