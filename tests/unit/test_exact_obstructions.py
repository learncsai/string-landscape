"""Exact obstructions from docs/exact_obstructions.md (P1, P2, P3, P5)."""
import json
import random
from itertools import product
from math import gcd
from pathlib import Path

import pytest

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.physics.anomaly import check_anomaly, check_bogomolov
from string_sm_sat.physics.index import bundle_index, index
from string_sm_sat.search.filters import quadratic_form, anomaly_budget

CATALOG = Path(__file__).resolve().parents[2] / "data/processed/published_gut_models.json"


@pytest.mark.parametrize('name', ['7862', '7447', 'bicubic', 'quintic'])
def test_index_identity(name):
    """P1: ind(wedge^2 V) = ind(V) for any rank-five sum with c1(V)=0."""
    g = benchmark(name); h = g.h11; rng = random.Random(17)
    for _ in range(200):
        columns = [tuple(rng.randint(-9, 9) for _ in range(h)) for _ in range(4)]
        columns.append(tuple(-sum(c[i] for c in columns) for i in range(h)))
        v = BundleSum.from_columns(columns)
        assert not any(v.c1)
        assert bundle_index(g, v) == bundle_index(g, v.wedge2())


@pytest.mark.parametrize('name,expected', [('7862', 2), ('7447', 2)])
def test_index_divisibility_constant(name, expected):
    """P2: d_X = gcd of all line-bundle indices, computed on {0..3}^h."""
    g = benchmark(name)
    d = 0
    for k in product(range(4), repeat=g.h11):
        d = gcd(d, index(g, LineBundle(k)))
    assert d == expected
    # the closed form for these two geometries: ind(L) = 2(e3(k)+e1(k))
    rng = random.Random(3)
    for _ in range(200):
        k = tuple(rng.randint(-9, 9) for _ in range(g.h11))
        e3 = sum(k[a] * k[b] * k[c] for a in range(g.h11)
                 for b in range(a + 1, g.h11) for c in range(b + 1, g.h11))
        assert index(g, LineBundle(k)) == 2 * (e3 + sum(k))


def test_index_divisibility_excludes_odd_gamma():
    """P2 consequence: d_X=2 makes ind(V) = -3|Gamma| impossible for odd |Gamma|."""
    g = benchmark('7862'); rng = random.Random(5)
    for _ in range(500):
        columns = [tuple(rng.randint(-6, 6) for _ in range(4)) for _ in range(4)]
        columns.append(tuple(-sum(c[i] for c in columns) for i in range(4)))
        assert bundle_index(g, BundleSum.from_columns(columns)) % 2 == 0


@pytest.mark.parametrize('name', ['7862', '7447'])
def test_partial_anomaly_budget_is_sound(name):
    """P3: a bundle satisfying the anomaly condition passes every prefix budget."""
    g = benchmark(name); h = g.h11; rng = random.Random(23)
    pool = [tuple(rng.randint(-3, 3) for _ in range(h)) for _ in range(400)]
    maxima = tuple(max(quadratic_form(g, k)[r] for k in pool) for r in range(h))
    budget = tuple(-2 * x for x in g.c2)
    checked = 0
    for _ in range(2000):
        columns = [rng.choice(pool) for _ in range(4)]
        columns.append(tuple(-sum(c[i] for c in columns) for i in range(h)))
        if any(abs(x) > 3 for x in columns[-1]):
            continue
        v = BundleSum.from_columns(columns)
        if check_anomaly(v, g).outcome != 'PASS':
            continue
        checked += 1
        partial = (0,) * h
        for m, k in enumerate(columns, start=1):
            partial = tuple(partial[r] + quadratic_form(g, k)[r] for r in range(h))
            assert anomaly_budget(partial, 5 - m, maxima, budget)
    assert checked > 20


def test_partial_anomaly_budget_rejects_a_hopeless_prefix():
    g = benchmark('7862')
    maxima = (24,) * 4
    budget = tuple(-2 * x for x in g.c2)
    assert anomaly_budget((0, 0, 0, 0), 4, maxima, budget)
    assert not anomaly_budget((-200, 0, 0, 0), 1, maxima, budget)


@pytest.mark.skipif(not CATALOG.exists(), reason='published catalog not converted')
def test_published_models_satisfy_bogomolov_and_anomaly():
    """P5 plus the anomaly rule against real published models."""
    catalog = json.loads(CATALOG.read_text())
    for key, identifier in (('7862,2', '7862'), ('7447,2', '7447')):
        g = benchmark(identifier)
        for matrix in catalog['models'][key]:
            v = BundleSum.from_columns(tuple(map(tuple, matrix)))
            assert check_anomaly(v, g).outcome == 'PASS'
            assert check_bogomolov(v, g).outcome == 'PASS'


@pytest.mark.skipif(not CATALOG.exists(), reason='published catalog not converted')
def test_divisibility_predictions_match_the_published_catalog():
    """P2 predicts zero models whenever d_X does not divide 3|Gamma|."""
    catalog = json.loads(CATALOG.read_text())
    from string_sm_sat.geometry.cicy import CICY
    predictions = 0
    for record in catalog['geometries']:
        configuration = tuple(tuple(row) for row in record['configuration'])
        ambient = tuple(sum(row) - 1 for row in configuration)
        g = CICY(str(record['number']), ambient, configuration, record['h11'],
                 record['h21'], tuple(record['symmetry_orders']), 'POSITIVE_ORTHANT')
        d = 0
        for k in product(range(4), repeat=g.h11):
            d = gcd(d, index(g, LineBundle(k)))
        for order in record['symmetry_orders']:
            if (3 * order) % d == 0:
                continue
            predictions += 1
            assert len(catalog['models'].get(f"{record['number']},{order}", [])) == 0
    assert predictions == 2
