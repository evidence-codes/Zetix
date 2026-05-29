"""Object storage abstraction (EPIC-1, task 1.A.5).

Provides a small :class:`ObjectStorage` protocol plus two backends used for product
images and index snapshots:

- :class:`LocalObjectStorage` — filesystem backend for local dev / tests.
- :class:`S3ObjectStorage` — S3-compatible backend (lazy-imports ``boto3``); the
  ``endpoint_url``/``region``/``bucket`` come from the constructor or env so it works
  against AWS S3, MinIO, R2, etc.

These are utilities to be wired later (snapshot persistence, image hosting); nothing
here is imported by the running app.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ObjectStorage(Protocol):
    """Minimal blob store interface keyed by string object keys."""

    def put(self, key: str, data: bytes) -> str:
        """Store ``data`` under ``key`` and return a locator (path or URL)."""
        ...

    def get(self, key: str) -> bytes:
        """Return the bytes previously stored under ``key``."""
        ...

    def url(self, key: str) -> str:
        """Return an addressable URL/locator for ``key``."""
        ...


class LocalObjectStorage:
    """Filesystem-backed object storage rooted at ``base_dir``."""

    def __init__(self, base_dir: str | os.PathLike[str]) -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Guard against path traversal / absolute keys escaping the root.
        rel = Path(key.lstrip("/"))
        if ".." in rel.parts:
            raise ValueError(f"invalid object key: {key!r}")
        return self._base / rel

    def put(self, key: str, data: bytes) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def url(self, key: str) -> str:
        return self._path(key).resolve().as_uri()


class S3ObjectStorage:
    """S3-compatible object storage backed by ``boto3``.

    Configuration resolves from explicit arguments first, then environment:
    ``ZETIX_S3_BUCKET``, ``ZETIX_S3_ENDPOINT_URL``, ``ZETIX_S3_REGION``. ``boto3`` is
    imported lazily so the ``[storage]`` extra is only required when used.
    """

    def __init__(
        self,
        bucket: str | None = None,
        *,
        endpoint_url: str | None = None,
        region: str | None = None,
        public_base_url: str | None = None,
        client: object | None = None,
    ) -> None:
        self._bucket = bucket or os.environ.get("ZETIX_S3_BUCKET")
        if not self._bucket:
            raise ValueError("S3ObjectStorage requires a bucket (arg or ZETIX_S3_BUCKET)")
        self._endpoint_url = endpoint_url or os.environ.get("ZETIX_S3_ENDPOINT_URL")
        self._region = region or os.environ.get("ZETIX_S3_REGION")
        self._public_base_url = public_base_url or os.environ.get("ZETIX_S3_PUBLIC_BASE_URL")
        self._client = client

    @property
    def client(self):
        # Return type is the dynamic boto3 S3 client; kept untyped to avoid the import.
        if self._client is None:
            import boto3  # lazy import: only needs the [storage] extra when used

            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                region_name=self._region,
            )
        return self._client

    def put(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self._bucket, Key=key, Body=data)
        return self.url(key)

    def get(self, key: str) -> bytes:
        resp = self.client.get_object(Bucket=self._bucket, Key=key)
        return resp["Body"].read()

    def url(self, key: str) -> str:
        if self._public_base_url:
            return f"{self._public_base_url.rstrip('/')}/{key}"
        if self._endpoint_url:
            return f"{self._endpoint_url.rstrip('/')}/{self._bucket}/{key}"
        return f"https://{self._bucket}.s3.amazonaws.com/{key}"
