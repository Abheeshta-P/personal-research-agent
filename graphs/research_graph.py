from langgraph.prebuilt import ToolNode
from states.state import ResearchState
from langgraph.graph import StateGraph, START, END
from agents.researcher import researcher, update_searches, get_research_tools

# util to select dynamic tools based on source and attach it to graph
def research_tools(state: ResearchState):
    tools = get_research_tools(state["source"])
    result = ToolNode(tools).invoke(state)
    return result

# Conditional edge after researcher agent:
# If tool calls are generated, execute them via research_tools; otherwise, end the research subgraph.
def research_should_continue(state: ResearchState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "research_tools"

    return END

# Conditional edge after updating searches and evidence:
# If valid evidence was retrieved, loop back to the researcher agent for answer synthesis.
# If no evidence was found, exit immediately to END to prevent the LLM from hallucinating an answer.
def after_update(state: ResearchState):
    if state.get("evidence_found", False):
        return "researcher"
    return END

# Build the research StateGraph
research_builder = StateGraph(ResearchState)

# Add nodes for researcher LLM, search tracking, and dynamic tool execution
research_builder.add_node("researcher", researcher)
research_builder.add_node("update_searches", update_searches)
research_builder.add_node("research_tools", research_tools)

# Connect START to the researcher node
research_builder.add_edge(START, "researcher")

# Route to tools if tool calls are present
research_builder.add_conditional_edges(
    "researcher",
    research_should_continue
)

# Route tool results to update_searches for evidence tracking
research_builder.add_edge("research_tools", "update_searches")

# between tool call and researcher
# Check evidence: synthesize answer if evidence found, otherwise exit early
research_builder.add_conditional_edges(
    "update_searches",
    after_update
)

# Compile the research subgraph
research_graph = research_builder.compile()