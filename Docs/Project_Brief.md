
# PROJECT CHARTER & ARCHITECTURE BRIEF
**Project Codename:** Project *SwarmForge*

**Date:** April 5, 2026

**Authors / Core Founders:** `[Michele Bisignano]`, `[Alessandro Campani]`

**Document Status:** Architectural & Initiation Draft (V2.0 - Proprietary / Commercial Edition)

---

## 1. Vision and Project Goals (The Idea)
The goal of *SwarmForge* is to build a proprietary, enterprise-grade architecture for private and secure distributed AI computing. We are engineering a closed-source, highly scalable ecosystem where a "team of virtual agents" (coders, reviewers, architects) lives natively within the IDE, powered by pooling the computing resources of a decentralized, privately controlled hardware network.

By breaking away from reliance on third-party paid APIs while retaining absolute control over our infrastructure, we are creating a "Private AWS for Artificial Intelligence." This initiative is being meticulously designed from day one with immense commercial potential. The ultimate objective is to forge a robust, highly monetizable product, perfectly positioned for future enterprise licensing, SaaS commercialization, or venture capital investor pitching.

## 2. Project Scope
**In-Scope (What we will do):**
*   Development of a proprietary multi-agent framework integrated directly into code editors (e.g., VS Code, JetBrains).
*   Creation of a "Switchboard" (Gateway / Load Balancer) to dynamically route IDE requests to the most suitable proprietary nodes.
*   Establishment of a secure, encrypted P2P/Mesh virtual network to seamlessly link physically distant machines.
*   Implementation of an agnostic data collection pipeline for the future fine-tuning of models, retaining all data entirely in-house.

**Out-of-Scope (What we will NOT do):**
*   Open-sourcing the core engine, the Gateway, or the agent logic.
*   Public distribution of our architecture designs or source code.
*   Development or pre-training of Foundation Models from scratch (we will leverage existing open-weights models locally to run our proprietary workflows).

## 3. Intellectual Property (IP) & Confidentiality
This project operates under strict stealth and confidentiality protocols. All source code, architecture designs, custom workflows, prompts, and data generated during this project are strictly confidential and remain the **exclusive intellectual property (IP) of the Founders**. 
The entire codebase is classified as **"All Rights Reserved."** To protect our future ability to sell or license the software, any future onboarding of external collaborators, developers, or beta testers will strictly require the execution of legally binding Non-Disclosure Agreements (NDAs) and IP Assignment contracts.

## 4. Absolute Requirements & Architectural Pillars
The system will not be a monolith, but a purely agnostic micro-services ecosystem designed for enterprise deployment. The engineering pillars are:

1.  **Total Scalability & Extensibility:** The architecture must scale horizontally infinitely regarding the number of active agents. The design must mandate standardized interfaces to allow agents to easily communicate with external APIs, databases, or future tools.
2.  **Portability & Nomadic "Remote Access":** The infrastructure must never depend on static IPs. It must be "nomadic": whether a founder is working from their home server, a laptop on a train, or a hotel network, the system must guarantee frictionless access to the remote cluster.
3.  **Extreme "Plug & Play" Modularity:** Component coupling must be incredibly loose. Swapping an AI model, adding a new hardware node to the cluster, or completely revamping a local node must be effortlessly executed.
4.  **Dynamic Orchestration & Auto-balancing:** The gateway will act as a smart traffic controller via telemetry. The system must autonomously evaluate the compute load (GPU/CPU/RAM) of each connected node, dynamically routing jobs to prevent bottlenecks.
5.  **Continual Learning & Absolute Data Portability:** AI must not be static. Training data and historical interaction logs must reside in totally agnostic and physically portable formats. 
6.  **Data Sovereignty & Zero-Trust Security:** Our source code is our most valuable asset. All traffic within the distributed network must be shielded by End-to-End (E2E) encryption. The architecture mandates strict node isolation: if one device is compromised, it must absolutely lack the permissions to infect the rest of the swarm or exfiltrate our proprietary code.
7.  **AI-First Code Standards & Maniacal Documentation:** The codebase must be pristine, modular, and highly maintainable. This code will be read by humans and our proprietary AI Agents—maximum clarity is vital. Every single function, class, or module MUST feature exhaustive, native documentation (e.g., Docstrings, JSDoc). Undocumented code will be automatically rejected. **All source code, variables, functions, comments, commits, and documentation must be strictly written in ENGLISH. No exceptions.**

