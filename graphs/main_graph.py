from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from agents.main_agent import agent, tool_node

# conditional rendering of tools in main graph
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END

graph_builder = StateGraph(AgentState)

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