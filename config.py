from tools.arxiv import search_arxiv
from tools.files import search_files
from tools.web import search_web
from tools.wikipedia import search_wikipedia, get_wikipedia_article

# Available research sources mapped to option numbers
RESEARCH_SOURCES = {
    "1": "Wikipedia",
    "2": "Web",
    "3": "Research Papers",
    "4": "Files",
    "5": "All",
}

# Mapping of research sources to their specific tool implementations
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
    ],

    "Files": [
        search_files,
    ],
}

# Prompts user via CLI to choose their desired research source
def choose_source():
    print("\nChoose a research source:")

    for key, source in RESEARCH_SOURCES.items():
        print(f"{key}. {source}")

    choice = input("Enter your choice: ").strip()

    # Default fallback to "All" if an unrecognized choice is provided
    return RESEARCH_SOURCES.get(choice, "All")

# Returns the list of tool functions bound to a specific research source
def get_research_tools(source: str):
    if source == "All":
        tools = []
        for source_tools in SOURCE_TOOLS.values():
            tools.extend(source_tools)
        return tools

    return SOURCE_TOOLS.get(source, [])
