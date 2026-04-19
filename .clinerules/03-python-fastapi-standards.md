---
paths:
  - "**/*.py"
  - "src/**"
  - "tests/**"
---

# 03-python-fastapi-standards.md
# Python & FastAPI Standards (Python projects only)
# Last modified: April 2026

General OOP, comment, and naming rules live in `02-universal-code-standards.md`.
This file covers Python-specific and FastAPI-specific rules only.

---

## Tooling Baseline

| Tool | Role |
|---|---|
| Python 3.10+ | Runtime — mandatory |
| `uv` | Package manager — preferred over pip |
| `ruff` | Linting + formatting (replaces flake8, black, isort) |
| `pytest` + `pytest-asyncio` | Test runner |

`pyproject.toml` minimum:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## Type Hints — Mandatory on Everything

Type hints required on all function parameters, return types, and non-trivial variables.
Code without type hints is not accepted.

**Python 3.10+ syntax (preferred):**
```python
# PREFERRED
def process(value: str | None) -> list[str]: ...

# AVOID (legacy)
from typing import Optional, List
def process(value: Optional[str]) -> List[str]: ...
```

Explicit `None` guard before using any nullable value:
```python
def route(agent: AgentConfig | None) -> str:
    if agent is None:
        raise ValueError("AgentConfig required before routing.")
    return agent.endpoint
```

---

## Docstrings — Google Style

```python
def method(self, param: str, count: int) -> bool:
    """Short description — what it does.

    @param param: Description of param.
    @param count: Description of count.
    @return: True if successful.
    @raise ValueError: When param is empty.
    """
```

---

## OOP — Python Access Modifiers

```python
class AgentRouter:
    def route(self) -> str:           # public — external contract
        return self._select_node()

    def _select_node(self) -> str:    # protected — usable in subclasses
        return self.__score_nodes()[0]

    def __score_nodes(self) -> list:  # private — internal, name-mangled
        ...
```

---

## FastAPI — Required Patterns

**Pydantic v2 for all models:**
```python
from pydantic import BaseModel, Field

class CompletionRequest(BaseModel):
    """OpenAI-compatible completion request."""
    model: str
    messages: list[dict[str, str]]
    stream: bool = False
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
```

**Annotated dependencies (not legacy default-argument style):**
```python
from typing import Annotated
from fastapi import Depends

TelemetryDep = Annotated[NodeTelemetry, Depends(get_node_telemetry)]

# CORRECT
@app.post("/v1/chat/completions", response_model=CompletionResponse)
async def handle_completion(request: CompletionRequest, telemetry: TelemetryDep) -> CompletionResponse: ...

# WRONG — legacy style
@app.post("/v1/chat/completions")
async def handle_completion(request: CompletionRequest, telemetry=Depends(get_node_telemetry)): ...
```

**Endpoint rules:**
- All endpoints: `async def`. No sync endpoints.
- Explicit `response_model` on every endpoint.
- Semantic status codes (`status.HTTP_200_OK`, `status.HTTP_201_CREATED`, etc.).
- Errors via `HTTPException` with a meaningful `detail` string.

---

## Testing

Naming: `test_should_[expected]_when_[condition]`

```python
def test_should_raise_503_when_vram_exceeds_threshold(): ...
def test_should_failover_to_flash_when_gemma_rate_limited(): ...
```

Mock external dependencies (APIs, hardware, DB). Do not mock internal classes you own.

```python
@pytest.mark.asyncio
async def test_should_raise_503_when_vram_exceeds_threshold():
    mock_telemetry = NodeTelemetry(vram_utilization=0.95)
    with patch("module.get_node_telemetry", return_value=mock_telemetry):
        response = await client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 503
```

---

## FastAPI Lifespan (not on_event)
`@app.on_event("startup")` and `@app.on_event("shutdown")` are deprecated.
Always use the lifespan context manager:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    yield
    # shutdown logic

app = FastAPI(lifespan=lifespan)
```

---

## Placeholder Dependencies
Never use `Depends(lambda: None)` or any lambda that returns None as a dependency.
For Phase 1 stubs, always return a valid typed instance:
```python
async def get_current_user() -> UserIdentity:
    return UserIdentity(user_id="dev-user", role="developer")
```