# SwarmForge — Phase 2 Stack Definition
**Document ID:** `SF-ARCH-002`
**Codename:** *The Swarm*
**Version:** 1.0
**Status:** Approved — Architecture Draft
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026

---

## 1. Objective

Phase 2 transitions SwarmForge from a single-agent vibe-coding assistant into a
coordinated multi-agent system. The core shift is architectural: instead of one
agent receiving all tasks, a dedicated orchestration layer decomposes complex jobs
and dispatches them to specialized agents with distinct roles.

**The key design decision for Phase 2:** all agents are cloud-based (API-driven)
at launch. Local agents are explicitly deferred to a later sub-phase (2.C) once
the orchestration layer is stable and validated. This avoids conflating two
independent problems — "how do agents collaborate?" and "where do agents run?" —
into a single, unmanageable complexity spike.

---

## 2. Architectural Shift from Phase 1

```
PHASE 1 — Single Agent, Human-in-the-Loop
─────────────────────────────────────────
  Developer
     │
  VS Code (Cline / Aider)
     │
  Gemma 4 API  ←── one model, one agent, human approves every step


PHASE 2 — Multi-Agent Orchestration
─────────────────────────────────────────
  Developer
     │
  VS Code (Cline — supervision layer)
     │
  ┌──▼──────────────────────────────────┐
  │        ORCHESTRATION LAYER          │
  │   LangGraph (DAG state machine)     │
  └──┬─────────────┬────────────┬───────┘
     │             │            │
  Agent:        Agent:       Agent:
  Architect     Coder        Reviewer
     │             │            │
  Gemma 4 API  Gemma 4 API  Gemma 4 API
  (cloud)      (cloud)      (cloud)
```

The developer no longer manages individual agents. They interact exclusively with
the orchestrator, which decomposes tasks, assigns them to the correct agent, and
synthesizes the output before surfacing it in VS Code.

---

## 3. License Audit Summary

| Component | License | Status |
|---|---|---|
| LangGraph | MIT | ✅ Approved |
| OpenJarvis | Apache 2.0 | ✅ Approved |
| Langflow | MIT | ✅ Approved |
| Flowise | Apache 2.0 | ✅ Approved (secondary option) |
| SWE-agent | MIT | ✅ Approved (pending ACI deep-dive) |
| AG2 / AutoGen sandbox | MIT + Apache 2.0 | ⚠️ Pending license audit on sandbox module |

> **AG2 Policy:** The AG2 sandbox module must not be integrated until a line-by-line
> license audit of its transitive dependencies is completed. The top-level MIT
> declaration does not guarantee clean transitive licenses.

---

## 4. Phase 2 Sub-Phases

Phase 2 is divided into three sequential sub-phases to control complexity.
Each sub-phase has its own success criteria before the next one begins.

---

### Sub-Phase 2.A — Orchestration Layer (Cloud-Only Agents)

**Goal:** Replace the single Cline agent with a LangGraph-coordinated team of
cloud agents. All agents consume the Gemma 4 API. No local models, no hardware
changes, no new infrastructure.

#### 4.1 Orchestrator — LangGraph

LangGraph is the orchestration engine. It models agent collaboration as a
directed acyclic graph (DAG) where each node is an agent and each edge is a
state transition.

**Why LangGraph over CrewAI:**

| Criterion | LangGraph | CrewAI |
|---|---|---|
| Execution model | Deterministic DAG | Role-based loop |
| State management | Native checkpointing | External |
| Error recovery | Built-in (rollback to checkpoint) | Manual |
| Parallelism | Native | Limited |
| Debuggability | Full graph trace | Opaque |
| License | MIT | MIT |

LangGraph's checkpointing is critical for our use case: if the Coder agent
fails mid-task, the orchestrator restores the last valid state and retries
without losing context. CrewAI has no equivalent mechanism.

**Agent Roles (Phase 2.A initial set):**

```python
# Conceptual role definitions — not operational code
AGENT_ROLES = {
    "architect": "Decomposes the task. Produces a structured plan with 
                  file-level scope and dependency order.",
    "coder":     "Executes the plan. Writes or modifies code files 
                  according to the architect's specification.",
    "reviewer":  "Validates the output. Checks for logical errors, 
                  style violations, and missing edge cases. 
                  Returns a pass/fail verdict with notes.",
}
```

