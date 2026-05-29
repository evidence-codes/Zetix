from __future__ import annotations

from pathlib import Path

import pytest
from zetix_api.storage import LocalObjectStorage, ObjectStorage


def test_local_storage_put_get_url_roundtrip(tmp_path) -> None:
    store = LocalObjectStorage(tmp_path)
    assert isinstance(store, ObjectStorage)

    key = "snapshots/acme/index.bin"
    locator = store.put(key, b"hello-snapshot")
    assert Path(locator).is_file()
    assert store.get(key) == b"hello-snapshot"

    url = store.url(key)
    assert url.startswith("file://")
    assert url.endswith("index.bin")


def test_local_storage_rejects_path_traversal(tmp_path) -> None:
    store = LocalObjectStorage(tmp_path)
    with pytest.raises(ValueError):
        store.put("../escape.txt", b"nope")


def test_s3_storage_construction_no_network() -> None:
    pytest.importorskip("boto3")
    from zetix_api.storage import S3ObjectStorage

    # Construction must not create a client or touch the network.
    store = S3ObjectStorage(
        bucket="zetix-snapshots",
        endpoint_url="https://s3.example.com",
        region="us-east-1",
    )
    assert isinstance(store, ObjectStorage)
    assert store.url("a/b.bin") == "https://s3.example.com/zetix-snapshots/a/b.bin"


def test_s3_storage_requires_bucket(monkeypatch) -> None:
    pytest.importorskip("boto3")
    from zetix_api.storage import S3ObjectStorage

    monkeypatch.delenv("ZETIX_S3_BUCKET", raising=False)
    with pytest.raises(ValueError):
        S3ObjectStorage(bucket=None)
