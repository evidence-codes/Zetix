# Zetix Admin Dashboard

A small **standalone** FastAPI app for operating a Zetix catalog
([EPIC-1](../../TASKS.md#epic-1--server-pipeline-phase-1), sub-tasks 1.D.1–1.D.3).
It is a separate app from the main API (`server/api/zetix_api`) — it does **not**
import or modify it. It talks to the API over HTTP via `httpx`.

## What it does

| Section | Source | Notes |
| --- | --- | --- |
| **Catalog upload** (1.D.1) | `POST /admin/catalog` | Paste products as JSON or CSV; push full (replace) or delta (upsert). |
| **Index status** (1.D.2) | `GET /admin/index/status?store=…` | Shows `product_count`, `status`, `last_indexed_at`. |
| **Search logs** (1.D.3) | **stub** | The API does not persist query vectors (ADR-0002) and has no logs endpoint yet, so this view is backed by placeholder metadata and clearly labelled as a stub, pending a real `GET /admin/search/logs` endpoint. |

## Dependencies

Beyond the server's base deps (`fastapi`, `uvicorn`), this app needs:

- `jinja2` — declared in the server's `[dashboard]` extra: `pip install -e ".[dashboard]"`.
- `httpx` — to call the API (also in the `[dev]` / `[ingest]` extras).
- `python-multipart` — required by FastAPI to parse the HTML form POST.

```bash
cd server
pip install -e ".[dashboard]" httpx python-multipart
```

## Run

```bash
cd server/admin-dashboard
uvicorn app:app --port 8001
```

Then open <http://localhost:8001/>. The main Zetix API must be running separately
(e.g. `uvicorn zetix_api.main:app --port 8000` from `server/api`).

## Environment variables

| Var | Default | Purpose |
| --- | --- | --- |
| `ZETIX_API_URL` | `http://localhost:8000` | Base URL of the Zetix API. |
| `ZETIX_DEFAULT_STORE` | `acme` | Store namespace pre-filled in the UI. |
| `ZETIX_HTTP_TIMEOUT` | `10` | httpx request timeout (seconds). |

## Test

```bash
cd server/admin-dashboard
pytest -q
```

Tests use FastAPI's `TestClient` and monkeypatch the httpx client factory
(`get_client`), so no live API is required.
