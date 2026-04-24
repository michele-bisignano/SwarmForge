# Class Hierarchy Map — SwarmOrchestrator (Phase 1 Skeleton)

**Feature:** SwarmOrchestrator
**Phase:** 1 — *Single-Node Genesis*
**Status:** Draft — **awaiting developer approval before Step 4 (contract production)**
**Authoring rule:** `04-contract-architect.md` Step 3.

---

## 1. Tree

```
─── Value Objects (Pydantic v2 models — pure data, no logic) ─────────────────

TaskRequest        (description: str)
Subtask            (id: str, kind: SubtaskKind, description: str,
                    dependencies: list[str])
SubtaskResult      (subtask_id: str, agent_id: str,
                    status: SubtaskStatus, content: str,
                    error: str | None)
SwarmResult        (task_id: str, final_content: str,
                    subtask_results: list[SubtaskResult],
                    status: SwarmStatus)

SubtaskKind        (Enum — ARCHITECT | CODER | REVIEWER)
SubtaskStatus      (Enum — OK | FAILED | SKIPPED)
SwarmStatus        (Enum — OK | PARTIAL | FAILED)

─── Abstractions (ABCs — cross-layer contracts, swap-ready) ──────────────────

AbstractAgent (ABC)
  │   async run(subtask: Subtask) -> SubtaskResult
  │   capabilities() -> set[SubtaskKind]
  │   agent_id() -> str
  │
  ├── ArchitectAgent          (Phase 1 stub — returns canned plan text)
  ├── CoderAgent              (Phase 1 stub — returns canned code text)
  └── ReviewerAgent           (Phase 1 stub — returns canned review text)

AbstractTaskDecomposer (ABC)
  │   async decompose(request: TaskRequest) -> list[Subtask]
  │
  └── RuleBasedTaskDecomposer (Phase 1 — keyword-driven rules)

AbstractAgentSelector (ABC)
  │   select(subtask: Subtask, registry: AgentRegistry) -> AbstractAgent
  │
  └── CapabilityMatchSelector (matches Subtask.kind ⊆ agent.capabilities())

AbstractResultAggregator (ABC)
  │   aggregate(task_id: str, results: list[SubtaskResult]) -> SwarmResult
  │
  └── SequentialResultAggregator (ordered concatenation by subtask order)

─── Registry (concrete, no abstraction needed — single behavior) ─────────────

AgentRegistry
    register(agent: AbstractAgent) -> None
    all() -> list[AbstractAgent]
    by_capability(kind: SubtaskKind) -> list[AbstractAgent]

─── Coordinator (this cycle's contract target) ───────────────────────────────

SwarmOrchestrator
  │   async run(task_description: str) -> SwarmResult
  │
  ├── depends on: AbstractTaskDecomposer
  ├── depends on: AgentRegistry
  ├── depends on: AbstractAgentSelector
  └── depends on: AbstractResultAggregator
```

---

## 2. Dependency Direction (no cycles)

```
SwarmOrchestrator
       │
       ├──▶ AbstractTaskDecomposer ─────▶ TaskRequest, Subtask
       │
       ├──▶ AgentRegistry ──────────────▶ AbstractAgent
       │
       ├──▶ AbstractAgentSelector ──────▶ AbstractAgent, AgentRegistry, Subtask
       │
       └──▶ AbstractResultAggregator ───▶ SubtaskResult, SwarmResult
```

All arrows point downward. Value objects sit at the leaves and depend on nothing. **No circular dependencies.**

---

## 3. Plug & Play Verification

| Swap scenario | Files changed in `SwarmOrchestrator` |
|---|---|
| Replace rule-based decomposer with LLM-driven | 0 |
| Add a 4th agent type (e.g. `TesterAgent`) | 0 |
| Replace capability-match selector with semantic-router | 0 |
| Replace sequential aggregator with graph-aware aggregator | 0 |
| Move from in-process agents to remote A2A agents | 0 (new `AbstractAgent` subclass) |

Project Brief Pillar §4.3 (Plug & Play) and §4.4 (Dynamic Orchestration) honored at the architectural level.

---

## 4. SOLID Audit

| Principle | Compliance |
|---|---|
| **S** — Single Responsibility | Each class has one reason to change. `SwarmOrchestrator` = workflow loop only. |
| **O** — Open/Closed | New agents / decomposers / selectors / aggregators added by subclassing. No edits to existing classes. |
| **L** — Liskov | Every concrete `Abstract*` subclass returns the exact contract type. |
| **I** — Interface Segregation | Each ABC exposes 1–3 methods. No fat interfaces. |
| **D** — Dependency Inversion | `SwarmOrchestrator` depends only on ABCs. Concrete classes injected via constructor. |

---

## 5. File Placement Plan (per `repository_tree.md`)

| Class group | Target path |
|---|---|
| Value objects + enums | `src/orchestrator/models.py` |
| `AbstractAgent` + concrete stub agents | `src/orchestrator/agents/` (new package) |
| `AbstractTaskDecomposer` + concrete | `src/orchestrator/decomposer.py` |
| `AbstractAgentSelector` + concrete | `src/orchestrator/selector.py` |
| `AbstractResultAggregator` + concrete | `src/orchestrator/aggregator.py` |
| `AgentRegistry` | `src/orchestrator/registry.py` |
| `SwarmOrchestrator` | `src/orchestrator/orchestrator.py` *(file already exists, empty)* |

Final placement is locked per-class in each future contract. Listed here for reviewer visibility only.

---

## 6. What This Cycle Will Contract

**This cycle:** `SwarmOrchestrator` only.

**Future cycles, in dependency order (upstream first, so ClassCoders can use griffe snippets of completed dependencies):**

1. Value objects (`models.py`)
2. `AbstractAgent` + 3 stub agents
3. `AgentRegistry`
4. `AbstractTaskDecomposer` + `RuleBasedTaskDecomposer`
5. `AbstractAgentSelector` + `CapabilityMatchSelector`
6. `AbstractResultAggregator` + `SequentialResultAggregator`
7. *(SwarmOrchestrator already contracted — implementation last)*

Implementation order is the reverse of contract order: dependencies built first, orchestrator built last (top-down design, bottom-up implementation).

---

## 7. STOP — Approval Gate

**Per `04-contract-architect.md` Step 3:** present hierarchy → wait for explicit user approval → only then proceed to Step 4 (contract documents).

**Awaiting:** developer approval of this hierarchy.

**On approval:** Step 4 produces `docs/contracts/SwarmOrchestrator.contract.md` only. Other classes remain uncontracted in this cycle.
