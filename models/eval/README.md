# models/eval — search-quality evaluation harness

Computes **Top-1 / Top-3 / Top-5** accuracy and a **per-category breakdown** for visual
product search, by driving the real server pipeline in-process. Implements
[`TASKS.md`](../../TASKS.md) sub-tasks **1.E.2** (Top-3 harness), **1.E.3** (per-category
breakdown) and provides the gate for **1.E.4 / Milestone M1** (Top-3 accuracy > 80% on a
10k-product test set).

## What it does

1. Builds the FastAPI app via `from zetix_api import create_app` and a FastAPI
   `TestClient` — **in-process, no network, no Docker.**
2. Pushes a labelled catalog through **`POST /admin/catalog`** (full replace).
3. For each labelled query, derives the query vector and calls **`POST /search`**,
   then records the 1-based rank of the expected product id (or a miss).
4. Aggregates Top-1/3/5 accuracy, breaks it down per category, and prints a
   human-readable report. The same structured result is returned as a `dict` and can
   be written to JSON (`--json`).

The backend is whatever the server env selects (default: **stub embedder +
in-memory store**; see `zetix_api.factory`).

## Methodology (read this)

The catalog indexes each product by embedding its `image_url or id` bytes
(`services/catalog.py` → `_index_seed` → `StubEmbeddingService`). The harness derives
each **query vector the same way** — it embeds the query's `image_url` bytes with the
same embedder family — so the query and indexing vectors are produced identically and
the search is a genuine end-to-end pass through the public API.

**On the stub embedder this is an exact-vector match, so synthetic accuracy is high BY
CONSTRUCTION** (the expected item is essentially always the top hit). The synthetic run
therefore validates the *plumbing and the metric*, **not** model quality.

> **Real M1 accuracy requires `ZETIX_EMBEDDER=openclip` and a real labelled 10k
> catalog**, where the query image differs from the catalog image and visual similarity
> is actually tested. Only that configuration can legitimately claim Top-3 > 80%.

## Run

```bash
# From the repo root (delegates root -> models -> eval):
make eval

# From models/ directly:
python -m eval                      # synthetic set, prints the report
python -m eval --json result.json   # also write the structured result
python -m eval --dataset path.json  # target a real labelled catalog (format below)

# Real model + real catalog + enforce the M1 bar (exit non-zero if below 80%):
ZETIX_EMBEDDER=openclip python -m eval --dataset real_10k.json --require-bar
```

`python -m eval` is run from the `models/` directory (the `Makefile` and `make eval`
handle this). The harness puts `server/api` and `server/embedding` on `sys.path`
automatically (see the path-wiring block at the top of `harness.py`), so no install of
the server package is required — only `fastapi` and `numpy` (already a server
dependency) need to be importable. `make eval` prefers the `server/.venv` created by
`make server-bootstrap`; otherwise it uses the ambient `python3`.

## Smoke test

```bash
make test            # from models/  (runs: python -m pytest eval -q)
# or directly:
python -m pytest models/eval -q
```

`test_eval.py` runs the harness on the synthetic set and asserts the result has the
expected structure (`top1`/`top3`/`top5`, `per_category`, per-query records) and that
all accuracies are within `[0, 1]`. It deliberately **does not** assert the >80% bar —
that needs the real model + catalog, not the stub.

## Real dataset format

`--dataset PATH` reads a JSON file:

```json
{
  "store": "acme",
  "products": [
    {
      "id": "sku-1", "title": "Mid-century credenza",
      "price": 899.0, "currency": "USD", "availability": "in_stock",
      "image_url": "https://store.example/img/credenza.jpg",
      "product_url": "https://store.example/p/credenza",
      "store": "acme", "category": "furniture"
    }
  ],
  "queries": [
    { "query_id": "q1", "expected_id": "sku-1",
      "image_url": "https://store.example/img/credenza.jpg",
      "category": "furniture" }
  ]
}
```

* `products[]` — full Product payloads accepted by `POST /admin/catalog` (see
  [`packages/contracts/openapi.yaml`](../../packages/contracts/openapi.yaml)).
* `queries[]` — each maps a query to the `expected_id` it should retrieve; `image_url`
  is the image whose embedding is the search input; `category` (optional) drives the
  per-category breakdown.

For a real 10k run, the query `image_url` should point at a *different* photo of the
product than the one indexed (e.g. a user-style "in the wild" shot), so the harness
measures real visual-similarity accuracy rather than an exact match.

## Files

| File | Purpose |
| --- | --- |
| `harness.py` | `evaluate()` / `run()` / `format_report()` — the core pipeline + metrics; wires the server packages onto `sys.path` |
| `dataset.py` | `synthetic_dataset()` generator + `load_dataset()` JSON loader |
| `__main__.py` | CLI (`python -m eval`) |
| `test_eval.py` | Smoke test (structure + ranges) |
| `conftest.py` | Makes the `eval` package importable under pytest |
