---
description: Run the full SwarmForge test suite
---

Run all tests and report results:

```bash
uv run pytest tests/ -v --tb=short
```

Show a summary of pass/fail counts. If any tests fail, identify the root cause
and suggest the minimal fix. Do not modify tests unless the contract requires it.