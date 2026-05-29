"""Zetix admin dashboard — a standalone FastAPI app (sub-tasks 1.D.1–1.D.3).

This is a SEPARATE app from the main Zetix API (``server/api/zetix_api``). It does
not import or modify the API; it talks to it over HTTP via ``httpx`` using the base
URL in ``ZETIX_API_URL`` (default ``http://localhost:8000``).

Sections rendered:
  * Catalog upload (1.D.1) — paste CSV or JSON products and POST them to
    ``/admin/catalog`` (full or delta).
  * Index status (1.D.2) — calls ``GET /admin/index/status?store=...``.
  * Search logs (1.D.3) — STUB. The API does not persist query vectors (ADR-0002)
    and exposes no logs endpoint yet, so this is backed by placeholder data and
    clearly labelled as such, pending a real logs endpoint.

Run:  ``uvicorn app:app --port 8001``  (from this directory).
"""

from __future__ import annotations

import csv
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

API_URL = os.environ.get("ZETIX_API_URL", "http://localhost:8000").rstrip("/")
DEFAULT_STORE = os.environ.get("ZETIX_DEFAULT_STORE", "acme")
HTTP_TIMEOUT = float(os.environ.get("ZETIX_HTTP_TIMEOUT", "10"))

_TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

app = FastAPI(title="Zetix Admin Dashboard", version="0.1.0")


def get_client() -> httpx.Client:
    """Return an httpx client for the Zetix API.

    Factored into a function so tests can monkeypatch it (avoiding live calls).
    """
    return httpx.Client(base_url=API_URL, timeout=HTTP_TIMEOUT)


# --- Search-logs stub -------------------------------------------------------
# ADR-0002: the API does not persist query vectors and has no logs endpoint yet.
# These rows are placeholder data so the view can be built; they carry only the
# non-reversible metadata an eventual logs endpoint is allowed to record
# (timestamp, store, latency, result count, ephemeral query id) — never a vector.
_STUB_SEARCH_LOGS: list[dict[str, Any]] = [
    {
        "query_id": "q_2f9c1a",
        "store": "acme",
        "ts": "2026-05-29T10:14:02Z",
        "result_count": 10,
        "latency_ms": 84.2,
        "top_score": 0.91,
    },
    {
        "query_id": "q_8b30de",
        "store": "acme",
        "ts": "2026-05-29T10:13:51Z",
        "result_count": 7,
        "latency_ms": 102.5,
        "top_score": 0.77,
    },
    {
        "query_id": "q_1147af",
        "store": "demo",
        "ts": "2026-05-29T10:09:18Z",
        "result_count": 0,
        "latency_ms": 61.0,
        "top_score": None,
    },
]


def fetch_search_logs() -> list[dict[str, Any]]:
    """Return recent search logs (STUB — pending a real logs endpoint)."""
    return list(_STUB_SEARCH_LOGS)


# --- Index status -----------------------------------------------------------
def fetch_index_status(store: str) -> dict[str, Any]:
    """Call GET /admin/index/status?store=... ; return a render-friendly dict."""
    try:
        with get_client() as client:
            resp = client.get("/admin/index/status", params={"store": store})
        resp.raise_for_status()
        return {"data": resp.json(), "error": None}
    except httpx.HTTPError as exc:
        return {"data": None, "error": f"Could not reach API at {API_URL}: {exc}"}


# --- Catalog parsing --------------------------------------------------------
@dataclass
class ParsedCatalog:
    products: list[dict[str, Any]]
    error: str | None = None


def parse_products(raw: str, fmt: str) -> ParsedCatalog:
    """Parse pasted catalog text (``json`` or ``csv``) into a list of product dicts."""
    text = (raw or "").strip()
    if not text:
        return ParsedCatalog(products=[], error="No catalog data provided.")
    try:
        if fmt == "json":
            return ParsedCatalog(products=_parse_json(text))
        if fmt == "csv":
            return ParsedCatalog(products=_parse_csv(text))
        return ParsedCatalog(products=[], error=f"Unknown format: {fmt!r}")
    except (json.JSONDecodeError, csv.Error, ValueError) as exc:
        return ParsedCatalog(products=[], error=f"Could not parse {fmt.upper()}: {exc}")


def _parse_json(text: str) -> list[dict[str, Any]]:
    data = json.loads(text)
    if isinstance(data, dict):
        # Allow either a bare list or a {"products": [...]} envelope.
        data = data.get("products", [])
    if not isinstance(data, list):
        raise ValueError("expected a JSON array of products or a {'products': [...]} object")
    return [dict(item) for item in data]


_NUMERIC_FIELDS = {"price"}


def _parse_csv(text: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text))
    products: list[dict[str, Any]] = []
    for row in reader:
        product = {k: v for k, v in row.items() if k and v not in (None, "")}
        for field in _NUMERIC_FIELDS & product.keys():
            product[field] = float(product[field])
        products.append(product)
    if not products:
        raise ValueError("no rows found (expected a header row + at least one product)")
    return products


def push_catalog(store: str, mode: str, products: list[dict[str, Any]]) -> dict[str, Any]:
    """POST parsed products to /admin/catalog ; return a render-friendly dict."""
    payload = {"store": store, "mode": mode, "products": products}
    try:
        with get_client() as client:
            resp = client.post("/admin/catalog", json=payload)
        resp.raise_for_status()
        return {"data": resp.json(), "error": None}
    except httpx.HTTPError as exc:
        return {"data": None, "error": f"Catalog push failed ({API_URL}): {exc}"}


# --- Routes -----------------------------------------------------------------
def _context(request: Request, store: str, **extra: Any) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "request": request,
        "api_url": API_URL,
        "store": store,
        "index_status": fetch_index_status(store),
        "search_logs": fetch_search_logs(),
        "upload_result": None,
        "parse_error": None,
    }
    ctx.update(extra)
    return ctx


@app.get("/", response_class=HTMLResponse)
def index(request: Request, store: str = DEFAULT_STORE) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", _context(request, store))


@app.post("/catalog", response_class=HTMLResponse)
def upload_catalog(
    request: Request,
    store: str = Form(...),
    mode: str = Form("full"),
    fmt: str = Form("json"),
    data: str = Form(""),
) -> HTMLResponse:
    parsed = parse_products(data, fmt)
    if parsed.error is not None:
        ctx = _context(request, store, parse_error=parsed.error)
        return templates.TemplateResponse(request, "index.html", ctx)
    result = push_catalog(store, mode, parsed.products)
    ctx = _context(request, store, upload_result=result)
    return templates.TemplateResponse(request, "index.html", ctx)
