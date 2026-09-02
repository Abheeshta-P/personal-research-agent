from langchain_core.messages import SystemMessage

from agents.model import model
from config import get_research_tools
from states.state import ResearchState

# Specialized researcher agent node: dynamically binds tools for the selected source
def researcher(state: ResearchState):
    source = state["source"]
    searches = state.get("searches_done", [])
    sources_used = state.get("sources_used", [])

    # Dynamically retrieve and bind tools corresponding to the user-selected source
    research_tools = get_research_tools(source)
    research_model = model.bind_tools(research_tools)

    # Inform user when synthesizing retrieved evidence
    if state.get("evidence_found", False):
        print("Synthesizing research findings...")

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

    response = research_model.invoke(messages)

    return {
        "messages": [response]
    }

# Tracks search history, source results, and detects whether valid evidence was found across steps
def update_searches(state: ResearchState):

    searches = state.get("searches_done", []).copy()
    sources = state.get("sources_used", []).copy()

    # Preserve any evidence found in earlier turns
    evidence_found = state.get("evidence_found", False)

    # Inspect tool responses in the current step to determine if valid evidence exists
    for message in reversed(state["messages"]):
        if message.type == "tool":
            content = str(message.content)
            # If tool returns content that does not start with NO_RESULTS, evidence was found
            if content and not content.startswith("NO_RESULTS:"):
                evidence_found = True
        elif message.type == "ai":
            break

    # Track distinct search queries attempted by the researcher ai output
    for message in reversed(state["messages"]):
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if "topic" in tool_call["args"]:
                    topic = tool_call["args"]["topic"].lower()

                    if topic not in searches:
                        searches.append(topic)
            break

    return {
        "searches_done": searches,
        "sources_used": sources,
        "evidence_found": evidence_found,
    }
