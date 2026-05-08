# Active Context

> **Update this file at the start of every session.**
> It loads automatically and prevents context loss between sessions.

---

## Current Phase

**Phase 2.B — Real LLM Agents**

## Last Completed

- OpenCode migration complete (Cline replaced, May 2026)
- `opencode.json` created with full config
- `AGENTS.md` created with project rules
- `memory-bank/` initialized
- Documentation updated (SF-ONBOARD-001 v2.0, SF-ARCH-002 v1.4)

## Current Task

_[Update at session start]_

## Next Actions

1. Formal integration test with real LLM agents
   → `tests/integration/test_real_agents_integration.py`
2. Reviewer cycle: ClineAgent + SwarmFactory
   → `Docs/reviews/ClineAgent.review.md`
3. License & Credits agent
   → deterministic, `pip-licenses` scan, generates `CREDITS.md`

## Blockers

_[Fill if any]_

## Notes

- Test suite baseline: **67/67 passing** — do not break
- Primary model: `gemma-4-26b-a4b-it` via Google AI Studio
- httpx timeout on ClineAgent: 180s (Gemma thinking mode)
- OpenJarvis integration with OpenCode not yet tested