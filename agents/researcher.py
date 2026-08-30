from langchain_core.messages import SystemMessage

from agents.model import model
from config import get_research_tools
from states.state import ResearchState

# research agent
def researcher(state:ResearchState):
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
            Do not use another source.

            Always research before answering.

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

            1. A concise synthesized answer.
            2. A Sources section.

            Citation rules:
            - ALWAYS include a Sources section.
            - If you used a research tool, the Sources section MUST NOT be empty.
            - Use ONLY sources explicitly returned by the research tools.
            - For Research Papers, include the actual paper title and URL returned by search_arxiv.
            - For Web, include the URLs returned by search_web.
            - For Wikipedia, include the Wikipedia URL returned by the Wikipedia tools.
            - For Files, include the actual filenames returned by search_files.
            - Do NOT say that a source is unnecessary because the information is common knowledge, foundational knowledge, or well established.
            - Do NOT omit sources because the topic is well known.
            - NEVER invent a source.
            - NEVER create or modify a URL.
            - If a research tool returned evidence but you cannot determine the source information, explicitly say:
            "Sources could not be extracted from the tool result."
            Do not fabricate one.
            """),

        *state["messages"]
    ]

    response = research_model.invoke(messages)

    return {
        "messages":[response]
    }

# between the tool calls track the search and search source
def update_searches(state: ResearchState):
    searches = state.get("searches_done", []).copy()
    sources = state.get("sources_used", []).copy()

    # Track searches made by the researcher ai output
    for message in reversed(state["messages"]):
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if "topic" in tool_call["args"]:
                    topic = tool_call["args"]["topic"].lower()

                    if topic not in searches:
                        searches.append(topic)
            break

    # Store the actual tool result
    for message in reversed(state["messages"]):
        if message.type == "tool":
            sources.append(message.content)
            break

    return {
        "searches_done": searches,
        "sources_used": sources,
    }
