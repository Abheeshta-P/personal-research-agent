from pathlib import Path
from langchain_core.tools import tool

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from pypdf import PdfReader
from docx import Document as DocxDocument

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
    document = DocxDocument(file_path)
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
    print(f"Searching local documents with RAG for: '{topic}'...")

    store = get_vector_store()

    # Retrieve top 3 most relevant chunks with distance scores
    results = store.similarity_search_with_score(topic,k=3)

    if not results:
        return f"NO_RESULTS: No relevant files found for: {topic}"

    formatted_results = []
    for doc, score in results:
        # lower dist means (closer)
        if score > 0.85:
            continue
        
        formatted_results.append(
            f"SOURCE:\n"
            f"Title: {doc.metadata['source']}\n"
            f"URL: local://{doc.metadata['source']}\n\n"
            f"CONTENT:\n{doc.page_content}"
        )
    
    if not formatted_results:
        return f"NO_RESULTS: No relevant files found for: {topic}"

    return "\n\n".join(formatted_results)

def load_and_chunk_documents() -> list[Document]:
    if not DOCUMENTS_DIR.exists():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_docs = []

    for file in DOCUMENTS_DIR.iterdir():
        if not file.is_file():
            continue

        text = read_file(file)
        if not text.strip():
            continue

        chunks = splitter.split_text(text)
        for chunk in chunks:
            all_docs.append(Document(page_content=chunk, metadata={"source":file.name}))

    return all_docs


def get_vector_store():
    CHROMA_DIR = Path("data/chroma")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    vector_store = Chroma(
        collection_name = "research_documents",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    current_files = set(f.name for f in DOCUMENTS_DIR.iterdir() if f.is_file()) if DOCUMENTS_DIR.exists() else set()
    data = vector_store.get()
    indexed_files = set(m["source"] for m in data["metadatas"]) if data["metadatas"] else set()

    # If documents were added, deleted, or if Chroma is empty, re-sync!
    if current_files != indexed_files:
        print("Document changes detected. Syncing vector store...")
        vector_store.reset_collection()
        docs = load_and_chunk_documents()
        if docs:
            vector_store.add_documents(docs)
    
    return vector_store
