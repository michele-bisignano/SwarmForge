# 06-doc-and-test-pipeline.md
# Doc Extraction & Test Pipeline
# Last modified: April 2026

---

## Overview

Two pipelines. Both run **without AI involvement**:

1. **Doc Extraction** — extracts API documentation from source using `griffe`, producing the doc snippets that ClassCoders receive instead of source code.
2. **Test Pipeline** — defines how ClassCoders write parametrized tests and how model-tier decisions are made.

---

## Part 1 — Doc Extraction (griffe)

### Why griffe

`griffe` (MIT) parses Python source statically — no code execution. Produces structured JSON queryable without regex. Alternatives (pdoc, pydoc, sphinx-apidoc) are worse fits: pydoc executes the module; the others produce less machine-readable output.

### Setup — Automatic, Not Manual

griffe is a dev dependency. The agent installs it during project setup:

```bash
uv add --dev griffe
```

Add to `Makefile`:
```makefile
griffe-dump:
    python -m griffe dump src/$(PROJECT_NAME) \
        --output docs/api/$(PROJECT_NAME).json \
        --resolve-aliases

.PHONY: griffe-dump
```

Add to `.pre-commit-config.yaml` (optional but recommended):
```yaml
- repo: local
  hooks:
    - id: griffe-dump
      name: Regenerate griffe API JSON
      entry: make griffe-dump
      language: system
      pass_filenames: false
      always_run: false
      files: '\.py$'
```

Commit `docs/api/[project].json`. Regenerate after every public interface change via `make griffe-dump`.

### Extracting a Doc Snippet for a ClassCoder

```bash
python scripts/extract_contract_doc.py \
    --api-json docs/api/[project].json \
    --class DependencyClass \
    --methods method_a method_b \
    --output docs/snippets/dependencyclass_snippet.md
```

`scripts/extract_contract_doc.py` is a zero-AI utility that lives in the repo:

```python
"""
extract_contract_doc.py — extracts a markdown doc snippet from a griffe JSON dump.
Produces the context slice for ClassCoders. Never touches source files.

Usage:
    python scripts/extract_contract_doc.py \
        --api-json <path> --class <ClassName> \
        --methods <method1> [<method2> ...] \
        --output <output_path>
"""
import argparse
import json
from pathlib import Path


def extract_snippet(
    api_json_path: str,
    class_name: str,
    method_names: list[str],
    output_path: str,
) -> None:
    """Extract a markdown doc snippet for the specified class methods.

    @param api_json_path: Path to the griffe JSON dump.
    @param class_name: Target class name.
    @param method_names: Method names to include.
    @param output_path: Output markdown path.
    @raise KeyError: If the class or method is not found.
    """
    with open(api_json_path) as f:
        api: dict = json.load(f)

    target = _find_class(api.get("members", {}), class_name)
    if target is None:
        raise KeyError(f"Class '{class_name}' not found in {api_json_path}.")

    lines: list[str] = [
        f"# Doc Snippet: {class_name}\n",
        f"**Class:** {target.get('docstring', {}).get('value', 'No docstring.')}\n\n## Methods\n",
    ]
    for name in method_names:
        method = target.get("members", {}).get(name)
        if method is None:
            raise KeyError(f"Method '{class_name}.{name}' not found.")
        doc = method.get("docstring", {}).get("value", "No docstring.")
        params = method.get("parameters", [])
        ret = method.get("returns", {}).get("annotation", "None") if method.get("returns") else "None"
        sig = f"{name}({', '.join(f'{p[\"name\"]}: {p.get(\"annotation\", \"Any\")}' for p in params if p['name'] != 'self')}) -> {ret}"
        lines.append(f"### `{sig}`\n```\n{doc}\n```\n")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def _find_class(members: dict, name: str) -> dict | None:
    for k, node in members.items():
        if k == name and node.get("kind") == "class":
            return node
        if "members" in node:
            result = _find_class(node["members"], name)
            if result is not None:
                return result
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-json", required=True)
    parser.add_argument("--class", dest="class_name", required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    extract_snippet(args.api_json, args.class_name, args.methods, args.output)
    print(f"Snippet → {args.output}")
```

### When to Run

| Event | Action |
|---|---|
| Class skeleton finalized (docstrings done, bodies `...`) | `make griffe-dump` |
| ContractArchitect assigns ClassCoder that depends on class X | `extract_contract_doc.py` for class X |
| Public interface of a class changes | `make griffe-dump` + re-extract affected snippets |

---

## Part 2 — Test Pipeline

### Test-First Toggle

Test-first is a per-project decision, set in the Contract Document:
```
Test-first enabled: YES
```

When YES: ClassCoder writes the full test file before filling method bodies.
When NO: ClassCoder implements first, writes tests after (or the developer writes them manually).

**Recommended:** YES for projects with rate-limit budgets that can absorb the token cost.
NO for rapid prototyping or when tests are written manually.

### Test File Structure

One test file per class. Location: `tests/[package]/test_[module].[ext]`

```python
"""Tests for [ClassName]."""
import pytest
from [package].[module] import [ClassName]


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def instance() -> [ClassName]:
    """Return a canonical valid instance for reuse across tests."""
    return [ClassName](...)


# ─── [method_name] ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("input_a, input_b, expected", [
    (..., ..., ...),   # happy path 1
    (..., ..., ...),   # happy path 2
    (..., ..., ...),   # boundary min
    (..., ..., ...),   # boundary max
])
def test_should_[expected]_when_[condition](input_a, input_b, expected) -> None:
    result = instance.[method](input_a, input_b)
    assert result == expected


@pytest.mark.parametrize("bad_input, exc_type", [
    (None, TypeError),
    (-1,   ValueError),
])
def test_should_raise_when_[condition](bad_input, exc_type) -> None:
    with pytest.raises(exc_type):
        [ClassName](bad_input)
```

### Parametrize Coverage Requirements

Every public method must have test cases covering:

| Case | Required? |
|---|---|
| Happy path — 3+ distinct valid inputs | ✅ |
| Boundary minimum | ✅ |
| Boundary maximum | ✅ |
| None input (nullable params) | ✅ |
| Wrong type | ✅ |
| Out-of-range value (constrained params) | ✅ if applicable |
| Empty collection (collection params) | ✅ if applicable |

### Naming

```
test_should_[expected_behavior]_when_[condition]
```

All lowercase with underscores. No abbreviations.

### Running Tests

```bash
# Single class during implementation
pytest tests/[package]/test_[module].py -v --tb=short

# Full suite before committing
pytest tests/ -v --tb=short

# Async (service layer, endpoints)
pytest tests/ -v --tb=short --asyncio-mode=auto
```

### Model Tier — ContractArchitect Decides

The ClassCoder does not choose its model tier. ContractArchitect sets it in the Contract Document and logs every escalation in `docs/testing/tier-decisions.md`.

Default: cheap model (local quantized or free API tier).
Escalation triggers: logic errors requiring cross-class reasoning, or contract ambiguities that tests reveal.