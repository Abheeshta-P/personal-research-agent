# Building an AI Agent with Gemini, LangChain & LangGraph

This project is my step-by-step journey learning how to build an AI agent using Python.

The goal is not just to copy code from a tutorial. The goal is to understand how an AI agent actually works, starting from a simple Gemini API call and gradually building toward a proper agent with tools, memory, web research, and LangGraph.

---

# What We Are Building

The eventual goal is an AI Research Agent.

For example, I want to eventually be able to ask:

> Research the best laptop under ₹80,000 for programming in India. Compare several options and recommend the best one.

The eventual architecture will look something like:

```text
                    USER
                      │
                      ▼
                 AI AGENT
                      │
                      ▼
                   PLANNER
                      │
             ┌────────┴────────┐
             ▼                 ▼
        WEB SEARCH          TOOLS
             │                 │
             └────────┬────────┘
                      ▼
                   ANALYZE
                      │
                      ▼
                 FACT CHECK
                      │
                      ▼
                FINAL REPORT
```

But we are building this one concept at a time.

---

# Technologies

## Python

Python is the programming language used to build the application.

We use Python because it has a huge ecosystem for AI, automation, APIs, web applications, data processing, and machine learning.

---

## uv

`uv` is our Python project and dependency manager.

Instead of manually installing packages with `pip`, we use commands such as:

```bash
uv add langchain
```

and:

```bash
uv run graph.py
```

`uv` also keeps track of our dependencies in:

```text
pyproject.toml
uv.lock
```

---

# Why LangChain?

We could communicate with Gemini directly using Google's API.

So why use LangChain?

Because eventually our application needs more than just:

```text
Question → Gemini → Answer
```

We want:

```text
Question
   ↓
AI
   ↓
Tool?
   ↓
Search / Calculator / Files / APIs
   ↓
AI
   ↓
More decisions
   ↓
Final answer
```

LangChain gives us useful abstractions for working with:

* Chat models
* Messages
* Tools
* Tool calls
* Structured output
* Agents
* Prompts
* Model integrations

So LangChain helps us build the components around the model.

---

# Why LangGraph?

LangGraph will eventually control the workflow of our agent.

Instead of manually writing a complicated loop like:

```text
Ask model
 ↓
Did it request a tool?
 ↓
Run tool
 ↓
Send result to model
 ↓
Did it request another tool?
 ↓
Run tool
 ↓
...
```

LangGraph lets us represent the process as a graph.

For example:

```text
START
  ↓
Agent
  ↓
Tool?
 ┌───────┐
 │       │
YES      NO
 │       │
 ▼       ▼
Tool    END
 │
 └──→ Agent
```

We haven't started using LangGraph yet because we first wanted to understand what is happening underneath.

---

# Why Gemini?

We originally considered OpenAI, but decided to use Google's Gemini API instead.

The project therefore uses:

```text
Gemini
   +
LangChain
   +
LangGraph
```

The LangChain integration is provided by:

```text
langchain-google-genai
```

---

# Project Setup

We started with a blank GitHub Codespace.

Our project directory is:

```text
/workspaces/codespaces-blank
```

We initialized the Python project:

```bash
uv init
```

This created the Python project configuration.

---

# Installing Dependencies

We installed:

```bash
uv add langchain langgraph python-dotenv langchain-google-genai
```

These packages are used for different purposes.

### `langchain`

The main LangChain framework.

### `langgraph`

Used later to build the actual agent workflow.

### `python-dotenv`

Allows us to load secrets such as our Gemini API key from a `.env` file.

### `langchain-google-genai`

Connects LangChain to Google's Gemini models.

---

# API Key

We do NOT put the Gemini API key directly into Python code.

Instead, we created:

```text
.env
```

with:

```text
GEMINI_API_KEY=YOUR_KEY_HERE
```

We also created `.gitignore`:

```text
.env
.venv/
__pycache__/
```

This prevents the API key from accidentally being committed to GitHub.

## Important

Never publish or share the real API key.

If a key is accidentally exposed, it should be revoked/replaced.

---

# Current Project Structure

Our project has now grown beyond the original single-file setup.

The current structure is roughly:

```text
codespaces-blank/
│
├── graph.py
├── main.py
│
├── tools/
│   ├── __init__.py
│   ├── calculator.py
│   └── wikipedia.py
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

The `tools/` directory contains our LangChain tools.

* `calculator.py` contains the calculator tool.
* `wikipedia.py` contains the first version of our Wikipedia research tool.

---

# Step 1 — First Gemini Program

The first thing we wanted to prove was:

> Can Python successfully communicate with Gemini?

We created:

```text
main.py
```

and started with:

```python
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
```

---

# Step 2 — Loading the API Key

We added:

```python
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set!")
```

## What is happening?

`load_dotenv()` reads the `.env` file.

Then:

```python
os.getenv("GEMINI_API_KEY")
```

looks for our API key.

The safety check:

```python
if not api_key:
    raise ValueError(...)
