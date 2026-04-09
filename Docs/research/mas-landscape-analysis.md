# Open-Source Multi-Agent Systems: Landscape Analysis

---

## 1. Orchestration Frameworks

### Tier 1 — Production-Grade (Recommended)

**🥇 LangGraph** *(LangChain ecosystem)*
- **Model:** Graph-based state machine. Agents are nodes, transitions are edges.
- **Strengths:** Fine-grained control over agent flow, built-in persistence/checkpointing, human-in-the-loop support, cycles (unlike simple DAGs), streaming native.
- **Best for:** Complex workflows where you need deterministic control + LLM flexibility.
- **Repo:** `langgraph` on PyPI / GitHub

```
Supervisor Node
    ├── Agent A (Research)
    ├── Agent B (Code)
    └── Agent C (Review)
          └── loops back to Supervisor
```

---

**🥇 Microsoft AutoGen** *(v0.4+ "AgentChat")*
- **Model:** Conversation-driven. Agents communicate via structured message passing.
- **Strengths:** Native multi-agent conversations, GroupChat orchestration, built-in human proxy agent, strong tool-calling abstraction, excellent async support.
- **Best for:** Dialogue-heavy workflows, debate/critique agent patterns, research automation.
- **Repo:** `pyautogen` / `autogen-agentchat`

> ⚠️ **Note:** AutoGen v0.4 is a near-complete rewrite. If starting fresh, use v0.4+ (`autogen-agentchat`). Ignore tutorials based on v0.2.

---

**🥇 CrewAI**
- **Model:** Role-based crew with explicit task assignment.
- **Strengths:** Lowest barrier to entry, declarative agent/task definition, built-in delegation, sequential and hierarchical process modes.
- **Best for:** Teams that need fast prototyping, clear role separation, business-process-style workflows.
- **Repo:** `crewai` on PyPI

```python
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.hierarchical,  # Manager LLM delegates
    manager_llm=ChatOpenAI(model="gpt-4o")
)
```

---

### Tier 2 — Specialized / Emerging

| Framework | Model | Best For |
|---|---|---|
| **OpenAI Swarm** | Handoff-based routing | Lightweight, educational, low overhead |
| **Haystack Pipelines** | DAG pipelines | Document/RAG-heavy workflows |
| **Semantic Kernel** (MS) | Plugin/skill model | .NET shops or hybrid C#/Python |
| **Agno** (ex-PhiData) | Agent teams | Structured data + tool-heavy agents |

---

## 2. Agent Selection & Routing

This is where most teams **do** reinvent the wheel unnecessarily. Here's what already exists:

### Pattern A — Supervisor / Manager LLM (Most Common)

A dedicated LLM node reads the task and decides which agent to invoke. Both **LangGraph** and **CrewAI** implement this natively.

```
User Input → Supervisor LLM → [routes to] → Agent_X
                              ↑_______________|
                              (result + next decision)
```

**LangGraph implementation:** `create_react_agent` + a supervisor node that outputs `next: agent_name`.

---

### Pattern B — Semantic Router (Pre-LLM, fast & cheap)

Use **`semantic-router`** (by Aurelio AI) — a dedicated OSS library for this exact problem.

```bash
pip install semantic-router
```

```python
from semantic_router import Route, RouteLayer
from semantic_router.encoders import OpenAIEncoder

routes = [
    Route(name="code_agent", utterances=["write a function", "debug this", "implement..."]),
    Route(name="research_agent", utterances=["find information", "summarize", "what is..."]),
    Route(name="data_agent", utterances=["analyze dataset", "plot", "run SQL..."]),
]

layer = RouteLayer(encoder=OpenAIEncoder(), routes=routes)
layer("fix the bug in my auth module")  # → "code_agent"
```

> ✅ **Why use this:** Semantic router runs *before* hitting an LLM — it's fast, deterministic, and cheap. Use it as a first-pass filter before your orchestrator.

---

### Pattern C — LangChain Agent Router

For LLM-driven routing with tool descriptions:

```python
from langchain.agents import AgentExecutor
# Each "agent" is exposed as a Tool with a clear description
# The router LLM reads tool descriptions and selects
tools = [
    Tool(name="ResearchAgent", func=research_agent.run, description="Use for..."),
    Tool(name="CodeAgent", func=code_agent.run, description="Use for..."),
]
```

