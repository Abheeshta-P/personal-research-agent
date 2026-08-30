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

answer = result["messages"][-1].text

print("\n" + "─" * 50)
print("ANSWER")
print("─" * 50)
print(answer)
print("─" * 50)

save_research_prompt(
    question,
    answer,
)