```

makes the program stop with a useful error if the key is missing.

---

# Step 3 — Creating the Gemini Model

We created:

```python
model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
)
```

This creates a LangChain chat-model object connected to Gemini.

Conceptually:

```text
Python
   ↓
LangChain
   ↓
Gemini
```

At this point, `model` represents the Gemini model we can communicate with.

---

# Step 4 — First Gemini Request

Initially we used a hard-coded question:

```python
response = model.invoke(
    "Explain what an AI agent is in one sentence."
)
```

Then:

```python
print(response.text)
```

prints the answer.

This proved that our basic system worked:

```text
Python
  ↓
LangChain
  ↓
Gemini API
  ↓
Gemini response
  ↓
Python
```

---

# Step 5 — Understanding the Response

One important lesson happened here.

The response from LangChain is not simply a normal Python string.

It is an `AIMessage` object.

We initially tried:

```python
response.context
```

which produced:

```text
AttributeError:
'AIMessage' object has no attribute 'context'
```

The important response content was available through properties such as:

```python
response.content
```

and, with the newer response format we encountered:

```python
response.text
```

The lesson:

> A model response is a structured message object, not necessarily just a string.

This becomes very important when we start dealing with tool calls.

---

# Step 6 — Making the Program Interactive

We didn't want the question permanently written into the program.

We changed it to:

```python
question = input("Ask me anything: ")

response = model.invoke(question)

print(response.text)
```

Now the program waits for the user.

Example:

```text
Ask me anything: What is LangGraph?
```

The user's input is stored in:

```python
question
```

and sent to Gemini.

Now our application became:

```text
USER
 ↓
Python
 ↓
LangChain
 ↓
Gemini
 ↓
Answer
```

---

# Step 7 — System and Human Messages

We then introduced a system instruction.

Instead of:

```python
response = model.invoke(question)
```

we used:

```python
response = model.invoke([
    (
        "system",
        "You are a helpful AI research assistant. Explain things clearly and accurately."
    ),
    ("human", question),
])
```

Now Gemini receives two different types of messages.

## System

```text
You are a helpful AI research assistant.
```

This tells the model how it should behave.

## Human

```text
The user's actual question.
```

This tells the model what the user wants.

Conceptually:

```text
SYSTEM
"You are a helpful research assistant."
        +
HUMAN
"What is LangGraph?"
        ↓
      GEMINI
        ↓
      ANSWER
