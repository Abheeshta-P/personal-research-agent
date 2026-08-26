# Think of LangGraph as a way to draw our program as a flowchart that can actually run.
# State is the information our graph carries around while it works.
# For our agent, the most important state will initially be: message


#                  RESEARCHER
#                      │
#           "What source should I use?"
#                      │
#        ┌─────────────┼─────────────┐
#        ▼             ▼             ▼
#    Wikipedia        Web          Files
#        │             │             │
#        └─────────────┼─────────────┘
#                      ▼
#                 Evidence
#                      │
#                      ▼
#                 Researcher
#                      │
#                      ▼
#               Synthesized answer


from langgraph.graph import StateGraph, START, END

from typing import Annotated, TypedDict
# We're going to use it to tell LangGraph how the messages state should be updated.
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
# reducer: what to do when state gets updated? replace or add

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode

# tool
from tools.calculator import calculator
from tools.wikipedia import search_wikipedia, get_wikipedia_article
from tools.web import search_web
from tools.arxiv import search_arxiv
from tools.files import search_files

load_dotenv()

model = ChatGoogleGenerativeAI(
    # model="gemini-3.6-flash"
    # model="gemini-3.5-flash-lite",
    model="gemini-3.1-flash-lite",
    thinking_level="minimal",
)

RESEARCH_SOURCES = {
    "1": "Wikipedia",
    "2": "Web",
    "3": "Research Papers",
    "4": "Files",
    "5": "All",
}

SOURCE_TOOLS = {
    "Wikipedia": [
        search_wikipedia,
        get_wikipedia_article,
    ],

    "Web": [
        search_web,
    ],

    "Research Papers": [
        search_arxiv,
        # search_ieee,
        # search_acm,
    ],

    "Files": [
        search_files,
    ],
}

def choose_source():
    print("\nChoose a research source:")

    for key, source in RESEARCH_SOURCES.items():
        print(f"{key}. {source}")

    choice = input("Enter your choice: ")

    # if rubbish is put in the choice falls back to All 
    return RESEARCH_SOURCES.get(choice, "All")

def get_research_tools(source: str):
    if source == "All":
        tools = []

        for source_tools in SOURCE_TOOLS.values():
            # you get one flat list
            tools.extend(source_tools)
        
        return tools

    return SOURCE_TOOLS.get(source, [])

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
        "searches_done":[],
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

# # research model
# research_tool_node = ToolNode([
#     search_wikipedia,
#     search_web,
#     get_wikipedia_article,
# ])


# each node looks like this in that graph 
class AgentState:
    messages: Annotated[list[AnyMessage],add_messages]

# Make the research request itself a tool/route that Gemini can choose.
class ResearchState: 
    messages: Annotated[list[AnyMessage], add_messages]
    searches_done: list[str]
    source: str

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
    """),
            *state["messages"]
    ]

    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Agent called tool: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
    else:
        print(f"Final answer: {response.text}")

    return {
        "messages": [response]
    }

# research
def researcher(state:ResearchState):
    source = state["source"]
    searches = state.get("searches_done", [])

    research_tools = get_research_tools(source)
    research_model = model.bind_tools(research_tools)

    messages = [
        SystemMessage(content=f"""
            You are a research agent.

            The user selected this research source:
            {source}

            Only use the tools available to you for that source.
            Do not use another source.

            Always research before answering.

            Previous searches:
            {searches}

            Rules:
            - Do not repeat a previous search.
            - Do not rephrase a previous search just to search the same information again.
            - If a tool says the query was already searched, use the existing evidence.
            - Continue researching only when a genuinely new search can add evidence.
            - Stop when you have sufficient reliable evidence.

            At the end, provide:
            1. A concise synthesized answer.
            2. A Sources section containing only sources actually used with url.
            """),

        *state["messages"]
    ]

    response = research_model.invoke(messages)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Researcher called tool: {tool_call['name']}")
            print(f"Arguments: {tool_call['args']}")
    else:
        print(f"Researcher answer: {response.text}")
    
    return {
        "messages":[response]
    }



# state update node

def update_searches(state: ResearchState):
    searches = state.get("searches_done", []).copy()

    # Find the latest AI message containing tool calls
    for message in reversed(state["messages"]):
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if "topic" in tool_call["args"]:
                    topic = tool_call["args"]["topic"].lower()

                    if topic not in searches:
                        searches.append(topic)
            break

    return {
        "searches_done": searches
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
    "searches_done": []
})

print(f"\n\nFINAL RESULT: \n{result["messages"][-1].text}")
