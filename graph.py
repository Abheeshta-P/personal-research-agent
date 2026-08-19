# Think of LangGraph as a way to draw our program as a flowchart that can actually run.
# State is the information our graph carries around while it works.
# For our agent, the most important state will initially be: message


from langgraph.graph import StateGraph, START, END

from typing import Annotated, TypedDict
# We're going to use it to tell LangGraph how the messages state should be updated.
from langchain_core.messages import AnyMessage, HumanMessage
# HumanMessage
# AIMessage
# ToolMessage
# SystemMessage
from langgraph.graph.message import add_messages
# reducer: what to do when state gets updated? replace or add

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode

# tool
from tools.calculator import calculator
from tools.wikipedia import research_wikipedia

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# tools
# @tool
# def calculator(a: float, b: float) -> float:
#     """Add two numbers together."""
#     return a + b

model_with_tools = model.bind_tools([
    calculator,
    research_wikipedia,
])

# make this tool a node 
tool_node = ToolNode([
    calculator,
    # research_wikipedia,
])

research_model = model.bind_tools([
    research_wikipedia,
])


# the researcher doesnt have normal nodes like just llm most are tool nodes 
research_tool_node = ToolNode([
    research_wikipedia,
])

# each node looks like this in that graph 
class AgentState:
    messages: Annotated[list[AnyMessage],add_messages]

# Make the research request itself a tool/route that Gemini can choose.
class ResearchState: 
    messages: Annotated[list[AnyMessage], add_messages]

graph_builder = StateGraph(AgentState)
research_builder = StateGraph(ResearchState)

#node

# def agent(state:AgentState):
#     print("Agent node running!")
#     return {} #"Don't modify the state."
# def agent(state: AgentState):
#     print("Agent node running!")
#     print("Current state:", state)

#     return {}

def agent(state: AgentState):
    # response = model.invoke(state["messages"])
    response = model_with_tools.invoke(state["messages"])

    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Agent called tool: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
    else:
        print(f"Final answer: {response.text}")

    return {
        "messages": [response]
    }

def researcher(state:ResearchState):
    response = research_model.invoke(state["messages"])

    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Researcher called tool: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
    else:
        print(f"Researcher answer: ${response.text}")
    
    return {
        "messages":[response]
    }

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

# adding node 
graph_builder.add_node("agent",agent)
# graph_builder.add_node("calculator", calculator) wrong
graph_builder.add_node("tools",tool_node)

# add edge
graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue
)

graph_builder.add_edge("tools", "agent")
# graph_builder.add_edge("agent",END) handled by the conditional edges

#complete the graph/ create it
graph = graph_builder.compile()

# every graph starts with an llm call
research_builder.add_node("researcher", researcher)
research_builder.add_node("research_tools", research_tool_node)

research_builder.add_edge(START, "researcher")
research_builder.add_conditional_edges(
    "researcher",
    research_should_continue
)
# tool call should return result to agent 
research_builder.add_edge("research_tools", "researcher")

research_graph = research_builder.compile()

#run
# result = graph.invoke({
#     "messages":[
#         HumanMessage(content="What is 25 multiplied by 9?")
#     ]
# })

# result = research_wikipedia.invoke({"topic": "LangGraph"})
# print(result)

# result = graph.invoke({
#     "messages": [
#         HumanMessage(content="What is LangGraph?")
#     ]
# })

result = research_graph.invoke({
    "messages": [
        HumanMessage(content="Research LangGraph on Wikipedia")
    ]
})

# print(result["messages"][-1].text)

                #          USER
                #            │
                #            ▼
                # "What is 25 + 9?"
                #            │
                #            ▼
                #     ┌───────────┐
                #     │   AGENT   │
                #     │  Gemini   │
                #     └─────┬─────┘
                #           │
                #     tool call?
                #        YES
                #           │
                #           ▼
                #     ┌───────────┐
                #     │   TOOLS   │
                #     │ calculator│
                #     └─────┬─────┘
                #           │
                #         34.0
                #           │
                #           ▼
                #     ┌───────────┐
                #     │   AGENT   │
                #     │  Gemini   │
                #     └─────┬─────┘
                #           │
                #     tool call?
                #          NO
                #           │
                #           ▼
                #          END

        #                  USER
        #                    │
        #                    ▼
        #              GEMINI AGENT
        #                    │
        #      ┌─────────────┼─────────────┐
        #      │             │             │
        #      ▼             ▼             ▼
        #   Answer       Calculator     Research
        #                                 │
        #                                 ▼
        #                            RESEARCHER