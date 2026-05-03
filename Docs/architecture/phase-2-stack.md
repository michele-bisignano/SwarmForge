# SwarmForge — Phase 2 Stack Definition
**Document ID:** `SF-ARCH-002`
**Codename:** *The Swarm*
**Version:** 1.2 (Updated — Phase 2.A complete, 27/27 tests passing)
**Status:** Phase 2.C ✅ COMPLETE — Phase 2 is fully finished. Phase 3 ⬜ NEXT
**Authors:** Michele Bisignano, Alessandro Campani
**Date:** April 2026

---

## 1. Objective

Phase 2 transitions SwarmForge from a single-agent vibe-coding assistant into a
coordinated multi-agent system. A dedicated orchestration layer decomposes complex
jobs and dispatches them to specialized agents with distinct roles.

**Phase 2 does not introduce new hardware or inter-device networking.**
All compute remains on the single Phase 1 node or via cloud APIs.
Physical distribution is explicitly deferred to a future optional phase.

---

## 2. Phase 2.A — COMPLETE

### What Was Built

A complete multi-agent orchestration pipeline with all components implemented,
tested, and validated end-to-end. 27/27 unit and integration tests passing.

### Architecture

```
Developer
    │
VS Code + Cline (Gemini Flash — Google AI Studio free tier)
    │
Cline Kanban (localhost:3484)
    │
    ├── contract-architect → produces Contract Documents
    ├── class-coder        → implements from Contract
    └── code-reviewer      → validates implementation
```

### Data Flow

```
task_description: str
        │
        ▼
RuleBasedTaskDecomposer.decompose()
        │  splits by ". " + keyword routing
        ▼
list[Subtask]  (kind: "architect" | "coder" | "reviewer")
        │
        ▼  (for each subtask, sequentially)
CapabilityMatchSelector.select(subtask, registry)
        │  matches subtask.kind → agent.capabilities()
        ▼
AbstractAgent.run(subtask) → SubtaskResult
        │
        ▼  (after all subtasks complete)
SequentialResultAggregator.aggregate(task_id, results)
        │  concatenates OK results with "\n"
        ▼
SwarmResult(task_id, results, final_content)
```

### Implemented Components

| Component | File | Responsibility | Tests |
|---|---|---|---|
| Value Objects | `src/orchestrator/models.py` | Pydantic v2 data models | — |
| SwarmOrchestrator | `src/orchestrator/orchestrator.py` | Thin coordinator, workflow loop | 18/18 |
| AbstractTaskDecomposer | `src/orchestrator/decomposer.py` | ABC for decomposition | — |
| RuleBasedTaskDecomposer | `src/orchestrator/decomposer.py` | Rule-based, keyword routing | — |
| AgentRegistry | `src/orchestrator/registry.py` | Agent pool management | 3/3 |
| AbstractAgentSelector | `src/orchestrator/selector.py` | ABC for agent selection | — |
| CapabilityMatchSelector | `src/orchestrator/selector.py` | Matches kind → capabilities() | 2/2 |
| AbstractResultAggregator | `src/orchestrator/aggregator.py` | ABC for aggregation | — |
| SequentialResultAggregator | `src/orchestrator/aggregator.py` | Concatenates OK results | — |
| AbstractAgent | `src/agents/base.py` | ABC for all agents | — |
| ArchitectAgent (stub) | `src/agents/stubs.py` | Phase 1 stub, hardcoded response | — |
| CoderAgent (stub) | `src/agents/stubs.py` | Phase 1 stub, hardcoded response | — |
| ReviewerAgent (stub) | `src/agents/stubs.py` | Phase 1 stub, hardcoded response | — |
| Integration Test | `tests/integration/` | End-to-end pipeline validation | 1/1 |
| **Total** | | | **27/27** |

### Class Hierarchy

```
AbstractAgent (ABC)                    ← src/agents/base.py
  ├── ArchitectAgent (stub)            capabilities: ["architect"]
  ├── CoderAgent (stub)               capabilities: ["coder"]
  └── ReviewerAgent (stub)            capabilities: ["reviewer"]

AbstractTaskDecomposer (ABC)           ← src/orchestrator/decomposer.py
  └── RuleBasedTaskDecomposer

AbstractAgentSelector (ABC)            ← src/orchestrator/selector.py
  └── CapabilityMatchSelector

AbstractResultAggregator (ABC)         ← src/orchestrator/aggregator.py
  └── SequentialResultAggregator

AgentRegistry                          ← src/orchestrator/registry.py
SwarmOrchestrator                      ← src/orchestrator/orchestrator.py
  depends on: AbstractTaskDecomposer
  depends on: AgentRegistry
  depends on: AbstractAgentSelector
  depends on: AbstractResultAggregator
```

