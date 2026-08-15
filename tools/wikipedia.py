import requests
from langchain_core.tools import tool

@tool
def research_wikipedia(topic: str) -> str:
    """Research a topic using Wikipedia."""
    print(f"Researching Wikipedia for: {topic}")
    
    url = "https://en.wikipedia.org/w/api.php"

    # params = {
    #     "action":"query",
    #     "format":"json",
    #     "prop":"extracts",
    #     "exintro":True,
    #     "explaintext":True,
    #     "titles":topic,
    #     }
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": topic,
        "srlimit": 5,
    }

    headers = {
        "User-Agent": "ai-research-agent/0.1"
    }

    response = requests.get(url, params=search_params, headers=headers)

    print(response.status_code)

    data = response.json()

    search_results = data["query"]["search"]

    print(search_results)

    if not search_results:
        return f"No Wikipedia article found for: {topic}"

    title = search_results[0]["title"]

    print(f"Found article: {title}")

    article_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
    }

    response = requests.get(
        url,
        params=article_params,
        headers=headers,
    )

    print(response.status_code)

    article_data = response.json()

    pages = article_data["query"]["pages"]
    page = next(iter(pages.values()))

    extract = page.get("extract")

    if not extract:
        return f"No article content found for: {title}"

    return extract

    # return str(article_data)

    # return response.text