from pathlib import Path
from langchain_core.tools import tool

from pypdf import PdfReader
from docx import Document

DOCUMENTS_DIR = Path("data/documents")

def read_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)

def read_docx(file_path: Path) -> str:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)

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
def search_files(topic:str) -> str:
    """Search local documents for information related to a topic."""

    results = []

    # go through all files 
    for file_path in DOCUMENTS_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in [".txt", ".md", ".pdf", ".docx"]:
            continue

        text = read_file(file_path)

        filename = file_path.stem.lower()

        if topic.lower() in filename or topic.lower() in text.lower():
            results.append(
                f"SOURCE:\n"
                f"Title: {file_path.name}\n"
                f"URL: local://{file_path.name}\n\n"
                f"CONTENT:\n{text}"
            )

    if not results:
        return f"No relevant files found for: {topic}"

    return "\n\n".join(results)
