from langchain_core.messages import SystemMessage

from agents.model import model
from config import get_research_tools
from states.state import ResearchState

# research agent
def researcher(state: ResearchState):
    source = state["source"]
    searches = state.get("searches_done", [])
    sources_used = state.get("sources_used", [])

    research_tools = get_research_tools(source)
    research_model = model.bind_tools(research_tools)

    messages = [
        SystemMessage(content=f"""
        You are a research agent.

        The user selected this research source:
        {source}

        Only use the tools available to you for that source.

        IMPORTANT:
        - You MUST base your answer only on evidence returned by the selected source.
        - If the selected source cannot find relevant information, DO NOT answer from your own knowledge.
        - Instead return exactly:
          "Could not find relevant information in the selected source: {source}"
        - Never invent or fill gaps using your own knowledge.
        - Never use another source.
        - Always research before answering.

        Previous searches:
        {searches}

        Sources already used:
        {sources_used}

        Rules:
            - Do not repeat a previous search.
            - Do not rephrase a previous search just to search the same information again.
            - If a tool says the query was already searched, use the existing evidence.
            - Continue researching only when a genuinely new search can add evidence.
            - Stop when you have sufficient reliable evidence.
            - When writing the Sources section, use ONLY URLs, filenames, or source information explicitly present in the tool results stored in Sources already used.
            - Do not invent sources.
            - Do not add sources from your own knowledge.

        At the end, ALWAYS provide:
            1. A concise synthesized answer based ONLY on retrieved evidence.
            2. A Sources section containing ONLY sources found in the tool results.
        """),
        *state["messages"]
    ]

    print("\n[DEBUG] researcher()")
    print("source:", source)
    print("messages:", state["messages"])
    print("tools:", [tool.name for tool in research_tools])
    response = research_model.invoke(messages)
    print("[DEBUG] researcher response:")
    print("content:", response.content)
    print("tool_calls:", response.tool_calls)

    return {
        "messages": [response]
    }

# between the tool calls track the search and search source
def update_searches(state: ResearchState):

    print("\n[DEBUG] update_searches() ENTERED")
    print("messages:", state["messages"])
    searches = state.get("searches_done", []).copy()
    sources = state.get("sources_used", []).copy()

    evidence_found = state.get("evidence_found", False)

    # Evidence Reset in Multi-Step Research
    for message in reversed(state["messages"]):
        if message.type == "tool":
            content = str(message.content)
            if content and not content.startswith("NO_RESULTS:"):
                evidence_found = True
        elif message.type == "ai":
            break

    # Track searches made by the researcher ai output
    for message in reversed(state["messages"]):
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if "topic" in tool_call["args"]:
                    topic = tool_call["args"]["topic"].lower()

                    if topic not in searches:
                        searches.append(topic)
            break

    print("[DEBUG] evidence_found:", evidence_found)

    return {
        "searches_done": searches,
        "sources_used": sources,
        "evidence_found": evidence_found,
    }
