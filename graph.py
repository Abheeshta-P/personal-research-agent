from langgraph.graph import StateGraph, START, END


from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode

# model
from agents.model import model

# states
from research.state import AgentState, ResearchState

# source
from research.sources import choose_source, get_research_tools

# tool
from tools.calculator import calculator

# research agent 
from agents.researcher import researcher, update_searches


@tool
def research(topic: str) -> str:
    """Research a topic using a user-selected source."""
    # select source when research tool call is done

    source = choose_source()

    # call the llm with research tool as first step 
    result = research_graph.invoke({ 
        "messages": [
            HumanMessage(content=f"Research {topic}")
        ], 
        "searches_done": [],
        "sources_used": [],
        "source": source,
    })

    return result["messages"][-1].text


# main model
model_with_tools = model.bind_tools([
    calculator,
    # research_wikipedia,
    research,
])

# make this tool a node 
tool_node = ToolNode([
    calculator,
    # research_wikipedia, add the researcher as a tool instead
    research,
])


def research_tools(state: ResearchState):
    tools = get_research_tools(state["source"])
    return ToolNode(tools).invoke(state)


graph_builder = StateGraph(AgentState)
research_builder = StateGraph(ResearchState)

# node

# main
def agent(state: AgentState):
    messages = [
            SystemMessage(content="""
    You are the main agent.

    Use the research tool when the user asks for:
    - factual information that may require external sources
    - current or potentially changing information
    - detailed explanations where reliable source material is useful
    - research questions
    - Call the research tool at most once for a user request.
    - Pass the complete user question to the research tool.
    - Do not split one research request into multiple research tool calls.
    - The research agent will decide how to investigate the question.

    Use the calculator for mathematical calculations.

    If the question can be answered reliably without a tool, answer directly.

    When using the result from the research tool:
    - Preserve the Sources section from the research result.
    - Include the retrieved sources in your final answer.
    - Only use URLs explicitly provided by the research result.
    - Do not invent, modify, or hallucinate URLs.
    """),
            *state["messages"]
    ]

    response = model_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# conditional rendering of tools
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END

def research_should_continue(state: ResearchState):
    last_message = state["messages"][-1]

    # it will choose the tool out of the list 
    if last_message.tool_calls:
        return "research_tools"
    
    return END

def save_research_prompt(question: str, answer: str):

    print("\n" + "─" * 50)
    print("How would you like to save this research?")
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

    from tools.save_research import save_research

    extension = "md" if choice == "1" else "txt"

    result = save_research(
        topic=question,
        content=answer,
        extension=extension,
    )

    print(result)
    
# adding node 
graph_builder.add_node("agent",agent)
graph_builder.add_node("tools",tool_node)

# add edge
graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue
)

graph_builder.add_edge("tools", "agent")

#complete the graph/ create it
graph = graph_builder.compile()

# every graph starts with an llm call
research_builder.add_node("researcher", researcher)
research_builder.add_node("update_searches", update_searches)
# research_builder.add_node("research_tools", research_tool_node)
research_builder.add_node("research_tools", research_tools)

research_builder.add_edge(START, "researcher")
research_builder.add_conditional_edges(
    "researcher",
    research_should_continue
)
# tool call should return result to agent 
research_builder.add_edge("research_tools", "update_searches")
# between tool call and researcher
research_builder.add_edge("update_searches", "researcher")

research_graph = research_builder.compile()

# --------------------------- RUN ---------------------------------

question = input("What's on your mind?: ")

# select source when research tool call is done for research not here

result = graph.invoke({
    "messages": [
        HumanMessage(content=question)
    ],
})

# print(f"\n\nFINAL RESULT: \n{result["messages"][-1].text}")
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