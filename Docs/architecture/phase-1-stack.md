# SwarmForge — Phase 1 Stack Definition
**Document ID:** `SF-ARCH-001`
**Codename:** *Single-Node Genesis*
**Version:** 1.4 (Updated — stack corrections, Gemma 26B confirmed as primary)
**Status:** ✅ COMPLETE — All KPIs validated
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026

---

## 1. Objective

Define the complete, reproducible technology stack for Phase 1 of Project SwarmForge.
The goal of this phase was a fully functional local vibe-coding environment where an AI
agent lives inside VS Code, powered by cloud APIs (free tier), and can autonomously
write, edit, and debug code.

**Phase 1 is complete. This document is the historical record.**
Active development is now in Phase 2. See `SF-ARCH-002`.

---

## 2. Success Criteria (KPIs) — VALIDATED

| KPI | Target | Result |
|---|---|---|
| Time to First Token (TTFT) | < 1.5 seconds | ✅ Validated |
| Autonomous IDE command success rate | 100% on 5 basic commands | ✅ Validated |
| Agent-triggered OOM crashes | 0 | ✅ Validated |
| External paid API calls | 0 during standard sessions | ✅ Validated |

---

## 3. License Audit Summary

All components vetted for IP compatibility.
**Copyleft licenses (GPL, AGPL, LGPL) are strictly forbidden.**

| Component | License | Status |
|---|---|---|
| VS Code | MIT | ✅ Approved |
| Cline (v3.80.0) | Apache 2.0 | ✅ Approved |
| Cline Kanban (v0.1.64) | Apache 2.0 | ✅ Approved |
| Aider | Apache 2.0 | ✅ Approved |
| Gemma 4 (weights) | Apache 2.0 | ✅ Approved |
| Gemma 4 API (Google AI Studio) | SaaS — Google ToS | ✅ Approved |
| Gemini Flash API (fallback) | SaaS — Google ToS | ✅ Approved |
| FastAPI | MIT | ✅ Approved |
| SQLite / LibSQL | Public Domain | ✅ Approved |
| Ollama | MIT | ✅ Approved |
| uv | MIT | ✅ Approved |
| ruff | MIT | ✅ Approved |
| pytest + pytest-asyncio | MIT | ✅ Approved |
| pydantic v2 | MIT | ✅ Approved |
| httpx | MIT | ✅ Approved |
| python-dotenv | MIT | ✅ Approved |
| pyyaml | MIT | ✅ Approved |

---

## 4. Stack Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      DEVELOPER                          │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    IDE LAYER                            │
│              VS Code (MIT)                              │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
┌──────────────▼──────────┐ ┌─────────▼───────────────────┐
│  KNOWLEDGE LAYER        │ │      AGENT LAYER             │
│  .clinerules/           │ │                              │
│  00-vibe-architect.md   │ │  PRIMARY: Cline v3.80        │
│  01-token-economy.md    │ │  (Apache 2.0)                │
│  02-python-standards.md │ │  - Plan / Act modes          │
│  caveman.md             │ │  - Multi-file editing        │
│                         │ │  - Autonomous debugging      │
│  Read at every session  │ │  - MCP integration           │
│  by Cline automatically │ │  - Browser headless testing  │
│                         │ │  - Checkpoints / rollback    │
│                         │ │  - Subagents (parallel)      │
│                         │ │                              │
│                         │ │  SECONDARY: Aider (terminal) │
│                         │ │  (Apache 2.0)                │
│                         │ │  - Git-native, auto-commit   │
│                         │ │  - Mass refactoring          │
└──────────────┬──────────┘ └─────────┬───────────────────┘
               └──────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API ROUTING LAYER                     │
│                                                         │
│  PRIMARY   →  Gemma 4 26B — Google AI Studio (free)     │
│              Model: gemma-4-26b-a4b-it                  │
│              Endpoint: generativelanguage.googleapis.com │
│              Limit: ~15 RPM                             │
│                                                         │
│  FALLBACK  →  Gemini Flash — Google AI Studio (free)    │
│              Model: gemini-2.0-flash                    │
│              Limit: 1,000 req/day, 60 RPM               │
│                                                         │
│  LOCAL     →  Ollama + gemma4:e4b (offline only)        │
│              Limit: 8GB VRAM constraint                 │
│              Note: NOT suitable for Cline agent mode    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Component Details

### 5.1 IDE — VS Code
- **Version:** Latest stable
- **Why not Cursor:** No BYO API key on free plan, insufficient rate limits
- **Extensions installed:** Cline, GitLens, Ruff

### 5.2 Primary Agent — Cline (v3.80.0)

**Validated settings for SwarmForge:**

