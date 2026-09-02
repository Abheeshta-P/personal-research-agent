from langchain_core.messages import HumanMessage

# main graph
from graphs.main_graph import graph

from output.display import save_research_prompt

# --------------------------- RUN ---------------------------------

question = input("What's on your mind?: ")

result = graph.invoke({
    "messages": [
        HumanMessage(content=question)
    ],
})

last_message = result["messages"][-1]
answer = getattr(last_message, "text", None) or getattr(last_message, "content", str(last_message))

is_failed = False
if isinstance(answer, str) and answer.startswith("RESEARCH_FAILED:"):
    is_failed = True
    answer = answer.replace("RESEARCH_FAILED:", "").strip()

print("\n" + "─" * 50)
print("ANSWER")
print("─" * 50)
print(answer)
print("─" * 50)

if not is_failed:
    save_research_prompt(
        question,
        answer,
    )