```

This distinction becomes important when building agents.

---

# Step 8 — Creating Our First Tool

Now we moved from a chatbot toward an agent.

The important idea:

> A model can generate text, but tools allow the AI application to perform actions.

Examples of future tools could include:

* Calculator
* Web search
* Reading files
* Database queries
* APIs
* Sending emails
* Searching documents

We started with the simplest possible tool: a calculator.

We imported:

```python
from langchain_core.tools import tool
```

Then created:

```python
@tool
def calculator(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b
```

---

# What Does `@tool` Do?

Without `@tool`, this is simply a Python function:

```python
def calculator(a, b):
    return a + b
```

With:

```python
@tool
```

LangChain knows that this function should be treated as a tool available to an AI model.

Conceptually:

```text
             GEMINI
                │
                │ can request
                ▼
          ┌───────────┐
          │ Calculator│
          └───────────┘
```

The docstring:

```python
"""Add two numbers together."""
```

is also important because it describes what the tool does.

The model can use this information when deciding whether the tool is useful.

---

# Step 9 — Giving the Tool to Gemini

We created:

```python
model_with_tools = model.bind_tools([calculator])
```

This tells Gemini:

> You have access to the calculator tool.

Then instead of:

```python
model.invoke(...)
```

we used:

```python
model_with_tools.invoke(...)
```

---

# Step 10 — The Empty Response

We tested:

```text
What is 25 + 37?
```

We expected:

```text
62
```

But instead:

```python
response.text
```

was empty.

At first this looked like something was broken.

It wasn't.

This was an important discovery.

Gemini had decided:

> I should use the calculator tool.

But Gemini had not actually executed our Python function.

---

# Step 11 — Inspecting the Response

Instead of:

```python
print(response.text)
```

we temporarily used:

```python
print(response)
```

This showed information like:

```text
tool_calls=[
    {
        'name': 'calculator',
        'args': {
            'b': 9,
            'a': 29
        },
        ...
    }
]
```

This was a major learning moment.

Gemini had produced a tool call.

It essentially said:

```text
Use the calculator.

calculator(
    a=29,
    b=9
)
```

The AI wasn't directly running our Python function.

It was requesting that our application run it.

---

# The Important Difference

This distinction is extremely important:

## Gemini decides

```text
"I need a calculator."
```

## Our Python program executes

```python
calculator(29, 9)
```

The model itself does not magically execute arbitrary Python code.

Our application is responsible for executing tools safely.

---

# Step 12 — Executing the Tool

We checked:

```python
if response.tool_calls:
```

This means:

> Did Gemini request a tool?

Then:

```python
tool_call = response.tool_calls[0]
```

gets the first tool request.

Then:

```python
result = calculator.invoke(tool_call["args"])
```

actually executes the calculator.

So the process becomes:

```text
USER
 │
 │ "What is 29 + 9?"
 ▼
GEMINI
 │
 │ tool call
 ▼
calculator
 │
 │ 38
 ▼
Python
```

At this stage, we could print:

```python
print("Calculator result:", result)
```

and get:

```text
Calculator result: 38.0
```

---

# Step 13 — Completing the Agent Loop

But there was still a problem.

We had:

```text
User
↓
Gemini
↓
Calculator
↓
Python
```

Gemini hadn't seen the calculator result yet.

A proper tool-using workflow should be:

```text
User
↓
Gemini
↓
Tool call
↓
Calculator
↓
Tool result
↓
Gemini AGAIN
↓
Final answer
```

So we kept the conversation in:

```python
messages = [
    (
        "system",
        "You are a helpful AI research assistant. Use the calculator when you need to calculate numbers."
    ),
    ("human", question),
]
```

Then:

```python
response = model_with_tools.invoke(messages)
```

Gemini decides whether it needs the calculator.

If it does:

```python
if response.tool_calls:
```

we extract the tool call:

```python
tool_call = response.tool_calls[0]
```

execute it:

```python
result = calculator.invoke(tool_call["args"])
```

Then we add the model response to the conversation:

```python
messages.append(response)
```

and add the tool result:

```python
messages.append({
    "role": "tool",
    "content": str(result),
    "tool_call_id": tool_call["id"],
})
```

Finally, we call Gemini again:

```python
final_response = model_with_tools.invoke(messages)
```

and print:

```python
print(final_response.text)
```

---

# The Complete Flow We Have Built

We now understand the basic mechanism behind a tool-using agent:

```text
                         USER
                           │
                           ▼
                     ┌──────────┐
                     │  GEMINI  │
                     └────┬─────┘
                          │
                    Need a tool?
                     /          \
                   NO            YES
                   │              │
                   ▼              ▼
                Answer       Tool Request
                                  │
                                  ▼
                            Python Tool
                                  │
                                  ▼
                              Tool Result
                                  │
                                  ▼
                              GEMINI
                                  │
                                  ▼
                             Final Answer
```

This is the fundamental idea we wanted to understand before introducing LangGraph.

---

# What We Have Learned So Far

## 1. A model is not an agent

A basic model call is:

```text
Question
   ↓
Model
   ↓
Answer
```

That alone is not a full agent.

---

## 2. Agents can use tools

We created:

```python
@tool
def calculator(...):
    ...
```

and made it available to Gemini with:

```python
model.bind_tools([calculator])
```

---

## 3. The model can request a tool

Gemini returned something like:

```text
tool_calls=[
    {
        "name": "calculator",
        "args": {
            "a": 29,
            "b": 9
        }
    }
]
```

This is different from a normal text response.

---

## 4. Our application executes the tool

The Python program is responsible for:

```python
calculator.invoke(...)
```

The model requests the action.

Our program performs the action.

---

## 5. The result goes back to the model

The model needs the tool result to continue reasoning and generate a final answer.

Therefore:

```text
Model
↓
Tool request
↓
Tool
↓
Tool result
↓
Model
↓
Final answer
```

---

# Step 14 — Introducing LangGraph

After understanding the manual tool-calling loop, we moved the workflow into LangGraph.

We created a state object:

```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

The state carries the conversation between graph nodes.

Conceptually:

```text
STATE
└── messages
```

We then created a graph:

```python
graph_builder = StateGraph(AgentState)
```

and an Agent node:

```python
graph_builder.add_node("agent", agent)
```

The Agent node sends the current messages to Gemini:

```python
response = model_with_tools.invoke(state["messages"])
```

and returns the response back into the state.

---

# Step 15 — Conditional Routing

We created a routing function that checks whether Gemini requested a tool:

```python
def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END
```

Then we connected it to the graph:

```python
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
)
```

The resulting workflow is:

```text
START
  ↓
AGENT
  ↓
Tool call?
  ├── YES → TOOLS
  │          ↓
  │        AGENT
  │
  └── NO → END
```

This is the agent loop we previously wrote manually.

---

# Step 16 — ToolNode

Instead of manually calling:

```python
calculator.invoke(...)
```

LangGraph provides `ToolNode`.

We created:

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([calculator])
```

and registered it:

```python
graph_builder.add_node("tools", tool_node)
```

Now the flow is:

```text
Gemini
  ↓
AIMessage with tool call
  ↓
ToolNode
  ↓
calculator()
  ↓
ToolMessage
  ↓
Gemini
```

The `ToolMessage` is associated with the exact tool request using the tool-call ID.

---

# Step 17 — First Successful LangGraph Agent Run

We tested:

```text
What is 25+9
```

The graph produced the following sequence:

```text
HumanMessage
  ↓
AIMessage
  └── tool_calls:
      calculator(a=25, b=9)
  ↓
ToolMessage
  └── 34.0
  ↓
AIMessage
  └── 25 + 9 = 34
```

This proved that the complete LangGraph tool loop works.

---

# Step 18 — Starting the Research Tool

After the calculator agent worked, we decided to add research capability.

The long-term goal is a Personal Research Agent that can eventually:

1. Answer simple questions directly.
2. Use the calculator when necessary.
3. Research topics using external sources.
4. Save research into Markdown files.
5. Read saved research later.
6. Potentially search multiple sources.
7. Eventually use RAG/vector search.
8. Potentially remember previous research.

We intentionally did not add every research source at once.

We started with one source: Wikipedia.

The first intended pipeline is:

```text
Topic
  ↓
Wikipedia
  ↓
Extract useful information
  ↓
Save Markdown
  ↓
Return file path
  ↓
Gemini continues
```

Wikipedia is only the first source. Later sources could include official documentation, ArXiv, general web pages, news, YouTube transcripts, and user files.

---

# Step 19 — Creating the Wikipedia Tool

We created:

```text
tools/wikipedia.py
```

with a LangChain tool:

```python
from langchain_core.tools import tool


@tool
def research_wikipedia(topic: str) -> str:
    """Research a topic using Wikipedia."""
    ...
```

The first version was only a placeholder so that we could verify the tool interface independently.

We tested it with:

```python
research_wikipedia.invoke({"topic": "LangGraph"})
```

This confirmed that the tool itself could be invoked through LangChain.

---

# Step 20 — The First Wikipedia Package Attempt

We initially tried using the Python `wikipedia` package.

We installed it with:

```bash
uv add wikipedia
```

but the request failed inside the package with:

```text
requests.exceptions.JSONDecodeError:
Expecting value: line 1 column 1 (char 0)
```

The traceback showed that the failure happened while the package was trying to parse Wikipedia's HTTP response as JSON.

The important lesson was that the problem was inside the Wikipedia wrapper, not in our LangChain tool or LangGraph architecture.

We therefore removed the package:

```bash
uv remove wikipedia
```

We decided to communicate with Wikipedia's API directly instead.

---

# Step 21 — Direct Wikipedia API

We installed the HTTP library:

```bash
uv add requests
```

and imported it:

```python
import requests
from langchain_core.tools import tool
```

We then made our first direct request to Wikipedia's API:

```python
url = "https://en.wikipedia.org/w/api.php"

params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "exintro": True,
    "explaintext": True,
    "titles": topic,
}

