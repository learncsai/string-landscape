"""Exactness, soundness and dominance of the span slope obstruction.

Mathematical statements: docs/slope_obstruction_note.md Propositions 2-5.
"""
import random
from fractions import Fraction
from itertools import combinations, product
import pytest
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.physics.stability import (span_slope_obstruction, check_span_slope,
                                             necessary_stability, slope_matrix,
                                             signed_matrix_ok, slopes, solve_coefficients,
                                             slope_forms)

GEOMETRIES = ['7862', '7447']


def random_columns(rng, h, n, bound=3):
    return [tuple(rng.randint(-bound, bound) for _ in range(h)) for _ in range(n)]


@pytest.mark.parametrize('name', GEOMETRIES)
def test_witness_is_an_exact_obstruction(name):
    """Every emitted rejection carries a verifiable integer witness in the span."""
    g = benchmark(name); rng = random.Random(2024 + int(name)); found = 0
    for _ in range(1500):
        cols = random_columns(rng, g.h11, rng.randint(1, 5))
        witness = span_slope_obstruction(g, cols)
        if witness in (None, 'UNKNOWN_LINEALITY'):
            continue
        found += 1
        assert not signed_matrix_ok(slope_matrix(g, witness))     # one-signed and nonzero
        c = solve_coefficients(cols, witness)
        assert c is not None
        for i in range(g.h11):
            assert sum(c[a] * cols[a][i] for a in range(len(cols))) == witness[i]
    assert found > 50


@pytest.mark.parametrize('name', GEOMETRIES)
def test_never_rejects_a_slope_feasible_bundle(name):
    """Soundness: a candidate with a genuine positive common zero must survive."""
    g = benchmark(name); h = g.h11; rng = random.Random(99)
    for _ in range(600):
        cols = []
        for _ in range(5):
            k = [rng.randint(-6, 6) for _ in range(h - 1)]
            k.append(-sum(k)); rng.shuffle(k); cols.append(tuple(k))
        # t = (1,...,1) is an exact common zero-slope witness for these geometries
        assert not any(slopes(g, BundleSum.from_columns(cols), (Fraction(1),) * h))
        assert span_slope_obstruction(g, cols) in (None, 'UNKNOWN_LINEALITY')
        assert necessary_stability(g, [LineBundle(k) for k in cols], 1).outcome == 'PASS'


@pytest.mark.parametrize('name', GEOMETRIES)
def test_dominates_the_finite_coefficient_box(name):
    """Prop. 3: the complete test rejects whenever the {-1,0,1} box rejects."""
    g = benchmark(name); rng = random.Random(7); stronger = 0
    for _ in range(800):
        cols = random_columns(rng, g.h11, 5)
        box = necessary_stability(g, [LineBundle(k) for k in cols], 1).outcome == 'FAIL'
        span = span_slope_obstruction(g, cols) not in (None, 'UNKNOWN_LINEALITY')
        assert not (box and not span)
        stronger += span and not box
    assert stronger > 0            # strictly stronger on at least one sample


@pytest.mark.parametrize('name', GEOMETRIES)
def test_monotone_in_the_column_set(name):
    """Prop. 5: enlarging the set can only preserve an obstruction."""
    g = benchmark(name); rng = random.Random(13)
    for _ in range(400):
        cols = random_columns(rng, g.h11, 4)
        if span_slope_obstruction(g, cols[:2]) in (None, 'UNKNOWN_LINEALITY'):
            continue
        for extra in (3, 4):
            assert span_slope_obstruction(g, cols[:extra]) not in (None,)


def test_shift_invariance_of_combinations():
    """With c1(V)=0 the combined matrix depends only on c modulo (1,1,1,1,1)."""
    g = benchmark('7862'); rng = random.Random(5)
    for _ in range(200):
        cols = [tuple(rng.randint(-4, 4) for _ in range(4)) for _ in range(4)]
        cols.append(tuple(-sum(c[i] for c in cols) for i in range(4)))
        matrices = [slope_matrix(g, k) for k in cols]
        c = [rng.randint(-2, 2) for _ in range(5)]
        for shift in (-2, 1, 3):
            a = tuple(sum(x * m[t] for x, m in zip(c, matrices)) for t in range(16))
            b = tuple(sum((x + shift) * m[t] for x, m in zip(c, matrices)) for t in range(16))
            assert a == b


def test_zero_matrix_is_not_an_obstruction():
    g = benchmark('7862')
    assert slope_matrix(g, (0, 0, 0, 0)) == (0,) * 16
    assert span_slope_obstruction(g, [(0, 0, 0, 0)]) is None
    assert check_span_slope(g, [(0, 0, 0, 0)]).outcome == 'PASS'


def test_single_column_case_matches_the_individual_test():
    """For one column the complete test reduces to the published individual test."""
    g = benchmark('7862')
    for k in product(range(-2, 3), repeat=4):
        individual = not signed_matrix_ok(slope_matrix(g, k))
        span = span_slope_obstruction(g, k and [k] or [k]) not in (None, 'UNKNOWN_LINEALITY')
        assert individual == span


@pytest.mark.parametrize('name', GEOMETRIES)
def test_extreme_rays_of_the_obstruction_cone(name):
    """The rays generate P and each is a genuine extreme ray."""
    from string_sm_sat.physics.stability import slope_cone_rays, slope_forms
    g = benchmark(name)
    rays = slope_cone_rays(g)
    forms = slope_forms(g)
    assert rays is not None and len(rays) == 2 * g.h11
    for r in rays:
        values = [sum(f[i] * r[i] for i in range(g.h11)) for f in forms]
        assert all(v >= 0 for v in values) and any(values)      # inside P, nonzero
        tight = [f for f, v in zip(forms, values) if v == 0]
        assert len(tight) >= g.h11 - 1                          # extreme


@pytest.mark.parametrize('name', GEOMETRIES)
def test_dual_and_primal_decisions_agree(name):
    """The fast dual decision matches the extreme-ray primal on every rank."""
    from string_sm_sat.physics.stability import span_obstructed, span_key
    g = benchmark(name); rng = random.Random(4242); ranks = {}
    for _ in range(1200):
        cols = random_columns(rng, g.h11, rng.randint(1, 5), 4)
        primal = span_slope_obstruction(g, cols)
        if primal == 'UNKNOWN_LINEALITY':
            continue
        ranks[len(span_key(cols, g.h11))] = True
        assert span_obstructed(g, cols) == (primal is not None)
    assert len(ranks) >= 4          # exercised several span ranks, dual and fallback
