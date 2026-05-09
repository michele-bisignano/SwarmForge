# Architecture Patterns
---
valid: true
last_verified: 2026-05-09
---

## Core Pattern: Thin Coordinator

SwarmOrchestrator owns workflow loop only. All decisions delegated:
- Decomposition → AbstractTaskDecomposer
- Agent selection → AbstractAgentSelector
- Aggregation → AbstractResultAggregator
- Agent pool → AgentRegistry

Never add business logic to SwarmOrchestrator. SRP limit: ~150 lines.

## Pattern: ABC Boundaries

Every cross-layer boundary = ABC. Concrete implementations injected via constructor.
Swapping any implementation = zero changes to layer above.

```
AbstractAgent → ClineAgent (real) / StubAgents (test)
AbstractTaskDecomposer → RuleBasedTaskDecomposer
AbstractAgentSelector → CapabilityMatchSelector
AbstractResultAggregator → SequentialResultAggregator
```

## Pattern: OpenAI-Compatible Interface

Every AI call goes through /v1/chat/completions. Never call provider SDKs directly.
ClineAgent is canonical implementation. Swap provider = change YAML only.

## Pattern: Context Chaining

Each subtask receives output of all previous successful subtasks.
Failed subtask output excluded from context (prevents error propagation).
Format: `--- {agent_id} output ---\n{content}\n\n`

## Pattern: YAML-Driven Wiring

SwarmFactory reads configs/agents/{role}.yaml → AgentConfig → ClineAgent.
New role = new YAML file, zero code changes.
Env var overrides: `{ROLE}_MODEL`, `{ROLE}_API_BASE_URL`.

## Pattern: Sequential Execution

Phase 2: subtasks run sequentially. No parallelism yet.
Phase 3+: parallel execution requires Gateway + Load Balancer.

## Pattern: Vertical AI Hierarchy

```
AbstractAIModel (core/)
  └── AbstractTextModel (text/)
        └── AbstractWebTextModel (text/web/)
              └── ConcreteWebModel (text/web/providers/{provider}/)
```

Each inheritance level = one directory deeper. One class per file.