**State schema (minimal):**

```python
# Conceptual state schema — not operational code
class SwarmState(TypedDict):
    task_description: str         # original developer request
    plan: list[dict]              # architect output
    code_changes: list[dict]      # coder output (file, diff)
    review_result: dict           # reviewer verdict
    iteration_count: int          # loop guard
    status: Literal["pending", "in_progress", "approved", "failed"]
```

**Loop Guard:** The orchestrator must enforce a maximum iteration count
(recommended: 3 retry cycles) before escalating to the developer. Unbounded
agent loops are a known failure mode — LangGraph's `loop_guard` pattern
handles this natively.

#### 4.2 Agent Backend — OpenJarvis

OpenJarvis is integrated as the backend runtime layer, not as the orchestrator.
LangGraph handles the logic; OpenJarvis handles infrastructure concerns.

**What OpenJarvis provides in Phase 2.A:**

```
OpenJarvis Responsibility              Replaces
───────────────────────────────────────────────
FastAPI server (agent endpoints)   ←  hand-rolled FastAPI boilerplate
Interaction log tracing            ←  custom logging code
Hardware metrics collection        ←  manual pynvml calls
Engine abstraction layer           ←  direct API calls hardcoded to Google
```

**What OpenJarvis does NOT manage in Phase 2.A:**
- Orchestration logic (LangGraph owns this)
- VS Code integration (Cline owns this)
- Model selection (config file, not OpenJarvis)

**Integration point:**

```
VS Code (Cline)
     │
     │  OpenAI-compatible request
     ▼
OpenJarvis FastAPI server   ←── receives task from Cline
     │
     │  dispatches to LangGraph
     ▼
LangGraph Orchestrator
     │
     ├── Architect Agent → Gemma 4 API
     ├── Coder Agent     → Gemma 4 API
     └── Reviewer Agent  → Gemma 4 API
```

From Cline's perspective, nothing has changed. It sends a standard
OpenAI-compatible request to a local endpoint. The entire multi-agent
coordination is invisible to the IDE layer.

#### 4.3 Success Criteria — Sub-Phase 2.A

| KPI | Target |
|---|---|
| Successful multi-agent task completion | 100% on 5 test tasks spanning 3+ files |
| Orchestrator infinite loop incidents | 0 (loop guard active) |
| Agent coordination overhead (latency vs Phase 1) | < 2× Phase 1 TTFT |
| External paid API calls | 0 during standard sessions |
| Rollback on agent failure | Functional in 100% of tested failure scenarios |

---

### Sub-Phase 2.B — Visual Prototyping Layer

**Goal:** Add Langflow as a visual interface for designing and testing new
agent workflows without writing Python. This is a developer productivity tool,
not a production component.

#### 4.4 Visual Orchestration — Langflow

Langflow provides a node-based drag-and-drop interface where agent workflows
are assembled visually. Each node maps 1:1 to a LangGraph node in Python.

**Role in SwarmForge:**

```
DESIGN TIME (Langflow)          PRODUCTION (LangGraph)
──────────────────────          ─────────────────────
Drag nodes onto canvas    →     Python DAG definition
Connect edges visually    →     State transition logic
Test prompt flows         →     Validated agent prompts
Export as Python          →     Merge into codebase
```

Langflow is used exclusively during workflow design and iteration. Once a
workflow is validated, it is exported to Python and integrated into the
LangGraph codebase. Langflow never runs in production.

**Deployment:** self-hosted locally via Docker (MIT license, no external
data sent). Never expose Langflow to a public network — it contains
proprietary workflow designs.

**Flowise** (Apache 2.0, TypeScript/Node.js) is documented as the secondary
fallback if Langflow introduces blockers. The evaluation criterion is simple:
use whichever exports cleaner LangGraph-compatible Python.

#### 4.5 Success Criteria — Sub-Phase 2.B

