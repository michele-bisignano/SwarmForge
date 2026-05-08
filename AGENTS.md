# SwarmForge — Agent Instructions

> Proprietary project. All code, architecture, and data are confidential IP
> of Michele Bisignano and Alessandro Campani. NDA required before access.

---

## Project Overview

SwarmForge is a closed-source, enterprise-grade multi-agent AI development
platform. A "team of virtual agents" (Architect, Coder, Reviewer) lives inside
VS Code and runs on a decentralized, privately controlled hardware network.

**Current phase:** Phase 2.B — Real LLM Agents replacing Phase 1 stubs.
**Test suite:** `uv run pytest tests/ -v` — must stay at 67/67 passing.
**Primary model:** Gemma 4 26B via Google AI Studio (free tier).

---

## Critical Rules

### Language
All code, variables, comments, docstrings, commit messages, and documentation
**must be in English**. No exceptions.

### Licenses
Only **MIT, Apache 2.0, BSD, Public Domain** allowed.
**GPL, AGPL, LGPL are strictly forbidden.** Before adding any dependency,
state its license explicitly. If unsure, stop and ask.

### Documentation
Every public class and method requires a Google-style docstring:

```python
def method(self, param: str) -> bool:
    """Short description.

    @param param: Description.
    @return: True if successful.
    @raise ValueError: When param is empty.
    """
```

Undocumented public code is rejected. No exceptions.

### No print()
Use `logging` exclusively. `print()` is forbidden in all production code.

### Type hints
Mandatory on all function parameters and return types. No untyped code accepted.

### Secrets
API keys live only in `.env` (gitignored). Never hardcode. Never commit.
Always use `os.getenv("KEY_NAME")`.

---

## Architecture Principles

### OpenAI-Compatible Interface
Every AI call goes through `/v1/chat/completions`. Never call provider SDKs
directly in business logic. `ClineAgent` in `src/agents/cline_agent.py` is
the canonical implementation.

### Dependency Injection
Never instantiate dependencies inside a class. All collaborators injected
via constructor. See `SwarmOrchestrator.__init__` as reference.

### Repository Pattern + Service Layer
Data access in repositories. Business logic in services.
Never mix layers.

### Abstract Classes as Contracts
Every cross-layer boundary is an ABC. Swapping any concrete implementation
requires zero changes to the layer above it.

### Single Responsibility Principle
Each class has one reason to change. If you cannot describe a class in one
sentence without "and", split it. Hard limit: ~150 lines of logic.

---

## Workflow — Mandatory Sequence

For every new module or feature:

```
1. Plan mode — analyze, propose plan, STOP for approval
2. @contract-architect — hierarchy map → Contract Document → approval
3. @class-coder — implement from Contract Document
4. @reviewer — validate against contract
5. Commit with conventional commits format
```

**Never skip steps. Never merge without a review.**

### Commit Format

```
type(scope): short imperative description

Why: one sentence — motivation, not implementation.
```

Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

---

## Project Structure

```
src/
├── orchestrator/      ← SwarmOrchestrator, decomposer, registry, selector, aggregator, factory
└── agents/            ← AbstractAgent, ClineAgent, AgentConfig, stubs

tests/
├── agents/            ← ClineAgent unit tests
├── orchestrator/      ← orchestration unit tests
└── integration/       ← end-to-end tests

configs/agents/        ← YAML per role (architect, coder, reviewer)
memory-bank/           ← persistent session context
Docs/contracts/        ← one Contract Document per class
Docs/architecture/     ← SF-ARCH-001 (Phase 1), SF-ARCH-002 (Phase 2)
.clinerules/           ← extended standards (loaded by opencode.json)
.opencode/agents/      ← custom OpenCode agent definitions
```

---

## Commands

| Command | What it does |
|---|---|
| `uv run pytest tests/ -v` | Run full test suite |
| `uv run pytest tests/ -v --tb=short` | Run with compact tracebacks |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `python tools/project_tree/generate_tree.py` | Regenerate repository tree |
| `make griffe-dump` | Regenerate griffe API JSON for doc snippets |

---

## Memory Bank

Update `memory-bank/activeContext.md` at the **start of each session** with:
- Current task
- Last completed action
- Next step
- Any blockers

This file is loaded automatically and prevents context loss between sessions.