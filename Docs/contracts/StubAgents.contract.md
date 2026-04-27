# Contract: StubAgents
# File: src/agents/stubs.py

## Responsibility
Provides minimal, concrete implementations (stubs) of the three primary agent types: Architect, Coder, and Reviewer. These stubs fulfill the `AbstractAgent` contract with canned, predictable output for Phase 1 testing before core logic development begins.

## Public Interface

### `ArchitectAgent` (Implements AbstractAgent)
"""Stub implementation for the primary architectural planning agent.

@param config: Configuration necessary for agent instantiation.
@return: A stub result containing a pre-defined architectural plan.
@raise NotImplementedError: Only raises if stub logic is incorrectly bypassed.
"""

### `CoderAgent` (Implements AbstractAgent)
"""Stub implementation for the code generation agent.

@param config: Configuration necessary for agent instantiation.
@return: A stub result containing pre-generated code examples.
@raise NotImplementedError: Only raises if stub logic is incorrectly bypassed.
"""

### `ReviewerAgent` (Implements AbstractAgent)
"""Stub implementation for the code review and quality checking agent.

@param config: Configuration necessary for agent instantiation.
@return: A stub result containing a pre-written review summary.
@raise NotImplementedError: Only raises if stub logic is incorrectly bypassed.
"""

## Dependencies — What This Class Consumes

### `AbstractAgent` (ABC)
- Doc snippet: Inherits and completes the contract defined by the ABC.

### `Subtask` (Model)
- Doc snippet: Used to determine which canned output to return.

## SRP Boundary
This class is responsible solely for satisfying the ABC contract with placeholder data and minimum functionality to allow the orchestrator to pass unit tests.

## Ownership
- contract: Docs/contracts/StubAgents.contract.md
- implementation: src/agents/stubs.py
- responsible_contract: Docs/contracts/StubAgents.contract.md
