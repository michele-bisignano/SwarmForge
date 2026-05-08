# Decision Log

Append-only. Add new entries at the top. Never delete or modify past entries.
Format: `[YYYY-MM] Decision — Reason`

---

[2026-05] OpenCode (MIT) replaces Cline as primary IDE agent.
Reason: provider-agnostic, 100% open source, client/server architecture,
reads existing .clinerules/ natively. Cline Kanban decommissioned —
multi-agent orchestration correctly owned by SwarmOrchestrator Python layer.

[2026-05] Memory Bank pattern implemented natively (not via RooFlow).
Reason: RooFlow requires Roo Code fork (private repo, restricted access).
Four markdown files in memory-bank/ loaded via opencode.json instructions
achieves identical persistent context without external dependency.

[2026-05] `share: "disabled"` enforced in opencode.json.
Reason: proprietary project. Conversations must never leave the machine.

[2026-04] ClineAgent naming retained despite IDE agent being renamed.
Reason: `ClineAgent` is a Python class implementing `AbstractAgent` that
calls any OpenAI-compatible endpoint via httpx. The name reflects its origin
in the Cline Kanban workflow (contract-architect → class-coder cycle), not
the IDE tool. Renaming would break 21 tests and change nothing functionally.

[2026-04] SwarmFactory loads agents from YAML, not code.
Reason: new roles added without code changes. Provider swaps require
only YAML + .env changes. Zero coupling between agent behavior and wiring.

[2026-04] RuleBasedTaskDecomposer: keyword-based, not LLM-based.
Reason: Phase 2 focus is orchestration correctness, not decomposition quality.
LLM-based decomposer deferred to Phase 3 when we have more interaction data.

[2026-04] httpx timeout set to 180s on ClineAgent.
Reason: Gemma 4 26B thinking mode can take 60–120s on complex tasks.
60s caused false timeouts on architect subtasks.

[2026-04] SequentialResultAggregator uses newline join, not structured merge.
Reason: Phase 2 output is consumed by humans reviewing SwarmResult.
Structured merge (JSON, XML) deferred until Phase 3 pipeline needs it.

[2026-04] Stubs kept in src/agents/stubs.py after ClineAgent introduction.
Reason: integration tests use stubs for deterministic behavior. ClineAgent
integration tests require real API keys and network — not suitable for CI.

[2026-04] All four SwarmOrchestrator collaborators mandatory (no defaults).
Reason: optional collaborators hide configuration errors silently. Missing
any collaborator is a programming error — TypeError at construction is correct.

[2026-04] Context chaining: FAILED subtasks excluded from accumulated_context.
Reason: failed agent output is unreliable. Downstream agents receiving bad
context compounds errors. Exclusion is the safe default.

[2026-03] GPL/AGPL/LGPL strictly forbidden.
Reason: copyleft licenses would contaminate the proprietary codebase and
destroy commercial value (licensing, SaaS, VC exit). No exceptions.