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

     # Existing file
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

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return f"Research saved to: {file_path}"