import requests
from langchain_core.tools import tool

@tool
def research_wikipedia(topic: str) -> str:
    """Research a topic using Wikipedia."""
    print(f"Researching Wikipedia for: {topic}")
    
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action":"query",
        "format":"json",
        "prop":"extracts",
        "exintro":True,
        "explaintext":True,
        "titles":topic,
        }
    response = requests.get(url, params=params)

    print(response.status_code)

    return response.text