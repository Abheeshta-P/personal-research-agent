from pathlib import Path
from langchain_core.tools import tool

DOCUMENTS_DIR = Path("data/documents")

@tool
def search_files(topic:str) -> str:
    """Search local documents for information related to a topic."""

    results = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        if topic.lower() in text.lower():
            results.append(
                f"File: {file_path.name}\n"
                f"Content:\n{text}"
            )

    if not results:
        return f"No relevant files found for: {topic}"

    return "\n\n".join(results)


if __name__ == "__main__":
    result = search_files.invoke({
        "topic": "self-attention"
    })

    print(result)
        