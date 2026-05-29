# apps/android

Native Kotlin consumer app (Phases 2–3 /
[EPIC-2](../../TASKS.md#epic-2--android-app--on-device-embedding-phase-2),
[EPIC-3](../../TASKS.md#epic-3--local-chromadb--sync-phase-3)). Min API 26 (NFR-C1).

**Stack:** Kotlin, CameraX, TFLite/ONNX Runtime (on-device embedding), ChromaDB via
JNI / SQLite-backed local vector store.

**Privacy invariant:** the embedding is generated on-device and the raw image **never**
leaves the device; only the 512-dim query vector is sent on server fallback (FR-03,
NFR-S1/S2).

**Build** via the root surface: `make android-build` / `make android-test`. Gradle owns
file-level incrementality; the module [`Makefile`](./Makefile) is a thin wrapper. The
build depends on the converted model + shared contracts (declared in the root Makefile).

**Status:** 🔴 not started — see [TASKS.md](../../TASKS.md).
