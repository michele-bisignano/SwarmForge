# Doc Snippet: AgentRegistry

**Class docstring:** Manages a collection of registered AbstractAgent instances.

## Methods

### `register(agent: {'cls': 'ExprName', 'member': 'register', 'name': 'AbstractAgent'}) -> None`
```
Registers an agent instance for use within the swarm.

@param agent: The agent instance to register.
```

### `all() -> None`
```
Retrieves all currently registered agents.

@return: A list of registered AbstractAgent instances.
```

### `by_capability(kind: {'cls': 'ExprName', 'member': 'by_capability', 'name': 'str'}) -> None`
```
Retrieves all agents capable of handling a specific subtask kind.

@param kind: The subtask kind to filter by.
@return: A list of matching AbstractAgent instances.
```
