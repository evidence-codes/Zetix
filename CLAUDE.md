# Zetix — Session Operating Instructions

**Read this first, every session, before doing anything else.** These instructions
bind every Claude session and every spawned agent working in this repository.

## Source-of-Truth Documents

Before acting on any request, read these in order. They are the canonical source of
truth — never assume code or state that contradicts them:

1. [`README.md`](./README.md) — project overview, mono-repo layout, architecture
2. [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) — live status of every PRD requirement
3. [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) — what exists today vs. the PRD target
4. [`TASKS.md`](./TASKS.md) — EPICs and sub-tasks (the executable plan)
5. [`docs/Zetix_PRD_v1.0.docx`](./docs/Zetix_PRD_v1.0.docx) — the upstream PRD

> If any agent or sub-task is spawned, it must also be told to read these documents
> before acting.

## This Is a Mono-Repo

All surfaces live in one repository (`apps/`, `packages/`, `server/`, `models/`,
`plugins/`, `tools/`, `docs/`). Shared contracts (`packages/contracts`) and model
artifacts (`models/`) are the version-locked spine. A wire-format or schema change is
one atomic commit across every consumer. See the layout in
[`README.md`](./README.md#repository-layout-mono-repo).

## How to Work

1. **Break work into EPICs with sub-tasks** ([`TASKS.md`](./TASKS.md)) and take them
   **one at a time**, respecting phase dependencies (EPIC-0 → EPIC-1 → …).
2. **Resolve blocking decisions first** (see EPIC-D / open questions).
3. **Track status with the lifecycle below** — update both [`TASKS.md`](./TASKS.md)
   and [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) as you move a task.

## Status Lifecycle

| Symbol | Meaning |
| --- | --- |
| 🔴 | Not done |
| 🟡 | In process (actively being worked) |
| 🟢 | Dev-complete — implemented + self-tested, awaiting owner verification |
| ✅ | Verified by the owner personally |

**🔴 → 🟡 → 🟢 → ✅ → commit.**

- When you begin a task, set it 🟡.
- When it is dev-complete, set it 🟢 and summarise what you did.
- **Only the project owner promotes 🟢 → ✅** after personal verification.
- **Commits are made only after ✅.** Do not commit dev-complete (🟢) work on your own.

## Keep Documents Truthful

If reality diverges from the documents, update [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md)
and the relevant status rather than letting them drift.
