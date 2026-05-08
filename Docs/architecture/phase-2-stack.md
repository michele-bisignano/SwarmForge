# SwarmForge — Phase 2 Stack Definition
**Document ID:** `SF-ARCH-002`
**Codename:** *The Swarm*
**Version:** 1.4 (Updated — OpenCode replaces Cline, Memory Bank added)
**Status:** Phase 2.A ✅ COMPLETE — Phase 2.B 🔄 IN PROGRESS
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** May 2026

---

## 1. Objective

Phase 2 transitions SwarmForge from a single-agent vibe-coding assistant into a
coordinated multi-agent system with real LLM-backed agents, context chaining,
and provider-agnostic configuration.

**Phase 2 does not introduce new hardware or inter-device networking.**
All compute remains on the single Phase 1 node or via cloud APIs.
Physical distribution is explicitly deferred to a future optional phase.

---

## 2. Phase 2.A — ✅ COMPLETE

### What Was Built

A complete multi-agent orchestration pipeline with all components implemented,
tested, and validated end-to-end. 67/67 unit and integration tests passing.

### Implemented Components

| Component | File | Responsibility | Tests |
|---|---|---|---|
| Value Objects | `src/orchestrator/models.py` | Pydantic v2 data models | — |
| SwarmOrchestrator | `src/orchestrator/orchestrator.py` | Thin coordinator + context chaining | 22/22 |
| AbstractTaskDecomposer | `src/orchestrator/decomposer.py` | ABC for decomposition | — |
| RuleBasedTaskDecomposer | `src/orchestrator/decomposer.py` | Rule-based, keyword routing | — |
| AgentRegistry | `src/orchestrator/registry.py` | Agent pool management | 3/3 |
| AbstractAgentSelector | `src/orchestrator/selector.py` | ABC for agent selection | — |
| CapabilityMatchSelector | `src/orchestrator/selector.py` | Matches kind → capabilities() | 2/2 |
| AbstractResultAggregator | `src/orchestrator/aggregator.py` | ABC for aggregation | — |
| SequentialResultAggregator | `src/orchestrator/aggregator.py` | Concatenates OK results | — |
| AbstractAgent | `src/agents/base.py` | ABC for all agents | — |
| AgentConfig | `src/agents/config.py` | Provider-agnostic agent config | — |
| ClineAgent | `src/agents/cline_agent.py` | Real LLM agent via httpx | 21/21 |
| SwarmFactory | `src/orchestrator/factory.py` | Wires real agents from YAML | 15/15 |
| Stub Agents | `src/agents/stubs.py` | Phase 1 stubs (kept for testing) | — |
| Integration Test (stubs) | `tests/integration/` | End-to-end with stub agents | 1/1 |
| **Total** | | | **67/67** |

### Phase 2.A KPIs — VALIDATED

| KPI | Target | Result |
|---|---|---|
| Multi-agent task completion | 5 cycles, 3+ files each | ✅ Complete |
| Orchestrator loop incidents | 0 | ✅ Loop guard active |
| External paid API calls | 0 | ✅ Free tier only |
| Integration test (stubs) | Pass | ✅ 1/1 |
| Total tests | 67 passing | ✅ 67/67 |

---

## 3. Phase 2.B — 🔄 IN PROGRESS

### Goal
Real LLM-backed agents replacing stubs, with context chaining,
provider-agnostic configuration via YAML + environment variables,
and OpenCode as the new IDE agent layer.

### What Has Been Done

- [x] `AgentConfig` (Pydantic v2) — provider-agnostic, role extensible via `role: str`
- [x] `ClineAgent` — calls any OpenAI-compatible endpoint via httpx
- [x] `SwarmFactory` — builds SwarmOrchestrator from YAML configs
- [x] YAML configs — `configs/agents/{architect,coder,reviewer}.yaml`
- [x] Context chaining — each agent receives output of previous agents
- [x] End-to-end test with real LLM — Gemma 4 26B, 3/3 agents OK
- [x] `.env` structure — provider keys + per-agent model assignment
- [x] httpx timeout = 60s (required for Gemma thinking mode)
- [x] **OpenCode migration** — replaces Cline as IDE agent (MIT, provider-agnostic)
- [x] **Memory Bank** — persistent context across sessions (`memory-bank/`)

### What Remains

#### Core Phase 2.B
- [ ] Formal integration test with real agents (`tests/integration/test_real_agents_integration.py`)
- [ ] Reviewer review of ClineAgent + SwarmFactory (code-reviewer cycle)
- [ ] Update Ownership section in all contracts with current state
- [ ] License & Credits agent — deterministic algorithm (not LLM) that:
      - scans all dependencies via `pip-licenses` (MIT)
      - verifies licenses against approved list (MIT, Apache 2.0, BSD)
      - auto-generates `CREDITS.md`
      - runs as git pre-commit hook

#### Phase 2.B KPIs (to validate before closing)

| KPI | Target | Status |
|---|---|---|
| Real agent end-to-end task | 3/3 agents OK | ✅ Validated manually |
| Formal integration test | Pass | ⬜ Not yet written |
| Context chaining verified | Coder uses Architect output | ✅ Validated |
| TTFT per agent | < 60s (Gemma thinking mode) | ✅ Within timeout |
| Paid API calls | 0 | ✅ Free tier only |
| OpenCode migration complete | Cline fully replaced | ✅ Complete |

---

## 4. Phase 2.C — ⬜ DEFERRED

**Gate:** Phase 2.B must be fully stable and all KPIs validated.

Introduce `OllamaAgent` as optional local backend for the Reviewer agent.

```
Cloud Agent (current)              Local Agent (Phase 2.C)
──────────────────────             ──────────────────────
model:    gemma-4-26b-a4b-it       model:    gemma4:e4b (quantized)
endpoint: Google AI Studio         endpoint: http://localhost:11434/v1
api_key:  GOOGLE_AI_STUDIO_KEY     api_key:  "ollama" (any string)
```

