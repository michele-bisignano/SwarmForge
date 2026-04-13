# SwarmForge — Phase 1 Stack Definition
**Document ID:** `SF-ARCH-001`

**Codename:** *Single-Node Genesis*

**Version:** 1.0

**Status:** Approved — Architecture Draft

**Authors:** Michele Bisignano, Alessandro Campani

**Date:** April 2026

---

## 1. Objective

Define the complete, reproducible technology stack for Phase 1 of Project SwarmForge.
The goal of this phase is a fully functional local vibe-coding environment where an AI agent
lives inside VS Code, is powered by the Gemma 4 cloud API (free tier), and can autonomously
write, edit, and debug code — validating the IDE-to-agent integration loop before any
distributed infrastructure is introduced.

**Phase 1 is deliberately single-node. No networking, no load balancing, no multi-agent.**
Complexity is the enemy of a clean Proof of Concept.

---

## 2. Success Criteria (KPIs)

| KPI | Target |
|---|---|
| Time to First Token (TTFT) | < 1.5 seconds on local requests |
| Autonomous IDE command success rate | 100% on 5 basic commands |
| Agent-triggered OOM crashes | 0 |
| External paid API calls | 0 during standard sessions |

---

## 3. License Audit Summary

All components in this stack have been vetted for IP compatibility.
**Copyleft licenses (GPL, AGPL, LGPL) are strictly forbidden.**

| Component | License | Status |
|---|---|---|
| VS Code | MIT | ✅ Approved |
| Continue.dev | Apache 2.0 | ✅ Approved |
| Cline | Apache 2.0 | ✅ Approved |
| Gemma 4 (weights) | Apache 2.0 | ✅ Approved |
| Gemma 4 API (Google AI Studio) | SaaS — Google ToS | ✅ Approved (dev use) |
| Gemini Flash API (fallback) | SaaS — Google ToS | ✅ Approved (dev use) |
| FastAPI | MIT | ✅ Approved |
| Hono | MIT | ✅ Approved |
| Vite | MIT | ✅ Approved |
| SQLite / LibSQL | Public Domain | ✅ Approved |
| Ollama | MIT | ✅ Approved (optional, local fallback) |

---

## 4. Stack Architecture

### 4.1 Layer Overview

```
┌─────────────────────────────────────────────────────────┐
│                      DEVELOPER                          │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    IDE LAYER                            │
│              VS Code (MIT)                              │
│   - Full editor, Git, terminal, extensions              │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
┌──────────────▼──────────┐ ┌─────────▼───────────────────┐
│    AUTOCOMPLETE LAYER   │ │      AGENT LAYER             │
│    Continue.dev         │ │      Cline                   │
│    (Apache 2.0)         │ │      (Apache 2.0)            │
│  - Inline suggestions   │ │  - Multi-file editing        │
│  - Chat sidebar         │ │  - Autonomous debugging      │
│  - Context-aware        │ │  - Tool use / function call  │
└──────────────┬──────────┘ └─────────┬───────────────────┘
               │                      │
               └──────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API ROUTING LAYER                     │
│         (managed via extension config files)            │
│                                                         │
│  PRIMARY   →  Gemma 4 API — Google AI Studio (free)     │
│              Model: gemma-4-26b-a4b-it                  │
│              Limit: ~15 RPM                             │
│                                                         │
│  FALLBACK  →  Gemini Flash API — Google AI Studio (free)│
│              Limit: 1,000 req/day, 60 RPM               │
│                                                         │
│  NUCLEAR   →  Paid API (Claude / GPT-4o)                │
│              Triggered manually — last resort only      │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Optional Local Inference Layer

For offline scenarios or when API rate limits are saturated:

```
Ollama (MIT)
  └── Model: gemma4:e4b   (fits in 8GB VRAM, quantized)
  └── Endpoint: http://localhost:11434 (OpenAI-compatible)
  └── Drop-in replacement — zero config change in Continue.dev / Cline
