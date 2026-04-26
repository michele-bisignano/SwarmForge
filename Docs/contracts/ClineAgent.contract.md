# Contract: AgentConfig and ClineAgent
# Files: src/agents/config.py, src/agents/cline_agent.py

## Responsibility

AgentConfig carries provider-agnostic agent configuration as a Pydantic v2 value object. ClineAgent implements AbstractAgent by calling any OpenAI-compatible chat completions endpoint, returning the response text as a SubtaskResult.

---

## AgentConfig — Public Interface

### `role: str`
Role identifier for this agent instance (e.g. "architect", "coder", "reviewer"). No enum constraint — new roles added via YAML config without code changes.

### `system_prompt: str`
System-level instruction injected as the first message in every API call. Defines the agent's behavior, constraints, and output format.

### `model: str`
Model name string sent in the API request body (e.g. "gemini-2.0-flash", "gpt-4o"). No default — must be explicitly set in YAML or injected at runtime.

### `api_base_url: str`
Base URL of the OpenAI-compatible endpoint. The agent appends `/v1/chat/completions` to this value at call time. No trailing slash expected.

### `api_key_env_var: str`
Name of the environment variable holding the API key (e.g. "GOOGLE_AI_STUDIO_API_KEY"). The agent reads the key at call time via `os.getenv()`, not at construction. This allows late binding for testing and runtime injection.

### `extra_params: dict = {}`
Provider-specific parameters merged into the top level of the JSON request body alongside `model` and `messages`. Typical values: `temperature`, `max_tokens`, `top_p`. Parameters unsupported by a given provider are silently ignored by that provider's API. No validation beyond dict type.

---

## ClineAgent — Public Interface

### `__init__(config: AgentConfig) -> None`
"""Initialize the agent with its configuration.

@param config: AgentConfig instance with role, model, endpoint, and API key metadata.
"""

### `async run(subtask: Subtask) -> SubtaskResult`
"""Execute the subtask by calling the configured OpenAI-compatible endpoint.

Reads the API key from the environment variable named by config.api_key_env_var.
If the key is missing, returns SubtaskResult with status FAILED and a descriptive error.
Sends a POST to {config.api_base_url}/v1/chat/completions with the system prompt
and subtask description as messages. Spreads config.extra_params into the request body.
On HTTP success, extracts the first choice's message content as the result.
On HTTP error or exception, returns FAILED with the exception message.

@param subtask: The Subtask to execute. Its description field is used as the user message.
@return: SubtaskResult with status OK and the model's response text, or FAILED with an error.
"""

### `agent_id() -> str`
"""Return a unique, role-scoped identifier for this agent.

@return: A string of the form "cline_{role}" (e.g. "cline_architect").
"""

### `capabilities() -> list[str]`
"""Return the task types this agent can handle.

@return: Single-element list containing config.role — the agent claims capability
         for subtasks whose kind matches its configured role.
"""

### `health() -> bool`
"""Check whether the configured endpoint is reachable.

Performs a lightweight HEAD or GET request to config.api_base_url.
Catches ALL exceptions (ConnectionError, TimeoutException, HTTPError, etc.)
and returns False gracefully. Never propagates exceptions.

@return: True if the endpoint responds without error; False if unreachable,
         timed out, or the API key environment variable is not set.
"""

---

## Dependencies — What ClineAgent Consumes

### AgentConfig (value object)
- Source: same file (src/agents/config.py)
- Fields used: all six fields — role, system_prompt, model, api_base_url, api_key_env_var, extra_params.

### Subtask (existing model)
- Source: src/orchestrator/models.py
- Fields used:
  - `id: str` — copied to SubtaskResult.subtask_id
  - `description: str` — used as the user message in the API call

### SubtaskResult (existing model)
- Source: src/orchestrator/models.py
- Used to construct the return value — never read as input.

### AbstractAgent (ABC)
- Source: src/agents/base.py
- Methods implemented: run, agent_id, capabilities, health.
- Doc snippet reference: docs/snippets/abstractagent_snippet.md

### httpx (external, MIT)
- Used for async HTTP POST to the OpenAI-compatible endpoint.
- Pattern: `async with httpx.AsyncClient() as client: response = await client.post(...)`
- Reads `Authorization: Bearer {api_key}` header.
- Reads `Content-Type: application/json` header.

### os.getenv (stdlib)
- Used to read the API key at call time from the environment variable name stored in config.api_key_env_var.

---

## Request Body Construction

```json
POST {api_base_url}/v1/chat/completions
Authorization: Bearer {value of os.getenv(api_key_env_var)}
Content-Type: application/json

{
    "model": "{config.model}",
    "messages": [
        {"role": "system", "content": "{config.system_prompt}"},
        {"role": "user", "content": "{subtask.description}"}
    ],
    **config.extra_params
}
```

Response extraction: `response.json()["choices"][0]["message"]["content"]`

---

## Error Handling

