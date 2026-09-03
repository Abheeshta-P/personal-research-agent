from langchain_core.messages import HumanMessage

# main graph
from graphs.main_graph import graph

from output.display import save_research_prompt
from output.save_research import markdown_to_text

# --------------------------- RUN ---------------------------------

# Prompt the user for input query
question = input("What's on your mind?: ")

# Run the query through the main LangGraph orchestrator
result = graph.invoke({
    "messages": [
        HumanMessage(content=question)
    ],
})

# Safely extract the final message content
last_message = result["messages"][-1]
answer = getattr(last_message, "text", None) or getattr(last_message, "content", str(last_message))

# Check if research failed to find relevant evidence
is_failed = False
if isinstance(answer, str) and answer.startswith("RESEARCH_FAILED:"):
    is_failed = True
    # Strip the internal failure prefix for clean user display
    answer = answer.replace("RESEARCH_FAILED:", "").strip()

# Print clean plain text to console (stripping raw markdown asterisks, hashes, and link syntax)
print(f"\nAnswer:\n{markdown_to_text(answer)}\n")

# Only prompt to save research if valid content was generated
if not is_failed:
    print("\nNote: AI-generated research may contain inaccuracies or hallucinations. Please cross-check important facts with the cited sources.")
    save_research_prompt(
        question,
        answer,
    )