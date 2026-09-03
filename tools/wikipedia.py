import time
import requests
from langchain_core.tools import tool

# Coherent User-Agent header to comply with Wikimedia bot policy and avoid 429 blocks
USER_AGENT = "PersonalResearchAgent/1.0"

@tool
def search_wikipedia(topic: str) -> str:
    """Search Wikipedia for relevant articles."""

    print(f"Searching Wikipedia for: '{topic}'...")

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": topic,
        "srlimit": 5,
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    response = None
    last_error = None
    
    # Retry loop: allow up to 2 attempts with a 30s timeout
    for attempt in range(2):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.Timeout:
            last_error = f"NO_RESULTS: Wikipedia search timed out for: {topic}"
            if attempt == 0:
                time.sleep(1)
                continue
        except Exception as e:
            last_error = f"NO_RESULTS: Wikipedia search failed: {e}"
            if attempt == 0:
                # If rate-limited (HTTP 429), pause 2s before retry; otherwise pause 1s
                time.sleep(2 if "429" in str(e) else 1)
                continue

    # Return failure message if all attempts fail
    if response is None:
        return last_error or f"NO_RESULTS: Wikipedia search failed for: {topic}"

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

    print(f"Fetching Wikipedia article: '{title}'...")

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    response = None
    last_error = None

    # Retry loop: allow up to 2 attempts with a 30s timeout for large article extracts
    for attempt in range(2):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.Timeout:
            last_error = f"NO_RESULTS: Fetching Wikipedia article timed out for: {title}"
            if attempt == 0:
                time.sleep(1)
                continue
        except Exception as e:
            last_error = f"NO_RESULTS: Failed to fetch Wikipedia article: {e}"
            if attempt == 0:
                # If rate-limited (HTTP 429), pause 2s before retry; otherwise pause 1s
                time.sleep(2 if "429" in str(e) else 1)
                continue

    # Return failure message if all attempts fail
    if response is None:
        return last_error or f"NO_RESULTS: Failed to fetch Wikipedia article for: {title}"

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