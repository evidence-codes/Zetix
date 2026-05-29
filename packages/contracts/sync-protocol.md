# Zetix Sync Protocol — shared contract (STUB, EPIC-0.5 → defined in EPIC-3)

The catalog sync protocol is shared by the server and every on-device client
(Android, iOS). It is the version-locked spine for keeping local indexes current.
This document is the single source of truth for the wire format; a change here is one
atomic commit across all consumers.

## Transport
- HTTP chunked transfer with **ETag-based delta diffs** (PRD §7.1).
- TLS 1.3 minimum (NFR-S3).

## Operations (to be specified in EPIC-3 / 3.B)
- **Full snapshot** — first launch downloads the complete catalog index snapshot (FR-20).
- **Delta sync** — server sends only changed/added/removed vectors since last sync (FR-21).
- **Resumable** — sync survives network loss / background kill (FR-22).
- **Integrity** — per-batch checksum verification; full re-sync as fallback (PRD §9).

## Vector format
- 512-dim float embedding (PRD §7.3). Exact dtype/quantisation TBD in EPIC-3.

## Open questions feeding this contract
- OQ-2: confidence threshold for server fallback.
- OQ-3: multi-store on a single device.
- OQ-7: server-side fallback vector retention.

> TODO: formalise message schemas (snapshot manifest, delta batch, ack/cursor) in EPIC-3.
