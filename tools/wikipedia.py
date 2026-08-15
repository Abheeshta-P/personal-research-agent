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
  

    headers = {
        "User-Agent": "ai-research-agent/0.1"
    }

    # exact search 
    exact_params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "explaintext": True,
    "titles": topic,
    }

    exact_response = requests.get(
        url,
        params=exact_params,
        headers=headers
    )

    print(exact_response.status_code)
    exact_data = exact_response.json()

    pages = exact_data["query"]["pages"]
    page = next(iter(pages.values()))

    if "missing" in page:
        print(f"No exact Wikipedia article found for: {topic}")

        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": topic,
            "srlimit": 5,
        }

        search_response = requests.get(
            url,
            params=search_params,
            headers=headers,
        )

        print(search_response.status_code)

        search_data = search_response.json()
        search_results = search_data["query"]["search"]

        if not search_results:
            return f"No Wikipedia results found for: {topic}"

        return search_results

    # 1. random rank search 
    # search_params = {
    #     "action": "query",
    #     "format": "json",
    #     "list": "search",
    #     "srsearch": topic,
    #     "srlimit": 5,
    # }

    # response = requests.get(url, params=search_params, headers=headers)

    # print(response.status_code)

    # data = response.json()

    # search_results = data["query"]["search"]

    # print(search_results)

    # if not search_results:
    #     return f"No Wikipedia article found for: {topic}"

    # title = search_results[0]["title"]

    # print(f"Found article: {title}")

    # 2. as per title article data 

    # article_params = {
    #     "action": "query",
    #     "format": "json",
    #     "prop": "extracts",
    #     "explaintext": True,
    #     "titles": title,
    # }

    # response = requests.get(
    #     url,
    #     params=article_params,
    #     headers=headers,
    # )

    # print(response.status_code)

    # article_data = response.json()

    # pages = article_data["query"]["pages"]
    # page = next(iter(pages.values()))

    # extract = page.get("extract")

    # if not extract:
    #     return f"No article content found for: {title}"

    # return extract

    # return str(article_data)

    # return response.text