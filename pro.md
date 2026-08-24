# Personal Research Agent — Locked Architecture & Project Scope

## 1. Project Idea

Build a **LangGraph-based personal research agent** that can answer normal questions directly, perform calculations through a calculator tool, and conduct grounded research using selectable source types.

The key idea is:

> The user can either let the agent automatically decide how to answer/research, or explicitly choose the source type.

This is **not** intended to become a Perplexity-style search engine or a universal web scraper.

---

# 2. Core User Flow

```text
USER
  |
  v
Question
  |
  v
Choose research source
  |
  +--> Auto
  +--> General Web
  +--> Wikipedia
  +--> Research Papers
  +--> My Documents
  |
  v
GEMINI AGENT
  |
  +--> Simple question ------> Direct Answer
  |
  +--> Calculation ----------> Calculator
  |
  +--> Research -------------> Researcher
                                  |
                                  v
                              Selected Source
                                  |
                                  v
                              Gather Evidence
                                  |
                                  v
                              Synthesize Answer
                                  |
                                  v
                              Answer + Sources
````

---

# 3. Source Selection

The user should select a **source type**, not a specific website.

Recommended options:

```text
1. Auto
2. General Web
3. Wikipedia
4. Research Papers
5. My Documents
```

## Auto

The agent decides what is appropriate.

Examples:

```text
"What is 25 * 37?"
        -> Calculator

"What is LangGraph?"
        -> Wikipedia / Web

"What are recent approaches to crowd counting?"
        -> Research Papers

"What does my uploaded document say about X?"
        -> Documents
```

## General Web

Used for current/general information.

Do **not** scrape Google HTML manually.

Use a proper search API/tool when web search is implemented.

## Wikipedia

A dedicated Wikipedia tool.

This is useful for factual/background questions and is simple enough to keep as a separate source.

## Research Papers

This represents the academic/research ecosystem.

Potential sources later:

```text
arXiv
IEEE Xplore
ACM Digital Library
Semantic Scholar
Crossref
```

Important:

**Do not build separate HTML scrapers for these websites.**

Use APIs/search services where available.

The project is about the research agent, not reverse-engineering website HTML.

## My Documents

Search/retrieve information from user-provided documents.

This will be the final major source added to the MVP.

---

# 4. Locked Architecture

```text
                         USER
                           |
                           v
                  +-------------------+
                  | Source Preference |
                  +---------+---------+
                           |
                           v
                     GEMINI AGENT
                           |
              +-------------+-------------+
              |             |             |
              v             v             v
           Answer       Calculator     Research
                                         |
                                         v
                                    RESEARCHER
                                         |
                        +-----------------+-----------------+
                        |                 |                 |
                        v                 v                 v
                    Wikipedia        Web Search       Research Papers
                                                           |
                                                         arXiv / IEEE /
                                                         ACM / etc.
                        |
                        +-----------------+
                                         |
                                         v
                                   My Documents
                                         |
                                         v
                                 Evidence / Results
                                         |
                                         v
                                   Final Synthesis
                                         |
                                         v
                                     USER ANSWER
```

---

# 5. LangGraph Responsibility

LangGraph manages the **workflow/state**, not the actual research content.

Conceptually:

```text
START
  |
  v
Agent
  |
  +---- direct answer ----> END
  |
  +---- calculator -------> Calculator
  |                           |
  |                           v
  |                          Agent
  |
  +---- research ----------> Researcher
                              |
                              v
                            Tool(s)
                              |
                              v
                            Evidence
                              |
                              v
                            Agent
                              |
                              v
                             END
```

The researcher can loop when more evidence is genuinely needed, but it must have a clear stopping condition.

---

# 6. Important Rule: Research Must Stop

The earlier implementation showed a major failure mode:

```text
search
 -> search
 -> search
 -> search
 -> ...
 -> GraphRecursionError
```

This must not happen in the final architecture.

The researcher should follow:

```text
Research
   |
   v
Gather evidence
   |
   v
Enough evidence?
   |
   +--> YES --> Synthesize --> END
   |
   +--> NO --> Another search
```

Also keep a hard maximum number of research/tool iterations as a safety limit.

The recursion limit should **not** be treated as the solution.

The real solution is a correct stop condition.

---

# 7. Web Search Decision

### Do NOT do this:

```text
requests.get("https://www.google.com/search")
BeautifulSoup(...)
soup.select("div.MjjYud")
```

Why?

Because Google's HTML is a UI implementation, not a stable search API.

It can return different HTML, JavaScript/challenge pages, or change selectors.

The project should not spend its time maintaining Google scraping logic.

### Instead:

Use a proper search API/tool.

The desired flow is:

```text
Researcher
    |
    v
Web Search Tool
    |
    v
Search API
    |
    v
Structured Results
    |
    v
Researcher
```

---

# 8. Research Papers Scope

We are **not** building a complete academic search engine.

For the MVP:

```text
Research Papers
       |
       +--> one reliable paper-search source
