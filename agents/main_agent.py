from langchain_core.messages import SystemMessage
from core.state import AgentState
from langgraph.prebuilt import ToolNode

# model
from agents.model import model

# tool
from tools.calculator import calculator
from tools.research import research

# create 2 tool node (main tools)
tool_node = ToolNode([
    calculator,
    research,
])

# main model access to tools
model_with_tools = model.bind_tools([
    calculator,
    research,
])

# main agent
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
