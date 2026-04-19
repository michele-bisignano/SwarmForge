# 00-vibe-architect.md
# Universal Agent Methodology
# Last modified: April 2026

---

## Plan Mode — Non-Negotiable

Always enter Plan Mode before touching any file.

- Produce an explicit plan listing: files to read, files to modify, files to create, and the why for each action.
- Do not switch to Act Mode until the user has explicitly approved the plan.
- If the request is ambiguous, ask one targeted clarifying question before planning. Do not plan under ambiguity.

---

## Intent Before Code

Understand the *why* before writing anything.

- If the task is ambiguous, ask. Do not infer silently.
- One clarifying question maximum. Ask only what unblocks the plan.

---

## Project Tree Is the Structural Source of Truth

Before making any decision involving folder layout or file placement:

1. Read `docs/Project_Structure/repository_tree.md` — it is auto-generated on every commit and reflects the live state of the repo.
2. Never reorganize folder structure based on assumptions. The tree file is authoritative.
3. If the tree file is missing, list the repo root with `list_code_definition_names` before proceeding.

---

## Full-File Read Before Any Edit

Before modifying an existing file:

1. Read the entire file. No partial reads.
2. Map imports, class hierarchies, and function signatures that could be affected.
3. Identify downstream dependents (files that import this module).

---

## Commit Standard — Conventional Commits

Every completed task produces a commit in this format:

```
type(scope): short imperative description

Why: one sentence — motivation, not implementation.
```

Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

Example:
```
feat(auth): add token refresh on 401 response

Why: prevents session expiry silently breaking API calls in long-running tasks.
```

Commits describing *what* without explaining *why* are not acceptable.

---

## Logging — No print()

`print()` is forbidden in production code. Use the language's native logging facility at the appropriate level.

This includes FastAPI lifecycle hooks, `__init__` methods, and startup events — 
not only business logic functions.

In Python:
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("trace")    # dev only
logger.info("event")     # normal ops
logger.warning("odd")    # degraded but alive
logger.error("failure")  # needs attention
```

---

## Mandatory Architecture Patterns

### Repository Pattern
Data access lives in repository classes. Business logic never touches the database directly.

### Service Layer
Business logic lives in service classes. Services depend on abstractions, not concrete implementations.

### Dependency Injection
Never instantiate dependencies inside a class. Receive all collaborators via constructor. This applies in every language.

### Abstract Classes as Contracts
Every cross-layer boundary is an abstract class or interface. Concrete implementations are always swappable.

### Composition Over Inheritance
Prefer injecting behavior through collaborators. Inherit only when the subclass genuinely *is a* specialization.

---

## AI Backend — OpenAI-Compatible Interface Only

Every call to an AI model — cloud or local — goes through the standard OpenAI-compatible endpoint (`/v1/chat/completions`).

Never call provider SDKs directly in business logic. This makes backend swaps require zero orchestration changes.

---

## Secrets

API keys and credentials live only in `.env` files that are gitignored before the first commit.
Always read via environment variables (e.g., `os.getenv()`). Never hardcode. Never commit, even to private repos.
Commit a `.env.example` with placeholder values as documentation.

---

## Project-Specific Skills — Placement Rules

Do NOT create `.cline/SKILL.md` directly in the `.cline/` root.
Project skills follow this structure only:
.cline/skills/[skill-name]/SKILL.md

Do NOT duplicate content already present in global rules into project-level files.
If a standard is already covered globally, it does not need a local copy.

Global rules location: `~/Documents/Cline/Rules/`
Project skills location: `.cline/skills/[skill-name]/SKILL.md`

---

## Post-Write Validation

After creating any source file, verify it before marking the task complete:
1. Run the linter for the current project's language.
2. Run the language-appropriate import/compile check to verify the module loads without errors.
3. Scan for duplicate function or class definitions.  Duplicate definitions are silent bugs — the second silently overwrites the first.

Zero errors required before proceeding to the next file.

---

## Makefile — Runtime Invocation

Never use `source venv/bin/activate` in Makefile recipes — it does not persist 
across recipe lines on any OS and fails on Windows entirely.
Always invoke the runtime directly:

```makefile
test:
    uv run pytest tests/ -v --tb=short
```