# SwarmForge — Phase 1 Stack Definition
**Document ID:** `SF-ARCH-001`

**Codename:** *Single-Node Genesis*

**Version:** 1.1 (Updated)

**Status:** Approved — Architecture Draft

**Authors:** Michele Bisignano, Alessandro Campani

**Date:** April 2026

---

## 1. Objective

Define the complete, reproducible technology stack for Phase 1 of Project SwarmForge.
The goal of this phase is a fully functional local vibe-coding environment where AI agents 
live inside VS Code and the terminal, powered by the Gemma 4 cloud API (free tier), and can autonomously
write, edit, and debug code — validating the IDE-to-agent integration loop before any
distributed infrastructure is introduced.

**Phase 1 is deliberately single-node. No networking, no load balancing, no multi-agent orchestration.**
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
| Aider | Apache 2.0 | ✅ Approved |
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
│    Continue.dev         │ │      Cline + Aider          │
│    (Apache 2.0)         │ │      (Apache 2.0)            │
│  - Inline suggestions   │ │  - Cline: IDE-integrated,    │
│  - Chat sidebar         │ │    human-in-the-loop, editing│
│  - Context-aware        │ │  - Aider: Terminal-based,    │
│                         │ │    Git-native, mass refactor │
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
  └── Drop-in replacement — zero config change in Continue.dev / Cline / Aider
```

---

## 5. Component Details

### 5.1 IDE — VS Code
- **Version:** Latest stable release.
- **Why not Cursor:** Lack of BYO API key on free plan and strict rate limits.
- **Required extensions:** Continue.dev, Cline, GitLens, ESLint/Pylint.

### 5.2 Autocomplete & Chat — Continue.dev
- **Role:** Inline suggestions and codebase-aware Q&A.
- **Context strategy:** Use `@codebase` and `@file` tags to minimize token waste.

### 5.3 Agent Mode (IDE) — Cline
- **Role:** Autonomous multi-file editing and debugging loops within the IDE.
- **Workflow:** Human-in-the-loop. Every destructive action (file write, shell command) requires explicit user approval.
- **Capabilities:** Browser headless testing and MCP protocol integration.

### 5.4 Agent Mode (Terminal) — Aider
- **Role:** Autonomous pair-programming via CLI.
- **Workflow:** High-autonomy. Specialized in mass refactoring and architectural changes across multiple files.
- **Core Strength:** Native Git integration. Aider automatically commits changes with semantic messages, allowing instant rollbacks of agent-generated code.

### 5.5 Knowledge Layer — agentskills.io (SKILL.md)
- **Role:** Stateless procedural memory for the agents.
- **Implementation:** Integration of `SKILL.md` files in the repository root.
- **Purpose:** Define project-specific standards, coding style, and architectural rules. This ensures agents follow "SwarmForge way" without needing to repeat instructions in every prompt, significantly reducing token consumption.

### 5.6 AI Backend — Gemma 4 via Google AI Studio
- **Primary Model:** `gemma-4-26b-a4b-it` (MoE).
- **Fallback Model:** `gemini-2.5-flash` (for high-frequency, low-complexity tasks).
- **Context window:** 256K tokens.

### 5.7 Backend & Database (for SwarmForge services)
- **Framework:** FastAPI (MIT) or Hono (MIT).
- **Database:** SQLite / LibSQL (Public Domain) — file-based, portable, zero-config.

---

## 6. API Key Management Protocol

```
1. Keys are stored ONLY in local .env files
2. .env files are listed in .gitignore before the first commit
3. Keys are NEVER hardcoded in source files
4. Keys are NEVER committed, even in private repositories
5. Each founder maintains their own API keys independently
6. A .env.example file with placeholder values IS committed as documentation
```

---

## 7. Immediate Setup Checklist (Next 7 Days)

- [ ] Install VS Code (latest stable)
- [ ] Install Continue.dev and Cline extensions
- [ ] Install Aider (`pip install aider-chat`)
- [ ] Create Google AI Studio account $\rightarrow$ generate API key
- [ ] Configure primary model (`gemma-4-26b-a4b-it`) in Continue.dev, Cline, and Aider
- [ ] Configure Gemini Flash as fallback provider
- [ ] **Create initial `SKILL.md`** defining the project's basic coding standards
- [ ] Validate Phase 1 KPI #1: TTFT < 1.5s on a test prompt
- [ ] Validate Phase 1 KPI #2: agent autonomously executes 5 basic IDE commands
- [ ] (Optional) Install Ollama + `gemma4:e4b` for offline fallback

---

## 8. Open Questions for Phase 2

1. **Primary backend language:** Python (FastAPI) vs TypeScript (Hono)?
2. **Database ORM:** SQLAlchemy vs Drizzle vs raw SQL?
3. **Containerisation baseline:** Docker Compose structure.
4. **VPN/Mesh solution:** WireGuard vs Tailscale.

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Next review:* Phase 1 KPI validation — target within 14 days of setup completion