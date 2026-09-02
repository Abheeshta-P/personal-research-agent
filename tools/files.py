from pathlib import Path
from langchain_core.tools import tool

from pypdf import PdfReader
from docx import Document

# Directory containing local research documents
DOCUMENTS_DIR = Path("data/documents")

# Extract text content from PDF files using pypdf
def read_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)

# Extract text paragraphs from DOCX files
def read_docx(file_path: Path) -> str:
    document = Document(file_path)
    paragraphs = []
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)
    return "\n".join(paragraphs)

# Read file based on its extension (.txt, .md, .pdf, .docx)
def read_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    if ext in [".txt", ".md"]:
        return file_path.read_text(encoding="utf-8")

    if ext == ".pdf":
        return read_pdf(file_path)

    if ext == ".docx":
        return read_docx(file_path)

    return ""


@tool
def search_files(topic: str) -> str:
    """Search local documents for information related to a topic."""

    print(f"Searching local documents for: '{topic}'...")

    # Ensure document folder exists before searching
    if not DOCUMENTS_DIR.exists():
        return f"NO_RESULTS: Documents directory '{DOCUMENTS_DIR}' does not exist."

    import re
    # Extract significant alphanumeric keywords (3+ characters)
    topic_words = [
        word.lower()
        for word in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", topic)
    ]

    results = []

    # Iterate over all files in the documents directory
    for file_path in DOCUMENTS_DIR.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in [".txt", ".md", ".pdf", ".docx"]:
            continue

        try:
            text = read_file(file_path)
        except Exception as e:
            continue

        filename = file_path.stem.lower()
        text_lower = text.lower()

        # Match exact topic substring or fallback to individual keyword matches
        matched = (topic.lower() in filename or topic.lower() in text_lower)
        if not matched and topic_words:
            matched = any(word in filename or word in text_lower for word in topic_words)

        if matched:
            results.append(
                f"SOURCE:\n"
                f"Title: {file_path.name}\n"
                f"URL: local://{file_path.name}\n\n"
                f"CONTENT:\n{text}"
            )

    # Return standard failure string if no matching files found
    if not results:
        return f"NO_RESULTS: No relevant files found for: {topic}"

    return "\n\n".join(results)
