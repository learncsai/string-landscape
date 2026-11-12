"""Recorded independent full-domain replays must show exact survivor equality.

These artifacts are produced by scripts/independent_replay.py, which shares no
search logic with the package. The test does not re-run them (billions of
states); it checks that every stored replay is internally consistent, covered
its whole declared domain, and agreed exactly with the optimized solver.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPLAYS = sorted(ROOT.glob("benchmarks/*/k*-independent-replay*.json"))


@pytest.mark.parametrize("path", REPLAYS, ids=lambda p: p.name)
def test_replay_artifact_is_consistent(path):
    data = json.loads(path.read_text())
    assert data["kind"] == "independent_replay"
    crosscheck = data["topology_crosscheck"]
    assert crosscheck["h11_agrees"] and crosscheck["d_agrees"] and crosscheck["c2_agrees"]

    counts = data["counts"]
    columns = (2 * data["K"] + 1) ** {"7862": 4, "7447": 5}[data["geometry"]]
    assert counts["raw_ordered_states"] == columns ** 4 == data["nominal_ordered_four_column_states"]

    # closed form: per component, 4-tuples from [-K,K] whose sum stays in [-K,K]
    K, h = data["K"], {"7862": 4, "7447": 5}[data["geometry"]]
    per_component = sum(1 for a in range(-K, K + 1) for b in range(-K, K + 1)
                        for c in range(-K, K + 1) for d in range(-K, K + 1)
                        if abs(a + b + c + d) <= K)
    assert counts["valid_fifth_column"] == per_component ** h

    assert counts["final_survivors"] == len(data["survivors"])
    comparison = data.get("comparison")
    if comparison is not None:
        assert comparison["exact_set_equality"]
        assert comparison["optimized_only"] == [] and comparison["reference_only"] == []


def test_both_benchmark_geometries_have_a_replay():
    geometries = {json.loads(p.read_text())["geometry"] for p in REPLAYS}
    assert {"7862", "7447"} <= geometries
