# server

Backend services (Phase 1 / [EPIC-1](../TASKS.md#epic-1--server-pipeline-phase-1)).
Docker-deployable on 2-vCPU / 4GB RAM minimum (NFR-C3).

| Sub-dir | Purpose |
| --- | --- |
| `api/` | FastAPI app — `POST /search` (FR-34), admin catalog push (FR-35), sync endpoints |
| `embedding/` | CLIP/OpenCLIP embedding service (GPU-accelerated on the indexing path) |
| `admin-dashboard/` | Catalog upload, index status, search logs UI |

**Stack:** Python 3.11+, FastAPI, OpenCLIP, ChromaDB (or Weaviate for multi-tenant
scale), PostgreSQL, S3-compatible object storage, Kong/Nginx gateway.

**Build/run** via the root command surface: `make server-build`, `make server-test`,
`make server-up`. The module [`Makefile`](./Makefile) wraps the native Python toolchain.

**Contracts:** consumes [`packages/contracts`](../packages/contracts) — the API schema
is defined there, not here. **Status:** 🔴 not started — see [TASKS.md](../TASKS.md).
