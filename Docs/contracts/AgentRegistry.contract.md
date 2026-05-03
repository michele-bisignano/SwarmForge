# Contract: AgentRegistry
# File: src/orchestrator/registry.py

## Responsibility
Manages a collection of registered AbstractAgent instances.

## Public Interface

### `register(agent: AbstractAgent) -> None`
"""
Registers an agent instance for use within the swarm.
@param agent: The agent instance to register.
"""

### `all() -> list[AbstractAgent]`
"""
Retrieves all currently registered agents.
@return: A list of registered AbstractAgent instances.
"""

### `by_capability(kind: str) -> list[AbstractAgent]`
"""
Retrieves all agents capable of handling a specific subtask kind.
@param kind: The subtask kind to filter by.
@return: A list of matching AbstractAgent instances.
"""

## Dependencies — What This Class Consumes

### AbstractAgent
- Doc snippet: docs/snippets/abstractagent_snippet.md
- Methods used:
  - `capabilities() -> list[str]` — used to index and query agents by capability.

## SRP Boundary
Stop and escalate if implementation exceeds ~50 lines of logic (excl. docstrings).

## Test Coverage
- Registration of multiple agents
- Retrieval of all agents
- Filtering by capability (matching)
- Filtering by capability (no match/empty result)
- Test-first enabled: YES
- Model tier: cheap — registry logic is simple container management.

## Ownership
- contract: Docs/contracts/AgentRegistry.contract.md
- implementation: src/orchestrator/registry.py
- responsible_contract: Docs/contracts/AgentRegistry.contract.md
