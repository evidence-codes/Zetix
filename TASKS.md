# Zetix — Tasks (EPICs & Sub-Tasks)

> **Source of truth.** This is the executable breakdown of the
> [PRD](./docs/Zetix_PRD_v1.0.docx). Every major task is an **EPIC** with sub-tasks.
> **Work them one by one, in order**, respecting phase dependencies. Read this and the
> rest of the doc set before acting — see [`README.md`](./README.md#working-agreement).
>
> When you start a sub-task, set it 🟡. When dev-complete, set it 🟢 **and** mirror the
> status in [`FEATURE_STATUS.md`](./FEATURE_STATUS.md). **Only the owner promotes
> 🟢 → ✅, and commits happen only after ✅.**

**Last updated:** 2026-05-29

## Status Legend

| Symbol | Meaning |
| --- | --- |
| 🔴 | Not done | 
| 🟡 | In process |
| 🟢 | Dev-complete (awaiting owner verification) |
| ✅ | Verified by owner (eligible for commit) |

**Lifecycle:** 🔴 → 🟡 → 🟢 → ✅ → *commit*

---

## EPIC Index

| EPIC | Title | Phase | Status |
| --- | --- | --- | --- |
| [EPIC-0](#epic-0--mono-repo-bootstrap--foundations) | Mono-repo bootstrap & foundations | Pre-1 | ✅ |
| [EPIC-1](#epic-1--server-pipeline-phase-1) | Server pipeline | 1 | 🔴 |
| [EPIC-2](#epic-2--android-app--on-device-embedding-phase-2) | Android app + on-device embedding | 2 | 🔴 |
| [EPIC-3](#epic-3--local-chromadb--sync-phase-3) | Local ChromaDB + sync | 3 | 🔴 |
| [EPIC-4](#epic-4--ios-port-phase-4) | iOS port | 4 | 🔴 |
| [EPIC-5](#epic-5--sdk--integration-layer-phase-5) | SDK & integration layer | 5 | 🔴 |
| [EPIC-6](#epic-6--cross-cutting-quality-privacy-accessibility-ci) | Cross-cutting: quality, privacy, a11y, CI | All | 🔴 |
| [EPIC-D](#epic-d--decisions-open-questions) | Decisions / open questions | All | 🔴 |

---

## EPIC-0 — Mono-Repo Bootstrap & Foundations

**Goal:** A single repository that can house and build all surfaces (Android, iOS,
SDKs, server, models, plugins) with version-locked shared contracts.
**Orchestration:** **Make** is the coarse cross-ecosystem graph + single command
surface; native tools (Gradle/Xcode-SPM/Python) are the fine-grained incremental
builders; stamp files in `.make/` fill the Bazel-shaped cross-language gaps. See
[ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md).
**Blocks:** everything else.

| ID | Sub-task | Status |
| --- | --- | --- |
| 0.1 | Resolve OQ-8: mono-repo orchestration → **Make as coarse graph** ([ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md)) | ✅ |
| 0.2 | Scaffold directory layout (`apps/`, `packages/`, `server/`, `models/`, `plugins/`, `tools/`, `docs/`) per README — dirs + per-module READMEs + placeholder Makefiles | ✅ |
| 0.3 | Root `Makefile` command surface + cross-tool stamps + recursive per-module delegation | ✅ |
| 0.4 | Root tooling: `.gitignore`, `.editorconfig`, formatters (`ruff.toml`, `.swiftformat`, ktlint via editorconfig), pre-commit hooks (`.pre-commit-config.yaml`) | ✅ |
| 0.5 | `packages/contracts` skeleton — `openapi.yaml` + `sync-protocol.md` stubs + `gen` target wired into `make contracts` | ✅ |
| 0.6 | CI pipeline (`.github/workflows/ci.yml`): per-ecosystem jobs (Python/Kotlin/Swift) driving the Make surface; lint gate | ✅ |
| 0.7 | `CONTRIBUTING.md` referencing the working agreement + status lifecycle | ✅ |
| 0.8 | Local dev bootstrap docs (`docs/DEVELOPMENT.md`): prerequisites, `make bootstrap`, command surface, server/app run | ✅ |

---

## EPIC-1 — Server Pipeline (Phase 1)

**Goal:** A REST search API returning accurate results on a 10k-product test set.
**Milestone:** M1 (Week 4). **Success metric:** Top-3 accuracy > 80% on 10k test set.
**Depends on:** EPIC-0.

### 1.A Catalog ingestion
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 1.A.1 | Define product/catalog schema in PostgreSQL (metadata, store config, sync state) | — | 🔴 |
| 1.A.2 | CSV ingestion adapter | Phase 1 scope | 🔴 |
| 1.A.3 | JSON ingestion adapter | Phase 1 scope | 🔴 |
| 1.A.4 | Shopify API ingestion adapter (API 2024-01+), abstracted behind adapter interface | Phase 1, NFR-C4 | 🔴 |
| 1.A.5 | Object storage (S3-compatible) for product images + index snapshots | §7.2 | 🔴 |

### 1.B Embedding & vector store
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 1.B.1 | OpenCLIP embedding service (GPU-accelerated on indexing path) | §7.2 | 🔴 |
| 1.B.2 | Generate 512-dim embeddings for all catalog images | §7.3 | 🔴 |
| 1.B.3 | ChromaDB server vector store + ANN cosine search | Phase 1 | 🔴 |
| 1.B.4 | Index build job + status tracking | Phase 1 | 🔴 |

### 1.C REST & admin API
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 1.C.1 | FastAPI app skeleton (Python 3.11+), Docker-deployable on 2-vCPU/4GB | NFR-C3 | 🔴 |
| 1.C.2 | `POST /search`: accept base64 image **or** image URL → ranked product JSON | FR-34 | 🔴 |
| 1.C.3 | Rank by similarity score; return top 10 | FR-06 | 🔴 |
| 1.C.4 | Admin catalog push API: full replace + delta via JSON/CSV | FR-35 | 🔴 |
| 1.C.5 | TLS 1.3 enforcement | NFR-S3 | 🔴 |
| 1.C.6 | GDPR/NDPA-compliant data model; consent gating for any PII | NFR-S6 | 🔴 |

### 1.D Admin dashboard
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 1.D.1 | Catalog upload UI | Phase 1 | 🔴 |
| 1.D.2 | Index status view | Phase 1 | 🔴 |
| 1.D.3 | Search logs view | Phase 1 | 🔴 |

### 1.E Search-quality evaluation (gates M1)
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 1.E.1 | Build 10k-product test set + labelled query set | §3.1 | 🔴 |
| 1.E.2 | Eval harness computing Top-3 accuracy | §3.1 | 🔴 |
| 1.E.3 | Per-category quality breakdown (niche-category risk check) | §9 | 🔴 |
| 1.E.4 | Hit Top-3 accuracy > 80% (M1 DoD) | M1 | 🔴 |

---

## EPIC-2 — Android App + On-Device Embedding (Phase 2)

**Goal:** Camera → on-device embedding → server search → results on a physical device.
**Milestone:** M2 (Week 10). **Success metric:** < 300ms end-to-end target work begins.
**Depends on:** EPIC-1 (server search), EPIC-0.

### 2.A App foundation
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 2.A.1 | Kotlin app scaffold in `apps/android` (min API 26) | NFR-C1 | 🔴 |
| 2.A.2 | Navigation + app shell (camera, results, detail, settings) | §8.2 | 🔴 |
| 2.A.3 | Cold start to camera-ready < 2s budget instrumentation | NFR-P3 | 🔴 |

### 2.B Camera & preprocessing
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 2.B.1 | CameraX live viewfinder + single-tap capture | FR-01 | 🔴 |
| 2.B.2 | Camera-roll photo picker as search source | FR-02 | 🔴 |
| 2.B.3 | Crop / focus overlay before submit | FR-09 | 🔴 |
| 2.B.4 | Image resize + normalise to 224×224 RGB | §7.3 | 🔴 |

### 2.C On-device embedding
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 2.C.1 | Convert CLIP ViT-B/32 / MobileNet-V3 → TFLite/ONNX (`models/conversion`) | §7.1 | 🔴 |
| 2.C.2 | INT8 quantise to < 25MB (`models/quantisation`) | NFR-P6 | 🔴 |
| 2.C.3 | On-device inference → 512-dim vector; image never leaves device | FR-03, NFR-S1 | 🔴 |
| 2.C.4 | Send query vector only (never image) to server search | NFR-S2 | 🔴 |

### 2.D Results & detail
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 2.D.1 | Results list: image, name, price, availability, store, similarity badge | FR-06, FR-07 | 🔴 |
| 2.D.2 | Skeleton loading states (never a blank wait) | §8.1 | 🔴 |
| 2.D.3 | Result filters: category, price range, in-stock only | FR-10 | 🔴 |
| 2.D.4 | Product detail view | Phase 2 | 🔴 |
| 2.D.5 | Open product page via deep link / web view | FR-08 | 🔴 |
| 2.D.6 | Always-visible "image stays on device" trust badge | §8.1 | 🔴 |

---

## EPIC-3 — Local ChromaDB + Sync (Phase 3)

**Goal:** Fully on-device pipeline with delta sync and transparent server fallback.
**Milestone:** M3 (Week 16). **Success metric:** delta sync < 30s for 1k update.
**Depends on:** EPIC-2.

### 3.A On-device vector store
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 3.A.1 | ChromaDB on Android via JNI **or** SQLite-backed equivalent | §7.1 | 🔴 |
| 3.A.2 | Local cosine ANN query path, top-k | FR-04 | 🔴 |
| 3.A.3 | Index size cap + eviction (oldest / least-searched first) | §9, NFR-P7 | 🔴 |
| 3.A.4 | Keep 10k-product index < 80MB on-device | NFR-P7 | 🔴 |

### 3.B Sync protocol
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 3.B.1 | Define sync protocol in `packages/contracts` (HTTP chunked + ETag delta diffs) | §7.1 | 🔴 |
| 3.B.2 | Full snapshot sync on first launch (< 3 min / 10k on WiFi) | FR-20, NFR-P4 | 🔴 |
| 3.B.3 | Auto delta sync on app open if > 6h since last sync | FR-21 | 🔴 |
| 3.B.4 | Resumable sync across network loss / background kill | FR-22 | 🔴 |
| 3.B.5 | Per-batch checksum verification; full re-sync fallback | §9 | 🔴 |
| 3.B.6 | Delta sync < 30s for 1k update (M3 DoD) | NFR-P5 | 🔴 |

### 3.C Fallback & offline
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 3.C.1 | Local-first query; escalate to server on miss / low confidence | FR-04 | 🔴 |
| 3.C.2 | Confidence threshold (resolve OQ-2 empirically) | OQ-2 | 🔴 |
| 3.C.3 | Local search latency < 300ms P95 benchmarked on real mid-range device | FR-05, NFR-P1 | 🔴 |
| 3.C.4 | Server fallback latency < 1200ms P95 on 4G | NFR-P2 | 🔴 |
| 3.C.5 | Transparent graceful degradation when index stale/missing | NFR-R3 | 🔴 |
| 3.C.6 | Full offline search on cached catalog | FR-25, NFR-R1 | 🔴 |

### 3.D Sync & history UI
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 3.D.1 | Sync status UI: last synced, catalog size, pending count, storage usage | FR-23, §8.2 | 🔴 |
| 3.D.2 | Manual sync trigger in settings | FR-24 | 🔴 |
| 3.D.3 | Low-power / low-data mode handling (defer on mobile data if opted in) | FR-25 | 🔴 |
| 3.D.4 | Local, searchable search history | FR-11 | 🔴 |

---

## EPIC-4 — iOS Port (Phase 4)

**Goal:** iOS feature parity with Core ML on-device pipeline.
**Milestone:** M4 (Week 22). **Success metric:** Core ML pipeline within 10% of Android latency.
**Depends on:** EPIC-3.

| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 4.1 | Swift app scaffold in `apps/ios` (min iOS 15) | NFR-C2 | 🔴 |
| 4.2 | AVFoundation camera pipeline + capture | FR-01, §7.1 | 🔴 |
| 4.3 | Convert model → Core ML (`models/conversion`); inference on-device | §7.1, FR-03 | 🔴 |
| 4.4 | Core Data / SQLite-backed local vector store | §7.1 | 🔴 |
| 4.5 | Reuse `packages/contracts` sync protocol; full + delta sync | EPIC-3 parity | 🔴 |
| 4.6 | Results, detail, sync status, settings parity | §8.2 | 🔴 |
| 4.7 | iOS UX polish: haptics, share sheet, camera permissions flow | Phase 4 | 🔴 |
| 4.8 | Benchmark Core ML latency within 10% of Android | §3.1 | 🔴 |

---

## EPIC-5 — SDK & Integration Layer (Phase 5)

**Goal:** External stores integrate in < 1 day.
**Milestones:** M5 (Week 28), M6 (Week 32). **Success metric:** integration < 8h following docs.
**Depends on:** EPIC-3 (Android), EPIC-4 (iOS).

### 5.A Android SDK
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 5.A.1 | `packages/sdk-android` AAR: `CameraSearchView` embeddable in Activity/Fragment | FR-30 | 🔴 |
| 5.A.2 | Programmatic search API | FR-30 | 🔴 |
| 5.A.3 | Init with store API key + catalog namespace (Keystore-backed) | FR-32, NFR-S4 | 🔴 |
| 5.A.4 | Emit search result events for host-app navigation | FR-33 | 🔴 |
| 5.A.5 | Custom result-card theming | FR-37 | 🔴 |

### 5.B iOS SDK
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 5.B.1 | `packages/sdk-ios` Swift Package: SwiftUI View + UIViewController | FR-31 | 🔴 |
| 5.B.2 | Init with API key + namespace (Secure Enclave-backed) | FR-32, NFR-S4 | 🔴 |
| 5.B.3 | Search result events | FR-33 | 🔴 |
| 5.B.4 | Custom theming | FR-37 | 🔴 |

### 5.C Server / API productisation
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 5.C.1 | API key auth | FR-32 | 🔴 |
| 5.C.2 | Rate limiting (Kong/Nginx gateway) | §7.2 | 🔴 |
| 5.C.3 | Per-store catalog namespacing | Phase 5 | 🔴 |
| 5.C.4 | Per-store webhook on index rebuild completion | FR-36 | 🔴 |
| 5.C.5 | Evaluate Weaviate for multi-tenant scale | §7.2 | 🔴 |

### 5.D Plugin, docs, sandbox
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 5.D.1 | Shopify App Store plugin (hosted storefront injection, no-code setup) | Phase 5 | 🔴 |
| 5.D.2 | Developer docs site: quickstart, API reference, integration guides | Phase 5 | 🔴 |
| 5.D.3 | SDK sandbox environment (test without a live catalog) | Phase 5 | 🔴 |
| 5.D.4 | Submit Shopify plugin; onboard first 3 paying stores (M6 DoD) | M6 | 🔴 |

---

## EPIC-6 — Cross-Cutting: Quality, Privacy, Accessibility, CI

**Goal:** Enforce NFRs as invariants across all surfaces, continuously.
**Applies to:** all phases.

### 6.A Privacy & security
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 6.A.1 | Architectural test: image never crosses the network boundary | NFR-S1 | 🔴 |
| 6.A.2 | Verify only non-reversible vectors sent on fallback | NFR-S2 | 🔴 |
| 6.A.3 | No third-party analytics SDKs in consumer apps; first-party telemetry only | NFR-S5 | 🔴 |
| 6.A.4 | Keystore / Secure Enclave key storage audit | NFR-S4 | 🔴 |

### 6.B Reliability
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 6.B.1 | Crash reporting; crash-free session rate > 99.5% | NFR-R4 | 🔴 |
| 6.B.2 | Server uptime monitoring toward 99.5% SLA | NFR-R2 | 🔴 |

### 6.C Accessibility
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 6.C.1 | Content descriptions for TalkBack / VoiceOver | NFR-A1 | 🔴 |
| 6.C.2 | Minimum 48×48dp touch targets | NFR-A2 | 🔴 |
| 6.C.3 | Font scaling up to 200% | NFR-A3 | 🔴 |
| 6.C.4 | Audio feedback on camera capture | NFR-A4 | 🔴 |

### 6.D Performance budgets in CI
| ID | Sub-task | Maps to | Status |
| --- | --- | --- | --- |
| 6.D.1 | Automated latency/size budget checks (model < 25MB, index < 80MB) | NFR-P6/P7 | 🔴 |
| 6.D.2 | Device-lab or reference-device benchmarking for latency NFRs | NFR-P1/P2/P3 | 🔴 |

---

## EPIC-D — Decisions / Open Questions

**Goal:** Resolve PRD §10 open questions; record decisions (ADRs in `docs/`).
Each blocks or shapes downstream EPICs. See [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md#5-open-questions-from-prd-10).

| ID | Decision needed | Blocks | Status |
| --- | --- | --- | --- |
| D-8 (OQ-8) | Mono-repo orchestration tool → **Make as coarse graph** ([ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md)) | EPIC-0 | ✅ |
| D-1 (OQ-1) | Insert Phase 2b (local Chroma + toy catalog) before Phase 3? | Phase sequencing | 🔴 |
| D-2 (OQ-2) | Server-fallback confidence threshold (empirical) | 3.C.2 | 🔴 |
| D-3 (OQ-3) | Multi-store search on one device? | EPIC-3+ architecture | 🔴 |
| D-4 (OQ-4) | SDK pricing model | EPIC-5 / business | 🔴 |
| D-5 (OQ-5) | White-label per store vs single multi-store app | EPIC-2 product shape | 🔴 |
| D-6 (OQ-6) | Fine-tuning strategy (shared base + adapters vs per-vertical) | models pipeline | 🔴 |
| D-7 (OQ-7) | Server fallback vector retention policy (duration/format/ownership) | EPIC-1 data model | 🔴 |

---

## How to Pick the Next Task

1. Read [`FEATURE_STATUS.md`](./FEATURE_STATUS.md) and this file.
2. Start at the lowest-numbered EPIC with unfinished sub-tasks, respecting
   dependencies (EPIC-0 → EPIC-1 → …). Resolve any blocking decision in
   [EPIC-D](#epic-d--decisions-open-questions) first.
3. Take **one** sub-task. Set it 🟡 here and in `FEATURE_STATUS.md`.
4. Implement + self-test. Set it 🟢 in both files. Summarise what you did.
5. Wait for the owner to verify and promote 🟢 → ✅. **Commit only after ✅.**
