"""Exact agreement with the published Oxford SU(5) GUT catalog (arXiv:1307.4787).

The comparison is at the level of ambient-row orbits of column-canonical
five-column matrices, restricted to the finite box of our search. See
scripts/compare_catalog.py for the equivalence conventions.
"""
import json
from pathlib import Path

import pytest

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import canonical_row_orbit
from string_sm_sat.physics.spectrum import check_indices
from string_sm_sat.physics.stability import check_span_slope
from string_sm_sat.physics.structure_group import check_c1, check_structure_group

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/processed/published_gut_models.json"

pytestmark = pytest.mark.skipif(not CATALOG.exists(),
                                reason="published catalog not converted")


def published(key):
    return [tuple(map(tuple, m)) for m in json.loads(CATALOG.read_text())["models"][key]]


def test_catalog_totals():
    data = json.loads(CATALOG.read_text())
    assert data["geometry_count"] == 68           # as stated by the database page
    assert data["model_count"] == 63325           # ditto


@pytest.mark.parametrize("key,identifier,gamma", [("7862,2", "7862", 2),
                                                  ("7447,2", "7447", 2)])
def test_published_models_pass_our_exact_checks(key, identifier, gamma):
    g = benchmark(identifier)
    for columns in published(key):
        v = BundleSum.from_columns(columns)
        assert check_c1(v).outcome == "PASS"
        assert check_structure_group(v).outcome == "PASS"
        assert check_indices(v, g, gamma).outcome == "PASS"
        assert check_span_slope(g, list(columns)).outcome == "PASS"


@pytest.mark.parametrize("K,expected_orbits", [(2, 5), (3, 7), (4, 10), (5, 10),
                                               (6, 10), (7, 10)])
def test_row_orbit_sets_equal_the_published_catalog(K, expected_orbits):
    """Our span-rule survivors reproduce the published catalog exactly in-box."""
    artifact = ROOT / f"benchmarks/x7862/k{K}-gamma2-span.json"
    if not artifact.exists():
        pytest.skip("benchmark artifact not present")
    g = benchmark("7862")
    run = json.loads(artifact.read_text())
    assert run["enumeration"]["complete"]
    assert run["domain"]["slope_rule"] == "span" and run["domain"]["K"] == K
    ours = {canonical_row_orbit(g, tuple(map(tuple, m)))
            for m in run["enumeration"]["survivors"]}
    inside = {canonical_row_orbit(g, m) for m in published("7862,2")
              if max(abs(x) for k in m for x in k) <= K}
    assert len(inside) == expected_orbits
    assert ours == inside


def test_gamma_four_catalog_agreement():
    """The larger Gamma=4 catalog: all 58 published models, exactly."""
    artifact = ROOT / "benchmarks/x7862/k5-gamma4-span.json"
    if not artifact.exists():
        pytest.skip("benchmark artifact not present")
    g = benchmark("7862")
    run = json.loads(artifact.read_text())
    assert run["enumeration"]["complete"] and run["domain"]["gamma"] == 4
    ours = {canonical_row_orbit(g, tuple(map(tuple, m)))
            for m in run["enumeration"]["survivors"]}
    inside = {canonical_row_orbit(g, m) for m in published("7862,4")
              if max(abs(x) for k in m for x in k) <= run["domain"]["K"]}
    assert len(inside) == 58
    assert ours == inside


def test_survivor_set_is_stable_from_K4_to_K7():
    """Empirical saturation, not a theorem: the set stops growing at K=4."""
    sets = {}
    for K in (4, 5, 6, 7):
        artifact = ROOT / f"benchmarks/x7862/k{K}-gamma2-span.json"
        if not artifact.exists():
            pytest.skip("benchmark artifacts not present")
        sets[K] = {tuple(map(tuple, m))
                   for m in json.loads(artifact.read_text())["enumeration"]["survivors"]}
    assert sets[4] == sets[5] == sets[6] == sets[7]
    assert len(sets[4]) == 240
    assert max(abs(x) for s in sets[7] for k in s for x in k) == 4


def test_finite_coefficient_box_keeps_a_spurious_orbit():
    """Documented incompleteness of the published box rule, at K=3 and K=4."""
    g = benchmark("7862")
    for K in (3, 4):
        box = ROOT / f"benchmarks/x7862/k{K}-gamma2-box.json"
        span = ROOT / f"benchmarks/x7862/k{K}-gamma2-span.json"
        if not (box.exists() and span.exists()):
            pytest.skip("benchmark artifacts not present")
        orbits = []
        for path in (box, span):
            run = json.loads(path.read_text())
            orbits.append({canonical_row_orbit(g, tuple(map(tuple, m)))
                           for m in run["enumeration"]["survivors"]})
        assert orbits[1] < orbits[0]                 # span strictly smaller
        assert len(orbits[0]) - len(orbits[1]) == 1  # exactly one spurious orbit


@pytest.mark.parametrize("K,expected_orbits", [(1, 0), (2, 56), (3, 87), (4, 93)])
def test_x7447_catalog_agreement(K, expected_orbits):
    """h11=5 benchmark against the 93 published {7447, Gamma=2} models."""
    artifact = ROOT / f"benchmarks/x7447/k{K}-gamma2-span.json"
    if not artifact.exists():
        pytest.skip("benchmark artifact not present")
    g = benchmark("7447")
    run = json.loads(artifact.read_text())
    assert run["enumeration"]["complete"]
    ours = {canonical_row_orbit(g, tuple(map(tuple, m)))
            for m in run["enumeration"]["survivors"]}
    inside = {canonical_row_orbit(g, m) for m in published("7447,2")
              if max(abs(x) for k in m for x in k) <= K}
    assert len(inside) == expected_orbits
    assert ours == inside
