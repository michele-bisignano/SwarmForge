# SwarmForge — Phase 2 Stack Definition
**Document ID:** `SF-ARCH-002`
**Codename:** *The Swarm*
**Version:** 1.1 (Updated — Cline Kanban added, LangGraph role refined)
**Status:** Approved — Architecture Draft
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026

---

## 1. Objective

Phase 2 transitions SwarmForge from a single-agent vibe-coding assistant into a
coordinated multi-agent system. The core architectural shift: instead of one agent
receiving all tasks, a dedicated orchestration layer decomposes complex jobs and
dispatches them to specialized agents with distinct roles.

**The key design decision for Phase 2:** all agents are cloud-based (API-driven)
at launch. Local agents are deferred to sub-phase 2.C once the orchestration layer
is stable and validated. This isolates two independent problems:
"how do agents collaborate?" and "where do agents run?"

**Phase 2 does not introduce new hardware, new physical nodes, or inter-device
networking.** All compute remains on the single Phase 1 node or via cloud APIs.
Physical distribution is explicitly deferred to a future optional phase.

---

## 2. Architectural Shift from Phase 1

```
PHASE 1 — Single Agent, Human-in-the-Loop
──────────────────────────────────────────
  Developer
     │
  VS Code (Cline — Plan/Act)
     │
  Gemma 4 API  ←── one model, one agent, human approves every step


PHASE 2 — Multi-Agent Orchestration (cloud-only at launch)
──────────────────────────────────────────────────────────
  Developer
     │
  VS Code (Cline — supervision layer)
     │
  ┌──▼────────────────────────────────────┐
  │         ORCHESTRATION LAYER           │
  │   Cline Kanban (Phase 2.A default)    │
  │   LangGraph DAG (Phase 2.A fallback / │
  │                  Phase 2.B+ primary)  │
  └──┬──────────────┬─────────────┬───────┘
     │              │             │
  Agent:         Agent:        Agent:
  Architect      Coder         Reviewer
     │              │             │
  Gemma 4 API   Gemma 4 API   Gemma 4 API
  (cloud)       (cloud)       (cloud)
```

The developer interacts exclusively with the orchestrator. Task decomposition,
agent assignment, and output synthesis are invisible to the IDE layer.
From Cline's perspective, the orchestrator is just a local OpenAI-compatible endpoint.

---

## 3. License Audit Summary

| Component | License | Status |
|---|---|---|
| Cline / Cline CLI | Apache 2.0 | ✅ Approved |
| Cline Kanban | Apache 2.0 | ✅ Approved |
| LangGraph | MIT | ✅ Approved |
| OpenJarvis | Apache 2.0 | ✅ Approved |
| Langflow | MIT | ✅ Approved |
| Flowise | Apache 2.0 | ✅ Approved (secondary option) |
| SWE-agent | MIT | ✅ Approved (pending ACI dependency audit) |
| AG2 / AutoGen sandbox | MIT + Apache 2.0 | ⚠️ BLOCKED — pending transitive license audit |

> **AG2 Policy:** Do not integrate the AG2 sandbox module until a line-by-line
> audit of its transitive dependencies is complete. The top-level MIT declaration
> does not guarantee clean transitive licenses.

---

## 4. Phase 2 Sub-Phases

Phase 2 is divided into three sequential sub-phases with explicit completion gates.
A sub-phase does not begin until the previous one meets all its KPIs.

---

### Sub-Phase 2.A — Orchestration Layer (Cloud-Only Agents)

**Goal:** Replace the single Cline agent with a coordinated team of cloud agents.
All agents consume Gemma 4 API. No local models, no hardware changes, no new
infrastructure beyond what Phase 1 established.

#### 4.1 Primary Orchestrator — Cline Kanban

Cline Kanban is the default orchestration mechanism for Phase 2.A. It requires
zero additional infrastructure: it is built into the Cline ecosystem and is
agent-agnostic (compatible with Cline, Aider, Claude Code, Codex, etc.).

**How Cline Kanban works:**

