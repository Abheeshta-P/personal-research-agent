from langgraph.prebuilt import ToolNode
from states.state import ResearchState
from langgraph.graph import StateGraph, START, END
from agents.researcher import researcher, update_searches, get_research_tools

# util to select dynamic tools based on source and attach it to graph
def research_tools(state: ResearchState):
    print("\n[DEBUG] research_tools() ENTERED")
    print("source:", state["source"])
    print("messages:", state["messages"])

    tools = get_research_tools(state["source"])

    result = ToolNode(tools).invoke(state)

    print("[DEBUG] research_tools() RESULT:")
    print(result)

    return result

# conditional rendering of tools in research graph
def research_should_continue(state: ResearchState):
    last_message = state["messages"][-1]

    # it will choose the tool out of the list 
    if last_message.tool_calls:
        return "research_tools"

    return END

def after_update(state: ResearchState):
    if state.get("evidence_found", False):
        return "researcher"
    return END

research_builder = StateGraph(ResearchState)

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
research_builder.add_conditional_edges(
    "update_searches",
    after_update
)

research_graph = research_builder.compile()