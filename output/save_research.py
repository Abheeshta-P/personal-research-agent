from pathlib import Path
import re

# Creates a sanitized filename from the research topic
def create_filename(topic: str, extension: str) -> str:
    """Create a safe filename from the research topic."""

    # Remove non-alphanumeric characters (except spaces and hyphens)
    filename = re.sub(
        r"[^a-zA-Z0-9\s-]",
        "",
        topic,
    )

    # Replace whitespace sequences with single underscores
    filename = re.sub(
        r"\s+",
        "_",
        filename.strip(),
    )

    # Truncate filename length
    filename = filename[:80]

    if not filename:
        filename = "research"

    return f"{filename}.{extension}"


# Converts basic Markdown markup to clean plain text format
def markdown_to_text(content: str) -> str:
    """Convert basic Markdown formatting into plain text."""

    text = content

    # Markdown links:
    # [Wikipedia](https://...) -> Wikipedia (https://...)
    # [https://...] (https://...) -> https://...
    def _clean_link(match):
        label = match.group(1).strip()
        url = match.group(2).strip()
        if label == url:
            return url
        return f"{label} ({url})"

    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        _clean_link,
        text,
    )

    # Strip heading symbols (# Heading -> Heading)
    text = re.sub(
        r"^#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Strip horizontal divider rules (---, ***, ___, * * *, etc.)
    text = re.sub(
        r"^\s*([-*_]\s*){3,}\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Strip bold-italic markup within a line
    text = re.sub(
        r"\*\*\*([^\n]+?)\*\*\*",
        r"\1",
        text,
    )

    # Strip bold markup within a line
    text = re.sub(
        r"\*\*([^\n]+?)\*\*",
        r"\1",
        text,
    )

    # Strip italic markup within a line while preserving bullet points
    text = re.sub(
        r"(?<!\*)\*([^\n*]+?)\*(?!\*)",
        r"\1",
        text,
    )

    # Strip inline code ticks
    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

    # Clean up excessive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()

# Generates an incremental unique filename to avoid overwriting existing files
def get_unique_path(file_path: Path) -> Path:
    """Return a unique path without overwriting an existing file."""

    counter = 1

    while True:
        # Keep the same folder/path, but change the filename. 
        new_path = file_path.with_name(
            f"{file_path.stem}_{counter}{file_path.suffix}"
        )

        if not new_path.exists():
            return new_path

        counter += 1


# Saves generated research to research-output/ in Markdown (.md) or Text (.txt) format
def save_research(
        topic: str,
        content: str,
        extension: str,
) -> str:
    """Save research as Markdown or plain text."""

    if extension not in {"md", "txt"}:
        return "Unsupported file format."

    research_dir = Path("research-output")
    research_dir.mkdir(exist_ok=True)

    if extension == "txt":
        content = markdown_to_text(content)

    filename = create_filename(topic, extension)
    file_path = research_dir / filename

    # Handle existing file conflict interactively
    if file_path.exists():

        print(f"\nA file already exists:")
        print(f"{file_path}")

        print("\nWhat would you like to do?")
        print("1. Overwrite this file")
        print("2. Save as a new file")
        print("3. Cancel")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            pass

        elif choice == "2":
            file_path = get_unique_path(file_path)

        elif choice == "3":
            return "Research not saved."

        else:
            return "Invalid choice. Research not saved."

    # Write research text to disk
    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Research saved to: {file_path}"