---

### Pattern D — Embedding-Based Agent Registry

Roll your own with **ChromaDB or Qdrant**: store agent capability descriptions as vectors, query with the user task embedding, retrieve top-k candidate agents.

```
Task Embedding → Vector Search (ChromaDB) → Top-3 Agents → LLM picks final
```

This is the pattern to use when your agent pool is **dynamic** (agents can be added/removed at runtime).

---

## 3. Architecture & Best Practices

### Recommended Reference Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT / API LAYER                │
│              (FastAPI + LangServe or A2A Server)     │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│               SEMANTIC ROUTER (Layer 0)              │
│           semantic-router — fast, no LLM cost        │
│     Routes by intent category → agent domain        │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│            ORCHESTRATOR / SUPERVISOR (Layer 1)       │
│        LangGraph StateGraph  OR  AutoGen GroupChat   │
│  - Holds shared state / memory                      │
│  - Delegates subtasks to specialized agents         │
│  - Manages loops, retries, human-in-the-loop        │
└──────┬──────────────┬──────────────────┬────────────┘
       │              │                  │
┌──────▼───┐    ┌─────▼────┐    ┌────────▼────────┐
│ Agent A  │    │ Agent B  │    │    Agent C       │
│(Research)│    │  (Code)  │    │ (Data/Analysis)  │
│          │    │          │    │                  │
│ Tools:   │    │ Tools:   │    │ Tools:           │
│ WebSearch│    │ CodeExec │    │ SQLQuery         │
│ RAG      │    │ GitHub   │    │ PandasAI         │
└──────┬───┘    └─────┬────┘    └────────┬─────────┘
       │              │                  │
┌──────▼──────────────▼──────────────────▼─────────┐
│               A2A PROTOCOL LAYER                  │
│     (Your chosen A2A spec — e.g. Google A2A)      │
│   Agents communicate via standardized messages    │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────┐
│              SHARED MEMORY & STATE                 │
│  Short-term: LangGraph State / AutoGen context    │
│  Long-term:  Mem0 / Zep / Redis                  │
│  Vector:     ChromaDB / Qdrant                   │
└───────────────────────────────────────────────────┘
```

---

### Key Architectural Decisions & Recommendations

**① Use a two-stage routing strategy**
- Stage 1: `semantic-router` → fast intent classification, no LLM cost
- Stage 2: Supervisor LLM (inside LangGraph) → fine-grained agent selection with context

**② Separate orchestration from communication**
- Your **orchestrator** (LangGraph/CrewAI) handles *workflow logic*
- Your **A2A protocol** handles *inter-agent message format and transport*
- Don't conflate them — this keeps both layers replaceable

**③ Standardize your Agent interface**
Every agent should expose a uniform contract:
```python
class BaseAgent:
    async def run(self, task: AgentTask) -> AgentResult: ...
    def capabilities(self) -> list[str]: ...  # for the router
    def health(self) -> bool: ...
```
This is exactly what Google's A2A `AgentCard` spec formalizes — leverage it.

**④ Observability from day one**
- Use **Langfuse** (OSS, self-hostable) or **Phoenix Arize** for tracing agent calls
- Never debug multi-agent flows blind — trace every hop

**⑤ Framework selection guide**

```
Need maximum control + complex loops?     → LangGraph
Need fast prototyping + role clarity?     → CrewAI
Need conversation-heavy multi-agent?      → AutoGen v0.4
Need lightweight + educational?           → OpenAI Swarm
```

---

## Summary Decision Matrix

| Need | Tool |
|---|---|
| Orchestrate agents in a graph | **LangGraph** |
| Role-based crew workflows | **CrewAI** |
| Conversational multi-agent | **AutoGen** |
| Fast semantic routing | **semantic-router** |
| LLM-driven tool routing | **LangChain Tools/Agent** |
| Dynamic agent registry | **ChromaDB + embeddings** |
| Shared long-term memory | **Mem0 / Zep** |
| Observability & tracing | **Langfuse / Phoenix** |
| Serving & transport | **FastAPI + A2A protocol** |

---

What's your current A2A protocol choice? And do you have constraints on LLM provider (OpenAI, local models, etc.)? That'll let me give you a more targeted framework recommendation.