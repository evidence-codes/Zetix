# Zetix — Feature Status

> **Source of truth.** Live status of every requirement in the
> [PRD](./docs/Zetix_PRD_v1.0.docx). Read this before working. Update the status
> column as work progresses. See [`README.md`](./README.md#working-agreement) for the
> working agreement and [`TASKS.md`](./TASKS.md) for the executable EPIC breakdown.

**Last updated:** 2026-05-29

## Status Legend

| Symbol | Meaning |
| --- | --- |
| 🔴 | **Not done** — not started |
| 🟡 | **In process** — actively being worked on |
| 🟢 | **Dev-complete** — implemented + self-tested, awaiting owner verification |
| ✅ | **Verified** — personally verified by the owner; eligible for commit |

**Lifecycle:** 🔴 → 🟡 → 🟢 → ✅ → *commit*. Only the owner promotes 🟢 → ✅.

---

## Summary

| Area | Total | 🔴 | 🟡 | 🟢 | ✅ |
| --- | --- | --- | --- | --- | --- |
| Functional Requirements | 26 | 26 | 0 | 0 | 0 |
| Non-Functional Requirements | 24 | 24 | 0 | 0 | 0 |
| Phase deliverables | 5 phases | 5 | 0 | 0 | 0 |
| Milestones | 6 | 6 | 0 | 0 | 0 |

> Everything is 🔴 today: the repo contains only the PRD, a LICENSE, and these
> documents. No code has been scaffolded. See [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md).

---

## 1. Functional Requirements

### 1.1 Image Search Core (§5.1)

| ID | Requirement | Priority | Phase | Status |
| --- | --- | --- | --- | --- |
| FR-01 | Initiate a visual search from the device camera in one tap | P0 | 2 | 🔴 |
| FR-02 | Initiate a search from an existing photo in the camera roll | P0 | 2 | 🔴 |
| FR-03 | Image embedding generated entirely on-device; raw image never leaves device | P0 | 2 | 🔴 |
| FR-04 | Local ChromaDB queried first; server queried only on miss / low confidence | P0 | 3 | 🔴 |
| FR-05 | Search returns results in < 300ms on a mid-range device (local path) | P0 | 3 | 🔴 |
| FR-06 | Results ranked by visual similarity score; top 10 shown | P0 | 1 | 🔴 |
| FR-07 | Each result shows image, name, price, availability, store name | P0 | 2 | 🔴 |
| FR-08 | Tapping a result opens the product page (deep link / web view) | P0 | 2 | 🔴 |
| FR-09 | User can crop / focus the query image before submitting search | P1 | 2 | 🔴 |
| FR-10 | Filter results by category, price range, in-stock only | P1 | 2 | 🔴 |
| FR-11 | Search history stored locally and searchable | P2 | 3 | 🔴 |

### 1.2 Catalog Sync (§5.2)

| ID | Requirement | Priority | Phase | Status |
| --- | --- | --- | --- | --- |
| FR-20 | On first launch, app downloads the full catalog index snapshot | P0 | 3 | 🔴 |
| FR-21 | Delta sync runs automatically on app open if > 6 hours since last sync | P0 | 3 | 🔴 |
| FR-22 | Delta sync is resumable if interrupted (network loss, background kill) | P0 | 3 | 🔴 |
| FR-23 | App shows sync status: last updated, catalog size, pending count | P1 | 3 | 🔴 |
| FR-24 | User can manually trigger a sync from settings | P1 | 3 | 🔴 |
| FR-25 | Sync respects low-power / low-data modes (defers on mobile data if opted in) | P2 | 3 | 🔴 |

### 1.3 SDK / Integration (§5.3)

| ID | Requirement | Priority | Phase | Status |
| --- | --- | --- | --- | --- |
| FR-30 | Android SDK exposes a `CameraSearchView` embeddable in any Activity/Fragment | P0 | 5 | 🔴 |
| FR-31 | iOS SDK exposes an equivalent SwiftUI View and UIViewController | P0 | 5 | 🔴 |
| FR-32 | SDK accepts a store API key and catalog namespace at init | P0 | 5 | 🔴 |
| FR-33 | SDK emits search result events; host app handles navigation/display | P0 | 5 | 🔴 |
| FR-34 | REST API accepts base64 image or image URL; returns ranked product JSON | P0 | 1 | 🔴 |
| FR-35 | Admin API allows catalog push: full replace or delta via JSON/CSV | P0 | 1 | 🔴 |
| FR-36 | Per-store webhook fires on index rebuild completion | P1 | 5 | 🔴 |
| FR-37 | SDK supports custom result-card theming (colours, fonts, layout) | P2 | 5 | 🔴 |

---

## 2. Non-Functional Requirements

### 2.1 Performance (§6.1)

| ID | Requirement | Target | Status |
| --- | --- | --- | --- |
| NFR-P1 | On-device search latency (local hit) | < 300ms P95 on a 2021 mid-range Android | 🔴 |
| NFR-P2 | On-device search latency (server fallback) | < 1200ms P95 on 4G | 🔴 |
| NFR-P3 | App cold start to camera ready | < 2 seconds | 🔴 |
| NFR-P4 | Initial catalog sync (10k products) | < 3 minutes on WiFi | 🔴 |
| NFR-P5 | Delta sync (1k product update) | < 30 seconds | 🔴 |
| NFR-P6 | Embedding model size (on-device) | < 25MB after quantisation | 🔴 |
| NFR-P7 | Local ChromaDB index size (10k products) | < 80MB on-device storage | 🔴 |

### 2.2 Privacy & Security (§6.2)

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-S1 | Raw camera images never transmitted to any server under any circumstances | 🔴 |
| NFR-S2 | Only the query vector (non-reversible float array) sent on server fallback | 🔴 |
| NFR-S3 | All server communication is TLS 1.3 minimum | 🔴 |
| NFR-S4 | API keys stored in Android Keystore / iOS Secure Enclave | 🔴 |
| NFR-S5 | No third-party analytics SDKs in the consumer app (telemetry first-party only) | 🔴 |
| NFR-S6 | GDPR + NDPA (Nigeria) compliant; no PII stored without explicit consent | 🔴 |

### 2.3 Reliability (§6.3)

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-R1 | App functions fully offline for products in the local cache | 🔴 |
| NFR-R2 | Server API targets 99.5% monthly uptime SLA | 🔴 |
| NFR-R3 | Graceful degradation: stale/missing local index falls back to server transparently | 🔴 |
| NFR-R4 | Crash-free session rate > 99.5% | 🔴 |

### 2.4 Compatibility (§6.4)

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-C1 | Android API 26 (Android 8.0) minimum | 🔴 |
| NFR-C2 | iOS 15 minimum | 🔴 |
| NFR-C3 | Server Docker-deployable on 2-vCPU / 4GB RAM minimum | 🔴 |
| NFR-C4 | Shopify API 2024-01+ | 🔴 |

### 2.5 Accessibility (§8.3)

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-A1 | All interactive elements have content descriptions (TalkBack / VoiceOver) | 🔴 |
| NFR-A2 | Minimum touch target size 48×48dp | 🔴 |
| NFR-A3 | Support system font size scaling up to 200% | 🔴 |
| NFR-A4 | Camera viewfinder provides audio feedback on capture | 🔴 |

---

## 3. Phase Deliverables & Success Metrics

| Phase | Goal | Success Metric | Status |
| --- | --- | --- | --- |
| Phase 1 — Pipeline | Validate search quality on a real catalog | Top-3 accuracy > 80% on 10k product test set | 🔴 |
| Phase 2 — On-device | Embedding + search runs on-device | < 300ms end-to-end on mid-range Android | 🔴 |
| Phase 3 — Sync | Local index stays current with catalog | Delta sync < 30s for 1k product update | 🔴 |
| Phase 4 — iOS | Full feature parity on iOS | Core ML pipeline within 10% latency of Android | 🔴 |
| Phase 5 — SDK | External stores integrate in < 1 day | Integration < 8 hours following docs | 🔴 |

---

## 4. Milestones (§11)

| Milestone | Target Week | Definition of Done | Status |
| --- | --- | --- | --- |
| M1 — Pipeline live | Week 4 | REST search API returning accurate results on 10k product test set | 🔴 |
| M2 — Android app ships | Week 10 | Camera → server search → results on a physical device | 🔴 |
| M3 — Full on-device | Week 16 | End-to-end local pipeline; server fallback; delta sync tested | 🔴 |
| M4 — iOS parity | Week 22 | iOS feature-complete; Core ML pipeline benchmarked | 🔴 |
| M5 — SDK beta | Week 28 | Android + iOS SDK integrated into one external test store | 🔴 |
| M6 — SDK v1.0 launch | Week 32 | Docs live; Shopify plugin submitted; first 3 paying stores | 🔴 |

---

## 5. Business Metrics (12 Months Post-Launch) — Tracking Only

| Metric | Target | Status |
| --- | --- | --- |
| SDK integrations | 25 paying stores | 🔴 |
| Monthly active searchers | 50,000 across integrated stores | 🔴 |
| Search-to-purchase conversion | > 12% of visual searches → add-to-cart | 🔴 |
| Churn | < 5% monthly on SDK subscriptions | 🔴 |
| NPS (store developers) | > 45 | 🔴 |