## 5. Hardware Resources & Physical Constraints (Initial Census)
Before writing a single line of code, we must accurately map the initial cluster's resources. The hardware census will track the following for each node:
*   **VRAM (Video RAM):** The primary limiting factor determining the size and type of hostable AI models.
*   **CPU & System RAM:** Critical for orchestration, databases, and container management.
*   **Storage (I/O & Portability):** Distinguishing between internal NVMe drives (for high-speed inference) and external/removable storage (for datasets).
*   **Network Bottlenecks:** Mapping the Upload/Download speeds of each node's home internet connection to calculate our maximum latency budget.

## 6. Team Organization
The organizational structure is modular, designed to smoothly onboard vetted members under NDA.

*   **`[Name 1]` - Temporary Role: Lead Network & Infrastructure Architect.**
    *   *Focus:* P2P Network, Gateway, Orchestration, hardware telemetry, cryptography, and node security.
*   **`[Name 2]` - Temporary Role: Lead AI Agents & Integration.**
    *   *Focus:* Multi-agent logic, vibe coding workflows, IDE integration, and data pipelines for fine-tuning.

## 7. Macro-Phases Roadmap (High-Level)

*   **Phase 1: "Single-Node Genesis" (Local Proof of Concept)**
    *   Setup of a local vibe coding environment. Validation of the integration between the IDE and a local model.
    *   *Success Metrics (KPIs):*
        *   Time to First Token (TTFT) under 1.5 seconds for local requests.
        *   100% success rate in autonomously executing 5 basic IDE commands.

*   **Phase 2: "The Switchboard" (The Gateway & Network)**
    *   Establishment of the encrypted virtual network and implementation of the proprietary Gateway/Load Balancer.
    *   *Success Metrics (KPIs):*
        *   Inter-node network latency overhead maintained below 50-80 milliseconds.
        *   The Gateway successfully routes 100% of requests to the correct remote node, completely masking real IPs.

*   **Phase 3: "The Swarm" (Dynamic Multi-Agent Orchestration)**
    *   Transition to a "Team of Agents" and activation of real-time hardware load balancing.
    *   *Success Metrics (KPIs):*
        *   The Load Balancer successfully diverts requests away from any node exceeding 90% VRAM usage, ensuring zero Out-Of-Memory (OOM) crashes.
        *   Autonomous resolution of a complex ticket (modifying at least 3 linked files) via the collaboration of two agents on two different physical nodes.

*   **Phase 4: "The Forge" (Continual Learning & Fine-tuning)**
    *   Standardization of long-term memory onto portable databases and execution of the first fine-tuning run.
    *   *Success Metrics (KPIs):*
        *   Automated extraction and normalization of at least 5,000 clean interaction logs.
        *   Successful completion of a fine-tuning cycle without triggering catastrophic forgetting.

## 8. Major Risks & Mitigations
1.  **IP Contamination (License Breach):** Accidentally integrating viral open-source code that forces our product to become public. *Mitigation:* Strict manual license audits and automated CI/CD license checkers before any third-party dependency is merged.
2.  **Network Latency:** Transmitting massive amounts of tokens over networks can cause lag. *Mitigation:* Implement streaming flows (Server-Sent Events) to eliminate perceived delay.
3.  **Malicious Code Execution (Sandboxing):** A hallucinating agent might execute destructive commands or attempt data exfiltration. *Mitigation:* Agent tasks must run exclusively within ephemeral, isolated containers (strict sandboxing) with absolutely no root privileges.

## 9. Rules of Engagement
1.  **Strict English & Documentation Policy:** Code, variables, comments, documentation, and commits MUST be in English. Code must be heavily documented using standard language conventions.
2.  **Third-Party Integrations & Strict License Auditing:** We will leverage existing third-party tools to avoid reinventing the wheel (e.g., networking proxies, LLM wrappers). However, **before integrating any framework, the team must audit its license.** To protect our proprietary codebase, we heavily favor permissive licenses (MIT, Apache 2.0, BSD). **"Copyleft" or viral licenses (such as GPL or AGPL) are strictly forbidden.**
3.  **Modular Resilience:** If a component cannot be shut down, replaced, and restarted in under one hour without breaking the global system, it has been engineered poorly.

## 10. Next Steps (Immediate Action Items)
Following the approval of this document, the team commits to executing the following actions within the next 7 days:

1.  **Kick-off Meeting:** Schedule a 2-hour architectural sync to unblock Phase 1.
2.  **Hardware Census:** Compile a shared spreadsheet mapping VRAM, CPU, RAM, storage, and bandwidth.
3.  **Secure Workspace Setup:** Initialize a strictly private Git Repository (ensuring no public visibility) and set up the project management Kanban board.
4.  **Pilot Model Selection:** Agree upon a highly efficient, permissively licensed open-weights LLM to run locally for the Phase 1 Proof of Concept.

*Approved by:* `[Michele Bisignano]`, `[Alessandro Campani]`