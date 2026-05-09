


# Pitfalls & Fixes
---
valid: true
last_verified: 2026-05-09
---

## Merge Conflicts in pyproject.toml / orchestrator.py
**Cause:** Branch merge without resolution.
**Fix:** Search for `<<<<<<<`, resolve manually, verify with an import check.
**Verification:** `uv run python -c "import src.agents; import src.orchestrator; print('OK')"`

## httpx Timeout Too Low
**Cause:** Gemma 4 26B thinking mode requires 60-120s.
**Fix:** Set timeout=180.0 in ClineAgent. Do not go below this value.
**File:** `src/agents/cline_agent.py`

## Flaky test_web_model.py
**Cause:** Requires Playwright + active browser session with login.
**Fix:** Skip in CI. Handled by a colleague. Do not touch.
**Safe run:** `uv run pytest tests/ -v --ignore=tests/orchestrator/test_web_model.py`

## Duplication of src/ai/web/ vs src/ai/text/web/
**Cause:** Incomplete refactoring.
**Fix:** Deleted src/ai/web/. Web files MUST ONLY be in src/ai/text/web/.
**Status:** Resolved on 2026-05-09.

## Copyleft Licenses
**Cause:** GPL/AGPL/LGPL dependencies contaminate the proprietary codebase.
**Fix:** MIT/Apache 2.0/BSD/Public Domain only. Verify BEFORE adding dependencies.
**Example:** claude-mem is AGPL → forbidden as a dependency (ok as a dev tool).

## print() in Production
**Cause:** Quick debug left in the code.
**Fix:** Always use `logging.getLogger(__name__)`. print() is forbidden.

## Hardcoded API Keys
**Cause:** Rushed development.
**Fix:** ALWAYS use os.getenv(). ALWAYS put them in a gitignored .env file. NEVER in opencode.json.

## Binary Files in Git
**Cause:** docs/standards/ contains .mp4 and .pdf files.
**Fix:** Use Git LFS for large binaries or link them externally.
**Status:** To be resolved.

## Versioned Griffe Snippets
**Cause:** docs/snippets/ contains auto-generated files.
**Fix:** Add to .gitignore or always regenerate them using make griffe-dump.
**Status:** To be decided.