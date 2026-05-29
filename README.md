# Zetix

**Visual Product Search — SDK & App**

Zetix is a visual product search engine built for mobile. Users point their phone
camera at any physical product and the app instantly surfaces matching or similar
items from an ecommerce store's catalog — no search terms, no barcodes, no friction.

The defining technical characteristic: **both the image embedding model and the
vector index run entirely on the user's device.** Searches complete in
milliseconds with no server round-trip, no raw image transmission, and full offline
capability for cached catalogs. The server's role is reduced to catalog indexing,
incremental sync, and authoritative fallback — not the query hot path.

The commercial product is a **drop-in SDK and REST integration** that existing
ecommerce stores (Shopify, WooCommerce, or custom platforms) can embed into their
own apps to add visual search without building ML infrastructure themselves.

> **Source of truth.** This README, together with
> [`FEATURE_STATUS.md`](./FEATURE_STATUS.md), [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md),
> [`TASKS.md`](./TASKS.md), and the PRD in [`docs/`](./docs/), is the canonical
> source of truth for this project. **Every session, agent, and contributor must
> read these documents before acting.** See [Working Agreement](#working-agreement).

---

## Table of Contents

- [Vision & Mission](#vision--mission)
- [Repository Layout (Mono-Repo)](#repository-layout-mono-repo)
- [Architecture](#architecture)
- [Phased Roadmap](#phased-roadmap)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Working Agreement](#working-agreement)
- [Status Legend](#status-legend)
- [Document Map](#document-map)

---

## Vision & Mission

- **Vision** — Make "I want that" a complete search query. Eliminate the gap between
  seeing a product in the world and finding it to buy online.
- **Mission** — Ship the most accurate, fastest, and most private on-device visual
  product search engine available to independent ecommerce operators.

### Target Users

| Persona | Description |
| --- | --- |
| **End Consumer** | Mobile shopper who sees a product IRL and wants to find it online immediately |
| **Store Developer** | Technical operator integrating the Zetix SDK into an existing Shopify / WooCommerce / custom app |
| **Store Owner** | Non-technical merchant who installs the Zetix plugin from an app marketplace |
| **Zetix Operator** | Internal team managing catalog ingestion, model updates, and SDK releases |

---

## Repository Layout (Mono-Repo)

**Zetix is a mono-repo.** All platforms, the server, the SDKs, the plugins, and the
shared contracts live in a single repository so that the sync protocol, API schema,
and model artifacts stay version-locked across Android, iOS, and server. A change to
the wire format is a single atomic commit across every consumer.

```
zetix/
├── apps/                      # End-user consumer applications
│   ├── android/               # Native Kotlin app (CameraX, TFLite, local Chroma)
│   └── ios/                   # Native Swift app (AVFoundation, Core ML)
│
├── packages/                  # Distributable libraries (the commercial SDK)
│   ├── sdk-android/           # Android AAR: CameraSearchView + programmatic API
│   ├── sdk-ios/               # iOS Swift Package: SwiftUI View + UIViewController
│   └── contracts/             # Shared API + sync-protocol schemas (single source)
│                              #   — OpenAPI spec, delta-sync format, vector dims
│
├── server/                    # Backend services (Docker-deployable)
│   ├── api/                   # FastAPI: /search, admin catalog push, sync endpoints
│   ├── embedding/             # CLIP/OpenCLIP embedding service (GPU on index path)
│   └── admin-dashboard/       # Catalog upload, index status, search logs UI
│
├── models/                    # ML model pipeline
│   ├── conversion/            # CLIP/MobileNet → TFLite / Core ML / ONNX
│   ├── quantisation/          # INT8 quantisation to hit <25MB target
│   └── eval/                  # Search-quality evaluation harness (Top-3 accuracy)
│
├── plugins/                   # Platform marketplace integrations
│   └── shopify/               # Shopify App Store plugin (no-code storefront inject)
│
├── tools/                     # Shared dev tooling, scripts, CI helpers
│
├── docs/                      # PRD, architecture, integration guides, dev docs site
│   └── Zetix_PRD_v1.0.docx    # The Product Requirements Document
│
├── FEATURE_STATUS.md          # Live status of every PRD requirement
├── GAP_ANALYSIS.md            # PRD-vs-reality gap analysis
├── TASKS.md                   # EPICs and sub-tasks, worked one by one
└── README.md                  # This file
```

> **Mono-repo tooling — Make as the coarse graph** ([ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md)).
> The root [`Makefile`](./Makefile) is the single command surface and the coarse
> cross-ecosystem dependency graph — it tracks module-level edges ("server up", "model
> converted"), **not** individual source files. Each native tool (Gradle, Xcode/SPM,
> the Python toolchain) is the fine-grained, incremental, cached builder inside its own
> world; Make targets delegate to them. Stamp files in `.make/` plus order-only
> prerequisites fill the Bazel-shaped cross-language gaps. `packages/contracts` and
> `models/` are the version-locked spine.

```bash
make help     # list every target (the one command surface)
make build    # build every surface (delegates to each native tool)
make test     # run all suites
make ios-integration-test   # cross-edge: brings up server + converts model first
```

---

## Architecture

### On-Device Path (the query hot path)

1. User opens camera, frames a product.
2. CameraX (Android) / AVFoundation (iOS) captures the frame.
3. Image is resized and normalised to **224×224 RGB** on-device.
4. TFLite / Core ML model generates a **512-dim embedding vector**.
5. Local ChromaDB is queried with cosine similarity.
6. Top-k results return from the local index in **< 300 ms**.
7. Results render in the UI; user taps to open the product page.

If local index confidence is below threshold or the product is not found locally,
steps 4–6 are replaced by sending **only the vector** (never the image) to the
server search API.

### On-Device Stack

| Component | Technology |
| --- | --- |
| Embedding model | CLIP ViT-B/32 or MobileNet-V3 — TFLite (Android) / Core ML (iOS) |
| Local vector store | ChromaDB via JNI (Android) / SQLite-backed store (iOS) |
| Camera pipeline | CameraX (Android) / AVFoundation (iOS) |
| Image preprocessing | Bitmap resize + normalise to 224×224 RGB |
| Sync protocol | HTTP chunked transfer with ETag-based delta diffs |
| Credential storage | Android Keystore / iOS Secure Enclave |

### Server Stack

| Component | Technology |
| --- | --- |
| API layer | FastAPI (Python 3.11+) |
| Embedding service | CLIP via OpenCLIP; GPU-accelerated on indexing path |
| Vector store | ChromaDB (server) or Weaviate for multi-tenant scale |
| Catalog DB | PostgreSQL — product metadata, store configs, sync state |
| Object storage | S3-compatible (product images, index snapshots) |
| API gateway | Kong or Nginx — auth, rate limiting, per-store routing |
| Deployment | Docker Compose (self-host) / Kubernetes (managed cloud) |

---

## Phased Roadmap

| Phase | Scope | Weeks | Milestone Definition of Done |
| --- | --- | --- | --- |
| **Phase 1** | Server pipeline (ingestion, CLIP embeddings, ChromaDB, `POST /search`, admin dashboard) | 1–4 | M1: REST search API returning accurate results on a 10k-product test set |
| **Phase 2** | Native Android app + on-device embedding (query vector on-device, server search) | 5–10 | M2: Camera → server search → results on a physical device |
| **Phase 3** | Local ChromaDB + sync (full + delta sync, server fallback, offline mode) | 11–16 | M3: End-to-end local pipeline; server fallback working; delta sync tested |
| **Phase 4** | iOS port (Swift app, Core ML pipeline, local vector store, parity) | 17–22 | M4: iOS feature-complete; Core ML pipeline benchmarked |
| **Phase 5** | SDK & integration layer (AAR, Swift Package, Shopify plugin, REST API, docs site, sandbox) | 23–32 | M5/M6: SDK in an external store; docs live; Shopify plugin submitted; first 3 paying stores |

Full per-phase scope and the EPIC breakdown live in [`TASKS.md`](./TASKS.md).

---

## Tech Stack

- **Android:** Kotlin, CameraX, TFLite / ONNX Runtime, ChromaDB (JNI)
- **iOS:** Swift, AVFoundation, Core ML, SQLite-backed vector store
- **Server:** Python 3.11+, FastAPI, OpenCLIP, ChromaDB/Weaviate, PostgreSQL, S3-compatible storage
- **Plugins:** Shopify App (API 2024-01+)
- **Infra:** Docker Compose / Kubernetes, Kong/Nginx gateway

### Minimum Platform Targets

| Platform | Minimum |
| --- | --- |
| Android | API 26 (Android 8.0) |
| iOS | iOS 15 |
| Server | Docker-deployable; 2-vCPU / 4 GB RAM minimum |
| Shopify | API 2024-01+ |

---

## Getting Started

> ⚠️ **Status:** the mono-repo **layout is scaffolded** (directories, per-module
> READMEs, and placeholder Makefiles), and the Make command surface works end-to-end.
> The native builders (Gradle/Xcode/Python) are filled in per phase — each module's
> targets currently print a "not implemented yet (EPIC-N)" placeholder. See
> [`TASKS.md`](./TASKS.md) **EPIC-0** for remaining bootstrap items.

```bash
# Clone the mono-repo
git clone <repo-url> zetix && cd zetix

# The single command surface (works today on the scaffold):
make help     # list all targets
make build    # delegates to every module (placeholders until each phase lands)
make test
make bootstrap

# Per-surface, once the native builders are wired in their phase:
make server-up            # Phase 1 — FastAPI via Docker Compose
make android-build        # Phase 2 — Gradle (open apps/android in Android Studio, API 26+)
make ios-build            # Phase 4 — Xcode/SPM (open apps/ios in Xcode, iOS 15+)
```

---

## Working Agreement

**This applies to every human contributor, every Claude session, and every agent.**

1. **Read before you act.** At the start of every session, read this README,
   [`FEATURE_STATUS.md`](./FEATURE_STATUS.md), [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md),
   and [`TASKS.md`](./TASKS.md). These four documents plus the PRD are the source of
   truth. Do not begin work without grounding in them.
2. **Work the EPICs in order.** Every major task is an EPIC with sub-tasks in
   [`TASKS.md`](./TASKS.md). Take them one at a time. Do not jump ahead of phase
   dependencies.
3. **Update status as you go.** When you start a task, mark it 🟡. When it is
   dev-complete, mark it 🟢. Reflect the same status in `FEATURE_STATUS.md`.
4. **Do not self-promote to ✅.** Only the project owner changes 🟢 → ✅ after
   personal verification. **Commits are made only after ✅.**
5. **Keep the documents truthful.** If reality and the documents disagree, update
   [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) and the relevant status — do not silently
   diverge.
6. **Mono-repo discipline.** Shared contracts (`packages/contracts`) and model
   artifacts (`models/`) are the version-locked spine. A wire-format or schema
   change is one atomic commit across all consumers.

---

## Status Legend

| Symbol | Meaning |
| --- | --- |
| 🔴 | **Not done** — not started |
| 🟡 | **In process** — actively being worked on |
| 🟢 | **Dev-complete** — implemented and self-tested by dev/agent, awaiting owner verification |
| ✅ | **Verified** — personally verified by the project owner; eligible for commit |

**Lifecycle:** 🔴 → 🟡 → 🟢 → ✅ → *commit*

---

## Document Map

| Document | Purpose |
| --- | --- |
| [`README.md`](./README.md) | Project overview, architecture, layout, working agreement (this file) |
| [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) | Live status of every PRD functional & non-functional requirement |
| [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) | Gap between the PRD's target state and what exists today |
| [`TASKS.md`](./TASKS.md) | EPICs and sub-tasks, executed one by one with status tracking |
| [`docs/Zetix_PRD_v1.0.docx`](./docs/Zetix_PRD_v1.0.docx) | The Product Requirements Document (upstream source) |

---

*Zetix — point your camera, find the product. On-device, instant, private.*