| Condition | Action |
|---|---|
| `os.getenv(config.api_key_env_var)` returns None | Return `SubtaskResult(status=FAILED, error="Missing API key: {api_key_env_var}")` |
| HTTP status >= 400 | Return `SubtaskResult(status=FAILED, error="HTTP {status_code}: {response_text}")` |
| httpx.TimeoutException | Return `SubtaskResult(status=FAILED, error="Request timeout: {exception}")` |
| httpx.ConnectError or other network error | Return `SubtaskResult(status=FAILED, error="Connection failed: {exception}")` |
| JSON decode error on response | Return `SubtaskResult(status=FAILED, error="Invalid response: {exception}")` |
| Any other unexpected exception | Return `SubtaskResult(status=FAILED, error="{exception}")` |
| health() — any exception | Catch all, return False. Never raise. |

All error paths set `content=""` and populate `error` with the exception string.

---

## SRP Boundary

- AgentConfig: data carrier only. No methods, no logic. ~20 lines.
- ClineAgent: one responsibility — call OpenAI-compatible API and return result. Estimated ~80 lines of logic.

Stop and escalate if ClineAgent implementation exceeds ~150 lines of logic (excluding docstrings and blank lines).

---

## Test Coverage

AgentConfig:
- Instantiation with all required fields
- Instantiation with optional extra_params omitted (defaults to {})
- extra_params accepts arbitrary keys (provider-specific params pass through)
- role accepts any string value (not constrained to enum)

ClineAgent:
- Happy path: valid API key, valid endpoint, returns SubtaskResult OK with response content
- Missing API key: returns FAILED with "Missing API key: {name}" error
- HTTP 4xx error: returns FAILED with HTTP status in error message
- HTTP 5xx error: returns FAILED with HTTP status in error message
- Connection error (unreachable endpoint): returns FAILED with connection error
- Timeout: returns FAILED with timeout error
- Invalid JSON response: returns FAILED with decode error
- agent_id() returns correct pattern: "cline_{role}"
- capabilities() returns list containing config.role
- health() returns True when endpoint is reachable
- health() returns False when endpoint is unreachable
- health() returns False when API key is missing (does not raise)
- extra_params are present in the request body sent to the endpoint
- Authorization header contains the API key value

Test-first enabled: YES
Model tier: cheap (httpx can be mocked — no real API calls needed for unit tests)

---

## YAML Config Files

Three config files in configs/agents/:

### architect.yaml
```yaml
role: architect
system_prompt: |
  You are a software architect specialized in system design.
  Your task is to analyze requirements and produce a detailed architectural plan.
  Output your plan in structured markdown with the following sections:
  1. Overview
  2. Component Design
  3. Data Flow
  4. File Structure
  5. Dependencies and Risks
  Be precise. Every component must have a single responsibility.
model: ${ARCHITECT_MODEL}
api_base_url: ${ARCHITECT_API_BASE_URL}
api_key_env_var: ARCHITECT_API_KEY
extra_params:
  temperature: 0.3
  max_tokens: 4096
```

### coder.yaml
```yaml
role: coder
system_prompt: |
  You are an expert software engineer. Your task is to implement code
  according to the provided specification. Follow these rules strictly:
  - Write correct, tested, production-ready code
  - Every public function must have a Google-style docstring
  - Type hints mandatory on all parameters and return values
  - Follow the project's coding standards without deviation
  - Output only the implementation code, no explanatory text
model: ${CODER_MODEL}
api_base_url: ${CODER_API_BASE_URL}
api_key_env_var: CODER_API_KEY
extra_params:
  temperature: 0.1
  max_tokens: 8192
```

### reviewer.yaml
```yaml
role: reviewer
system_prompt: |
  You are a senior code reviewer. Your task is to review code for correctness,
  style, and adherence to project standards. For each issue found, report:
  1. File and line reference
  2. Severity (critical / warning / style)
  3. Description of the problem
  4. Suggested fix
  Also note any Single Responsibility Principle violations — any class
  or function doing more than one thing.
model: ${REVIEWER_MODEL}
api_base_url: ${REVIEWER_API_BASE_URL}
api_key_env_var: REVIEWER_API_KEY
extra_params:
  temperature: 0.2
  max_tokens: 4096
```

Placeholder values (`${...}`) are the production pattern. A `ConfigLoader` utility
(separate future cycle) will resolve env var substitution at runtime. For Phase 2.B
development, values can be hardcoded directly in YAML — placeholders are the target state.

Each role uses a separate API key and potentially a different model/provider —
this is intentional for provider-agnostic operation.

---

## Output Artifacts

| Artifact | Location |
|---|---|
| AgentConfig implementation | src/agents/config.py |
| ClineAgent implementation | src/agents/cline_agent.py |
| Test file | tests/agents/test_cline_agent.py |
| architect config | configs/agents/architect.yaml |
| coder config | configs/agents/coder.yaml |
| reviewer config | configs/agents/reviewer.yaml |
| New runtime dependency | httpx (MIT) added to pyproject.toml |
