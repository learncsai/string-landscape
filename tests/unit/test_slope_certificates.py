"""Exact slope certificates: the Polya hierarchy and the interior-zero decision."""
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.physics.stability import (decide_interior_slope_zero, polya_forms,
                                             polya_obstruction, verify_polya_certificate)

PUBLISHED = [(1, -3, 0, 2), (0, 1, 0, -1), (0, 1, 0, -1), (0, 0, -1, 1), (-1, 1, 1, -1)]
SPURIOUS = [(-3, -1, 1, 2), (0, 1, -1, 0), (0, 1, -1, 0), (1, 1, -1, -1), (2, -2, 2, -1)]


def test_polya_degree_zero_is_the_signed_matrix_test():
    geometry = benchmark('7862')
    # N = 0: the coefficients of t^T M(k) t, i.e. the distinct off-diagonal entries
    assert len(polya_forms(geometry, 0)) == 6
    # (sum t)^N q has all coefficients >= 0 whenever q does
    assert verify_polya_certificate(geometry, (1, 0, 0, 0), 0)
    assert verify_polya_certificate(geometry, (1, 0, 0, 0), 3)


def test_polya_certificate_is_sound_and_found():
    geometry = benchmark('7862')
    certificate = polya_obstruction(geometry, SPURIOUS)
    assert certificate is not None and certificate['N'] == 0
    k = tuple(sum(c * col[i] for c, col in zip(certificate['c'], SPURIOUS)) for i in range(4))
    assert list(k) == certificate['k']
    assert verify_polya_certificate(geometry, k, certificate['N'])
    # a published, poly-stable model never receives a certificate
    assert polya_obstruction(geometry, PUBLISHED) is None


def test_polya_gains_nothing_when_d_ijj_vanishes():
    """Proposition 4.4: with zero diagonal, positivity on the open orthant already
    forces nonnegative coefficients, so higher Polya degrees add no certificates."""
    geometry = benchmark('7862')
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                for d in range(-2, 3):
                    k = (a, b, c, d)
                    if verify_polya_certificate(geometry, k, 3):
                        assert verify_polya_certificate(geometry, k, 0), k


def test_polya_strictly_extends_degree_zero_on_a_synthetic_geometry():
    """2 t1^2 - 2 t1 t2 + 2 t2^2 is positive on the orthant but has a negative
    coefficient; multiplying by (t1 + t2) gives 2 t1^3 + 2 t2^3."""
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Stub:
        h11: int
        d: tuple

    # d_111 = 2, d_112 = -1 (all orderings), d_122 = 2 (all orderings), d_222 = 0
    d = (((2, -1), (-1, 2)), ((-1, 2), (2, 0)))
    geometry = Stub(2, d)
    assert not verify_polya_certificate(geometry, (1, 0), 0)
    assert verify_polya_certificate(geometry, (1, 0), 1)


def test_interior_zero_decision():
    geometry = benchmark('7862')
    decision = decide_interior_slope_zero(geometry, PUBLISHED)
    assert decision['status'] == 'STABLE_CERTIFIED'
    assert decision['t'] == ['1', '1', '1', '1']
    # rank below h-1 is refused, not guessed
    assert decide_interior_slope_zero(
        geometry, [(1, -1, 0, 0), (1, -1, 0, 0), (-1, 1, 0, 0), (-1, 1, 0, 0), (0, 0, 0, 0)]
    )['status'] == 'UNDECIDED'


def test_decision_never_rejects_a_published_model():
    """Soundness: published catalog models are poly-stable, so the exact decision
    must never call one of them unstable. (Two bugs -- a dropped positive root and
    a reversed polynomial remainder -- were caught by exactly this check.)"""
    import json
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    catalog = root / 'data/processed/published_gut_models.json'
    if not catalog.exists():
        import pytest
        pytest.skip('catalog not converted')
    sys.path.insert(0, str(root / 'scripts'))
    from phase8_suite import geometry_for
    data = json.loads(catalog.read_text())
    records = {r['number']: r for r in data['geometries']}
    stable = 0
    for key in ('7862,2', '7862,4', '7447,2'):
        number = int(key.split(',')[0])
        geometry = geometry_for(records[number])
        for model in data['models'][key][:40]:
            status = decide_interior_slope_zero(geometry, model)['status']
            assert status != 'UNSTABLE_CERTIFIED', (key, model)
            stable += status == 'STABLE_CERTIFIED'
    assert stable >= 60
