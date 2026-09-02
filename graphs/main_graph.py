from langgraph.graph import StateGraph, START, END
from states.state import AgentState
from agents.main_agent import agent, tool_node

# conditional rendering of tools in main graph
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END

def should_continue_after_tools(state: AgentState):
    last_message = state["messages"][-1]
    
    if last_message.type == "tool" and isinstance(last_message.content, str):
        if last_message.content.startswith("RESEARCH_FAILED:"):                                                                                                                                     
            return END

    return "agent"

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

# always returns to agent graph_builder.add_edge("tools", "agent") hence add conditionals
graph_builder.add_conditional_edges("tools", should_continue_after_tools, {"agent":"agent", END:END})

#complete the graph/ create it
graph = graph_builder.compile()