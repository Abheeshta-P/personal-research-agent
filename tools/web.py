from langchain_core.tools import tool
import requests

@tool
def search_web(topic: str) -> str:
    """Search the web for current or general information."""
    url = "https://www.google.com/search"

    print(f"Searching web for: {topic}")

    response = requests.get(
        url,
        params={"q":topic},
        headers={"User-Agent":"Mozilla/5.0"},
        timeout=10
    )

    return f"Searched: {topic}\n\n{response}"