| KPI | Target |
|---|---|
| New agent workflow designed in Langflow | ≥ 1 complete workflow |
| Langflow → Python export without manual rewriting | 100% clean export |
| Langflow running fully self-hosted (no external calls) | Verified |

---

### Sub-Phase 2.C — Hybrid Agent Layer (Cloud + Local)

**Goal:** Introduce local model inference as an optional backend for select
agents, reducing API dependency and rate-limit exposure for high-frequency tasks.

**This sub-phase is gated on Sub-Phase 2.A being fully stable.**
Do not begin 2.C while 2.A still has open issues.

#### 4.6 Local Inference Integration

Local agents use the same OpenAI-compatible interface as cloud agents.
The only change is the endpoint URL in the agent configuration.

```
Cloud Agent Configuration          Local Agent Configuration
──────────────────────────         ─────────────────────────
endpoint: AI Studio URL            endpoint: http://localhost:11434
model:    gemma-4-26b-a4b-it       model: gemma4:e4b (quantized)
api_key:  GOOGLE_AI_STUDIO_KEY     api_key: (none — local)
```

**Recommended local model for 8GB VRAM:**

| Model | VRAM Required | Quality vs Cloud | Use Case |
|---|---|---|---|
| `gemma4:e4b` (4.5B, quantized) | ~5GB | 70% | High-frequency, low-complexity tasks |
| `gemma4:26b` (26B MoE, Q4) | ~14GB | 95% | Requires RAM offload — unstable on 8GB |

On the current hardware, only `gemma4:e4b` is viable locally without RAM offload.
Reserve local inference for the Reviewer agent (low-complexity, high-frequency)
to preserve rate limit budget for Architect and Coder (high-complexity).

**SWE-agent ACI Pattern (pending deep-dive):**
SWE-agent's Agent-Computer Interface restricts the set of shell commands an LLM
can invoke, reducing the attack surface of autonomous code execution. If the
ACI audit confirms no GPL transitive dependencies, integrate the pattern into
the Coder agent's tool schema in this sub-phase.

#### 4.7 Success Criteria — Sub-Phase 2.C

| KPI | Target |
|---|---|
| Local agent TTFT | < 3 seconds (acceptable degradation vs cloud) |
| OOM crashes on 8GB VRAM node | 0 |
| Seamless failover local → cloud on rate limit | Functional |
| Paid API calls during local-primary sessions | 0 |

---

## 5. Open Decisions (Deferred to Phase 3)

The following are deliberately out of scope for Phase 2:

1. **Second physical node:** networking, mesh VPN, IP masking — all deferred.
2. **Gateway / Load Balancer:** not needed until there are 2+ physical nodes.
3. **Fine-tuning pipeline:** deferred to Phase 4 (requires stable log format
   established in Phase 2 via OpenJarvis tracing).
4. **AG2 sandbox integration:** blocked pending license audit of transitive
   dependencies.

---

## 6. Dependency on Phase 1 Outputs

Phase 2 cannot begin until the following Phase 1 deliverables are confirmed:

- [ ] Cline successfully executes 5 autonomous IDE commands (Phase 1 KPI #2)
- [ ] TTFT < 1.5s confirmed on Gemma 4 API (Phase 1 KPI #1)
- [ ] OpenJarvis installed and FastAPI server running locally
- [ ] At least one `SKILL.md` file authored and validated in Cline

---

## 7. Updated Technology Stack — Full Phase 2 Picture

```
┌─────────────────────────────────────────────────────────────┐
│                        DEVELOPER                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      IDE LAYER                              │
│         VS Code + Cline (supervision & approval)            │
└─────────────────────────┬───────────────────────────────────┘
                          │  OpenAI-compatible request
┌─────────────────────────▼───────────────────────────────────┐
│                  BACKEND RUNTIME                            │
│              OpenJarvis (FastAPI server)                    │
│         trace logging │ hardware metrics │ engine routing   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               ORCHESTRATION LAYER                           │
│                 LangGraph (DAG)                             │
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
    Langflow (self-hosted) → visual workflow design → exports to LangGraph Python
```

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Prerequisite document:* `SF-ARCH-001` (phase-1-stack.md)
*Next review:* Sub-Phase 2.A KPI validation
