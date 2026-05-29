"""Smoke test for the search-quality eval harness.

Runs the harness on the synthetic set and asserts the result has the expected shape and
that accuracies are valid probabilities. Deliberately does NOT assert the M1 Top-3 > 80%
bar — that requires the real OpenCLIP model and a real labelled 10k catalog, not the
deterministic stub.
"""

from __future__ import annotations

from eval import evaluate, format_report, synthetic_dataset
from eval.harness import TOP_KS


def test_synthetic_eval_structure_and_ranges():
    result = evaluate(synthetic_dataset())

    # Aggregate Top-k keys present and in [0, 1].
    for k in TOP_KS:
        key = f"top{k}"
        assert key in result, f"missing aggregate key {key}"
        assert 0.0 <= result[key] <= 1.0, f"{key}={result[key]} out of range"

    # Monotonic: a hit at Top-1 is also a hit at Top-3 and Top-5.
    assert result["top1"] <= result["top3"] <= result["top5"]

    # Per-category breakdown present, with valid counts and accuracies.
    assert "per_category" in result
    assert result["per_category"], "expected at least one category"
    total = 0
    for stats in result["per_category"].values():
        assert stats["count"] >= 1
        total += stats["count"]
        for k in TOP_KS:
            assert 0.0 <= stats[f"top{k}"] <= 1.0
    assert total == result["n_queries"]

    # Per-query records line up with the query set.
    assert len(result["queries"]) == result["n_queries"] == len(synthetic_dataset().queries)
    for q in result["queries"]:
        assert {"query_id", "expected_id", "rank", "hit_top1", "hit_top3", "hit_top5"} <= set(q)


def test_report_renders():
    result = evaluate(synthetic_dataset())
    report = format_report(result)
    assert "Top-3" in report
    assert "Per-category accuracy" in report
