# apps/ios

Native Swift consumer app (Phase 4 /
[EPIC-4](../../TASKS.md#epic-4--ios-port-phase-4)). Min iOS 15 (NFR-C2). Feature parity
with Android; Core ML pipeline target within 10% of Android latency.

**Stack:** Swift, AVFoundation, Core ML (on-device embedding), Core Data / SQLite-backed
local vector store.

**Privacy invariant:** same as Android — raw image never leaves the device; only the
query vector is sent on fallback (FR-03, NFR-S1/S2).

**Build** via the root surface: `make ios-build` / `make ios-test` /
`make ios-integration-test`. Xcode/SPM owns file-level incrementality; the module
[`Makefile`](./Makefile) is a thin wrapper. The integration test depends on the server
being up + the model converted (declared in the root Makefile).

**Status:** 🔴 not started — see [TASKS.md](../../TASKS.md).
