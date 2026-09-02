from langchain_core.messages import HumanMessage

# main graph
from graphs.main_graph import graph

from output.display import save_research_prompt

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

print("\n" + "─" * 50)
print("ANSWER")
print("─" * 50)
print(answer)
print("─" * 50)

# Only prompt to save research if valid content was generated
if not is_failed:
    save_research_prompt(
        question,
        answer,
    )