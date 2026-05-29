# models — embedding-model pipeline: conversion, INT8 quantisation, eval harness. EPIC-1,2.
# Native tool: Python (PyTorch / OpenCLIP / TFLite / coremltools).
# `convert` + `quantise` feed the on-device apps; `eval` gates Milestone M1.
.PHONY: convert quantise eval build test clean

# Python interpreter. The harness needs fastapi + numpy (server deps), so prefer the
# server venv created by `make server-bootstrap`; fall back to the ambient python3
# (e.g. CI, where the server package is already installed). Override with
# `make eval PYTHON=python3.11`.
SERVER_VENV := ../server/.venv/bin/python
PYTHON ?= $(if $(wildcard $(SERVER_VENV)),$(SERVER_VENV),python3)

convert:  ; @echo "[models] convert — not implemented yet (EPIC-2)"    # -> CLIP/MobileNet -> TFLite/CoreML/ONNX
quantise: ; @echo "[models] quantise — not implemented yet (EPIC-2)"   # -> INT8 quantise to <25MB (NFR-P6)

# Search-quality eval (TASKS 1.E.2–1.E.4): Top-1/3/5 + per-category accuracy through the
# real /admin/catalog + /search seams. Runs on the synthetic set with zero external data.
# Real M1 (Top-3 > 80% on 10k) needs ZETIX_EMBEDDER=openclip + a real --dataset.
eval:     ; @$(PYTHON) -m eval                                         # -> Top-3 accuracy (M1 gate)

build:    convert quantise

# Smoke test for the eval harness (synthetic set; does NOT assert the >80% bar).
test:     ; @$(PYTHON) -m pytest eval -q

clean:    ; @echo "[models] clean — nothing to clean yet"