**Hardware constraint:** only `gemma4:e4b` (~5GB VRAM) is viable on RTX 4060 (8GB).
Reserve for Reviewer agent (low-complexity, high-frequency).
Keep Architect and Coder on cloud API.

**Implementation:** zero code changes — only a new `configs/agents/reviewer_local.yaml`
and `OLLAMA_API_BASE_URL=http://localhost:11434/v1` in `.env`. Architecture is already provider-agnostic.

### Phase 2.C KPIs

| KPI | Target |
|---|---|
| Local Reviewer TTFT | < 3 seconds |
| OOM crashes on 8GB VRAM | 0 |
| Failover local → cloud on rate limit | Functional |
| Paid API calls during local sessions | 0 |

---

## 5. Architecture — Current State

```
┌─────────────────────────────────────────────────────────────┐
│                        DEVELOPER                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      IDE LAYER                              │
│    VS Code + OpenCode (MIT, v1.3+)                          │
│    Plan mode: read-only analysis (Tab to toggle)            │
│    Build mode: file edits + bash with permission gates      │
│    .clinerules/ loaded via opencode.json instructions       │
│    memory-bank/ loaded for persistent session context       │
│    .opencode/agents/ for custom agent definitions           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  SWARM FACTORY                              │
│    Loads YAML configs → instantiates ClineAgent per role    │
│    Wires SwarmOrchestrator with all components              │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               ORCHESTRATION LAYER                           │
│         SwarmOrchestrator (context chaining active)         │
│                                                             │
│  task_description                                           │
│       │                                                     │
│       ▼ RuleBasedTaskDecomposer                             │
│  [Subtask: architect] → ClineAgent(architect config)        │
│       │ output appended to accumulated_context              │
│  [Subtask: coder]     → ClineAgent(coder config)            │
│       │   receives architect output as context              │
│       │ output appended to accumulated_context              │
│  [Subtask: reviewer]  → ClineAgent(reviewer config)         │
│       │   receives architect + coder output as context      │
│       ▼ SequentialResultAggregator                          │
│  SwarmResult(final_content, results)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
    ┌─────────────────────▼──────────────────────┐
    │          API ROUTING LAYER                 │
    │  PRIMARY:  Gemma 4 26B (Google AI Studio)  │
    │  FALLBACK: Gemini Flash (Google AI Studio) │
    │  LOCAL:    Ollama + gemma4:e4b (2.C)       │
    └────────────────────────────────────────────┘

[TOOLS — not in production path]
  OpenJarvis (localhost:8080) → hardware metrics, trace logging
```

---

## 6. Technology Stack — Phase 2

| Component | License | Status | Role |
|---|---|---|---|
| OpenCode | MIT | ✅ Active | IDE agent — TUI + VS Code integration |
| ClineAgent | Apache 2.0 (our code) | ✅ Active | Real LLM agent (Python class) |
| AgentConfig | Apache 2.0 (our code) | ✅ Active | Provider-agnostic config |
| SwarmFactory | Apache 2.0 (our code) | ✅ Active | Agent wiring |
| httpx | MIT | ✅ Active | Async HTTP client |
| pyyaml | MIT | ✅ Active | YAML config loading |
| python-dotenv | MIT | ✅ Active | .env loading |
| OpenJarvis | Apache 2.0 | ⚠️ Partial | Hardware metrics (stream_options issue) |
| LangGraph | MIT | ⬜ Deferred | Phase 3 if DAG complexity requires it |
| SWE-agent | MIT | ⚠️ Pending audit | ACI pattern for Coder agent |
| AG2 sandbox | MIT+Apache 2.0 | 🚫 Blocked | License audit incomplete |
| ~~Cline~~ | ~~Apache 2.0~~ | ❌ Removed | Replaced by OpenCode (May 2026) |
| ~~Cline Kanban~~ | ~~Apache 2.0~~ | ❌ Removed | Multi-agent owned by SwarmOrchestrator |

---

## 7. OpenJarvis — Current Status

**Installed at:** `C:/Algoritmi/tools/openjarvis/` (outside SwarmForge repo)
**Config:** `C:/Users/Michele/.openjarvis/config.toml`

```toml
[security]
profile = "personal"
mode = "block"
guardrails_enabled = true
file_policy_enabled = true
allowed_paths = ["C:/Algoritmi/SwarmForge"]

[server]
host = "127.0.0.1"
port = 8080
```

**Known issue:** OpenCode → Jarvis connection not yet tested (Cline had
stream_options HTTP 422 incompatibility). Deferred.

**To start:**
```bash
ollama serve          # Terminal 1
cd C:/Algoritmi/tools/openjarvis && uv run jarvis serve  # Terminal 2
```

---

## 8. Deferred to Phase 3+

1. **Second physical node** — networking, mesh VPN, IP masking
2. **Gateway / Load Balancer** — not needed until 2+ physical nodes
3. **Fine-tuning pipeline** — Phase 4
4. **AG2 sandbox** — blocked pending transitive license audit
5. **LangGraph DAG** — evaluate in Phase 3 if needed
6. **SuperMemory** — external service; Memory Bank pattern implemented natively
7. **Cypress** — UI testing agent (Phase 3, web projects only)
8. **OpenCode client/server mode** — Phase 3+ for remote access use case

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Phase 2.A completed:* April 2026
*Phase 2.B started:* April 2026
*Phase 2.B tooling update:* May 2026 (OpenCode migration)
*Prerequisite document:* SF-ARCH-001 v1.4
*Next review:* Phase 2.B KPI validation
*Supersedes:* SF-ARCH-002 v1.3