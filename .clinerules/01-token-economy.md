# 01-token-economy.md
# Token Efficiency & Context Management
# Last modified: April 2026

---

## Output Compression — Caveman Protocol

Respond in caveman mode by default: drop articles, filler words, and pleasantries.
Keep full technical accuracy. Fragments are fine. Code blocks unchanged.

**Default level: Full** (drop articles and hedging, fragments OK)
**Level for inter-agent messages: Ultra** (maximum telegraphic compression)
**Level toward the developer: Full** unless they ask for lite or normal

Do NOT use 文言文 (Wenyan) mode with open-weights models — comprehension is unreliable.
Wenyan is only safe between Claude instances.

Off: "stop caveman" or "normal mode".

```
Pattern: [thing] [action] [reason]. [next step].
Drop: articles, filler (just/really/basically/certainly), pleasantries, hedging.
Never revert after many turns. Never drift back to verbose.
```

---

## Code Reading — Surgical Rules

**Structure before content.** Use `list_code_definition_names` before `read_file`.
Open a full file only to read or modify its implementation body — not just to understand its interface.

**Targeted mentions.** Use `@file:path/to/file.ext` for specific files.
Do NOT use `@folder` on directories with more than 5 files without explicit justification.

**Search before browse.** Use `search_files` with a precise regex to locate symbols before opening files.

**No redundant reads.** Never read the same file twice in the same session unless it changed since the first read.

---

## Output Rules

**No filler openers.** Start immediately with plan, code, or answer.
Never open with: "Sure!", "Certainly!", "Great question!", "Happy to help!", or any variant.

**Diff-first.** When modifying an existing file, show only the changed block or unified diff.
Show the full file only when: (a) the file is new, or (b) >50% of lines changed.

**Decisions = bullet points.** Max 3–4 bullets per architectural explanation. No narrative paragraphs.

**Comments explain why, not what.**
```
// BAD: increment counter
// GOOD: guard against unbounded retry loops (max 3 cycles)
```

---

## Context Budget

**10-file threshold.** If a task requires more than 10 files simultaneously, stop.
Propose a decomposition into sub-tasks before starting. Do not proceed with an oversized context.

**Pre-task estimate.** Before starting any multi-file task, state the estimated file count.
If >8 files, warn the user and propose a scoped approach.

**No redundant reloads.** At the start of each new task in an active session, note which files are already in context. Do not re-read them.

**Incremental commits.** Commit after each logical unit of work. Do not accumulate changes across many files and commit at the end.