# models

Embedding-model pipeline (Phases 1–2 / EPIC-1, EPIC-2). Part of the version-locked
spine: the converted/quantised model artifact is a cross-language dependency of both
apps, tracked by the root Makefile via `.make/model-converted.stamp`.

| Sub-dir | Purpose |
| --- | --- |
| `conversion/` | CLIP ViT-B/32 or MobileNet-V3 → TFLite (Android) / Core ML (iOS) / ONNX |
| `quantisation/` | INT8 quantisation to hit the < 25MB on-device target (NFR-P6) |
| `eval/` | Search-quality evaluation harness — Top-3 accuracy on 10k test set (gates M1) |

**Run:** `make models` (convert + quantise), `make eval` (quality gate). Native tool:
Python (PyTorch / OpenCLIP / TFLite / coremltools). **Status:** 🔴 not started.
