# 02-universal-code-standards.md
# Universal Code Standards — All Languages
# Last modified: April 2026

---

## Comments — Informative, Not Descriptive

Comments explain *why*, not *what*. The code explains what.

**Delete before committing:**
```
// increment counter
x += 1;
```

**Acceptable — explains non-obvious intent:**
```
iteration_count += 1  // guard: unbounded agent loops fail silently without this cap
```

Comments that describe what the next line does are noise. Remove them.

---

## Docstrings / Documentation Comments

Every public class and every public method requires a documentation comment.
Format: Google-style or the language-native equivalent (JSDoc, Javadoc, Rustdoc).

Minimum required fields:
- One-line summary (what it does, not how)
- `@param` / `@arg` for every non-obvious parameter
- `@return` / `@returns` if the return value is non-trivial
- `@throws` / `@raise` / `@exception` for every documented error path

Private and protected members need a docstring only when the logic is non-obvious.

---

## Access Modifiers — Three Levels, Always Explicit

Every method and field must declare its visibility. No implicit public.

| Level | Convention (Python) | Convention (JS/TS) | Meaning |
|---|---|---|---|
| Public | no prefix | `public` or no prefix | External contract — keep minimal |
| Protected | `_method` | `protected` | Usable in subclasses only |
| Private | `__method` | `#method` or `private` | Internal — name-mangled / inaccessible |

Public methods are the class contract. Minimize them. Every public method you add is a commitment you must maintain.

---

## Single Responsibility Principle (SRP) — Hard Limit

Each class has exactly one reason to change.

**Test:** can you describe the class in one sentence without the word "and"?
If not, split it.

**Line limit as a proxy:** ~150 lines of logic (excluding docstrings and blank lines) is a warning threshold.
Above 150 lines: stop, escalate, propose a split before continuing.

---

## SOLID — Required, Not Optional

All five principles apply to every class in every language:

- **S** Single Responsibility — one class, one job.
- **O** Open/Closed — extend via new classes, don't modify existing ones for new behavior.
- **I** Interface Segregation — small, focused interfaces. One fat interface is worse than three lean ones.
- **D** Dependency Inversion — depend on abstractions. Never instantiate a dependency inside a class.

---

## Abstract Classes / Interfaces as Architectural Contracts

Every cross-layer boundary is a formal contract: an abstract class or interface.

- The service layer depends on the repository interface, never on the concrete DB class.
- The orchestrator depends on the agent interface, never on the concrete API client.
- Swapping any concrete implementation must require zero changes to the layer above it.

Concrete implementation hierarchy (example — adapt to your domain):
```
AbstractAgent (interface / ABC)
  ├── AbstractCloudAgent
  │     ├── ConcreteCloudAgentA
  │     └── ConcreteCloudAgentB
  └── AbstractLocalAgent
        └── ConcreteLocalAgent
```

---

## Composition Over Inheritance

Prefer composing behaviors through injected collaborators.
Inherit only when the subclass genuinely *is a* specialization, not merely *uses* the base.

When in doubt: inject, don't extend.

---

## Error Handling — Explicit, Never Silent

- Never catch an exception and do nothing (empty catch blocks are bugs).
- Always log the error at the appropriate level before re-raising or returning.
- Define custom exception types for domain-specific error conditions.
- Distinguish between recoverable errors (warn + retry) and fatal errors (error + abort).

```
// BAD
try { doSomething() } catch (_) {}

// GOOD
try {
  doSomething()
} catch (err) {
  logger.error("doSomething failed — context: " + context, err)
  throw new DomainError("operation failed", { cause: err })
}
```

---

## Naming Conventions — Universal Rules

- Classes: `PascalCase`
- Functions / methods: `camelCase` (JS/TS/Java) or `snake_case` (Python/Rust)
- Constants: `UPPER_SNAKE_CASE`
- Variables: `camelCase` or `snake_case` (match language convention)
- Booleans: prefix with `is`, `has`, `can`, `should` (e.g., `isReady`, `hasPermission`)
- Do not abbreviate unless the abbreviation is universally understood in your domain (`url`, `id`, `api` are fine; `usr`, `cfg`, `mgr` are not)

---

## No Magic Numbers or Strings

Named constants for every value that has a semantic meaning:

```
// BAD
if (retries > 3) ...

// GOOD
const MAX_AGENT_RETRIES = 3
if (retries > MAX_AGENT_RETRIES) ...
```