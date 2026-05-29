# packages/contracts

**The version-locked spine of the mono-repo.** Shared API, sync-protocol, and
vector-format schemas consumed by the server, both apps, and both SDKs. A change to the
wire format is one atomic commit across every consumer.

| File | Purpose |
| --- | --- |
| [`openapi.yaml`](./openapi.yaml) | REST API contract — `POST /search` (FR-34), admin catalog push (FR-35) |
| [`sync-protocol.md`](./sync-protocol.md) | Catalog full + delta sync wire format (FR-20–22), 512-dim vector format |

`make contracts` runs `gen` here (codegen of per-language types) and stamps
`.make/contracts.stamp`, which downstream surfaces depend on.

**Status:** 🔴 skeleton only ([EPIC-0.5](../../TASKS.md)) — schemas fleshed out in
EPIC-1 (API) and EPIC-3 (sync).