```
KANBAN BOARD
  ┌─────────────────────────────────────────────────────┐
  │  TODO          IN PROGRESS       DONE               │
  │  ────────      ─────────────     ────────           │
  │  [Task C]      [Task A] ←──      [Task X] ✓         │
  │  [Task D]        Agent: Coder    [Task Y] ✓         │
  │     ↑          [Task B] ←──                         │
  │  blocked         Agent: Reviewer                    │
  │  (waits A)                                          │
  └─────────────────────────────────────────────────────┘

Dependency linking: Task C does not start until Task A completes.
Each card is a live agent task with its own context window.
The developer monitors status — not individual terminal windows.
```

**What Cline Kanban provides in Phase 2.A:**

```
Kanban Responsibility                  Replaces
──────────────────────────────────────────────────────
Visual task board with dependencies  ← manual terminal management
Automatic dependent task triggering  ← manual agent coordination
Live status per agent                ← guessing from terminal output
Agent-agnostic orchestration         ← framework lock-in
Zero Python/infrastructure setup     ← LangGraph boilerplate
```

**What Cline Kanban does NOT provide:**
- Deterministic DAG execution with checkpointing (LangGraph)
- Programmatic state management and rollback
- Complex conditional branching logic
- Loop guard enforcement (must be enforced via prompt/SKILL.md)

#### 4.2 Fallback / Advanced Orchestrator — LangGraph

LangGraph is the programmatic orchestration fallback for Phase 2.A and the
primary orchestrator from Phase 2.B onward when workflow complexity exceeds
what Cline Kanban can express visually.

**Why LangGraph over CrewAI:**

| Criterion | LangGraph | CrewAI |
|---|---|---|
| Execution model | Deterministic DAG | Role-based loop |
| State management | Native checkpointing | External |
| Error recovery | Rollback to checkpoint | Manual |
| Parallelism | Native | Limited |
| Debuggability | Full graph trace | Opaque |
| License | MIT | MIT |

**Agent Roles (Phase 2.A initial set):**

```python
# Conceptual role definitions — not operational code
AGENT_ROLES = {
    "architect": "Decomposes the task. Produces a structured plan with "
                 "file-level scope and dependency order.",
    "coder":     "Executes the plan. Writes or modifies code files "
                 "according to the architect's specification.",
    "reviewer":  "Validates the output. Checks for logical errors, "
                 "style violations, and missing edge cases. "
                 "Returns a pass/fail verdict with notes.",
}
```

**Minimal state schema:**

```python
# Conceptual state schema — not operational code
class SwarmState(TypedDict):
    task_description: str         # original developer request
    plan:             list[dict]  # architect output
    code_changes:     list[dict]  # coder output (file, diff)
    review_result:    dict        # reviewer verdict
    iteration_count:  int         # loop guard counter
    status:           Literal["pending", "in_progress", "approved", "failed"]
```

**Loop Guard:** Maximum 3 retry cycles before escalating to the developer.
Unbounded agent loops are a known failure mode — enforce via LangGraph's
native `loop_guard` pattern or via SKILL.md instructions when using Kanban.

#### 4.3 Backend Runtime — OpenJarvis

OpenJarvis provides infrastructure abstraction. LangGraph (or Cline Kanban) handles
orchestration logic; OpenJarvis handles infrastructure concerns.

**OpenJarvis responsibilities in Phase 2.A:**

```
OpenJarvis Responsibility              Replaces
────────────────────────────────────────────────────────
FastAPI server (agent endpoints)   ←  hand-rolled FastAPI boilerplate
Interaction log tracing            ←  custom logging code
Hardware metrics collection        ←  manual pynvml calls
Engine abstraction layer           ←  API calls hardcoded to Google
```

**OpenJarvis does NOT manage:**
- Orchestration logic (Cline Kanban / LangGraph owns this)
- VS Code integration (Cline owns this)
- Model selection (config file)

**Integration point:**

```
VS Code (Cline)
     │
     │  OpenAI-compatible request
     ▼
OpenJarvis FastAPI server   ←── receives task from Cline
     │
     │  dispatches to orchestrator
     ▼
Cline Kanban / LangGraph Orchestrator
     │
     ├── Architect Agent → Gemma 4 API
     ├── Coder Agent     → Gemma 4 API
     └── Reviewer Agent  → Gemma 4 API
```

From Cline's perspective, nothing changes from Phase 1.
It sends a standard OpenAI-compatible request to a local endpoint.
The entire multi-agent coordination is invisible to the IDE layer.

