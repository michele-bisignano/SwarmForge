# Contract: AbstractAgent
# File: src/agents/base.py

## Responsibility
Defines the foundational contract and common interface for all specialized, capability-providing agents within the SwarmForge execution framework. It ensures all derived agents adhere to a consistent operational structure.

## Public Interface

### `run(subtask: Subtask) -> SubtaskResult`
"""Executes the core logic defined by a specific subtask, coordinating necessary sub-operations (e.g., planning, coding, reviewing).

@param subtask: The Subtask object containing the task instructions, dependencies, and metadata.
@return: A SubtaskResult containing the outcome, status, and generated content.
@raises ConnectionError: If the underlying external resource (e.g., API) is unreachable during execution.
"""

### `agent_id() -> str`
"""Returns a unique, immutable identifier for this agent instance, typically composed of the agent type and a unique instance ID.

@return: A string identifier following the pattern [AgentType]_[UniqueID].
"""

### `capabilities() -> list[str]`
"""Returns a list of generic task types (strings) that this agent is capable of handling. This must be consistent with the naming in SubtaskKind.

@return: A list of strings corresponding to the subtask kinds this agent addresses (e.g., ["coder", "reviewer"]).
"""

### `health() -> bool`
"""Checks the operational status of the agent's external dependencies and internal state.

@return: True if the agent is fully operational; False otherwise.
"""

## Dependencies — What This Class Consumes

### `Subtask` (Model)
- Doc snippet: Contains the task description, priority, and required context data.

### `AbstractBaseClass`
- Doc snippet: Provides core initialization and utility methods and must be inherited.

## SRP Boundary
The class is strictly limited to defining the *interface* and common methods; core business logic must be implemented in concrete subclasses.