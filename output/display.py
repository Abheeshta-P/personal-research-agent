# Prompts the user to save research output in Markdown or plain Text format
def save_research_prompt(question: str, answer: str):

    print("\nHow would you like to save this research?")
    print("1. Markdown (.md)")
    print("2. Text (.txt)")
    print("3. Don't save")

    choice = input("Enter your choice: ").strip()

    if choice == "3":
        print("Research not saved.")
        return

    if choice not in ["1", "2"]:
        print("Invalid choice. Research not saved.")
        return

    from output.save_research import save_research

    # Map menu selection to appropriate file extension
    extension = "md" if choice == "1" else "txt"

    # Save research to output directory
    result = save_research(
        topic=question,
        content=answer,
        extension=extension,
    )

    print(result)