#### 4.4 Cline CLI — Headless Agent Execution

Cline CLI 2.0 enables agents to run outside the VS Code GUI, making them
usable in terminal pipelines and scheduled automation.

```
Cline CLI capabilities in Phase 2.A:
  --json flag    → structured output for programmatic consumption
  --acp flag     → ACP-compliant agent (works in any ACP editor)
  Plan/Act modes → same workflow as IDE extension, terminal UI
  Model switching mid-session → planning model ≠ execution model
```

**Use cases in Phase 2:**
- Running the Reviewer agent headless on a schedule
- Integrating agent tasks into CI/CD pipelines
- Parallel agent execution without multiple VS Code windows

#### 4.5 Cline Hooks → OpenJarvis Logging

With Hooks enabled in Phase 2.A, Cline lifecycle events feed directly into
OpenJarvis trace logging — building the interaction log corpus that Phase 4
(fine-tuning) depends on.

```
Cline lifecycle event        →  OpenJarvis trace log entry
─────────────────────────────────────────────────────────
task_start                   →  log: task_id, timestamp, model
tool_call (file read/write)  →  log: tool, args, result
agent_completion             →  log: output, token_count, latency
error / retry                →  log: error_type, retry_count
```

This is the data pipeline for Phase 4. It must be designed and stable in Phase 2.

#### 4.6 Success Criteria — Sub-Phase 2.A

| KPI | Target |
|---|---|
| Successful multi-agent task completion | 100% on 5 test tasks spanning 3+ files |
| Orchestrator infinite loop incidents | 0 (loop guard active) |
| Agent coordination overhead vs Phase 1 TTFT | < 2× Phase 1 TTFT |
| External paid API calls | 0 during standard sessions |
| Rollback on agent failure | Functional in 100% of tested failure scenarios |
| OpenJarvis trace logs generated | ≥ 1 complete log per task |

---

### Sub-Phase 2.B — Visual Prototyping Layer

**Goal:** Add Langflow as a visual interface for designing and testing new
agent workflows without writing Python. Developer productivity tool only —
never runs in production.

#### 4.7 Visual Orchestration — Langflow

Langflow provides a node-based drag-and-drop interface where agent workflows
are assembled visually. Each node maps 1:1 to a LangGraph node in Python.

**Role in SwarmForge:**

```
DESIGN TIME (Langflow)          PRODUCTION (LangGraph)
──────────────────────          ──────────────────────
Drag nodes onto canvas    →     Python DAG definition
Connect edges visually    →     State transition logic
Test prompt flows         →     Validated agent prompts
Export as Python          →     Merge into codebase
```

Langflow is used exclusively during workflow design and iteration. Once a
workflow is validated, it is exported to Python and merged into the LangGraph
codebase. **Langflow never runs in production.**

**Deployment:** self-hosted locally via Docker (MIT, no external data sent).
Never expose Langflow to a public network — it contains proprietary workflow designs.

**Flowise** (Apache 2.0, TypeScript/Node.js) is the documented secondary fallback.
Evaluation criterion: use whichever exports cleaner LangGraph-compatible Python.

#### 4.8 Success Criteria — Sub-Phase 2.B

| KPI | Target |
|---|---|
| New agent workflow designed in Langflow | ≥ 1 complete workflow |
| Langflow → Python export without manual rewriting | 100% clean export |
| Langflow running fully self-hosted (no external calls) | Verified |

---

### Sub-Phase 2.C — Hybrid Agent Layer (Cloud + Local)

**Goal:** Introduce local model inference as an optional backend for select agents,
reducing API dependency and rate-limit exposure for high-frequency tasks.

**Gate:** Sub-Phase 2.A must be fully stable before 2.C begins.
Do not start 2.C with any open Phase 2.A issues.

#### 4.9 Local Inference Integration

Local agents use the same OpenAI-compatible interface as cloud agents.
The only change is the endpoint URL in the agent configuration.

```
Cloud Agent Configuration          Local Agent Configuration
──────────────────────────         ─────────────────────────
endpoint: AI Studio URL            endpoint: http://localhost:11434
model:    gemma-4-26b-a4b-it       model:    gemma4:e4b (quantized)
api_key:  GOOGLE_AI_STUDIO_KEY     api_key:  (none — local)
```

