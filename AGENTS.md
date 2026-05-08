# SwarmForge — Agent Instructions

Proprietary. Confidential. NDA required.
All code, architecture, and data are exclusive IP of Michele Bisignano and Alessandro Campani.

---

## CRITICAL — Fix Before Anything Else

**`pyproject.toml` has an unresolved merge conflict** in the `[dependencies]` section
(`<<<<<<< HEAD` / `=======` / `>>>>>>>` markers). Invalid TOML — every `uv` command fails.

**`src/orchestrator/orchestrator.py`** has the same conflict at lines 4–16 (import block).

Fix both files first. Then verify:

```bash
uv run python -c "import src.agents; import src.orchestrator; print('OK')"
```

`make run` references `src.openjarvis.main:app` — that package does not exist. Do not use it.

---

## State of the Repo (May 2026)

**Phase 2.B** — Real LLM agents (`ClineAgent`) coexist with Phase 1 stubs.
Test baseline: **67/67 passing**. Do not break.

---

## Commands

| Intent | Command |
|---|---|
| Full test suite | `uv run pytest tests/ -v --tb=short` |
| Single test file | `uv run pytest tests/orchestrator/test_*.py -v --tb=short` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Import check | `uv run python -c "import src.agents; import src.orchestrator; print('OK')"` |
| Regenerate griffe API JSON | `make griffe-dump` |
| Install deps | `make install` (runs `uv sync`) |

---

## Source Layout

```
src/
├── agents/
│   ├── base.py              ← AbstractAgent (ABC)
│   ├── cline_agent.py       ← Real LLM agent via httpx + /v1/chat/completions
│   ├── config.py            ← AgentConfig (Pydantic v2, pure data)
│   └── stubs.py             ← Phase 1 stubs (Architect/Coder/ReviewerAgent)
├── orchestrator/
│   ├── orchestrator.py      ← Main coordinator (134 lines — near SRP limit)
│   ├── decomposer.py        ← RuleBasedTaskDecomposer (keyword-based split)
│   ├── registry.py          ← AgentRegistry (capability-based lookup)
│   ├── selector.py          ← CapabilityMatchSelector (first-match)
│   ├── aggregator.py        ← SequentialResultAggregator (concat OK results)
│   ├── factory.py           ← SwarmFactory (wires everything from YAML)
│   └── models.py            ← Pydantic models (Subtask, SubtaskResult, SwarmResult)
├── ai/
│   ├── core/ai_model.py     ← AbstractAIModel (root ABC)
│   ├── text/text_model.py   ← AbstractTextModel
│   ├── text/web/            ← Browser-automation models (Playwright)
│   └── image/               ← AbstractImageModel (stub)
└── __init__.py
```

---

## Architecture Facts (Verified from Code)

- Every cross-layer boundary is an ABC — `AbstractAgent`, `AbstractTaskDecomposer`,
  `AbstractAgentSelector`, `AbstractResultAggregator`. All dependencies injected via constructor.
- `ClineAgent` is the only real LLM agent — calls any OpenAI-compatible `/v1/chat/completions`
  endpoint via `httpx`. Reads API key from env var at call time. Timeout: 180s.
- Stubs in `src/agents/stubs.py` (`ArchitectAgent`, `CoderAgent`, `ReviewerAgent`) —
  used in integration tests when no real API key is available.
- `AgentConfig` is pure data (Pydantic v2) — no behavior. Role, model, endpoint,
  API key env var name, extra params. Loaded from YAML by `SwarmFactory`.
- `SwarmFactory` reads `configs/agents/{architect,coder,reviewer}.yaml`, creates
  `ClineAgent` instances, builds `SwarmOrchestrator` with default strategies.
- Default model: `gemma-4-26b-a4b-it` via Google AI Studio (free). Fallback: `gemini-2.0-flash`.
- Orchestrator execution is sequential — context from each completed subtask is appended
  to the next subtask description. Failed subtask outputs are excluded from context.

---

## Hard Rules (Non-Negotiable)

- **Language** — English in all code, comments, commits, and docs. No exceptions.
- **Licenses** — MIT / Apache 2.0 / BSD / Public Domain only.
  **GPL, AGPL, LGPL are strictly forbidden.** They contaminate proprietary IP.
  Verify license before adding any dependency. State it explicitly in the PR.
- **No `print()`** — use `logging.getLogger(__name__)` at the correct level.
- **Type hints** — mandatory on all params and return types. Python 3.10+ syntax:
  `str | None` not `Optional[str]`, `list[str]` not `List[str]`.
- **Google-style docstrings** — `@param`, `@return`, `@raise` on every public method.
  Undocumented public code is rejected.
- **No magic numbers** — named constants for every value with semantic meaning.
- **SRP hard limit** — ~150 lines of logic per class. Stop and escalate if exceeded.
- **Secrets** — API keys in `.env` only (gitignored). Never hardcode. Never commit.

---

## Three-Agent Workflow (Mandatory)

Every new module follows this sequence. Never skip steps. Never merge without review.

```
1. @contract-architect
   → Class Hierarchy Map → STOP for approval
   → Contract Document per class → STOP for approval

2. @class-coder
   → Skeleton → STOP for approval
   → Tests (if test-first enabled)
   → Method bodies one at a time, verify each
   → SRP check → Commit

3. @reviewer
   → Static analysis + runtime verification
   → Docs/reviews/[Module].review.md
   → LGTM or REJECTED with exact input/expected/actual

4. Merge to main
```

---

## Commit Format

```
type(scope): short imperative description

Why: one sentence — motivation, not implementation.
```

Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

---

## Testing Conventions

- `pytest-asyncio`, `asyncio_mode = "auto"` — decorator still applied per test.
- Mock external dependencies only — httpx, env vars. Do NOT mock internal classes you own.
- `ClineAgent` tests: patch `httpx.AsyncClient.post` and `os.getenv`.
- Orchestrator tests: mock all 4 collaborators. No real agents involved.
- Integration test (`test_swarm_integration.py`): real stubs + real strategies, no mocking, no API calls.
- Web model tests (`test_web_model.py`): require Playwright + login session. Flaky — skip in CI.
- Test naming: `test_should_[expected_behavior]_when_[condition]`

---

## .clinerules/ Coverage (Loaded via opencode.json)

8 files loaded as instructions — do not duplicate their content here:

| File | Covers |
|---|---|
| `00-vibe-architect.md` | Plan mode, intent-first, commit standard, logging, DI, ABCs, OpenAI interface |
| `01-token-economy.md` | Output compression, surgical reading, context budget |
| `02-universal-code-standards.md` | Comments (why/not what), docstrings, access modifiers, SRP, SOLID, naming, error handling |
| `03-python-fastapi-standards.md` | Type hints (3.10+), Pydantic v2, FastAPI patterns, test patterns |
| `04-contract-architect.md` | ContractArchitect role definition |
| `04-doc-and-test-pipeline.md` | griffe extraction, parametrized test coverage |
| `05-class-coder.md` | ClassCoder role definition |
| `caveman.md` | Ultra-compressed communication mode |

---

## Memory Bank

`memory-bank/` files load automatically via `opencode.json`.

| File | Purpose |
|---|---|
| `productContext.md` | Project overview, tech stack, hard constraints |
| `activeContext.md` | **Update at session start** — current task, last action, next step, blockers |
| `decisionLog.md` | Append-only architectural decisions |
| `progress.md` | Phase status and todo list |