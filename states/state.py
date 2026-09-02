from typing import Annotated, TypedDict

# We're going to use it to tell LangGraph how the messages state should be updated.
# reducer: what to do when state gets updated? replace or add
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

# each node looks like this in that graph 
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]

# Make the research request itself a tool/route that Gemini can choose.
class ResearchState(TypedDict): 
    messages: Annotated[list[AnyMessage], add_messages]
    searches_done: list[str]
    sources_used: list[str]
    source: str
    evidence_found: bool
