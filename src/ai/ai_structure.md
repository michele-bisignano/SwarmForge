## CLASS HIERARCHY MAP

First — clarifying the inheritance tree before touching folders:

```
AIModel (abstract)
├── ImageModel (abstract)
│   ├── GeminiImageModel
│   ├── OpenAIImageModel
│   └── ...
└── TextModel (abstract)
    ├── GeminiTextModel
    ├── ClaudeTextModel
    ├── DeepSeekTextModel
    └── WebTextModel (abstract)
        ├── GeminiWebModel
        ├── ClaudeWebModel
        ├── AIStudioWebModel
        ├── ChatGPTWebModel
        └── VertexWebModel
```

---

## VERTICAL FOLDER STRUCTURE

"Vertical" means: **each inheritance level lives one directory deeper than its parent.** No flat folders.

```
ai/
├── __init__.py
│
├── core/                                 ← LEVEL 0 — root abstract
│   ├── __init__.py
│   └── ai_model.py
│
├── image/                                ← LEVEL 1 — image branch
│   ├── __init__.py
│   ├── image_model.py                    ← abstract
│   │
│   └── providers/                        ← LEVEL 2 — concrete image models
│       ├── __init__.py
│       ├── gemini/
│       │   ├── __init__.py
│       │   └── gemini_image_model.py
│       └── openai/
│           ├── __init__.py
│           └── openai_image_model.py
│
└── text/                                 ← LEVEL 1 — text branch
    ├── __init__.py
    ├── text_model.py                     ← abstract
    │
    ├── api/                              ← LEVEL 2 — API-based concrete models
    │   ├── __init__.py
    │   ├── gemini/
    │   │   ├── __init__.py
    │   │   └── gemini_text_model.py
    │   ├── claude/
    │   │   ├── __init__.py
    │   │   └── claude_text_model.py
    │   └── deepseek/
    │       ├── __init__.py
    │       └── deepseek_text_model.py
    │
    └── web/                              ← LEVEL 2 — web branch
        ├── __init__.py
        ├── web_text_model.py             ← abstract
        │
        └── providers/                    ← LEVEL 3 — concrete web models
            ├── __init__.py
            ├── gemini/
            │   ├── __init__.py
            │   └── gemini_web_model.py
            ├── claude/
            │   ├── __init__.py
            │   └── claude_web_model.py
            ├── ai_studio/
            │   ├── __init__.py
            │   └── ai_studio_web_model.py
            ├── chatgpt/
            │   ├── __init__.py
            │   └── chatgpt_web_model.py
            └── vertex/
                ├── __init__.py
                └── vertex_web_model.py
```

---

## DESIGN RULES APPLIED

| Rule | Decision |
|------|----------|
| One class per file | Enforced — no bundling |
| Folder = inheritance level | `ai_model.py` → `text_model.py` → `web_text_model.py` → `gemini_web_model.py` |
| Provider isolation | Each provider in its own subfolder — swappable independently |
| Abstract classes at folder root | `text_model.py` sits at `text/`, not inside `api/` or `web/` |
| `__init__.py` everywhere | Required for clean imports and package resolution |

---

## KEY DECISION PENDING

`WebTextModel` needs a defined responsibility before you implement it. Two options — pick one:

| Option | What WebTextModel manages |
|--------|--------------------------|
| **A — Browser automation** | Selenium/Playwright sessions against web UIs (ChatGPT, Claude.ai, etc.) |
| **B — Session state abstraction** | Stateful multi-turn conversations that persist browser cookies/auth |

<<<<<<< HEAD
This changes what abstract methods `WebTextModel` must declare. Confirm direction before implementation starts.



for test: uv run pytest tests/orchestrator/test_web_model.py -s
results in [root]/[data]/*.json
=======
This changes what abstract methods `WebTextModel` must declare. Confirm direction before implementation starts.
>>>>>>> 032da50fe25cadf3a963696b1e8f883e078bf4d0
