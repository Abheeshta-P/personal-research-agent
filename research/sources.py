from tools.arxiv import search_arxiv
from tools.files import search_files
from tools.web import search_web
from tools.wikipedia import search_wikipedia, get_wikipedia_article

RESEARCH_SOURCES = {
    "1": "Wikipedia",
    "2": "Web",
    "3": "Research Papers",
    "4": "Files",
    "5": "All",
}

SOURCE_TOOLS = {
    "Wikipedia": [
        search_wikipedia,
        get_wikipedia_article,
    ],

    "Web": [
        search_web,
    ],

    "Research Papers": [
        search_arxiv,
        # search_ieee,
        # search_acm,
    ],

    "Files": [
        search_files,
    ],
}

def choose_source():
    print("\nChoose a research source:")

    for key, source in RESEARCH_SOURCES.items():
        print(f"{key}. {source}")

    choice = input("Enter your choice: ")

    # if rubbish is put in the choice falls back to All 
    return RESEARCH_SOURCES.get(choice, "All")

def get_research_tools(source: str):
    if source == "All":
        tools = []

        for source_tools in SOURCE_TOOLS.values():
            # you get one flat list
            tools.extend(source_tools)
        
        return tools

    return SOURCE_TOOLS.get(source, [])
