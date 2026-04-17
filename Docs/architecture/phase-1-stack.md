# SwarmForge — Phase 1 Stack Definition
**Document ID:** `SF-ARCH-001`
**Codename:** *Single-Node Genesis*
**Version:** 1.2 (Updated — Cline as primary agent, Aider added, Skills system added)
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
| Cline | Apache 2.0 | ✅ Approved |
| Aider | Apache 2.0 | ✅ Approved |
| Continue.dev | Apache 2.0 | ✅ Approved (optional — see §5.4) |
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
│  AUTOCOMPLETE LAYER     │ │      AGENT LAYER             │
│  Continue.dev           │ │                              │
│  (Apache 2.0, optional) │ │  PRIMARY: Cline              │
│  - Inline suggestions   │ │  (Apache 2.0)                │
│  - Chat sidebar         │ │  - Plan / Act modes          │
│  - Context-aware        │ │  - Multi-file editing        │
│                         │ │  - Autonomous debug loops    │
│  Setup AFTER Cline is   │ │  - MCP tool integration      │
│  stable. Not required   │ │  - Browser headless testing  │
│  for Phase 1 KPIs.      │ │  - Checkpoints / rollback    │
│                         │ │  - Subagents (parallel)      │
│                         │ │                              │
│                         │ │  SECONDARY: Aider (terminal) │
│                         │ │  (Apache 2.0)                │
│                         │ │  - Git-native, auto-commit   │
│                         │ │  - Mass refactoring          │
│                         │ │  - Full repo tree-sitter map │
└──────────────┬──────────┘ └─────────┬───────────────────┘
               │                      │
               └──────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│               KNOWLEDGE LAYER                           │
│         .cline/SKILL.md  (agentskills.io standard)      │
│   - SwarmForge coding standards                         │
│   - Architectural rules & forbidden patterns            │
│   - Active phase context — reduces token waste          │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API ROUTING LAYER                     │
│         (managed via Cline settings panel)              │
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
  └── Drop-in replacement — zero config change in Cline
```

> **Note:** The 26B MoE and 31B Dense variants require 16GB+ and 24GB+ VRAM
> respectively. With 8GB GPU, only gemma4:e4b is viable locally.
> Default to cloud API — local inference is a fallback only.

---

## 5. Component Details

### 5.1 IDE — VS Code

- **Version:** Latest stable release
- **Why not Cursor:** Cursor free tier is insufficient for daily vibe-coding
  (2,000 completions/month, no BYO API key on free plan). VS Code + Cline provides
  equivalent agentic capability with zero vendor lock-in.
- **Required extensions (in setup order):**
  1. Cline — install and validate first
  2. GitLens (MIT)
  3. ESLint / Pylint (per language)
  4. Continue.dev — optional, install after Cline is stable

### 5.2 Primary Agent — Cline

Cline is the primary agentic interface for all of Phase 1.

**Two-mode workflow:**

- **Plan Mode (read-only):** Cline analyses the repository, maps file dependencies,
  and proposes a complete action plan. No file is touched until the developer approves.
  Strict Plan Mode setting ensures this is enforced at the extension level.
- **Act Mode (execution):** Cline implements the approved plan step by step.
  Every file write and terminal command requires explicit developer approval.

**Full capabilities inventory (Phase 1 usage):**

```
CLINE CAPABILITY                    PHASE 1 USE CASE
────────────────────────────────────────────────────────────
Plan / Act mode separation      ←  safe agentic workflow
Multi-file editing (diff view)  ←  primary coding mechanism
Terminal command execution       ←  install deps, run tests
Linter/compiler error monitor   ←  autonomous fix loops
Browser headless (Chrome)        ←  visual debug, web testing
MCP protocol integration         ←  external tool extension
Checkpoints (workspace snapshot) ←  rollback at every step
Subagents (parallel exploration) ←  codebase analysis
Cline CLI (headless)             ←  terminal / pipeline use
Auto Compact                     ←  context window management
Double-Check Completion          ←  output quality gate
```

**Cline API configuration (Google AI Studio):**

```
Provider:  OpenAI Compatible
Base URL:  https://generativelanguage.googleapis.com/v1beta/openai/
API Key:   [GOOGLE_AI_STUDIO_KEY — from .env, never hardcoded]
Model ID:  gemma-4-26b-a4b-it
```

**Recommended Cline settings for SwarmForge Phase 1:**

```
AGENT
  Subagents              ON   — parallel codebase exploration
  Native Tool Call       ON   — Gemma 4 native function calling
  Parallel Tool Calling  ON   — reads multiple files simultaneously
  Strict Plan Mode       ON   — no file edits during Plan phase (mandatory)
  Auto Compact           ON   — context window management vs 15 RPM limit
  Focus Chain            ON   — reduces token waste across interactions
  Reminder Interval      4    — reduced from default 6 to save tokens

EDITOR
  Feature Tips           OFF  — noise reduction
  Background Edit        OFF  — full visibility in Phase 1
  Checkpoints            ON   — mandatory rollback capability

EXPERIMENTAL
  YOLO Mode              OFF  — STRICTLY FORBIDDEN Phase 1-2 (Zero-Trust policy)
  Double-Check           ON   — model re-verifies output before accepting
  Lazy Mode              OFF

ADVANCED
  Hooks                  OFF  — deferred to Phase 2 (OpenJarvis log integration)
  MCP Display            Minimal