response = requests.get(url, params=params)
```

The request flow is now:

```text
research_wikipedia(topic)
        ↓
requests
        ↓
Wikipedia API
        ↓
HTTP response
```

We currently return:

```python
return response.text
```

so that we can inspect the raw API response before extracting the useful article content.

The next step is to parse the JSON response and extract the actual article text.

---

# Why We Are Going to Use LangGraph

At the moment, we manually wrote the workflow:

```python
if response.tool_calls:
    ...
    calculator.invoke(...)
    ...
    model_with_tools.invoke(...)
```

That works for one simple tool.

But imagine we have:

```text
Web Search
Calculator
File Reader
Database
Weather
Email
Code Executor
```

and the model can call tools multiple times.

Our code could become a huge collection of:

```python
if
elif
while
if
try
...
```

This becomes difficult to manage.

LangGraph gives us a better way to represent the workflow.

Eventually we'll have something like:

```text
              ┌──────────────┐
              │    Agent     │
              └──────┬───────┘
                     │
                 Tool needed?
                /           \
              YES            NO
               │              │
               ▼              ▼
          ┌─────────┐       END
          │  Tools  │
          └────┬────┘
               │
               └──────────────┐
                              │
                              ▼
                            Agent
```

This is where LangGraph becomes extremely useful.

---

# Our Learning Roadmap

## Completed

* [x] Create Python project with `uv`
* [x] Install LangChain
* [x] Install LangGraph
* [x] Install Gemini integration
* [x] Create `.env`
* [x] Protect `.env` using `.gitignore`
* [x] Connect Python to Gemini
* [x] Send a basic prompt
* [x] Understand `AIMessage`
* [x] Use system and human messages
* [x] Create a LangChain tool
* [x] Bind a tool to Gemini
* [x] Inspect `tool_calls`
* [x] Execute a tool
* [x] Send the tool result back to Gemini
* [x] Understand the basic manual tool-calling loop
* [x] Create LangGraph state
* [x] Create an Agent node
* [x] Create a Tool node using `ToolNode`
* [x] Connect graph nodes with edges
* [x] Create conditional routing
* [x] Run a complete calculator agent
* [x] Create the first research tool
* [x] Test a Wikipedia wrapper
* [x] Remove the failing Wikipedia wrapper
* [x] Install `requests`
* [x] Make a direct Wikipedia API request
* [x] Inspect the raw API response

## Next

* [ ] Parse the Wikipedia JSON response
* [ ] Extract useful article content
* [ ] Handle missing/disambiguation pages
* [ ] Save research to `research/<topic>.md`
* [ ] Return the saved file path from the tool
* [ ] Connect `research_wikipedia` to the LangGraph agent
* [ ] Test Gemini choosing between calculator and research
* [ ] Add another research source
* [ ] Add better error handling
* [ ] Add memory
* [ ] Eventually add RAG/vector search
* [ ] Build the full AI Research Agent
* [ ] Add a user interface
* [ ] Eventually deploy the project

---

# Final Goal

The final project should become something like:

```text
                    USER
                      │
                      ▼
                 ┌─────────┐
                 │ PLANNER │
                 └────┬────┘
                      │
                      ▼
                 ┌─────────┐
                 │ AGENT   │◄─────────────┐
                 └────┬────┘              │
                      │                   │
                 Need tool?               │
                /      \                  │
              YES       NO                │
               │         │                │
               ▼         ▼                │
             TOOLS     ANSWER             │
               │                          │
               ▼                          │
           TOOL RESULT ───────────────────┘
