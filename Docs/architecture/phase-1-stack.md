# SwarmForge — Phase 1 Stack Definition
**Document ID:** `SF-ARCH-001`
**Codename:** *Single-Node Genesis*
**Version:** 1.3 (Updated — Phase 1 KPIs validated, Phase 2.A complete)
**Status:** ✅ COMPLETE — All KPIs validated
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026

---

## 1. Objective

Define the complete, reproducible technology stack for Phase 1 of Project SwarmForge.
The goal of this phase was a fully functional local vibe-coding environment where an AI
agent lives inside VS Code, powered by the Gemma 4 / Gemini Flash cloud API (free tier),
and can autonomously write, edit, and debug code.

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
| Cline | Apache 2.0 | ✅ Approved |
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
│  AUTOCOMPLETE LAYER     │ │      AGENT LAYER             │
│  (optional)             │ │                              │
│                         │ │  PRIMARY: Cline              │
│  Continue.dev removed   │ │  (Apache 2.0)                │
│  — Cline covers all     │ │  - Plan / Act modes          │
│  agentic use cases      │ │  - Multi-file editing        │
│                         │ │  - Autonomous debugging      │
│                         │ │  - MCP integration           │
│                         │ │  - Browser headless testing  │
│                         │ │  - Checkpoints / rollback    │
│                         │ │  - Subagents (parallel)      │
│                         │ │                              │
│                         │ │  SECONDARY: Aider (terminal) │
│                         │ │  (Apache 2.0)                │
│                         │ │  - Git-native, auto-commit   │
│                         │ │  - Mass refactoring          │
└─────────────────────────┘ └─────────┬───────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────┐
│               KNOWLEDGE LAYER                           │
│         .clinerules/  (Cline native rules system)       │
│   00-vibe-architect.md  — approach and methodology      │
│   01-token-economy.md   — token efficiency rules        │
│   02-python-fastapi-standards.md — coding standards     │
│   caveman.md            — output compression            │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API ROUTING LAYER                     │
│                                                         │
│  PRIMARY   →  Gemini Flash — Google AI Studio (free)    │
│              Model: gemini-2.0-flash                    │
│              Limit: 1,000 req/day, 60 RPM               │
│                                                         │
│  FALLBACK  →  Gemma 4 API — Google AI Studio (free)     │
│              Model: gemma-4-26b-a4b-it                  │
│              Limit: ~15 RPM                             │
│                                                         │
│  LOCAL     →  Ollama + gemma4:e4b (offline only)        │
│              Limit: 8GB VRAM — e4b model only           │
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

**API configuration:**
```
Provider:  Google Gemini
API Key:   [GOOGLE_AI_STUDIO_API_KEY from .env]
Model:     gemini-2.0-flash
```

### 5.3 Cline Kanban (v0.1.64)
Launched via `cline` CLI from repo root. Runs at `http://127.0.0.1:3484`.
Used for multi-agent task orchestration in Phase 2.

### 5.4 Knowledge Layer — .clinerules/
Cline reads all `.md` files in `.clinerules/` at every session.
These encode SwarmForge standards, coding conventions, and architectural rules.
Do not modify without team consensus.

### 5.5 AI Backend

**Primary:** Gemini Flash via Google AI Studio (free, 1000 req/day)
**Fallback:** Gemma 4 (26B MoE) — good for complex reasoning, 15 RPM limit
**Local:** gemma4:e4b via Ollama — offline only, fits 8GB VRAM

**Note:** gemma4:e4b is NOT suitable for Cline agent mode — too small (4.5B params)
to follow complex multi-step instructions reliably. Use for offline inference only.

### 5.6 Package Manager — uv
All Python dependencies managed via `uv`. Never use raw `pip` in this project.

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
  (stream_options compatibility issue). Active for hardware monitoring.

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

`.env.example`:
```env
GOOGLE_AI_STUDIO_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here      # optional paid fallback
OPENAI_API_KEY=your_key_here         # optional paid fallback
```

---

## 7. Setup Checklist — COMPLETED

- [x] VS Code installed (latest stable)
- [x] Cline extension installed and configured
- [x] Google AI Studio account + API key generated
- [x] Gemini Flash configured as primary model
- [x] .clinerules/ created and validated
- [x] KPI #1 validated: TTFT < 1.5s
- [x] KPI #2 validated: 5 autonomous IDE commands
- [x] Aider installed (`pip install aider-chat`)
- [x] Ollama installed + gemma4:e4b available
- [x] Cline Kanban installed (`npm i -g cline`)
- [x] OpenJarvis installed and configured

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Phase 1 completed:* April 2026
*Supersedes:* SF-ARCH-001 v1.2
*Next document:* SF-ARCH-002 (Phase 2)