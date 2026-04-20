> ⚠️ **STRICTLY CONFIDENTIAL & PROPRIETARY**
> 
> This repository and all its contents are strictly closed-source and confidential. All code, architecture designs, workflows, and data herein are the exclusive intellectual property of the Founders. **All Rights Reserved.** Unauthorized access, distribution, copying, or public disclosure of this repository is strictly prohibited.

# SwarmForge

**Our private AWS for Artificial Intelligence: a distributed, portable cluster delivering a full team of AI agents right into your IDE, completely free of charge.**

---

## 🚀 Quick Start

1. **Prerequisites**:
   - Ensure [uv](https://github.com/astral-sh/uv) is installed.
   - Python 3.10+ is required.

2. **Setup**:
   ```bash
   # Install dependencies
   make install

   # Configure environment
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

## 📚 Documentation & Onboarding

**STOP!** Before setting up your local environment, opening a pull request, or writing a single line of code, every team member, auditor, or approved co-founder **MUST** read the foundational project document. 

It contains our architectural pillars, hardware constraints, and the macro-roadmap for the distributed cluster:

👉 **[Project Brief & Architecture Charter](Docs/Project_Brief.md)**

---

## ⚖️ The Golden Rules of Development

To guarantee the long-term maintainability, commercial viability, and security of our proprietary ecosystem, the following rules are unconditionally enforced across the entire codebase:

*   🇬🇧 **Strictly English:** All source code, variable names, function names, inline comments, commit messages, and external documentation must be rigorously written in **English**. No exceptions.
*   📝 **Maniacal Documentation (AI-First Code):** Our code is not only read by humans but actively parsed by our AI agents. Clean, modular code is mandatory. Strict enforcement of native documentation standards (e.g., Python Docstrings, JSDoc/TSDoc) is required for *every single* function, class, and module. Code lacking formal documentation will be automatically rejected.
*   🛡️ **Third-Party Licenses (IP Protection):** Before integrating any framework, tool, or proxy, you must audit its license. To protect our proprietary rights and future commercialization efforts, there is a **strict ban on copyleft/viral licenses** (such as GPL or AGPL). We only allow dependencies that use permissive licenses (e.g., MIT, Apache 2.0, BSD).

## Development

### Repository Structure
The project structure is automatically documented. You can find the detailed tree in:
📂 [Docs/Project_Structure/repository_tree.md](Docs/Project_Structure/repository_tree.md)

### Internal Tools
Documentation for our internal utilities (like the Tree Generator) can be found in the [Tools/](Tools/) directory.