```

Then later, if useful:

```text
Research Papers
       |
       +--> arXiv
       +--> Semantic Scholar
       +--> IEEE Xplore
       +--> ACM Digital Library
```

The architecture should make adding these possible without changing the main agent.

---

# 9. Tool Responsibilities

Each tool should have one clear responsibility.

### Calculator

```text
Input: mathematical expression
Output: verified calculation
```

### Wikipedia

```text
Input: topic
Output: relevant factual evidence
```

### Web Search

```text
Input: search query
Output: structured search results
```

### Research Paper Search

```text
Input: research topic
Output: papers / metadata / abstracts / links
```

### Documents

```text
Input: user question
Output: relevant document evidence
```

The LLM decides **when/why to use a tool**.

The tool itself should perform the actual operation.

---

# 10. Evidence → Answer

The researcher should not simply search and immediately answer.

The intended flow is:

```text
Question
   |
   v
Search
   |
   v
Evidence
   |
   v
Evaluate
   |
   v
Sufficient?
   |
   v
Synthesize
   |
   v
Answer
```

The final answer should be grounded in the evidence gathered.

For research questions, sources should be shown to the user.

---

# 11. MVP Scope — LOCKED

The project is complete when it supports:

### Agent

* Gemini-based main agent
* LangGraph workflow
* Tool calling
* State management
* Clear stopping conditions

### Tools

* Calculator
* Wikipedia
* Web Search
* Documents

### Source preference

* Auto
* General Web
* Wikipedia
* Research Papers
* My Documents

### Research behavior

* Gather evidence
* Avoid unnecessary repeated searches
* Stop when sufficient evidence is available
* Produce a grounded final answer
* Include sources where applicable

---

# 12. What Is OUT OF SCOPE

Do not expand the MVP into:

* A full search engine
* Google HTML scraping
* Scraping every website
* Custom scrapers for dozens of sites
* Full IEEE/ACM crawler
* Browser automation for arbitrary websites
* Building a vector database before documents actually require it
* Multi-agent complexity just for the sake of it
* UI/frontend before the core agent works
* Trying to support every possible research source

These can be future extensions.

---

# 13. Development Order

Follow this order and avoid jumping around.

```text
STEP 1
Agent
  |
  +--> direct answers
  +--> calculator
```

```text
STEP 2
Researcher
  |
  +--> Wikipedia
```

```text
STEP 3
Research stopping logic
  |
  +--> enough evidence?
  +--> maximum research attempts
```

```text
STEP 4
Web Search
  |
  +--> proper search API/tool
```

```text
STEP 5
Research Papers
  |
  +--> one reliable academic source
```

```text
STEP 6
Documents
  |
  +--> final major source
```

```text
STEP 7
Testing
  |
  +--> simple questions
  +--> calculations
  +--> factual research
  +--> academic research
  +--> document questions
  +--> source selection
  +--> failure cases
```

---

# 14. Example Final Experience

### Example 1 — Auto

```text
User:
Who is the current President of India?

Source:
Auto
```

Agent decides:

```text
Research required
       |
       v
Web / reliable source
       |
       v
Evidence
       |
       v
Answer + source
```

---

### Example 2 — Calculation

```text
User:
What is 847 * 923?

Source:
Auto
```

Agent:

```text
Calculator
   |
   v
782?...
   |
   v
Answer
```

The exact calculation is delegated to the calculator instead of relying on the LLM's mental arithmetic.

---

### Example 3 — Research Papers

```text
User:
What are recent deep learning approaches for crowd counting?

Source:
Research Papers
```

Flow:

```text
Researcher
    |
    v
Paper Search
    |
    v
Relevant papers
    |
    v
Evidence
    |
    v
Synthesis
    |
    v
Answer + papers
```

---

### Example 4 — Documents

```text
User:
What does my project report say about CSRNet?

Source:
My Documents
```

Flow:

```text
Document Search
       |
       v
Relevant chunks
       |
       v
Evidence
       |
       v
Answer
```

---

# 15. The Main Learning Goals

This project is primarily meant to teach and demonstrate:

1. LLM tool calling
2. LangGraph stateful workflows
3. Agent routing
4. Conditional edges
5. Research loops
6. Tool design
7. Evidence gathering
8. Grounded synthesis
9. Source selection
10. Failure handling
11. API/tool integration
12. Document retrieval

The project should prioritize understanding these concepts over adding endless sources.

---

# 16. Final Architectural Principle

The most important principle to remember:

> **The agent decides what it needs. The tools know how to get it. LangGraph controls the workflow.**

```text
LLM
  = reasoning / decision making

Tools
  = external capabilities

LangGraph
  = workflow + state

Sources
  = evidence

Final LLM step
  = synthesis
```

This is the architecture we are locking for the project.

Future improvements should be added **inside this architecture**, not by continually expanding the project's scope.

```
```