**Recommended local model for 8GB VRAM:**

| Model | VRAM Required | Quality vs Cloud | Recommended Use |
|---|---|---|---|
| `gemma4:e4b` (4.5B, Q4) | ~5GB | ~70% | Reviewer agent (high-freq, low-complexity) |
| `gemma4:26b` (26B MoE, Q4) | ~14GB | ~95% | Not viable on 8GB without RAM offload |

Reserve local inference for the Reviewer agent. Architect and Coder require
higher-quality outputs — keep them on cloud API to preserve rate limit budget.

**SWE-agent ACI Pattern (pending audit):**
SWE-agent's Agent-Computer Interface restricts the shell commands an LLM can invoke,
reducing the attack surface of autonomous code execution. If the ACI audit confirms
no GPL transitive dependencies, integrate the pattern into the Coder agent's
tool schema in this sub-phase.

#### 4.10 Success Criteria — Sub-Phase 2.C

| KPI | Target |
|---|---|
| Local Reviewer agent TTFT | < 3 seconds |
| OOM crashes on 8GB VRAM node | 0 |
| Seamless failover local → cloud on rate limit | Functional |
| Paid API calls during local-primary sessions | 0 |

---

## 5. Open Decisions (Deferred to Phase 3 or later)

The following are explicitly out of scope for Phase 2:

1. **Second physical node:** networking, mesh VPN, IP masking — all deferred
2. **Gateway / Load Balancer:** not needed until 2+ physical nodes exist
3. **Fine-tuning pipeline:** deferred to Phase 4 (requires stable log format
   from Phase 2 OpenJarvis tracing)
4. **AG2 sandbox:** blocked pending transitive license audit

---

## 6. Dependency on Phase 1 Outputs

Phase 2 cannot begin until all Phase 1 deliverables are confirmed:

- [ ] Cline executes 5 autonomous IDE commands (Phase 1 KPI #2)
- [ ] TTFT < 1.5s confirmed on Gemma 4 API (Phase 1 KPI #1)
- [ ] OpenJarvis installed and FastAPI server running locally
- [ ] SKILL.md authored and validated in Cline

---

## 7. Full Phase 2 Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                        DEVELOPER                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      IDE LAYER                              │
│    VS Code + Cline (supervision, approval, Kanban board)    │
│    Cline CLI (headless agent execution, pipeline tasks)     │
└─────────────────────────┬───────────────────────────────────┘
                          │  OpenAI-compatible request
┌─────────────────────────▼───────────────────────────────────┐
│                  BACKEND RUNTIME                            │
│              OpenJarvis (FastAPI server)                    │
│      trace logging  │  hardware metrics  │  engine routing  │
│      Hooks ←── Cline lifecycle events                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               ORCHESTRATION LAYER                           │
│                                                             │
│  Phase 2.A default:  Cline Kanban                          │
│  ─────────────────── (zero setup, visual, agent-agnostic)   │
│                                                             │
│  Phase 2.A fallback / Phase 2.B+ primary:  LangGraph (DAG) │
│  ──────────────────────────────────────────────────────     │
│    ┌────────────┬──────────────┬──────────────┐             │
│    │ Architect  │    Coder     │   Reviewer   │             │
│    └─────┬──────┴──────┬───────┴───────┬──────┘             │
└──────────┼─────────────┼───────────────┼────────────────────┘
           │             │               │
    ┌──────▼─────────────▼───────────────▼──────┐
    │           API ROUTING LAYER               │
    │   PRIMARY:  Gemma 4 API (cloud, free)     │
    │   FALLBACK: Gemini Flash (cloud, free)    │
    │   LOCAL:    Ollama + gemma4:e4b (2.C)     │
    └───────────────────────────────────────────┘

[DESIGN TIME ONLY — never in production]
  Langflow (self-hosted Docker)
    → visual workflow design
    → exports to LangGraph Python
    → merged into codebase
```

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Prerequisite document:* SF-ARCH-001 v1.2 (phase-1-stack.md)
*Next review:* Sub-Phase 2.A KPI validation
*Supersedes:* SF-ARCH-002 v1.0