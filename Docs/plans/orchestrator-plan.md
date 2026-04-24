# Plan — SwarmOrchestrator Module

**Feature:** SwarmOrchestrator — thin coordinator for task → subtasks → agents → result.
**Phase:** 1 — *Single-Node Genesis*. Skeleton with stub agents. No real LLM calls.
**Author role:** ContractArchitect (writes no implementation code).
**Status:** Awaiting Class Hierarchy Map approval before contract production.

---

## 1. Intent (Locked)

**Single observable behavior:** Given a task description string, produce a final aggregated result by:
1. Decomposing the description into subtasks.
2. Routing each subtask to a matching agent (architect / coder / reviewer).
3. Aggregating subtask results into one structured output.

**Inputs at system boundary:** `task_description: str`.
**Outputs at system boundary:** `SwarmResult` (Pydantic v2 model — final content + per-subtask trace).
**Existing classes affected:** none. All classes in this feature are net-new.

**Non-goals (Phase 1):**
- No real LLM invocation. Agents are stubs implementing `AbstractAgent`.
- No persistence. No telemetry. No load balancing. No multi-node routing.
- No streaming responses. Single `await orchestrator.run(...)` returning the full result.
- No FastAPI endpoints in this cycle. The class is library-level; HTTP exposure is a later concern.

---

## 2. Architectural Pillars Honored

| Pillar (Project Brief §4) | How it is honored |
|---|---|
| Total Scalability & Extensibility | Agents register dynamically into `AgentRegistry`. New agent types = new `AbstractAgent` subclasses. |
| Plug & Play Modularity | Every collaborator of `SwarmOrchestrator` is an ABC. Swapping any concrete implementation = zero change to orchestrator. |
| AI-First Code Standards | Pydantic v2 models for every value object. Full Google-style docstrings on every public method. Type hints mandatory. |
| Data Sovereignty | No external service calls in Phase 1 stubs. |
| OpenAI-Compatible Interface (Rule §00) | Reserved for Phase 2 `LLM*Agent` concrete implementations. Phase 1 stubs do not call any backend. |

---

## 3. Decomposition Decision Record

`SwarmOrchestrator` is a **thin coordinator**. The three responsibilities it would otherwise absorb are split into dedicated abstractions:

| Responsibility | Owner Class | Rationale |
|---|---|---|
| Break description into subtasks | `AbstractTaskDecomposer` | Strategy will evolve (rule-based stub → LLM-driven). Must be swappable without touching orchestrator. |
| Pick agent for a subtask | `AbstractAgentSelector` | Strategy will evolve (capability match → semantic-router → telemetry-aware). Must be swappable. |
| Combine subtask results | `AbstractResultAggregator` | Strategy will evolve (sequential concat → graph-aware merge). Must be swappable. |
| Hold the live agent pool | `AgentRegistry` | Single source of truth for available agents. Selector queries it. Orchestrator never holds agents directly. |

**Result:** `SwarmOrchestrator` owns only the *workflow loop*. It cannot grow past ~150 lines without an SRP escalation.

---

## 4. Target Artifacts (this cycle)

| Artifact | Path | Status |
|---|---|---|
| Plan (this file) | `docs/plans/orchestrator-plan.md` | Drafted |
| Class Hierarchy Map | `docs/architecture/orchestrator-hierarchy.md` | Drafted — **awaiting approval** |
| Contract: `SwarmOrchestrator` | `docs/contracts/SwarmOrchestrator.contract.md` | Pending hierarchy approval |

**Out of scope for this cycle** (separate ContractArchitect cycles, one per class):
- `AbstractAgent` + `ArchitectAgent` / `CoderAgent` / `ReviewerAgent` contracts
- `AbstractTaskDecomposer` + `RuleBasedTaskDecomposer` contract
- `AbstractAgentSelector` + `CapabilityMatchSelector` contract
- `AbstractResultAggregator` + `SequentialResultAggregator` contract
- `AgentRegistry` contract
- Pydantic value objects (`TaskRequest`, `Subtask`, `SubtaskResult`, `SwarmResult`)

The `SwarmOrchestrator` contract will reference these by name and will be produced *first* (top-down) so that ClassCoders implementing the dependencies later have a stable downstream consumer to validate against.

---

## 5. Workflow Gates

1. ✅ Step 1 — Intent clarified (developer reply received).
2. ✅ Step 2 — Project tree re-read.
3. ⏸ Step 3 — Hierarchy map drafted → **STOP for approval**.
4. ⏳ Step 4 — Contract document for `SwarmOrchestrator` (after Step 3 approval).
5. ⏳ Future cycles — One contract per dependency class, in dependency order (upstream first).

No source code will be written in any step of this cycle. ContractArchitect role boundary.
