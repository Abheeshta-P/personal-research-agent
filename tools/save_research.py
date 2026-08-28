from pathlib import Path
import re

def create_filename(topic:str, extention:str) -> str:
    """Create a safe filename from the research topic."""

    filename = re.sub(
        r"[^a-zA-Z0-9\s-]",
        "",
        topic,
    )

    filename = re.sub(
        r"\s+",
        "_",
        filename.strip(),
    )

    filename = filename[:80]

    if not filename:
        filename = "research"

    return f"{filename}.{extention}"


def markdown_to_text(content: str) -> str:
    """Convert basic Markdown formatting into plain text."""

    text = content

     # Markdown links:
    # [Wikipedia](https://...)
    # ->
    # Wikipedia (https://...)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"\1 (\2)",
        text,
    )

    # Headings
    text = re.sub(
        r"^#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Bold
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text,
    )

    # Italic
    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text,
    )

    # Inline code
    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

    # Horizontal rules
    text = re.sub(
        r"^\s*[-*_]{3,}\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    return text.strip()


def save_research(
        topic: str,
        content: str,
        extension: str,
) -> str:
    """Save research as Markdown or plain text."""

    if extension not in {"md", "txt"}:
        return "Unsupported file format."

    research_dir = Path("research")

    research_dir.mkdir(exist_ok=True)

    if extension == "txt":
        content = markdown_to_text(content)

    filename = create_filename(topic, extension)

    file_path = research_dir/filename

    file_path.write_text(content, encoding="utf-8")

    return f"Research saved to: {file_path}"