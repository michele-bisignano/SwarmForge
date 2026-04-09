# SwarmForge — Learning Catalog: Anthropic Skilljar
<!-- Document version: v1.0.0 | Owner: AI Infrastructure TPM | Date: 2026-04-09 -->

## Purpose

This document maps the Anthropic Skilljar course catalog to SwarmForge's technical needs.
It is **not** a complete course list — it is a filtered, prioritized study plan for the founding team.

Courses are evaluated against SwarmForge's architecture, not against Claude-specific tooling.
The goal is to extract transferable knowledge on **multi-agent orchestration, API patterns,
protocol standards, and production distributed systems** — regardless of which LLM backend is used.

> **Policy reminder:** SwarmForge is provider-agnostic. Courses covering Claude Code agent management
> or cloud vendor lock-in (Bedrock, Vertex AI) are excluded by architectural constraint.

---

## Evaluation Criteria

Each course is scored 1–10 on SwarmForge relevance based on:

| Factor | Weight |
|--------|--------|
| Transferability to non-Anthropic backends | High |
| Applicability to multi-agent orchestration | High |
| Relevance to distributed systems architecture | High |
| Protocol or standards coverage | Medium |
| Foundational AI knowledge for hardware planning | Low |

---

## Excluded Courses (With Justification)

The following courses were reviewed and explicitly excluded:

| Course | Reason for Exclusion |
|--------|---------------------|
| Claude 101 | End-user product knowledge. No architectural value. |
| Claude Code 101 | Claude Code agent management. Explicitly out of scope. |
| Claude Code in Action | Claude Code workflow. Explicitly out of scope. |
| Introduction to Claude Cowork | Anthropic product-specific. No transfer value. |
| Introduction to agent skills | Claude Code Skills system. Locked to Claude Code runtime. |
| Introduction to subagents | Claude Code subagent model. Runtime-specific with minimal transfer. |
| Claude with Amazon Bedrock | Vendor lock-in. Violates data sovereignty principle. |
| Claude with Google Cloud's Vertex AI | Vendor lock-in. Violates data sovereignty principle. |
| AI Fluency for educators | Out of domain. No engineering relevance. |
| AI Fluency for students | Out of domain. No engineering relevance. |
| AI Fluency for nonprofits | Out of domain. No engineering relevance. |
| Teaching AI Fluency | Out of domain. No engineering relevance. |

---

## Selected Courses — Full Analysis

---

### 1. AI Capabilities and Limitations
**URL:** https://anthropic.skilljar.com/ai-capabilities-and-limitations
**SwarmForge Relevance Score:** 4 / 10
**Phase Alignment:** Genesis (Pre-Phase 1 — Foundation)

**What it covers:**
An introductory course on how AI models work, their strengths, failure modes,
and general operational boundaries (context windows, hallucination patterns, reasoning limits).

**Why it matters for SwarmForge:**
Before allocating VRAM budgets, designing the Switchboard routing logic, or writing agent
orchestration prompts, the founding team must have a calibrated mental model of what LLMs
can and cannot reliably do. This course prevents over-engineering based on false assumptions
about model capability and informs hardware planning decisions (e.g., context window vs. VRAM
tradeoffs when selecting models for Phase 1).

**What to extract:**
- Model failure modes → informs sandboxing requirements (Section 8.3 of the Project Brief)
- Context window behavior → informs token budget management for the Switchboard
- Hallucination patterns → informs mandatory sandboxed execution design

**What to skip:**
Sections framed around consumer Claude.ai usage. Focus only on model behavior fundamentals.

---

### 2. AI Fluency: Framework & Foundations
**URL:** https://anthropic.skilljar.com/ai-fluency-framework-foundations
**SwarmForge Relevance Score:** 5 / 10
**Phase Alignment:** Genesis (Pre-Phase 1 — Foundation)

**What it covers:**
A framework for working with AI systems effectively, efficiently, ethically, and safely.
Covers prompt design philosophy, human-AI collaboration patterns, and responsible AI integration.

**Why it matters for SwarmForge:**
SwarmForge agents are not static tools — they are collaborative participants in a workflow.
This course builds the mental model needed to design effective human-agent and agent-agent
interaction loops. The prompt design patterns are directly applicable to engineering system
prompts for SwarmForge's agent roles (coder, reviewer, architect).

**What to extract:**
- Prompt design principles → applicable to agent role definition
- Human-in-the-loop patterns → informs agent approval gates in the orchestration layer
- Efficiency frameworks → informs task decomposition strategy for the Swarm layer

**What to skip:**
Ethics sections oriented toward general consumer use. Focus on workflow and efficiency content.

---

### 3. Building with the Claude API
**URL:** https://anthropic.skilljar.com/claude-with-the-anthropic-api
**SwarmForge Relevance Score:** 9 / 10
**Phase Alignment:** Genesis (Phase 1 — Core Technical)

**What it covers:**
The complete spectrum of working with LLMs via REST API: request/response structure,
streaming (Server-Sent Events), tool use (function calling), multi-turn conversation management,
prompt caching, and production API integration patterns.

**Why it matters for SwarmForge:**
This is the highest-priority technical course. Even though SwarmForge is provider-agnostic,
the API patterns covered here — particularly **streaming, tool use, and multi-turn state management**
— are universal across all major LLM providers (Anthropic, OpenAI, Mistral, local Ollama endpoints).
The Switchboard's core routing logic and the agent communication layer will be built on
exactly these primitives.

