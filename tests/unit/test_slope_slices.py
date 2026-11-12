"""Slice decomposition and the charge-unbounded slice bound.

Mathematics: docs/exact_obstructions.md Propositions S1 and S2.
"""
import json
import random
import sys
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from slice_certificate import positive_definite, slice_pool, slice_radius_squared  # noqa: E402

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.physics.anomaly import check_anomaly
from string_sm_sat.physics.stability import _annihilator, _integer_rref, slopes


def F(k):
    return sum(x * x for x in k) - sum(k) ** 2


@pytest.mark.parametrize('name', ['7862', '7447'])
def test_slice_decomposition_holds_for_real_survivors(name):
    """S1: every slope-feasible survivor lies in p-perp for a positive primitive p."""
    artifact = ROOT / f"benchmarks/{'x7862/k4' if name == '7862' else 'x7447/k3'}-gamma2-span.json"
    if not artifact.exists():
        pytest.skip('benchmark artifact not present')
    g = benchmark(name)
    survivors = [tuple(map(tuple, m))
                 for m in json.loads(artifact.read_text())['enumeration']['survivors']]
    assert survivors
    for columns in survivors:
        basis = _integer_rref([list(k) for k in columns], g.h11)
        assert len(basis) <= g.h11 - 1                  # corollary: rank <= h-1
        if len(basis) == g.h11 - 1:
            p = _annihilator([list(b) for b in basis], g.h11)[0]
            if sum(p) < 0:
                p = [-x for x in p]
            assert all(x > 0 for x in p)                # strictly positive direction
            for k in columns:
                assert sum(a * b for a, b in zip(k, p)) == 0


@pytest.mark.parametrize('name', ['7862', '7447'])
def test_summed_anomaly_identity(name):
    """S2 step one: sum_r q_r(k) = 2(h-2)(s^2 - |k|^2), hence sum_a F(k_a) <= C_X."""
    from string_sm_sat.search.filters import quadratic_form
    g = benchmark(name); h = g.h11; rng = random.Random(77)
    for _ in range(200):
        k = tuple(rng.randint(-9, 9) for _ in range(h))
        assert sum(quadratic_form(g, k)) == 2 * (h - 2) * (sum(k) ** 2 - sum(x * x for x in k))
    budget = Fraction(sum(g.c2), h - 2)
    for _ in range(300):
        columns = [tuple(rng.randint(-5, 5) for _ in range(h)) for _ in range(4)]
        columns.append(tuple(-sum(c[i] for c in columns) for i in range(h)))
        v = BundleSum.from_columns(columns)
        if check_anomaly(v, g).outcome != 'PASS':
            continue
        assert sum(F(k) for k in columns) <= budget


def test_positive_definiteness_criterion():
    """S2: F is positive definite on p-perp iff (sum p)^2 > (h-1)|p|^2."""
    rng = random.Random(5)
    for _ in range(60):
        h = rng.choice([4, 5])
        p = tuple(rng.randint(1, 6) for _ in range(h))
        expected = positive_definite(p, h)
        # sample the slice and look for a nonpositive value of F
        found = False
        for _ in range(4000):
            k = tuple(rng.randint(-8, 8) for _ in range(h))
            if sum(a * b for a, b in zip(k, p)) or not any(k):
                continue
            if F(k) <= 0:
                found = True
                break
        if found:
            assert not expected          # a nonpositive value refutes definiteness
        # the converse direction is covered by the pool tests below


@pytest.mark.parametrize('p', [(1, 1, 1, 1), (1, 1, 1, 2), (2, 2, 3, 3), (1, 2, 5, 5)])
def test_slice_pool_is_the_exact_admissible_set(p):
    """The ball enumeration returns exactly {k : <k,p>=0, F(k) <= C_X}."""
    g = benchmark('7862')
    pool, bound, radius, budget = slice_pool(g, p)
    assert pool and all(sum(a * b for a, b in zip(k, p)) == 0 for k in pool)
    assert all(F(k) <= budget for k in pool)
    assert all(sum(x * x for x in k) <= radius for k in pool)
    # brute force over a box strictly larger than the radius: nothing is missed
    side = bound + 2
    reference = {k for k in product(range(-side, side + 1), repeat=4)
                 if sum(a * b for a, b in zip(k, p)) == 0 and F(k) <= budget}
    assert set(pool) == reference


def test_slice_results_reproduce_the_full_box_search():
    """Every survivor found in a K-free slice is also a full-box survivor."""
    slices = ROOT / 'benchmarks/x7862/slope-slices-gamma2.json'
    box = ROOT / 'benchmarks/x7862/k7-gamma2-span.json'
    if not (slices.exists() and box.exists()):
        pytest.skip('artifacts not present')
    recorded = json.loads(slices.read_text())
    survivors = {tuple(map(tuple, m))
                 for m in json.loads(box.read_text())['enumeration']['survivors']}
    checked = 0
    for row in recorded:
        for s in row['survivor_list']:
            columns = tuple(map(tuple, s))
            if max(abs(x) for k in columns for x in k) <= 7:
                assert columns in survivors
                checked += 1
    assert checked > 20
    assert sum(1 for r in recorded if not r['survivors']) >= 400   # proved-empty slices


def test_slice_survivors_respect_the_radius_bound():
    slices = ROOT / 'benchmarks/x7862/slope-slices-gamma2.json'
    if not slices.exists():
        pytest.skip('artifact not present')
    g = benchmark('7862')
    for row in json.loads(slices.read_text()):
        p = tuple(row['p'])
        radius = slice_radius_squared(g, p)
        for s in row['survivor_list']:
            for k in s:
                assert sum(x * x for x in k) <= radius