```
AGENT
  Subagents              ON
  Native Tool Call       ON
  Parallel Tool Calling  ON
  Strict Plan Mode       ON   ← mandatory
  Auto Compact           ON
  Focus Chain            ON
  Reminder Interval      4

EDITOR
  Feature Tips           OFF
  Background Edit        OFF
  Checkpoints            ON   ← mandatory

EXPERIMENTAL
  YOLO Mode              OFF  ← STRICTLY FORBIDDEN
  Double-Check           ON
  Lazy Mode              OFF

TERMINAL
  Profile                PowerShell 7 / Git Bash
  Shell timeout          15-20 seconds
  Aggressive reuse       ON
  Execution Mode         VS Code Terminal
  Output limit           800 lines
```

**API configuration (Cline for development assistance):**
```
Provider:  Google Gemini
API Key:   [GOOGLE_AI_STUDIO_API_KEY from .env]
Model:     gemini-2.0-flash  (for Cline dev assistance)
```

**Note:** Cline uses Gemini Flash for development assistance (fast, free).
SwarmOrchestrator agents use Gemma 4 26B (better reasoning, also free).

### 5.3 Cline Kanban (v0.1.64)
Launched via `cline` CLI from repo root. Runs at `http://127.0.0.1:3484`.
Used for multi-agent task orchestration in Phase 2.

```bash
cd C:/Algoritmi/SwarmForge
cline
```

### 5.4 Knowledge Layer — .clinerules/
Cline reads all `.md` files in `.clinerules/` at every session.
These encode SwarmForge standards, coding conventions, and architectural rules.
Do not modify without team consensus.

### 5.5 AI Backend

**Primary (SwarmOrchestrator agents):** Gemma 4 26B via Google AI Studio
- Model: `gemma-4-26b-a4b-it`
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/v1`
- Cost: Free
- Thinking mode: active (adds latency — timeout must be ≥ 60s)

**Development assistant (Cline):** Gemini Flash
- Model: `gemini-2.0-flash`
- Cost: Free, 1000 req/day

**Local (offline fallback):** gemma4:e4b via Ollama
- Fits in 8GB VRAM
- NOT suitable for Cline agent mode (4.5B params too small)

### 5.6 Package Manager — uv
All Python dependencies managed via `uv`. Never use raw `pip`.

```bash
uv add <package>          # add dependency
uv sync                   # install all dependencies
uv run pytest             # run in venv
uv run python script.py   # run script in venv
```

### 5.7 OpenJarvis (installed, Phase 2 tool)
- **Location:** `C:/Algoritmi/tools/openjarvis/` (outside SwarmForge repo)
- **Config:** `C:/Users/Michele/.openjarvis/config.toml`
- **Security profile:** `personal`, mode: `block`
- **Status:** Installed and configured. Integration with Cline deferred
  (stream_options compatibility issue — HTTP 422). Active for hardware monitoring.

---

## 6. API Key Management Protocol

```
1. Keys stored ONLY in local .env files
2. .env listed in .gitignore before first commit
3. Keys NEVER hardcoded in source files
4. Keys NEVER committed, even in private repos
5. Each founder maintains independent API keys
6. .env.example with placeholders IS committed
```

`.env.example` (current structure):
```env
# Provider API keys (one per provider)
GOOGLE_AI_STUDIO_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Provider base URLs
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai

# Agent model assignments (SwarmOrchestrator)
ARCHITECT_MODEL=gemma-4-26b-a4b-it
ARCHITECT_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
ARCHITECT_API_KEY=GOOGLE_AI_STUDIO_API_KEY

CODER_MODEL=gemma-4-26b-a4b-it
CODER_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
CODER_API_KEY=GOOGLE_AI_STUDIO_API_KEY

REVIEWER_MODEL=gemma-4-26b-a4b-it
REVIEWER_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
REVIEWER_API_KEY=GOOGLE_AI_STUDIO_API_KEY
```

---

## 7. Setup Checklist — COMPLETED

- [x] VS Code installed (latest stable)
- [x] Cline extension installed and configured
- [x] Google AI Studio account + API key generated
- [x] Gemma 4 26B configured as primary SwarmOrchestrator model
- [x] Gemini Flash configured as Cline development assistant
- [x] .clinerules/ created and validated
- [x] KPI #1 validated: TTFT < 1.5s
- [x] KPI #2 validated: 5 autonomous IDE commands
- [x] Aider installed (`pip install aider-chat`)
- [x] Ollama installed + gemma4:e4b available
- [x] Cline Kanban installed (`npm i -g cline`)
- [x] OpenJarvis installed and configured
- [x] pyproject.toml configured with pytest settings
- [x] uv environment set up with all dependencies

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Phase 1 completed:* April 2026
*Supersedes:* SF-ARCH-001 v1.3
*Next document:* SF-ARCH-002 (Phase 2)