### Development Workflow Used

Every module followed the mandatory three-agent cycle:

```
1. contract-architect  →  Docs/contracts/[Module].contract.md
         STOP — await approval
2. class-coder         →  src/[path]/[module].py + tests/
         STOP — await approval  
3. code-reviewer       →  Docs/reviews/[Module].review.md
         STOP — await approval
4. merge to main
```

### License Audit

| Component | License | Status |
|---|---|---|
| Cline / Cline Kanban | Apache 2.0 | ✅ Approved |
| LangGraph | MIT | ✅ Approved (deferred to Phase 3) |
| OpenJarvis | Apache 2.0 | ✅ Approved (installed, partial integration) |
| Langflow | MIT | ✅ Approved (Phase 2.B) |
| SWE-agent | MIT | ⚠️ Pending ACI dependency audit |
| AG2 / AutoGen sandbox | MIT + Apache 2.0 | ⚠️ BLOCKED — transitive license audit |

### Phase 2.A KPIs — VALIDATED

| KPI | Target | Result |
|---|---|---|
| Multi-agent task completion | 100% on 5 test tasks, 3+ files | ✅ 5 cycles complete |
| Orchestrator loop incidents | 0 | ✅ Loop guard active |
| Agent coordination overhead | < 2× Phase 1 TTFT | ✅ |
| External paid API calls | 0 | ✅ Gemini Flash free tier only |
| Integration test | Pass | ✅ 1/1 passed |
| Total tests | 27 passing | ✅ 27/27 |

---

## 3. Phase 2.B — Real Agents (COMPLETE)

**Goal:** Replace stub agents with real LLM-backed implementations.

### What Was Built (Architectural Pivot)

Instead of creating distinct subclasses (`ArchitectAgent`, `CoderAgent`, `ReviewerAgent`) as initially planned, the architecture was refactored to use a single, provider-agnostic `ClineAgent` powered by `AgentConfig`. 

`ClineAgent` implements the `AbstractAgent` contract and dynamically assumes roles based on YAML configurations (`configs/agents/*.yaml`). This approach dramatically reduced code duplication while maintaining strict separation of concerns via system prompts.

```python
# Phase 2.B (current) — real LLM call via ClineAgent
class ClineAgent(AbstractAgent):
    async def run(self, subtask: Subtask) -> SubtaskResult:
        # Calls Gemini Flash via Google AI Studio API or any OpenAI-compatible endpoint
        ...
```

### Files Implemented

```
src/agents/
  ├── base.py             ← unchanged
  ├── stubs.py            ← kept for testing
  ├── config.py           ← NEW: AgentConfig value object
  └── cline_agent.py      ← NEW: ClineAgent concrete implementation
configs/agents/
  ├── architect.yaml      ← NEW: role, model, and system prompt config
  ├── coder.yaml          ← NEW: role, model, and system prompt config
  └── reviewer.yaml       ← NEW: role, model, and system prompt config
src/orchestrator/
  └── factory.py          ← NEW: SwarmFactory to wire agents dynamically
```

### Success Criteria — Phase 2.B (VALIDATED)

| KPI | Target | Result |
|---|---|---|
| Real agent completes a multi-file task | 100% on test tasks | ✅ Achieved via `ClineAgent` |
| No paid API calls | 0 (Gemini Flash free tier only) | ✅ Achieved |
| TTFT per agent | < 5 seconds | ✅ Verified via integration |

---

## 4. Phase 2.C — Local Inference (COMPLETE)

**Goal:** Enable an optional local backend for the Reviewer agent to reduce API dependency.

### What Was Built (Configuration Pivot)

Thanks to the architectural pivot in Phase 2.B, `ClineAgent` natively supports any OpenAI-compatible API endpoint. Ollama exposes exactly such an endpoint at `http://localhost:11434/v1`. 

Therefore, **no new `OllamaAgent` class was required.** Local inference is achieved purely via configuration.

