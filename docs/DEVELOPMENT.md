# Zetix — Local Development

How to set up and drive the Zetix mono-repo locally. Read
[`CONTRIBUTING.md`](../CONTRIBUTING.md) first for the working agreement and status
lifecycle.

> **Current state:** the mono-repo layout is scaffolded and the **Make command
> surface works today**, but the native builders are filled in per phase. Module
> targets currently print `not implemented yet (EPIC-N)` until that phase lands.

## Prerequisites

You only need the toolchain for the surface(s) you're working on.

| Surface | Toolchain | Notes |
| --- | --- | --- |
| Everything | `make`, `git` | Make is the single command surface |
| Server / models / eval (Phase 1) | Python 3.11+, Docker + Docker Compose | FastAPI, OpenCLIP, ChromaDB, PostgreSQL |
| Android (Phase 2–3) | JDK 17, Android SDK (API 26+), Android Studio | Gradle wrapper ships with the module |
| iOS (Phase 4) | macOS, Xcode (iOS 15+ SDK), Swift 5.9+ | AVFoundation, Core ML |
| Hooks/format | `pre-commit` (`pip install pre-commit`) | ruff for Python; ktlint/SwiftFormat via `make fmt` |

## First-time setup

```bash
git clone <repo-url> zetix && cd zetix

# Install git hooks (universal hygiene + ruff)
pip install pre-commit && pre-commit install

# Cross-surface bootstrap (delegates to each module's `bootstrap`)
make bootstrap
```

## The command surface

Everything runs from the repo root via `make` (see
[ADR-0001](./adr/0001-mono-repo-orchestration-make.md)):

```bash
make help        # list every target
make build       # build every surface (placeholders until each phase lands)
make test        # run all suites
make lint        # lint every surface
make fmt         # auto-format every surface
make clean       # reset .make/ stamps + delegate clean
```

Per-surface targets: `make server-*`, `make android-*`, `make ios-*`, `make sdk-*`,
plus `make contracts`, `make models`, `make eval`.

## Running the server (Phase 1)

```bash
make server-up     # start FastAPI + deps via Docker Compose (background)
make server-test
make server-down
```

The server is Docker-deployable on 2-vCPU / 4 GB RAM minimum (NFR-C3).

## Running the apps

```bash
# Android (Phase 2+): build depends on the converted model + shared contracts,
# which Make brings up automatically.
make android-build         # or open apps/android in Android Studio (API 26+)

# iOS (Phase 4+):
make ios-build             # or open apps/ios in Xcode (iOS 15+)

# Cross-ecosystem integration test — Make brings the server up and converts the
# model first, then runs the iOS integration suite:
make ios-integration-test
```

## Cross-tool dependencies (the `.make/` stamps)

Outputs that aren't a single tracked file are represented by stamp files under
`.make/` (git-ignored): `model-converted.stamp`, `contracts.stamp`. Surfaces that
depend on them declare the stamp as a prerequisite, so Make builds each cross-language
dependency once and in the right order. If a cross-tool build seems stale, reset with:

```bash
make clean     # removes .make/ and delegates clean to each module
```

## Before you push

```bash
make fmt && make lint && make test
```

CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) runs the same Make
targets across Python / Kotlin / Swift runners and must be green before merge.
