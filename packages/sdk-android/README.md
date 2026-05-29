# packages/sdk-android

Distributable Android SDK (AAR) — the commercial product (Phase 5 /
[EPIC-5](../../TASKS.md#epic-5--sdk--integration-layer-phase-5)).

Exposes a drop-in `CameraSearchView` embeddable in any Activity/Fragment (FR-30), a
programmatic search API, init with store API key + catalog namespace backed by Android
Keystore (FR-32, NFR-S4), search-result events for host-app navigation (FR-33), and
custom result-card theming (FR-37).

**Build:** `make sdk-build`. Native tool: Gradle. Consumes
[`packages/contracts`](../contracts). **Status:** 🔴 not started.