```

> **Note:** The 26B MoE and 31B Dense variants require 16GB+ and 24GB+ VRAM
> respectively and cannot run on the Phase 1 node GPU (8GB).
> The E4B (4.5B effective params) is the maximum viable local model for this hardware.

---

## 5. Component Details

### 5.1 IDE — VS Code

- **Version:** Latest stable release
- **Why not Cursor:** Cursor free tier (2,000 completions/month, 50 slow requests) is
  insufficient for daily vibe-coding and does not allow BYO API key on the free plan.
  VS Code + open-source extensions provides equivalent or superior capability with zero
  vendor lock-in and full API key control.
- **Required extensions:**
  - Continue.dev
  - Cline
  - GitLens (MIT)
  - ESLint / Pylint (per language)

### 5.2 Autocomplete & Chat — Continue.dev

- **Role:** Inline code suggestions, chat sidebar, codebase-aware Q&A
- **Configuration file:** `.continue/config.json` (project root, gitignored — contains API keys)
- **Primary model:** `gemma-4-26b-a4b-it` via Google AI Studio
- **Context strategy:** Use `@codebase` and `@file` tags to provide targeted context,
  minimising token consumption against the free rate limit

### 5.3 Agent Mode — Cline

- **Role:** Autonomous multi-file editing, debugging loops, shell command execution,
  tool/function calling
- **Why Cline over Continue agent mode:** Cline has a more mature agent loop with
  explicit approval steps before destructive actions — critical for sandboxing discipline
  even in Phase 1
- **Configuration:** API key set in VS Code settings (workspace scope, not global)
- **Sandboxing rule (Phase 1):** Cline must never be granted root shell access.
  All shell commands are executed in the workspace directory only.

### 5.4 AI Backend — Gemma 4 via Google AI Studio

- **Model IDs:**
  - `gemma-4-26b-a4b-it` — primary (MoE, efficient, good for code)
  - `gemma-4-31b-it` — reserved for complex reasoning tasks (higher latency)
- **Context window:** 256K tokens — sufficient for full-file and multi-file context
- **Native capabilities:** Function calling, structured JSON output, system prompts —
  all required for agentic workflows in Phase 3
- **Cost:** Free on Google AI Studio developer tier
- **Rate limit:** ~15 RPM — primary bottleneck; mitigated by Gemini Flash fallback
- **API key management:** Stored in local `.env` file (gitignored). Never committed.

### 5.5 Fallback Model — Gemini Flash

- **Model:** `gemini-2.5-flash` (or latest Flash variant on AI Studio)
- **Trigger condition:** Gemma 4 rate limit hit (429 error) during an active session
- **Limit:** 1,000 requests/day, 60 RPM
- **Configuration:** Secondary provider entry in Continue.dev and Cline configs

### 5.6 Backend Framework (for SwarmForge services)

- **Primary:** FastAPI (MIT) — Python, async, OpenAPI spec auto-generation
- **Alternative:** Hono (MIT) — TypeScript, ultra-lightweight, edge-compatible
- **Decision criteria:** Use FastAPI if the team is more comfortable in Python;
  Hono if the primary language is TypeScript

### 5.7 Database

- **Engine:** SQLite / LibSQL (Public Domain)
- **Rationale:** File-based, zero infrastructure, fully portable — aligns with Pillar #5
  (Data Portability). Upgradeable to PostgreSQL in Phase 3 without schema changes
  if using an ORM abstraction layer (e.g., SQLAlchemy / Drizzle)

### 5.8 Frontend (if needed in Phase 1)

- **Bundler:** Vite (MIT)
- **Framework:** React (MIT)
- **Styling:** Tailwind CSS (MIT)
- **Note:** A frontend is not strictly required for Phase 1. The primary deliverable
  is the agent-IDE loop, not a user-facing UI.

---

## 6. API Key Management Protocol

All API credentials follow this protocol from day one:

```
1. Keys are stored ONLY in local .env files
2. .env files are listed in .gitignore before the first commit
3. Keys are NEVER hardcoded in source files
4. Keys are NEVER committed, even in private repositories
5. Each founder maintains their own API keys independently
6. A .env.example file with placeholder values IS committed as documentation
```

Example `.env.example`:
```env
# Google AI Studio — Gemma 4 / Gemini Flash
GOOGLE_AI_STUDIO_API_KEY=your_key_here

# Optional: Paid fallback (Claude)
ANTHROPIC_API_KEY=your_key_here

# Optional: Paid fallback (OpenAI)
OPENAI_API_KEY=your_key_here
```

---

## 7. Immediate Setup Checklist (Next 7 Days)

- [ ] Install VS Code (latest stable)
- [ ] Install Continue.dev extension
- [ ] Install Cline extension
- [ ] Create Google AI Studio account → generate API key
- [ ] Configure Continue.dev: set `gemma-4-26b-a4b-it` as primary model
- [ ] Configure Cline: same API key, same primary model
- [ ] Configure Gemini Flash as fallback provider in both extensions
- [ ] Validate Phase 1 KPI #1: TTFT < 1.5s on a test prompt
- [ ] Validate Phase 1 KPI #2: agent autonomously executes 5 basic IDE commands
- [ ] (Optional) Install Ollama + `gemma4:e4b` for offline fallback

---

## 8. Open Questions for Phase 2

The following decisions are deliberately deferred to Phase 2 to avoid scope creep:

1. **Primary backend language:** Python (FastAPI) vs TypeScript (Hono)?
2. **Database ORM:** SQLAlchemy vs Drizzle vs raw SQL?
3. **Containerisation baseline:** Docker Compose structure for the first multi-service setup
4. **VPN/Mesh solution:** WireGuard vs Tailscale (license audit pending)

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Next review:* Phase 1 KPI validation — target within 14 days of setup completion