```yaml
# configs/agents/reviewer.yaml (Local Inference Override)
role: reviewer
model: gemma4:e4b
api_base_url: http://localhost:11434/v1
api_key_env_var: OLLAMA_API_KEY # (Optional/Dummy)
```

Alternatively, it can be driven via environment variables without touching the YAML:
```bash
export REVIEWER_MODEL="gemma4:e4b"
export REVIEWER_API_BASE_URL="http://localhost:11434/v1"
```

**Hardware constraint:** only `gemma4:e4b` (4.5B effective params, ~5GB VRAM)
is viable locally on the RTX 4060 (8GB VRAM). Use for Reviewer only — low
complexity, high frequency. Keep Architect and Coder on cloud API.

### Success Criteria — Phase 2.C (VALIDATED)

| KPI | Target | Result |
|---|---|---|
| Local Reviewer TTFT | < 3 seconds | ✅ Achieved via local Ollama endpoint |
| OOM crashes on 8GB VRAM | 0 | ✅ Achieved via gemma4:e4b quantization |
| Paid API calls during local sessions | 0 | ✅ Achieved |

---

## 5. OpenJarvis — Current Status

**Installed at:** `C:/Algoritmi/tools/openjarvis/`
**Config at:** `C:/Users/Michele/.openjarvis/config.toml`

```toml
[engine]
default = "ollama"

[intelligence]
default_model = "gemma4:e4b"

[agent]
default_agent = "orchestrator"
max_iterations = 3

[security]
profile = "personal"
mode = "block"
guardrails_enabled = true
prompt_injection_detection = true
file_policy_enabled = true
allowed_paths = ["C:/Algoritmi/SwarmForge"]

[server]
host = "127.0.0.1"
port = 8080
auth_enabled = false
```

**Known issue:** Cline cannot connect to Jarvis FastAPI server due to
`stream_options` field incompatibility (HTTP 422). Jarvis serves correctly
when called directly (verified via curl). Resolution deferred — not blocking
for Phase 2.B.

**To start Jarvis:**
```bash
# Terminal 1
ollama serve

# Terminal 2
cd C:/Algoritmi/tools/openjarvis
uv run jarvis serve
```

---

## 6. Deferred to Phase 3+

The following are explicitly out of scope for Phase 2:

1. **Second physical node** — networking, mesh VPN, IP masking
2. **Gateway / Load Balancer** — not needed until 2+ physical nodes
3. **Fine-tuning pipeline** — Phase 4 (requires stable log format)
4. **AG2 sandbox** — blocked pending transitive license audit
5. **LangGraph DAG** — replaced by Cline Kanban for Phase 2; reintroduce
   in Phase 3 if orchestration complexity requires programmatic DAG control

---

## 7. Full Phase 2 Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                        DEVELOPER                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      IDE LAYER                              │
│    VS Code + Cline v3.80 (supervision, approval)            │
│    Cline Kanban v0.1.64 (multi-agent task board)            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               ORCHESTRATION LAYER                           │
│                 SwarmOrchestrator                           │
│    ┌────────────┬──────────────┬──────────────┐             │
│    │ Architect  │    Coder     │   Reviewer   │             │
│    │  (stub →   │  (stub →     │  (stub →     │             │
│    │   real)    │   real)      │  local/real) │             │
│    └─────┬──────┴──────┬───────┴───────┬──────┘             │
└──────────┼─────────────┼───────────────┼────────────────────┘
           │             │               │
    ┌──────▼─────────────▼───────────────▼──────┐
    │           API ROUTING LAYER               │
    │   PRIMARY:  Gemini Flash (cloud, free)    │
    │   FALLBACK: Gemma 4 API (cloud, free)     │
    │   LOCAL:    Ollama + gemma4:e4b (2.C)     │
    └───────────────────────────────────────────┘

[TOOLS — not in production path]
  OpenJarvis (localhost:8080) → hardware metrics, trace logging
  Cline Kanban (localhost:3484) → agent task orchestration UI

[DESIGN TIME ONLY]
  Langflow (Phase 2.B) → visual workflow design → exports to Python
```

---

*Document approved by:* Michele Bisignano, Alessandro Campani
*Phase 2.A completed:* April 2026
*Prerequisite document:* SF-ARCH-001 v1.3
*Next review:* Phase 2.B completion
*Supersedes:* SF-ARCH-002 v1.1