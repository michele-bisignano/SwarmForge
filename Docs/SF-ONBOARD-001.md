# SwarmForge — Developer Onboarding Guide
**Document ID:** `SF-ONBOARD-001`
**Version:** 1.0
**Status:** Active
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026
**Audience:** New technical collaborators (NDA required before access)

---

## 1. What Is SwarmForge?

SwarmForge is a proprietary, closed-source, enterprise-grade ecosystem for
AI-assisted development. The goal: a "Private AWS for AI" where a team of
virtual agents (Architect, Coder, Reviewer) lives natively inside VS Code,
powered by a decentralized, privately controlled hardware network.

**Current phase:** Phase 2.A — Multi-Agent Orchestration (cloud-only agents).
The single-agent Phase 1 PoC is complete and validated.

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
| Rust + rustup | stable | rustup.rs |

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
# Expected: 27 passed
```

---

## 4. VS Code Setup

### 4.1 Required Extensions

Install in this order:

1. **Cline** (Apache 2.0) — primary AI agent
2. **GitLens** — Git history and blame
3. **Ruff** — linting and formatting

### 4.2 Cline Configuration

```
Provider:   Google Gemini
API Key:    [your GOOGLE_AI_STUDIO_API_KEY]
Model:      gemini-2.0-flash  (free tier, 1000 req/day)
```

**Cline settings (mandatory):**

```
Strict Plan Mode:        ON   — no file edits without approved plan
Checkpoints:             ON   — rollback at every step
YOLO Mode:               OFF  — strictly forbidden
Double-Check Completion: ON
Native Tool Call:        ON
Auto Compact:            ON
```

### 4.3 Cline Rules

The `.clinerules/` folder at the repo root contains the agent's permanent
briefing. Cline reads these at every session — do not modify them without
team approval.

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
│   │   └── aggregator.py       ← AbstractResultAggregator + SequentialResultAggregator
│   └── agents/
│       ├── base.py             ← AbstractAgent (ABC)
│       └── stubs.py            ← ArchitectAgent, CoderAgent, ReviewerAgent (Phase 1 stubs)
├── tests/
│   ├── orchestrator/           ← Unit tests (27 passing)
│   └── integration/            ← End-to-end tests
├── Docs/
│   ├── architecture/           ← SF-ARCH-001 (Phase 1), SF-ARCH-002 (Phase 2)
│   ├── contracts/              ← Contract documents per class
│   ├── plans/                  ← Architect plans
│   └── reviews/                ← Reviewer reports
├── .clinerules/                ← Cline agent rules (do not modify without approval)
├── pyproject.toml              ← Project config, pytest settings
└── .env.example                ← Environment variables template
```

---

## 6. Architecture Overview

### 6.1 Current State (Phase 2.A)

```
Developer
    │
VS Code + Cline (Gemini Flash)
    │
    ├── Plan Mode: reads repo, proposes plan, STOPS for approval
    └── Act Mode: executes approved plan, one step at a time

Cline Kanban (browser, localhost:3484)
    │
    ├── contract-architect card → produces Contract Document
    ├── class-coder card        → implements from Contract
    └── code-reviewer card      → validates implementation
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
AbstractAgent.run(subtask) → SubtaskResult
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
```

---

## 7. Development Workflow

### 7.1 The Three-Agent Cycle

Every new module follows this mandatory sequence:

```
1. contract-architect  →  Docs/contracts/[Module].contract.md
         STOP — wait approval
2. class-coder         →  src/[path]/[module].py + tests/
         STOP — wait approval
3. code-reviewer       →  Docs/reviews/[Module].review.md
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
uv run pytest tests/orchestrator/ -v

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

## 8. What Has Been Built (Phase 2.A Complete)

| Component | File | Status | Tests |
|---|---|---|---|
| Value Objects | `src/orchestrator/models.py` | ✅ Complete | — |
| SwarmOrchestrator | `src/orchestrator/orchestrator.py` | ✅ Complete | 18/18 |
| AbstractAgent + Stubs | `src/agents/base.py`, `stubs.py` | ✅ Complete | — |
| TaskDecomposer | `src/orchestrator/decomposer.py` | ✅ Complete | — |
| AgentRegistry | `src/orchestrator/registry.py` | ✅ Complete | 3/3 |
| AgentSelector | `src/orchestrator/selector.py` | ✅ Complete | 2/2 |
| ResultAggregator | `src/orchestrator/aggregator.py` | ✅ Complete | — |
| Integration Test | `tests/integration/` | ✅ PASSED | 1/1 |
| **Total** | | | **27/27** |

---

## 9. What Comes Next (Phase 2.B and 2.C)

### Phase 2.B — Real Agents (replace stubs)
Replace `ArchitectAgent`, `CoderAgent`, `ReviewerAgent` stubs with concrete
implementations that call Gemini Flash via the Google AI Studio API. Each agent
receives a subtask and returns a real LLM-generated `SubtaskResult`.

### Phase 2.C — Local Inference
Introduce `OllamaAgent` as a local inference alternative for the Reviewer agent,
running `gemma4:e4b` on the local GPU (8GB VRAM). Seamless failover to cloud
when rate limit is hit.

### Phase 3 — Second Node (Optional)
Gateway / Load Balancer introduction. Two physical nodes, mesh VPN, IP masking.
Hardware: RTX 4060 (8GB VRAM), 28 cores, 16GB RAM.

### Phase 4 — Fine-Tuning
Collect interaction logs via OpenJarvis tracing. Normalize to ShareGPT format.
Fine-tune Gemma 4 with QLoRA via LLaMA-Factory on local hardware.

---

## 10. Key Tools and Their Roles

| Tool | License | Role |
|---|---|---|
| VS Code | MIT | IDE |
| Cline | Apache 2.0 | AI agent inside VS Code |
| Cline Kanban | Apache 2.0 | Multi-agent task orchestration (browser) |
| Gemini Flash API | Google ToS | Primary AI model (free, cloud) |
| Ollama | MIT | Local inference runtime |
| gemma4:e4b | Apache 2.0 | Local model (Phase 2.C+) |
| OpenJarvis | Apache 2.0 | Hardware metrics + trace logging |
| FastAPI | MIT | Backend framework |
| SQLite/LibSQL | Public Domain | Database |
| uv | MIT | Python package manager |
| ruff | MIT | Linter and formatter |
| pytest + pytest-asyncio | MIT | Test framework |

---

## 11. Contacts and Resources

- **Project Brief:** `Docs/Project_Brief.md`
- **Phase 1 Architecture:** `Docs/architecture/phase-1-stack.md`
- **Phase 2 Architecture:** `Docs/architecture/phase-2-stack.md`
- **All contracts:** `Docs/contracts/`
- **Founders:** Michele Bisignano, Alessandro Campani

*This document is confidential. Do not share outside the team.*