**What to extract:**
- Streaming via Server-Sent Events (SSE) → directly maps to SwarmForge Risk Mitigation 2 (latency)
- Tool use / function calling → the foundation of agent capability declaration
- Multi-turn conversation management → state handling across distributed agent sessions
- Error handling patterns → informs Switchboard fault tolerance design
- Prompt caching strategies → critical for VRAM-constrained nodes

**What to skip:**
Nothing. This course is fully applicable. Watch in its entirety.

---

### 4. Introduction to Model Context Protocol
**URL:** https://anthropic.skilljar.com/introduction-to-model-context-protocol
**SwarmForge Relevance Score:** 9 / 10
**Phase Alignment:** Genesis / Switchboard (Phase 1–2)

**What it covers:**
Building MCP servers and clients from scratch using Python. Covers the three MCP primitives:
**Tools** (callable functions), **Resources** (readable data), and **Prompts** (reusable templates).
Shows how to connect AI agents to external services using a standardized open protocol.

**Why it matters for SwarmForge:**
MCP is an **open, provider-agnostic standard** — not a Claude-only protocol. It is the correct
architectural layer for SwarmForge's agent-to-tool communication. Every SwarmForge agent that
needs to interact with the filesystem, a database, a Git repository, or a hardware telemetry
API should do so through an MCP-compliant interface. This course is the direct implementation
reference for the SwarmForge tool layer.

**What to extract:**
- MCP server implementation → template for all SwarmForge agent tool integrations
- MCP client implementation → how the Switchboard invokes agent capabilities
- Tools primitive → maps directly to agent capability declaration in SwarmForge
- Resources primitive → how agents expose internal state to the orchestration layer
- Python SDK usage → applicable regardless of backend model

**What to skip:**
Nothing. Watch in full. This protocol is a SwarmForge architectural pillar.

---

### 5. Model Context Protocol: Advanced Topics
**URL:** https://anthropic.skilljar.com/model-context-protocol-advanced-topics
**SwarmForge Relevance Score:** 8 / 10
**Phase Alignment:** Switchboard / Swarm (Phase 2–3)

**What it covers:**
Advanced MCP implementation: **sampling** (model-initiated LLM calls), **notifications**
(server-to-client event push), **file system access**, and **transport mechanisms**
(stdio vs. HTTP/SSE) for production MCP server deployment.

**Why it matters for SwarmForge:**
The standard MCP introduction covers single-node, synchronous interactions. This course
covers the production patterns required for SwarmForge's distributed, real-time, multi-node
environment. Specifically:

- **Notifications** → how nodes push telemetry updates to the Switchboard in real time
- **Sampling** → how agents can delegate sub-tasks to other model instances (critical for Phase 3)
- **Transport mechanisms** → selecting the right transport layer for encrypted inter-node MCP communication
- **File system access** → secure, sandboxed agent access to the codebase

**What to extract:**
- SSE transport → production transport layer for the SwarmForge mesh network
- Sampling → the protocol primitive enabling agent-to-agent task delegation
- Notification patterns → real-time telemetry push from nodes to the Switchboard
- Production deployment patterns → hardening MCP servers for zero-trust environments

**What to skip:**
Nothing. Every topic maps to a Phase 2–3 architectural requirement.

---

## Recommended Watching Order

> Watch courses in this exact sequence. Do not reorder.
> Later courses build directly on concepts introduced earlier.

| Order | Course | Score | Phase | Why This Position |
|-------|--------|-------|-------|-------------------|
| 1 | AI Capabilities and Limitations | 4/10 | Pre-Genesis | Calibrate your mental model before any technical work |
| 2 | AI Fluency: Framework & Foundations | 5/10 | Pre-Genesis | Build the human-AI collaboration mindset before touching APIs |
| 3 | Building with the Claude API | 9/10 | Genesis | Core API primitives: streaming, tool use, multi-turn — the technical foundation |
| 4 | Introduction to Model Context Protocol | 9/10 | Genesis–Switchboard | The open standard for agent-tool communication. Builds on API knowledge |
| 5 | Model Context Protocol: Advanced Topics | 8/10 | Switchboard–Swarm | Production MCP: notifications, sampling, transport. Requires intro MCP first |

**Total estimated time:** ~10–14 hours depending on pace.

**Skippable if already known:**
- Courses 1 and 2 can be skipped if the founding team already has a solid working model of LLM
  capabilities and prompt design. Courses 3–5 are mandatory for all technical contributors.

---

## Course Priority Matrix

```
Priority
  HIGH  │  [3] Building with the Claude API
        │  [4] Introduction to MCP
        │
  MED   │  [5] MCP Advanced Topics
        │
  LOW   │  [2] AI Fluency: Framework
        │  [1] AI Capabilities and Limitations
        └─────────────────────────────────────
          Foundation     Core     Production
                       (Phase 1)  (Phase 2–3)
```

---

## Maintenance

- **Version:** v1.0.0
- **Last updated:** 2026-04-09
- **Owner:** AI Infrastructure TPM
- **Review trigger:** Any new course added to https://anthropic.skilljar.com/ or a new SwarmForge
  phase kickoff
- **Change policy:** Updates require TPM approval before merge. Version must be bumped on every edit.
