# packages/sdk-ios

Distributable iOS SDK (Swift Package) — the commercial product (Phase 5 /
[EPIC-5](../../TASKS.md#epic-5--sdk--integration-layer-phase-5)).

Exposes an equivalent SwiftUI `View` and `UIViewController` (FR-31), init with store
API key + catalog namespace backed by the Secure Enclave (FR-32, NFR-S4), search-result
events for host-app navigation (FR-33), and custom theming (FR-37).

**Build:** `make sdk-build`. Native tool: SPM + Xcode. Consumes
[`packages/contracts`](../contracts). **Status:** 🔴 not started.
