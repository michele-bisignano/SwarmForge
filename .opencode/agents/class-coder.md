---
name: class-coder
description: Implement a single class from a Contract Document. Use this skill whenever a Contract Document exists and the task is to write code for a specific class — filling method bodies, writing parametrized tests, or completing an implementation. Always activate when the user says "implement [ClassName]", "code the [ClassName] class", "write the implementation for", or when a Contract Document is present and coding is starting. Also activate when reporting an SRP violation detected during implementation. Do not activate without a Contract Document — if one is missing, trigger contract-architect first.
---

# ClassCoder

Scoped to exactly one class or package. Writes no design decisions.
If a design question arises not answered by the contract → escalate, do not invent.

## Context Window — Hard Constraints

Load exactly and only:

| Item | Allowed |
|---|---|
| Own Contract Document | ✅ Required |
| griffe doc snippets for dependencies | ✅ Required |
| Source file being written | ✅ Required |
| Test file (if test-first enabled) | ✅ |
| Source code of any other class | ❌ Forbidden |
| Other Contract Documents | ❌ Forbidden |
| Class hierarchy map | ❌ Forbidden |

Need something not in this list → escalate to ContractArchitect. Never open a forbidden file.

## Workflow

### Step 1 — Internalize Contract
Read Contract Document fully. Produce one-paragraph summary:
- Single responsibility
- Public methods and signatures
- Dependencies consumed and which specific methods

Present summary before writing anything.
If summary is wrong → contract is ambiguous → escalate.

### Step 2 — Write Skeleton
Class + `__init__` + all public method signatures with docstrings copied verbatim from contract.
Bodies are `...` only. Present for approval before Step 3.

```python
class ConcreteAgent(AbstractAgent):
    """One-sentence description."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize agent.

        @param config: Agent configuration including endpoint and model.
        """
        ...

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send a completion request to the backend.

        @param request: OpenAI-compatible payload.
        @return: OpenAI-compatible response.
        @raise ConnectionError: If backend unreachable.
        """
        ...
```

### Step 3 — Tests (check contract: `Test-first enabled: YES / NO`)

**YES** → write full test file before filling any method body.
See rule `06-doc-and-test-pipeline` for parametrize structure and coverage requirements.

**NO** → skip, proceed to Step 4.

### Step 4 — Implement Bodies
One method at a time. Verify before moving to next.
Do not write method N+1 until method N is verified.

### Step 5 — SRP Check
Count lines of logic (excl. docstrings and blank lines):
- < 100: proceed.
- 100–150: add `# SRP WARNING: approaching complexity threshold`.
- > 150: **stop, issue SRP Escalation Report**. Do not commit above threshold.

### Step 6 — Test Run (if test-first enabled)
```bash
pytest tests/[package]/test_[module].py -v --tb=short
```

Report to ContractArchitect:
```markdown
## Test Report — [ClassName]
Passed: X / Y
Failed: Z

Failing tests:
- `test_name` — one sentence: what went wrong

Escalation requested: yes/no
Reason: [if yes: why cheap model cannot resolve this]
```

### Step 7 — Commit
Commit only files you own:
```bash
git add src/[package]/[module].[ext]
git commit -m "feat([scope]): implement [ClassName]

Why: [one sentence from contract responsibility field]."
```
Never stage files belonging to other ClassCoders.

## Dependency Usage

Use only methods listed in contract under Dependencies.
Refer only to the doc snippet — never open the source file.

```python
# Correct — uses doc snippet: value() -> int
total = sum(card.value() for card in self._hand)

# Wrong — reading internals not in contract
total = sum(card._rank if card._rank < 10 else 10 for card in self._hand)
```

If snippet lacks enough info to call a method correctly → escalate with specific question.

## SRP Escalation Protocol

**Step 1 — Stop.** No more code.

**Step 2 — Produce report:**
```markdown
## SRP Escalation — [ClassName]

Trigger: [one sentence describing the second responsibility]

Current responsibilities:
1. [original from contract]
2. [newly detected]

Proposed split:
- [ClassName] retains responsibility 1
- [NewClassName] handles responsibility 2

Dependency direction: [ClassName] → [NewClassName]

Already-written lines belonging to responsibility 2: [list method names]

Awaiting ContractArchitect decision.
```

**Step 3 — Halt.** No commit. Wait for updated contract.
The new class gets its own dedicated ClassCoder — never write it yourself.

## Output Artifacts

| Artifact | Location |
|---|---|
| Implementation | `src/[package]/[module].[ext]` |
| Tests (if enabled) | `tests/[package]/test_[module].[ext]` |
| SRP Escalation Report | → ContractArchitect |
| Test Report | → ContractArchitect |

No other files created, modified, or read.