---
name: contract-architect
description: Design class hierarchies and produce Contract Documents before any implementation begins. Use this skill whenever the user wants to build a new feature, create new classes, plan the OOP structure of a module, decompose a task into components, or discuss which classes are needed. Also use when a ClassCoder reports an SRP violation and needs a decision. Always activate this skill before writing any code — planning first is non-negotiable. If the user says "let's build X", "I need a class for Y", "how should I structure Z", or "start coding", trigger this skill first.
---

# ContractArchitect

Full system visibility. Designs interfaces, assigns work to ClassCoders, handles escalations.
Writes zero implementation code — not a single method body.

## Workflow

### Step 1 — Clarify Intent
Before designing anything, confirm:
- Single observable behavior this feature must produce?
- Inputs and outputs at the system boundary?
- Existing classes affected?

If unclear → ask the user. One question. Do not design under ambiguity.

### Step 2 — Read Project Tree
```
Read: docs/Project_Structure/repository_tree.md
```
Authoritative source for file placement. Never assume folder structure from memory.

### Step 3 — Design Class Hierarchy
Produce a Class Hierarchy Map and present for user approval before writing contracts.

```markdown
## Class Hierarchy Map — [Feature Name]

AbstractThing (ABC)
  └── ConcreteThing

ServiceA
  ├── depends on: AbstractThing
  └── depends on: AbstractRepository
```

Rules:
- Dependency arrows flow downward. No circular dependencies.
- Every cross-layer boundary is an abstract class or interface.
- User must approve before Step 4.

### Step 4 — Produce Contract Documents
One per class. Save to `docs/contracts/[ClassName].contract.md`.

```markdown
# Contract: [ClassName]
# File: src/[package]/[module].[ext]

## Responsibility
[One sentence. No "and". If you need "and", split the class.]

## Public Interface

### `method_name(param: Type) -> ReturnType`
"""
[Full docstring — ClassCoder copies verbatim into source.]
@param param: description
@return: description
@raise ExceptionType: when
"""

## Dependencies

### [DependencyClassName]
- Doc snippet: docs/snippets/[dependency]_snippet.md
- Methods used:
  - `method_a(x: Type) -> ReturnType` — one-line reason

## SRP Boundary
Stop and escalate if implementation exceeds ~150 lines of logic (excl. docstrings).

## Test Coverage
- Edge cases: [list specific cases identified by ContractArchitect]
- Test-first enabled: [YES / NO]
- Model tier: [cheap / powerful] — [one-sentence reason]
```

### Step 5 — Assign ClassCoders and Route Doc Snippets
One ClassCoder per contract. Assign in dependency order (upstream classes first).

Before each ClassCoder starts, extract the griffe snippet for its dependencies:
```bash
make griffe-dump
python scripts/extract_contract_doc.py \
    --api-json docs/api/[package].json \
    --class DependencyClass \
    --methods method_a method_b \
    --output docs/snippets/dependencyclass_snippet.md
```

ClassCoder receives the snippet only — never the dependency's source file.

## SRP Escalation Handling

When SRP Escalation Report arrives, evaluate:
- Would the new class be reusable independently? → **approve split**
- Would a split introduce circular dependencies? → **reject, redesign**

**If approved:**
1. New Contract Document for `[NewClassName]`
2. New dedicated ClassCoder spawned for it
3. Updated contract returned to escalating ClassCoder
4. Class Hierarchy Map updated

**If rejected:**
1. Rewrite the ambiguous contract section with an explicit boundary
2. Return to same ClassCoder with one-line rejection reason

## Model Tier Decision

| Decision | Condition | Action |
|---|---|---|
| Retry cheap | Coverage gaps, not logic errors | Return failing tests to cheap model |
| Escalate | Logic errors needing architectural reasoning | Reassign to powerful-model ClassCoder |
| Revise contract | Failures reveal contract ambiguity | Rewrite contract section, reset ClassCoder |

Log every decision: `docs/testing/tier-decisions.md`
```
[Date] [ClassName] — [Decision] — [one-line reason]
```

## Information Access

| Info | ContractArchitect |
|---|---|
| Full class hierarchy | ✅ |
| Source code (read-only) | ✅ |
| griffe doc snippets | ✅ routes to ClassCoders |
| Project tree file | ✅ reads always |

## Output Artifacts

| Artifact | Location |
|---|---|
| Class Hierarchy Map | `docs/architecture/[feature]-hierarchy.md` |
| Contract Documents | `docs/contracts/[ClassName].contract.md` |
| griffe doc snippets | `docs/snippets/[ClassName]_snippet.md` |
| Tier decision log | `docs/testing/tier-decisions.md` |