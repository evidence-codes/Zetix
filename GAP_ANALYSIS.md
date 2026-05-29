# Zetix — Gap Analysis

> **Source of truth.** This document captures the gap between the target state
> defined in the [PRD](./docs/Zetix_PRD_v1.0.docx) and what actually exists in the
> repository today. Read this before working so you never assume code exists that
> doesn't. Keep it honest: if reality and the documents diverge, update this file.
> See [`README.md`](./README.md#working-agreement).

**Last updated:** 2026-05-29

---

## 1. Current State of the Repository

What exists today (verified by inspection of the working tree):

| Item | Present? | Notes |
| --- | --- | --- |
| PRD (`docs/Zetix_PRD_v1.0.docx`) | ✅ | Version 1.0, the upstream requirements source |
| `LICENSE` | ✅ | Present at repo root |
| `README.md` | ✅ | Now comprehensive (this doc set) |
| `FEATURE_STATUS.md` / `GAP_ANALYSIS.md` / `TASKS.md` | ✅ | This source-of-truth doc set |
| **Any source code** | ❌ | None — no `apps/`, `server/`, `packages/`, `models/`, `plugins/` |
| **Mono-repo scaffold / tooling** | ❌ | Not initialised (EPIC-0) |
| **CI / tests** | ❌ | None |
| **Models / converted artifacts** | ❌ | None |
| **Infra (Docker, compose)** | ❌ | None |

**Bottom line:** Zetix is at **pre-Phase-1, ground zero**. The full PRD scope is a
gap. Every functional and non-functional requirement is 🔴 in
[`FEATURE_STATUS.md`](./FEATURE_STATUS.md). The first concrete unit of work is
**EPIC-0: mono-repo bootstrap** (see [`TASKS.md`](./TASKS.md)).

---

## 2. Structural Gap — Mono-Repo

The PRD describes five product surfaces (Android app, iOS app, Android SDK, iOS SDK,
server) plus a Shopify plugin and an ML model pipeline. These **must live in a single
mono-repo** so the wire format, API schema, and model artifacts stay version-locked.

| Target mono-repo area | Exists? | Gap |
| --- | --- | --- |
| `apps/android` | ❌ | Entire Android consumer app (Phase 2–3) |
| `apps/ios` | ❌ | Entire iOS consumer app (Phase 4) |
| `packages/sdk-android` | ❌ | Android AAR SDK (Phase 5) |
| `packages/sdk-ios` | ❌ | iOS Swift Package SDK (Phase 5) |
| `packages/contracts` | ❌ | Shared API + sync-protocol schema (needed from Phase 1) |
| `server/api` | ❌ | FastAPI service + `POST /search` + admin API (Phase 1) |
| `server/embedding` | ❌ | OpenCLIP embedding service (Phase 1) |
| `server/admin-dashboard` | ❌ | Catalog upload / index status / search logs UI (Phase 1) |
| `models/` | ❌ | Model conversion, quantisation, eval harness (Phase 1–2) |
| `plugins/shopify` | ❌ | Shopify App Store plugin (Phase 5) |
| `tools/` + root build orchestration | ❌ | Mono-repo task runner, CI, shared config (EPIC-0) |

**Decision (EPIC-0 / OQ-8 — resolved):** **Make** is the coarse cross-ecosystem graph
and single command surface; the native tools (Gradle, Xcode/SPM, Python toolchain) are
the fine-grained, incremental, cached builders inside their own worlds; stamp files in
`.make/` plus order-only prerequisites fill the Bazel-shaped cross-language gaps (e.g.
"the iOS integration test needs the server up and the model converted"). See
[ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md) and the root `Makefile`.
The directory layout above remains the contract; `packages/contracts` and `models/`
are the version-locked spine.

---

## 3. Functional Gaps by Phase

### Phase 1 — Server Pipeline (Weeks 1–4) — **0% complete**

| Capability | Status | Gap |
| --- | --- | --- |
| Catalog ingestion (CSV / JSON / Shopify API) | 🔴 | Not started |
| Server-side CLIP embedding generation | 🔴 | Not started |
| ChromaDB vector store + ANN search endpoint | 🔴 | Not started |
| `POST /search` (image → ranked matches) — FR-34, FR-06 | 🔴 | Not started |
| Admin catalog push API — FR-35 | 🔴 | Not started |
| Admin dashboard (upload, index status, search logs) | 🔴 | Not started |
| Search-quality eval harness (Top-3 > 80% on 10k) | 🔴 | Not started — gates M1 |

### Phase 2 — Android App + On-Device Embedding (Weeks 5–10) — **0% complete**

| Capability | Status | Gap |
| --- | --- | --- |
| Native Kotlin app + camera capture (CameraX) — FR-01 | 🔴 | Not started |
| Camera-roll photo search — FR-02 | 🔴 | Not started |
| Image preprocessing (224×224 RGB normalise) | 🔴 | Not started |
| On-device embedding (CLIP/MobileNet → TFLite/ONNX) — FR-03 | 🔴 | Not started |
| Query vector → server search | 🔴 | Not started |
| Results screen (image/name/price/deep link) — FR-07, FR-08 | 🔴 | Not started |
| Crop / focus query image — FR-09 | 🔴 | Not started |
| Result filters — FR-10 | 🔴 | Not started |
| Product detail view | 🔴 | Not started |

### Phase 3 — Local ChromaDB + Sync (Weeks 11–16) — **0% complete**

| Capability | Status | Gap |
| --- | --- | --- |
| ChromaDB on Android (JNI / SQLite-backed) | 🔴 | Not started |
| Full catalog snapshot sync — FR-20 | 🔴 | Not started |
| Delta sync protocol — FR-21 | 🔴 | Not started |
| Resumable sync — FR-22 | 🔴 | Not started |
| Local-first query w/ server fallback — FR-04, FR-05 | 🔴 | Not started; fallback confidence threshold is an open question |
| Sync status UI — FR-23, FR-24 | 🔴 | Not started |
| Offline mode — FR-25, NFR-R1 | 🔴 | Not started |
| Local search history — FR-11 | 🔴 | Not started |

### Phase 4 — iOS Port (Weeks 17–22) — **0% complete**

| Capability | Status | Gap |
| --- | --- | --- |
| Native Swift app w/ feature parity — FR-31 mirror | 🔴 | Not started |
| Core ML model conversion + inference | 🔴 | Not started |
| Core Data / SQLite-backed local vector store | 🔴 | Not started |
| iOS UX polish (haptics, share sheet, camera permissions) | 🔴 | Not started |

### Phase 5 — SDK & Integration (Weeks 23–32) — **0% complete**

| Capability | Status | Gap |
| --- | --- | --- |
| Android AAR `CameraSearchView` + API — FR-30 | 🔴 | Not started |
| iOS Swift Package (SwiftUI + UIKit) — FR-31 | 🔴 | Not started |
| API key + namespace init — FR-32 | 🔴 | Not started |
| Search result events — FR-33 | 🔴 | Not started |
| Shopify App Store plugin | 🔴 | Not started |
| REST API: auth, rate limiting, per-store namespacing | 🔴 | Not started |
| Index-rebuild webhook — FR-36 | 🔴 | Not started |
| SDK theming — FR-37 | 🔴 | Not started |
| Developer docs site (quickstart, API ref, guides) | 🔴 | Not started |
| SDK sandbox environment | 🔴 | Not started |

---

## 4. Non-Functional Gaps

All NFRs are unmet because no implementation exists. Highlighted risks to design for
early rather than retrofit:

| Area | Gap / Risk | When to address |
| --- | --- | --- |
| **Privacy (NFR-S1/S2)** | The "image never leaves device, only the vector does" guarantee must be an architectural invariant of the SDK boundary — easy to violate accidentally. Encode it in `packages/contracts`. | Phase 2 design |
| **Model size (NFR-P6)** | < 25MB after INT8 quantisation is a hard constraint that influences model choice (CLIP ViT-B/32 vs MobileNet-V3). | Phase 1–2 |
| **Index size (NFR-P7)** | < 80MB for 10k products on-device drives the on-device store design and eviction policy. | Phase 3 |
| **Latency (NFR-P1)** | < 300ms P95 local must be benchmarked on real mid-range hardware, not just emulators. | Phase 2–3 |
| **Sync integrity** | Delta sync edge cases can corrupt the local index (PRD risk). Need checksum verification + full re-sync fallback + automated tests. | Phase 3 |
| **Security (NFR-S3/S4)** | TLS 1.3 floor + Keystore/Secure Enclave key storage must be baked into the SDK from the start. | Phase 5 (design from Phase 1 contracts) |
| **Accessibility (NFR-A1–A4)** | Content descriptions, 48dp targets, 200% font scaling, capture audio feedback — build in, don't bolt on. | Phase 2 & 4 |
| **Compliance (NFR-S6)** | GDPR + NDPA-compliant handling; consent gating for any PII. | Phase 1 (data model) |

---

## 5. Open Questions (from PRD §10)

These are unresolved product/architecture decisions that block or shape work. They
are tracked here and surfaced as decision tasks in [`TASKS.md`](./TASKS.md).

| # | Question | Impacts |
| --- | --- | --- |
| OQ-1 | Insert Phase 2b (local ChromaDB w/ toy catalog) before Phase 3 to validate on-device quality earlier? | Phase sequencing |
| OQ-2 | What confidence threshold triggers server fallback? Needs empirical testing. | FR-04, FR-05 |
| OQ-3 | Multi-store search on a single device — simultaneous across stores? | Phase 3+ architecture |
| OQ-4 | SDK pricing model: per-query, flat monthly, or tiered by catalog size? | Phase 5 / business |
| OQ-5 | Consumer app white-labelled per store, or single Zetix-branded multi-store app? | Phase 2 product shape |
| OQ-6 | Fine-tuning strategy: shared base + per-store adapters, or separate models per vertical? | Phase 2b / model pipeline |
| OQ-7 | Data retention policy for server-side fallback vectors: how long, what format, who owns? | Phase 1 data model, compliance |
| OQ-8 | ~~Mono-repo orchestration tool~~ — **RESOLVED: Make as coarse graph** ([ADR-0001](./docs/adr/0001-mono-repo-orchestration-make.md)) | EPIC-0 (unblocked) |

---

## 6. Risks Carried from the PRD (§9)

| Risk | Likelihood | Mitigation (per PRD) |
| --- | --- | --- |
| Generic CLIP embeddings insufficient for niche categories | Medium | Fine-tune on domain data (Phase 2b); test quality per category before launch |
| On-device ChromaDB memory too high for low-end devices | Medium | Cap local index; evict oldest / least-searched first |
| Shopify / platform API changes break ingestion | Low | Abstracted catalog adapter layer; pin stable API versions |
| Commoditisation by Shopify native visual search | Medium | Differentiate on on-device privacy + cross-platform SDK |
| Model too large for OTA update constraints | Low | INT8 quantise (<25MB); distribute via CDN separate from binary |
| Delta sync edge cases corrupt local index | Low | Per-batch checksums; full re-sync fallback; automated tests |
| Low initial search quality damages reputation | Medium | Soft-launch to 3 friendly stores; iterate model before public SDK |

---

## 7. Recommended First Moves

1. **EPIC-0 — Mono-repo bootstrap.** Resolve OQ-8, then scaffold the directory layout
   in [`README.md`](./README.md#repository-layout-mono-repo) with placeholder build
   files and CI.
2. **Stand up `packages/contracts`** early — the API schema and sync/vector format are
   shared by every surface; defining them first prevents drift.
3. **Begin Phase 1** (`server/`) toward Milestone M1, including the search-quality eval
   harness, since M1's Definition of Done is a measurable accuracy bar (Top-3 > 80%).
