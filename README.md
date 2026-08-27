# Personal Research Agent

A research agent built with Python, Gemini, LangChain, and LangGraph.

The goal of this project is to understand how AI agents work by building one step by step — starting with tool calling and gradually adding research sources, state, and citations.

## Architecture

```text
flowchart TD
    U[USER] --> A[GEMINI AGENT]

    A -->|Simple question| ANS[Answer]

    A -->|Calculation| C[Calculator]
    C --> ANS

    A -->|Research| R[Researcher]

    R --> W[Wikipedia]
    R --> WEB[Web]
    R --> P[Research Papers]
    R --> F[Files]

    W --> G[Gather information]
    WEB --> G
    P --> G
    F --> G

    G --> S[Save research]
    S --> R

    R --> A
    A --> ANS
    ANS --> U
```

## What It Can Do

### Main Agent

The Gemini agent can:

* Answer normal questions
* Perform calculations using the calculator tool
* Send research questions to the research agent

### Research Agent

The research agent allows the user to choose where to research:

```text
1. Wikipedia
2. Web
3. Research Papers
4. Files
5. All
```

It then dynamically provides the researcher with the tools for the selected source.

### Research Sources

* **Wikipedia** — Search and retrieve Wikipedia articles
* **Web** — Search the web using Tavily
* **Research Papers** — Search arXiv
* **Files** — Search TXT, MD, PDF and DOCX files

## Research Flow

```text
User question
     ↓
Gemini Agent
     ↓
Research
     ↓
User selects source
     ↓
Researcher
     ↓
Search / retrieve information
     ↓
Save research state
     ↓
Researcher
     ↓
Synthesized answer
```

The researcher keeps track of previous searches and sources so it can avoid unnecessary repeated searches.

## Tech Stack

* Python
* Gemini
* LangChain
* LangGraph
* Tavily
* Wikipedia
* arXiv
* uv

## Project Structure

```text
personal-research-agent/
│
├── graph.py
│
├── tools/
│   ├── __init__.py
│   ├── calculator.py
│   ├── wikipedia.py
│   ├── web.py
│   ├── arxiv.py
│   └── files.py
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Environment Variables

Create a `.env` file:

```text
GEMINI_API_KEY=YOUR_KEY
TAVILY_API_KEY=YOUR_KEY
```

Never commit `.env` or expose API keys.

## Run

```bash
uv run graph.py
```

## Current Features

* Gemini main agent
* Calculator tool
* LangGraph workflows
* Wikipedia research
* Tavily web research
* arXiv research
* File research
* User-selected research sources
* Dynamic tool selection
* Research state tracking
* Source tracking
* Standardized research source format
* Citations

## Roadmap

* IEEE research
* ACM research
* Better source ranking
* Improved citations
* Better research planning
* More reliable evidence synthesis

