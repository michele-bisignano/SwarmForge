# SwarmForge — Developer Onboarding Guide
**Document ID:** `SF-ONBOARD-001`
**Version:** 2.0
**Status:** Active
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** May 2026
**Audience:** New technical collaborators (NDA required before access)

---

## 1. What Is SwarmForge?

SwarmForge is a proprietary, closed-source, enterprise-grade ecosystem for
AI-assisted development. The goal: a "Private AWS for AI" where a team of
virtual agents (Architect, Coder, Reviewer) lives natively inside VS Code,
powered by a decentralized, privately controlled hardware network.

**Current phase:** Phase 2.B — Real LLM Agents (ClineAgent replacing stubs).
Phase 2.A multi-agent orchestration is complete and validated (67/67 tests).

**IP notice:** All source code, architecture, prompts, and data are the
exclusive intellectual property of the founders. You are operating under NDA.

---

## 2. Mandatory Prerequisites

Before writing a single line of code, internalize these rules. They are not
guidelines — violations will be rejected.

### 2.1 Language
All code, variables, comments, docstrings, commit messages, and documentation
must be in **English**. No exceptions.

### 2.2 Licenses
Only permissive licenses are allowed: **MIT, Apache 2.0, BSD, Public Domain**.
GPL, AGPL, LGPL are strictly forbidden — they would contaminate our proprietary
codebase and destroy its commercial value. Before adding any dependency, verify
its license and state it explicitly in your PR.

### 2.3 Documentation
Every function, class, and module must have a Google-style docstring. Undocumented
code is rejected automatically by the CI rules.

```python
def route_request(request: ChatRequest) -> Response:
    """Select the optimal node and forward the request.

    @param request: The incoming OpenAI-compatible chat request.
    @return: The response from the selected node.
    @raise NoAvailableNodeError: If all nodes exceed the VRAM threshold.
    """
```

### 2.4 Secrets
API keys and credentials live exclusively in `.env` files (gitignored).
Never hardcode. Never commit. Always use `os.getenv("KEY_NAME")`.

### 2.5 OpenAI-Compatible Interface Contract
Every AI model endpoint in this project must expose or consume the standard
OpenAI-compatible interface:

```
POST /v1/chat/completions
{ "model": "...", "messages": [...], "stream": true/false }
```

This is the most critical architectural rule. It guarantees any component
can be swapped without code changes.

---

## 3. Local Environment Setup

### 3.1 Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | python.org |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 18+ | nodejs.org |
| Git | latest | git-scm.com |
| VS Code | latest | code.visualstudio.com |
| OpenCode | latest | `npm install -g opencode-ai@latest` |

### 3.2 Clone and Install

```bash
git clone https://github.com/michele-bisignano/SwarmForge.git
cd SwarmForge
uv sync
uv add pydantic pytest pytest-asyncio
```

### 3.3 Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in your own API keys
```

`.env.example` documents all required keys. Get your own Google AI Studio
key at: https://aistudio.google.com

### 3.4 Verify Setup

```bash
uv run pytest -v
# Expected: 67 passed
```

---

## 4. OpenCode Setup

OpenCode is the primary AI coding agent. It runs as a terminal UI (TUI) and
optionally integrates with VS Code. It is provider-agnostic and reads the
project's `.clinerules/` files automatically.

### 4.1 Required Extensions

Install in this order:

1. **OpenCode** (MIT) — primary AI agent (TUI + VS Code integration)
2. **GitLens** — Git history and blame
3. **Ruff** — linting and formatting

### 4.2 OpenCode Configuration

The project config lives in `opencode.json` at the repo root (committed to Git).
No manual configuration needed — it loads automatically when you run `opencode`
from the SwarmForge directory.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "google/gemini-2.0-flash",
  "share": "disabled",
  "permission": {
    "bash": "ask",
    "write": "ask",
    "edit": "ask"
  }
}
```

**Key settings:**

| Setting | Value | Why |
|---|---|---|
| `share` | `"disabled"` | Proprietary project — no external sharing |
| `permission.*` | `"ask"` | Agent asks before modifying files or running commands |
| `instructions` | `.clinerules/**` | All project standards loaded automatically |

**Add your API key to `.env`:**

```env
GOOGLE_GENERATIVE_AI_API_KEY=your_google_ai_studio_key_here
```

OpenCode auto-detects this variable for the Google provider.

### 4.3 Launch OpenCode

```bash
cd C:/Algoritmi/SwarmForge
opencode
```

**Essential keybindings:**

| Key | Action |
|---|---|
| `Tab` | Toggle Plan mode ↔ Build mode |
| `/init` | Regenerate AGENTS.md from codebase |
| `/undo` | Revert last agent change |
| `/redo` | Re-apply reverted change |
| `@filename` | Reference a specific file in prompt |
| `@agent-name` | Invoke a named agent (e.g. `@contract-architect`) |
| `Ctrl+C` | Exit |

**Modes:**

