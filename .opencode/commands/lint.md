---
description: Run ruff linter and formatter check
---

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Report all violations. Fix automatically only if asked.