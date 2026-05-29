# ADR-0001 — Mono-Repo Orchestration: Make as the Coarse Graph

- **Status:** Accepted
- **Date:** 2026-05-29
- **Resolves:** OQ-8 / D-8 (see [`GAP_ANALYSIS.md`](../../GAP_ANALYSIS.md), [`TASKS.md`](../../TASKS.md))
- **Deciders:** Project owner

## Context

Zetix is a polyglot mono-repo: Kotlin/Gradle (Android app + SDK), Swift/SPM+Xcode
(iOS app + SDK), Python/FastAPI (server, embedding, eval), a Python/ML model pipeline,
and a Shopify plugin. We need **one command surface** and a way to express
**cross-ecosystem dependencies** (e.g. "the iOS integration test needs the server up
and the model converted") without forcing every language into a single monolithic
build system.

We considered Bazel (hermetic, fine-grained, cross-language) but rejected it as the
primary driver: it demands rewriting each ecosystem's build into Bazel rules,
fighting Gradle and Xcode rather than using them, and a steep maintenance cost for a
small team. Nx/Turborepo are JS-ecosystem-first and a poor fit for a repo with no
significant JS surface.

## Decision

**Use Make as the coarse, cross-ecosystem dependency graph and the single command
surface. Let each native tool be the fine-grained, incremental, cached builder inside
its own world. Add a few small ingredients to fill the Bazel-shaped gaps.**

Concretely:

1. **Make is coarse, not fine.** Make does **not** track individual Kotlin/Swift/Python
   source files — Gradle, Xcode/SPM, and the Python toolchain already do that better,
   with their own incremental caches. Make tracks **module-level and cross-module**
   relationships only: "server is up," "model is converted," "contracts are generated,"
   "this surface's tests can now run."

2. **One command surface.** Every common action is a `make` target run from the repo
   root: `make build`, `make test`, `make lint`, `make fmt`, plus per-surface targets
   (`make server`, `make android`, `make ios`, `make models`, …). Each target delegates
   to the native tool in that module (`./gradlew`, `xcodebuild`/`swift build`,
   `uv`/`pytest`, etc.). Contributors and CI learn one interface.

3. **Native tools own incrementality and caching.** Make targets that delegate to a
   native builder are typically `.PHONY` — we trust Gradle/Xcode/pytest to decide what
   is actually stale. Make does not second-guess them at file granularity.

4. **Small extra ingredients fill the Bazel-shaped gaps** (cross-language graph edges
   and "is this side-effect done yet" state):
   - **Stamp / marker files** under `.make/` represent outputs that aren't a single
     tracked file — e.g. `.make/model-converted.stamp`, `.make/contracts.stamp`. A
     surface that needs the model declares the stamp as a prerequisite, so Make builds
     the cross-language dependency exactly once and in the right order.
   - **Order-only prerequisites** express "must happen first / must be running" without
     coupling to file timestamps (e.g. an integration test depending on a
     `server-up` target).
   - **A `.make/` artifacts dir** (git-ignored) holds stamps and bridge artifacts so
     the graph state is inspectable and `make clean` can reset it.

### The canonical example

```
ios-integration-test  ──needs──▶  server-up
                       ──needs──▶  .make/model-converted.stamp (Core ML)
```

Make knows the iOS integration test requires the server running and the model
converted; it brings those up in order. It does **not** know (or care) which Swift
files changed — Xcode handles that.

## Consequences

**Positive**
- One obvious entry point for humans, agents, and CI; low onboarding cost.
- Each ecosystem keeps its best-in-class incremental builder and cache.
- Cross-language edges are explicit and centralised in the root `Makefile`.
- No build-system rewrite; Make is ubiquitous and dependency-light.

**Negative / trade-offs**
- Make does not give Bazel's hermeticity or fully-cached cross-language rebuilds;
  the stamp-file approach is a pragmatic approximation, not airtight.
- Stamp invalidation is manual/coarse — when in doubt, `make clean` resets `.make/`.
- Contributors must resist pushing fine-grained file tracking into Make; that belongs
  in the native tools.

## Implementation

- Root [`Makefile`](../../Makefile) is the single command surface (EPIC-0.3).
- `.make/` is git-ignored and holds stamps/bridge artifacts.
- As modules are scaffolded (EPIC-0.2), each gets a thin Make target that delegates to
  its native tool; cross-module edges are added to the root `Makefile` as they arise.

## Related

- [`README.md`](../../README.md#repository-layout-mono-repo) — mono-repo layout
- [`TASKS.md`](../../TASKS.md) — EPIC-0 sub-tasks