BROWSER
  Disable browser        OFF  — keep headless testing capability
  Viewport               Large Desktop (1280x800)
  Remote browser         OFF  — attack surface reduction

TERMINAL
  Profile                PowerShell 7 (preferred) or Git Bash
  Shell timeout          15-20 seconds (increased for Windows stability)
  Aggressive reuse       ON
  Execution Mode         VS Code Terminal
  Output limit           800 lines
```

### 5.3 Secondary Agent — Aider (Terminal)

Aider complements Cline for high-autonomy terminal-based operations.

| Dimension | Cline | Aider |
|---|---|---|
| Interface | VS Code panel | Terminal (CLI) |
| Approval model | Per-action human approval | High autonomy |
| Git integration | Manual | Native — auto-commits |
| Best use case | Feature development, debugging | Mass refactoring |
| Codebase mapping | AST-aware | tree-sitter (full repo) |

**When to use Aider over Cline:**
- Refactoring a pattern across 20+ files simultaneously
- Architectural renames across the entire repo
- Situations where automatic Git commits at every step are desired

**Aider API configuration:**

```bash
# In .env (gitignored):
GEMINI_API_KEY=[GOOGLE_AI_STUDIO_KEY]

# Run:
aider --model gemini/gemma-4-26b-a4b-it
```

### 5.4 Autocomplete & Chat — Continue.dev (Optional)

Continue.dev provides inline code suggestions during regular (non-agentic) coding.

**It is not required for Phase 1 KPIs.** Configure only after Cline is fully validated.

**Common issue on Windows:** Continue.dev may throw permission errors on first run.
Fix: ensure the VS Code workspace is set to "Trusted" and the extension host has
file system access. Do not let this block Phase 1 progress — Cline covers all
agentic use cases independently.

### 5.5 Knowledge Layer — SKILL.md

The `SKILL.md` file is the agent's permanent briefing document, read at session start.

**Location:** `.cline/SKILL.md` (committed to repo — not gitignored)

**Contents to define in Phase 1:**
- SwarmForge coding standards (English-only code, documented functions)
- Forbidden patterns (hardcoded keys, GPL dependencies, undocumented functions)
- Architectural rules (OpenAI-compatible interfaces, modular design)
- Active phase context (current phase, active models, folder structure)
- Response format preferences (diff only, no explanation unless asked, etc.)

**Standard:** agentskills.io open standard (compatible with Hermes Catalog and skills.sh).

### 5.6 AI Backend — Gemma 4 via Google AI Studio

- **Primary model:** `gemma-4-26b-a4b-it` (MoE, strong on code, efficient)
- **Secondary model:** `gemma-4-31b-it` (reserved for complex reasoning tasks)
- **Context window:** 256K tokens
- **Native capabilities:** Function calling, structured JSON output, system prompts
- **Cost:** Free — Google AI Studio developer tier
- **Rate limit:** ~15 RPM — primary operational bottleneck
- **License:** Apache 2.0 — safe for proprietary product integration

### 5.7 Fallback Model — Gemini Flash

- **Trigger:** Gemma 4 returns 429 (rate limit exceeded)
- **Limit:** 1,000 requests/day, 60 RPM
- **Configuration:** Secondary provider in Cline API settings panel

### 5.8 Backend Framework (SwarmForge services)

- **Primary:** FastAPI (MIT) — Python, async, auto-generates OpenAPI spec
- **Alternative:** Hono (MIT) — TypeScript, ultra-lightweight
- **Decision deferred to Phase 2**

### 5.9 Database

- **Engine:** SQLite / LibSQL (Public Domain)
- **Rationale:** File-based, zero infrastructure, fully portable

---

## 6. API Key Management Protocol

```
1. Keys stored ONLY in local .env files
2. .env listed in .gitignore before the first commit
3. Keys NEVER hardcoded in source files
4. Keys NEVER committed, even in private repositories
5. Each founder maintains independent API keys
6. .env.example with placeholders IS committed as documentation
```

`.env.example`:

```env
# Google AI Studio — Gemma 4 / Gemini Flash
GOOGLE_AI_STUDIO_API_KEY=your_key_here

# Optional: Paid fallback
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

---

## 7. Immediate Setup Checklist

- [ ] Install VS Code (latest stable)
- [ ] Install Cline extension
- [ ] Create Google AI Studio account → generate API key
- [ ] Configure Cline with Gemma 4 API (see §5.2)
- [ ] Apply all recommended Cline settings (see §5.2 settings table)
- [ ] Create `.cline/SKILL.md` with SwarmForge standards
- [ ] Validate KPI #1: TTFT < 1.5s on test prompt
- [ ] Validate KPI #2: agent executes 5 basic IDE commands autonomously
- [ ] Install Aider: `pip install aider-chat` — configure Gemma 4 backend
- [ ] (Optional) Install Continue.dev after Cline is validated
- [ ] (Optional) Install Ollama + `gemma4:e4b` for offline fallback

---

## 8. Open Questions for Phase 2

1. **Backend language decision:** Python (FastAPI) vs TypeScript (Hono)?
2. **Database ORM:** SQLAlchemy vs Drizzle vs raw SQL?
3. **Docker Compose:** containerisation baseline structure
4. **Cline Hooks → OpenJarvis:** which lifecycle events feed the logging pipeline?
5. **Cline Kanban vs LangGraph:** can Kanban replace LangGraph for Phase 2.A?

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Next review:* Phase 1 KPI validation — within 14 days of setup completion
*Supersedes:* SF-ARCH-001 v1.1