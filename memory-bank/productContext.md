# Product Context

**Project:** SwarmForge
**Status:** Active development — Phase 2.B
**Classification:** Proprietary / Confidential

---

## What It Is

Closed-source, enterprise-grade multi-agent AI development platform.
Goal: "Private AWS for AI" — virtual agents (Architect, Coder, Reviewer)
living natively in VS Code, powered by a decentralized, privately controlled
hardware network.

## Current Phase

**Phase 2.B — Real LLM Agents.** ClineAgent replaces Phase 1 stubs.
All 67 unit and integration tests passing.

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| IDE agent | OpenCode (MIT) | Replaced Cline (May 2026) |
| Orchestration | SwarmOrchestrator (Python) | Thin coordinator, all logic in strategies |
| Real LLM agent | ClineAgent + httpx | Calls OpenAI-compatible endpoint |
| Agent config | AgentConfig (Pydantic v2) | YAML-driven, provider-agnostic |
| Factory | SwarmFactory | Wires agents from YAML |
| Primary model | Gemma 4 26B (Google AI Studio) | Free tier, `gemma-4-26b-a4b-it` |
| Fallback model | Gemini Flash | Dev assistance via OpenCode |
| Package manager | uv | Never raw pip |
| Linter | ruff | Replaces flake8 + black + isort |
| Tests | pytest + pytest-asyncio | `asyncio_mode = "auto"` |

## Hard Constraints

- **License:** MIT/Apache 2.0/BSD/Public Domain only. GPL/AGPL/LGPL **forbidden**.
- **Language:** English everywhere. No exceptions.
- **Docstrings:** Google-style on all public methods. Undocumented = rejected.
- **Type hints:** Mandatory on all params and returns.
- **No print():** Use `logging` exclusively.
- **No hardcoded secrets:** `.env` only, gitignored.
- **SRP hard limit:** ~150 lines of logic per class.

## Architecture Pattern

```
SwarmOrchestrator
  ├── AbstractTaskDecomposer → RuleBasedTaskDecomposer
  ├── AgentRegistry
  ├── AbstractAgentSelector → CapabilityMatchSelector
  └── AbstractResultAggregator → SequentialResultAggregator

AbstractAgent (ABC)
  └── ClineAgent (real) — calls /v1/chat/completions via httpx
```

Every cross-layer boundary is an ABC. All dependencies injected via constructor.
SwarmFactory builds the wired orchestrator from YAML configs.

## Repository Root

`C:/Algoritmi/SwarmForge/`

## Key Commands

```bash
uv run pytest tests/ -v          # full suite (must stay 67/67)
uv run ruff check src/ tests/    # lint
uv run ruff format src/ tests/   # format
```