- **Plan mode** — read-only analysis. Agent cannot modify files. Use for
  exploration and planning (equivalent to Cline's Strict Plan Mode).
- **Build mode** — full access with permission gates. Agent asks before
  each file write or bash command.

### 4.4 Project Agents

Custom agents live in `.opencode/agents/`. Invoke them with `@agent-name`:

| Agent | Invoke with | Role |
|---|---|---|
| `contract-architect` | `@contract-architect` | Designs class hierarchy, produces Contract Documents |
| `class-coder` | `@class-coder` | Implements one class from a Contract Document |
| `reviewer` | `@reviewer` | Validates implementation against contract |

### 4.5 Project Memory Bank

`memory-bank/` files load automatically at every session and give the agent
persistent context about the project state:

| File | Content |
|---|---|
| `memory-bank/productContext.md` | Project overview, tech stack, constraints |
| `memory-bank/activeContext.md` | Current sprint focus (update each session) |
| `memory-bank/decisionLog.md` | Append-only architectural decisions |
| `memory-bank/progress.md` | Phase status and todo list |

Update `memory-bank/activeContext.md` at the start of each session.

---

## 5. Repository Structure

```
SwarmForge/
├── src/
│   ├── orchestrator/           ← Core orchestration layer
│   │   ├── orchestrator.py     ← SwarmOrchestrator (thin coordinator)
│   │   ├── models.py           ← Pydantic v2 value objects
│   │   ├── decomposer.py       ← AbstractTaskDecomposer + RuleBasedTaskDecomposer
│   │   ├── registry.py         ← AgentRegistry
│   │   ├── selector.py         ← AbstractAgentSelector + CapabilityMatchSelector
│   │   ├── aggregator.py       ← AbstractResultAggregator + SequentialResultAggregator
│   │   └── factory.py          ← SwarmFactory (wires real agents from YAML)
│   └── agents/
│       ├── base.py             ← AbstractAgent (ABC)
│       ├── config.py           ← AgentConfig (Pydantic v2 value object)
│       ├── cline_agent.py      ← ClineAgent (real LLM via httpx)
│       └── stubs.py            ← Phase 1 stubs (kept for testing)
├── tests/
│   ├── agents/                 ← ClineAgent unit tests (21/21)
│   ├── orchestrator/           ← Orchestration unit tests (45/45)
│   └── integration/            ← End-to-end tests (1/1)
├── configs/agents/             ← YAML configs per agent role
│   ├── architect.yaml
│   ├── coder.yaml
│   └── reviewer.yaml
├── memory-bank/                ← Persistent agent context (loaded every session)
│   ├── productContext.md
│   ├── activeContext.md
│   ├── decisionLog.md
│   └── progress.md
├── Docs/
│   ├── architecture/           ← SF-ARCH-001 (Phase 1), SF-ARCH-002 (Phase 2)
│   ├── contracts/              ← Contract documents per class
│   ├── plans/                  ← Architect plans
│   └── reviews/                ← Reviewer reports
├── .clinerules/                ← Agent rules (loaded by OpenCode via instructions)
├── .opencode/agents/           ← Custom OpenCode agent definitions
├── opencode.json               ← OpenCode project config (committed)
├── AGENTS.md                   ← Project rules for OpenCode (committed)
├── pyproject.toml              ← Project config, pytest settings
└── .env.example                ← Environment variables template
```

---

## 6. Architecture Overview

### 6.1 Current State (Phase 2.B)

```
Developer
    │
VS Code + OpenCode (Google Gemini Flash)
    │
    ├── Plan mode:  reads repo, proposes plan, STOPS for approval
    └── Build mode: executes approved plan, one step at a time

Custom agents (.opencode/agents/)
    │
    ├── @contract-architect  → produces Contract Document
    ├── @class-coder         → implements from Contract
    └── @reviewer            → validates implementation
```

### 6.2 Core Data Flow

```
task_description: str
        │
        ▼
RuleBasedTaskDecomposer.decompose()
        │
        ▼
list[Subtask]  (kind: "architect" | "coder" | "reviewer")
        │
        ▼  (for each subtask)
CapabilityMatchSelector.select(subtask, registry)
        │
        ▼
ClineAgent.run(subtask) → SubtaskResult
        │
        ▼  (after all subtasks)
SequentialResultAggregator.aggregate(task_id, results)
        │
        ▼
SwarmResult  (final_content + per-subtask trace)
```

### 6.3 Class Hierarchy

```
AbstractAgent (ABC)                    ← src/agents/base.py
  ├── ClineAgent (real, Phase 2.B)     ← calls OpenAI-compatible endpoint
  ├── ArchitectAgent (stub, Phase 1)
  ├── CoderAgent (stub, Phase 1)
  └── ReviewerAgent (stub, Phase 1)

AbstractTaskDecomposer (ABC)           ← src/orchestrator/decomposer.py
  └── RuleBasedTaskDecomposer

AbstractAgentSelector (ABC)            ← src/orchestrator/selector.py
  └── CapabilityMatchSelector

AbstractResultAggregator (ABC)         ← src/orchestrator/aggregator.py
  └── SequentialResultAggregator

AgentRegistry                          ← src/orchestrator/registry.py
SwarmOrchestrator                      ← src/orchestrator/orchestrator.py
SwarmFactory                           ← src/orchestrator/factory.py
```

---

## 7. Development Workflow

### 7.1 The Three-Agent Cycle

Every new module follows this mandatory sequence:

```
1. @contract-architect  →  Docs/contracts/[Module].contract.md
         STOP — wait approval
2. @class-coder         →  src/[path]/[module].py + tests/
         STOP — wait approval
3. @reviewer            →  Docs/reviews/[Module].review.md
         STOP — wait approval
4. merge to main
```

Never skip steps. Never merge without a passing review.

### 7.2 Commit Convention

```
feat(scope): add new capability
fix(scope): correct a bug
docs(scope): update documentation
test(scope): add or fix tests
chore(scope): maintenance, dependencies, config
refactor(scope): restructure without behavior change
```

### 7.3 Running Tests

```bash
# All tests
uv run pytest -v

# Unit tests only
uv run pytest tests/orchestrator/ tests/agents/ -v

# Integration test
uv run pytest tests/integration/ -v

# Single file
uv run pytest tests/orchestrator/test_orchestrator.py -v
```

### 7.4 Code Quality

```bash
# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

---

## 8. What Has Been Built

| Component | File | Status | Tests |
|---|---|---|---|
| Value Objects | `src/orchestrator/models.py` | ✅ Complete | — |
| SwarmOrchestrator | `src/orchestrator/orchestrator.py` | ✅ Complete | 22/22 |
| AbstractAgent + Stubs | `src/agents/base.py`, `stubs.py` | ✅ Complete | — |
| AgentConfig | `src/agents/config.py` | ✅ Complete | — |
| ClineAgent | `src/agents/cline_agent.py` | ✅ Complete | 21/21 |
| SwarmFactory | `src/orchestrator/factory.py` | ✅ Complete | 15/15 |
| TaskDecomposer | `src/orchestrator/decomposer.py` | ✅ Complete | — |
| AgentRegistry | `src/orchestrator/registry.py` | ✅ Complete | 3/3 |
| AgentSelector | `src/orchestrator/selector.py` | ✅ Complete | 2/2 |
| ResultAggregator | `src/orchestrator/aggregator.py` | ✅ Complete | — |
| Integration Test | `tests/integration/` | ✅ PASSED | 1/1 |
| OpenCode Migration | `opencode.json`, `AGENTS.md` | ✅ Complete | — |
| Memory Bank | `memory-bank/` | ✅ Complete | — |
| **Total** | | | **67/67** |

---

## 9. What Comes Next

### Phase 2.B Remaining Tasks
- Formal integration test with real LLM agents
- Reviewer cycle: ClineAgent + SwarmFactory
- License & Credits agent (pip-licenses + auto-generate CREDITS.md)

### Phase 2.C — Local Inference (Deferred)
Introduce `OllamaAgent` as local backend for the Reviewer agent,
running `gemma4:e4b` on the local GPU (8GB VRAM). Zero code changes —
only a new `configs/agents/reviewer_local.yaml`.

### Phase 3 — Second Node (Optional)
Gateway / Load Balancer introduction. Two physical nodes, mesh VPN, IP masking.

### Phase 4 — Fine-Tuning
Collect interaction logs. Normalize to ShareGPT format.
Fine-tune Gemma 4 with QLoRA via LLaMA-Factory on local hardware.

---

## 10. Key Tools and Their Roles

| Tool | License | Role |
|---|---|---|
| VS Code | MIT | IDE |
| OpenCode | MIT | AI agent — TUI + VS Code integration |
| Gemini Flash API | Google ToS | OpenCode model (dev assistance) |
| Gemma 4 26B API | Google ToS | SwarmOrchestrator agents (primary) |
| Ollama | MIT | Local inference runtime (Phase 2.C+) |
| gemma4:e4b | Apache 2.0 | Local model (Phase 2.C+) |
| FastAPI | MIT | Backend framework |
| SQLite/LibSQL | Public Domain | Database |
| uv | MIT | Python package manager |
| ruff | MIT | Linter and formatter |
| pytest + pytest-asyncio | MIT | Test framework |
| httpx | MIT | Async HTTP client for ClineAgent |
| pydantic v2 | MIT | Data validation |

---

## 11. Contacts and Resources

- **Project Brief:** `Docs/Project_Brief.md`
- **Phase 1 Architecture:** `Docs/architecture/phase-1-stack.md`
- **Phase 2 Architecture:** `Docs/architecture/phase-2-stack.md`
- **OpenCode Migration:** `Docs/SF-TOOLING-MIGRATION.md` (SF-TOOLING-001)
- **All contracts:** `Docs/contracts/`
- **Founders:** Michele Bisignano, Alessandro Campani

*This document is confidential. Do not share outside the team.*