```text
SwarmForge/
├── .agents/
│   ├── .skill-lock.json
│   └── skills/
│       ├── caveman/
│       │   └── SKILL.md
│       ├── caveman-commit/
│       │   └── SKILL.md
│       ├── caveman-compress/
│       │   ├── README.md
│       │   ├── scripts/
│       │   │   ├── __init__.py
│       │   │   ├── __main__.py
│       │   │   ├── benchmark.py
│       │   │   ├── cli.py
│       │   │   ├── compress.py
│       │   │   ├── detect.py
│       │   │   └── validate.py
│       │   ├── SECURITY.md
│       │   └── SKILL.md
│       ├── caveman-review/
│       │   └── SKILL.md
│       ├── class-coder/
│       │   └── SKILL.md
│       ├── contract-architect/
│       │   └── SKILL.md
│       ├── find-skills/
│       │   └── SKILL.md
│       └── reviewer/
│           └── SKILL.md
├── .cline/
├── .clinerules/
│   ├── 00-vibe-architect.md
│   ├── 01-token-economy.md
│   ├── 02-universal-code-standards.md
│   ├── 03-python-fastapi-standards.md
│   ├── 04-contract-architect.md
│   ├── 04-doc-and-test-pipeline.md
│   ├── 05-class-coder.md
│   └── caveman.md
├── .gitignore
├── .opencode/
│   ├── agents/
│   │   ├── caveman.md
│   │   ├── class-coder.md
│   │   ├── contract-architect.md
│   │   └── reviewer.md
│   └── commands/
│       ├── lint.md
│       └── run-test.md
├── .pytest_cache/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v/
│       └── cache/
│           ├── lastfailed
│           ├── nodeids
│           └── stepwise
├── .ruff_cache/
│   ├── .gitignore
│   ├── 0.15.11/
│   │   └── 8051445607315972243
│   └── CACHEDIR.TAG
├── AGENTS.md
├── configs/
│   └── agents/
│       ├── architect.yaml
│       ├── coder.yaml
│       └── reviewer.yaml
├── CREDITS.md
├── data/
│   └── conversations/
│       ├── 2c689662-d816-46af-b988-86a33871f290.json
│       ├── 33a46c90-a4fd-4585-a0d1-60ee8266f9fe.json
│       ├── 393d8781-3b33-43c9-9855-5466c92c3a26.json
│       └── d38f6026-539b-492f-bdc4-b200150945ca.json
├── docs/
│   ├── architecture/
│   │   ├── orchestrator-hierarchy.md
│   │   ├── phase-1-stack.md
│   │   ├── phase-2-stack.md
│   │   └── web-automation-architecture.md
│   ├── contracts/
│   │   ├── AbstractAgent.contract.md
│   │   ├── AgentRegistry.contract.md
│   │   ├── AgentSelector.contract.md
│   │   ├── ClineAgent.contract.md
│   │   ├── ResultAggregator.contract.md
│   │   ├── StubAgents.contract.md
│   │   ├── SwarmOrchestrator.contract.md
│   │   └── TaskDecomposer.contract.md
│   ├── learning/
│   │   ├── anthropic-skilljar-catalog.md
│   │   └── README.md
│   ├── plans/
│   │   └── orchestrator-plan.md
│   ├── Project_Brief.md
│   ├── project_structure/
│   │   └── repository_tree.md
│   ├── research/
│   │   └── mas-landscape-analysis.md
│   ├── reviews/
│   │   └── SwarmOrchestrator.review.md
│   ├── SF-ONBOARD-001.md
│   ├── snippets/
│   │   ├── abstractagent_snippet.md
│   │   └── subtask_snippet.md
│   ├── standards/
│   │   └── a2a-protocol/
│   │       ├── a2a-protocol.md
│   │       ├── A2A_Protocol.mp4
│   │       └── A2A_Protocol.pdf
│   └── testing/
│       └── tier-decisions.md
├── legal/
│   └── apache-2.0.txt
├── Makefile
├── memory-bank/
│   ├── activeContext.md
│   ├── decisionLog.md
│   ├── productContext.md
│   └── progress.md
├── opencode.json
├── pyproject.toml
├── README.md
├── setup_browser_profile.py
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── cline_agent.py
│   │   ├── config.py
│   │   └── stubs.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── ai_structure.md
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── ai_model.py
│   │   ├── image/
│   │   └── text/
│   │       ├── __init__.py
│   │       ├── api/
│   │       ├── text_model.py
│   │       └── web/
│   │           ├── __init__.py
│   │           ├── conversation_logger.py
│   │           ├── providers/
│   │           │   ├── __init__.py
│   │           │   ├── chatgpt/
│   │           │   │   └── chatgpt_web_model.py
│   │           │   └── gemini/
│   │           │       ├── __init__.py
│   │           │       └── gemini_web_model.py
│   │           └── web_text_model.py
│   └── orchestrator/
│       ├── __init__.py
│       ├── aggregator.py
│       ├── decomposer.py
│       ├── factory.py
│       ├── models.py
│       ├── orchestrator.py
│       ├── registry.py
│       └── selector.py
├── test_ai_automation.py
├── tests/
│   ├── agents/
│   │   └── test_cline_agent.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_swarm_integration.py
│   └── orchestrator/
│       ├── test_aggregator.py
│       ├── test_factory.py
│       ├── test_orchestrator.py
│       ├── test_registry.py
│       ├── test_selector.py
│       └── test_web_model.py
├── tools/
│   ├── griffe/
│   │   └── extract_contract_doc.py
│   └── project_tree/
│       ├── generate_tree.py
│       ├── README.md
│       └── setup_hook.py
├── uv.lock
└── web_ai_examples.py
```
