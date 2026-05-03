# Doc Snippet: AbstractAgentSelector

**Class docstring:** Defines the strategy for selecting an agent for a given subtask.

## Methods

### `select(subtask: {'cls': 'ExprName', 'member': 'select', 'name': 'Subtask'}, registry: {'cls': 'ExprName', 'member': 'select', 'name': 'AgentRegistry'}) -> None`
```
Selects an appropriate agent from the registry for the given subtask.

@param subtask: The subtask requiring execution.
@param registry: The registry of available agents.
@return: The selected AbstractAgent, or None if no match is found.
```
