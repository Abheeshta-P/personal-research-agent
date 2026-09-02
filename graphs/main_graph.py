from langgraph.graph import StateGraph, START, END
from states.state import AgentState
from agents.main_agent import agent, tool_node

# Routing after the main agent runs:
# If the agent requests a tool call (e.g., calculator or research), route to "tools".
# Otherwise, finish the graph and return the response.
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END

# Routing after tool execution:
# If the research tool failed to find evidence in the selected source, terminate immediately at END
# to prevent the main agent LLM from hallucinating an answer from its internal memory.
# Otherwise, route back to "agent" for synthesis.
def should_continue_after_tools(state: AgentState):
    last_message = state["messages"][-1]
    
    if last_message.type == "tool" and isinstance(last_message.content, str):
        if last_message.content.startswith("RESEARCH_FAILED:"):                                                                                                                                     
            return END

    return "agent"

# Build the main StateGraph
graph_builder = StateGraph(AgentState)

# Add agent and tool nodes
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)

# Connect START to the main agent node
graph_builder.add_edge(START, "agent")

# Add conditional routing from the agent
graph_builder.add_conditional_edges(
    "agent",
    should_continue
)

# Add conditional routing after tool execution
graph_builder.add_conditional_edges(
    "tools",
    should_continue_after_tools,
    {"agent": "agent", END: END}
)

# complete the graph/ create it
graph = graph_builder.compile()