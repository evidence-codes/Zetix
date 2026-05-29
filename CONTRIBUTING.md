# Contributing to Zetix

Welcome. This guide is binding for **every contributor — human, Claude session, or
agent.** It exists so the project stays coherent across many sessions.

## 1. Read the source of truth first

Before touching anything, read these in order. They are canonical; never act against them:

1. [`README.md`](./README.md) — overview, mono-repo layout, architecture
2. [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) — live status of every PRD requirement
3. [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) — what exists today vs. the PRD
4. [`TASKS.md`](./TASKS.md) — EPICs and sub-tasks (the executable plan)
5. [`docs/Zetix_PRD_v1.0.docx`](./docs/Zetix_PRD_v1.0.docx) — the PRD
6. [`CLAUDE.md`](./CLAUDE.md) — session operating instructions (auto-loaded by Claude Code)

For local setup, see [`docs/DEVELOPMENT.md`](./docs/DEVELOPMENT.md).

## 2. Status lifecycle

Every task in [`TASKS.md`](./TASKS.md) carries a status. Keep [`TASKS.md`](./TASKS.md)
**and** [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) in sync as you move a task.

| Symbol | Meaning |
| --- | --- |
| 🔴 | Not done |
| 🟡 | In process (actively being worked) |
| 🟢 | Dev-complete — implemented + self-tested, awaiting owner verification |
| ✅ | Verified by the owner personally |

**🔴 → 🟡 → 🟢 → ✅ → commit.**

- Set a task 🟡 when you start it.
- Set it 🟢 when dev-complete, and summarise what you did.
- **Only the project owner promotes 🟢 → ✅.**
- **Commits land only after ✅.** Do not commit 🟢 work on your own.

## 3. How to pick the next task

1. Read [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) and [`TASKS.md`](./TASKS.md).
2. Start at the lowest-numbered EPIC with unfinished sub-tasks, respecting phase
   dependencies (EPIC-0 → EPIC-1 → …). Resolve any blocking decision (EPIC-D) first.
3. Take **one** sub-task. Mark it 🟡 in both docs.
4. Implement + self-test, then mark it 🟢.

## 4. Mono-repo discipline

- **One command surface — Make.** Build, test, lint, and format everything through
  the root [`Makefile`](./Makefile): `make build`, `make test`, `make lint`, `make fmt`.
  Make is the *coarse* cross-ecosystem graph; the native tools (Gradle, Xcode/SPM,
  Python) own file-level incrementality. See
  [ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md).
- **Shared spine.** [`packages/contracts`](./packages/contracts) (API + sync/vector
  format) and [`models/`](./models) are version-locked. A wire-format or schema change
  is **one atomic commit across all consumers**.
- **Privacy invariant.** The raw camera image never leaves the device; only the query
  vector is transmitted on server fallback (NFR-S1/S2). Do not introduce a code path
  that violates this.
- **Cross-module edges live in the root Makefile** (e.g. `ios-integration-test` needs
  the server up and the model converted). Add new edges there, not inside a module.

## 5. Code style & hooks

- Formatting is enforced by config at the repo root:
  [`.editorconfig`](./.editorconfig), [`ruff.toml`](./ruff.toml),
  [`.swiftformat`](./.swiftformat); Kotlin via ktlint (reads `.editorconfig`).
- Install pre-commit once: `pip install pre-commit && pre-commit install`
  ([`.pre-commit-config.yaml`](./.pre-commit-config.yaml)). It runs universal hygiene
  hooks + ruff. Kotlin/Swift formatting runs via `make fmt` and CI (they need platform
  toolchains).
- Before pushing: `make fmt && make lint && make test`.

## 6. Branches, commits, PRs

- Never commit directly to `main`. Branch per task (e.g. `epic-1/search-endpoint`).
- Keep commits scoped to a single ✅-verified task where possible.
- Reference the EPIC/sub-task ID and any FR/NFR IDs in the commit/PR description.
- CI ([`.github/workflows/ci.yml`](./.github/workflows/ci.yml)) runs the Make surface
  across all ecosystems; it must be green before merge.

## 7. Keep the documents truthful

If reality diverges from the docs, update [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) and
the relevant status rather than letting them drift. The documents are the contract.
