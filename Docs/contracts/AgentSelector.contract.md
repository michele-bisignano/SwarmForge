# Contract: AbstractAgentSelector and CapabilityMatchSelector
# File: src/orchestrator/selector.py

## Responsibility
AbstractAgentSelector: Defines the strategy for selecting an agent for a given subtask.
CapabilityMatchSelector: Selects the first agent that declares support for the subtask's capability.

## Public Interface (AbstractAgentSelector)

### `select(subtask: Subtask, registry: AgentRegistry) -> AbstractAgent | None`
"""
Selects an appropriate agent from the registry for the given subtask.
@param subtask: The subtask requiring execution.
@param registry: The registry of available agents.
@return: The selected AbstractAgent, or None if no match is found.
"""

## Dependencies — What This Class Consumes

### Subtask
- Doc snippet: docs/snippets/subtask_snippet.md
- Methods used:
  - `.kind` — used to match against agent capabilities.

### AgentRegistry
- Doc snippet: docs/snippets/agentregistry_snippet.md
- Methods used:
  - `by_capability(kind: str) -> list[AbstractAgent]` — used to find eligible agents.

## SRP Boundary
Stop and escalate if implementation exceeds ~30 lines of logic (excl. docstrings).

## Test Coverage
- `CapabilityMatchSelector`: Selection with a single matching agent
- `CapabilityMatchSelector`: Selection with multiple matching agents (must return first)
- `CapabilityMatchSelector`: Selection with no matching agents (must return None)
- Test-first enabled: YES
- Model tier: cheap — selection logic is simple matching.

## Ownership
- contract: Docs/contracts/AgentSelector.contract.md
- implementation: src/orchestrator/selector.py
- responsible_contract: Docs/contracts/AgentSelector.contract.md