```

Eventually the agent should be able to research real topics and produce useful reports.

The current research architecture is intentionally being built one source at a time:

```text
Agent
  ↓
Research Tool
  ↓
Source
  ↓
Extract
  ↓
Markdown file
  ↓
Agent
```

This is not RAG yet. RAG will come later, after we have a reliable document collection and retrieval pipeline.

---

# The Most Important Lesson So Far

The biggest thing learned in this project is that an AI agent is not simply:

```text
AI + prompt
```

A useful agent is a system where:

```text
LLM
+
State
+
Tools
+
Decision making
+
Workflow
```

work together.

The LLM decides what it wants to do.

The application executes the actions.

The results are given back to the LLM.

The process can repeat until the task is complete.

That is the foundation we will use to build the full AI Research Agent.

---

# Running the Project

From the Codespace terminal:

```bash
uv run main.py
```

The project runs inside the GitHub Codespace environment.

If the project is later downloaded to another computer, the dependencies can be recreated from the project configuration using `uv`.

---

# Security Reminder

Never commit:

```text
.env
```

to GitHub.

Never put the Gemini API key directly into:

```python
main.py
```

Never share the API key publicly.

Use:

```text
GEMINI_API_KEY=...
```

inside `.env`.

---

# Current Status

We have successfully gone from:

```text
Blank Codespace
```

to:

```text
Python
  ↓
Gemini
  ↓
LangChain
  ↓
Tools
  ↓
Tool calls
  ↓
LangGraph
  ↓
Agent node
  ↓
Conditional routing
  ↓
ToolNode
  ↓
Tool result
  ↓
Gemini
  ↓
Final answer
```

The calculator agent is working end-to-end.

We have also started building the research capability:

```text
Gemini Agent
     ↓
research_wikipedia
     ↓
Wikipedia API
     ↓
Raw JSON response
```

The current stopping point is after Step 21: we have successfully made a direct request to Wikipedia's API and are returning the raw response.

The immediate next step is to parse that JSON and extract the useful article content before saving it as Markdown.
