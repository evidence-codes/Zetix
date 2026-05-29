# ADR-0002 — No Server-Side Retention of Fallback Query Vectors

- **Status:** Accepted
- **Date:** 2026-05-29
- **Resolves:** OQ-7 / D-7 (see [`GAP_ANALYSIS.md`](../../GAP_ANALYSIS.md), [`TASKS.md`](../../TASKS.md))
- **Deciders:** Project owner

## Context

On the server-fallback path (local index miss / low confidence), the device sends a
512-dim query **vector** (never the raw image — NFR-S1/S2). PRD Open Question OQ-7 asks
how long the server retains these vectors, in what format, and who owns them.

## Decision

**The server does not persist fallback query vectors.** A query vector is held in
memory only for the duration of the search request and discarded once the response is
returned. No query-vector table, no logging of raw vectors.

## Consequences

- **Data model:** there is no retention/ownership schema to build — the simplest and
  most privacy-aligned option, consistent with Zetix's positioning (NFR-S, §6.2).
- **Search logs (admin dashboard):** may record non-reversible metadata (timestamp,
  store, latency, result count, anonymous query id) but **must not** store the vector
  itself.
- **Analytics:** search-quality analytics that would need historical vectors are out of
  scope for Phase 1. If introduced later, it requires a new ADR and explicit consent
  handling (revisit OQ-7).
- **Compliance:** removes a class of GDPR/NDPA data-retention obligations for the query
  hot path.

## Implementation

- `POST /search` accepts a vector, computes results, returns them; the request body is
  not written to any datastore.
- The response carries an **ephemeral** `query_id` for request tracing only; it is not a
  key into stored vector data.
- Enforced as part of the API contract in [`packages/contracts`](../../packages/contracts).
