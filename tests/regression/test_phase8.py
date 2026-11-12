"""Phase 8: the 68-geometry suite and its orbit comparison."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from phase8_suite import canonical, configuration_automorphisms, geometry_for  # noqa: E402

CATALOG = ROOT / 'data/processed/published_gut_models.json'


def record(number):
    catalog = json.loads(CATALOG.read_text())
    return next(r for r in catalog['geometries'] if r['number'] == number)


@pytest.mark.skipif(not CATALOG.exists(), reason='catalog not converted')
def test_configuration_automorphisms():
    # identical rows: every permutation of the four P^1 factors
    assert len(configuration_automorphisms(geometry_for(record(7862)))) == 24
    assert len(configuration_automorphisms(geometry_for(record(7447)))) == 120
    # the orbit representative is invariant under the automorphisms
    autos = configuration_automorphisms(geometry_for(record(7862)))
    columns = ((1, -3, 0, 2), (0, 1, 0, -1), (0, 1, 0, -1), (0, 0, -1, 1), (-1, 1, 1, -1))
    permuted = tuple(tuple(k[i] for i in (2, 0, 3, 1)) for k in columns)
    assert canonical(columns, autos) == canonical(permuted, autos)


def test_recorded_phase8_suite():
    """Soundness everywhere: no published model inside a box is ever missed.

    Our survivor sets are necessary-condition survivors, so they may contain
    extra orbits (classified in test_recorded_extra_classification); they must
    never lack a published one."""
    runs = []
    for name in ('phase8-suite.json', 'phase8-suite-h5-k2.json', 'phase8-suite-k3.json'):
        path = ROOT / 'benchmarks' / name
        if path.exists():
            runs += json.loads(path.read_text())['runs']
    if not runs:
        pytest.skip('suite artifacts not present')
    assert all(r['published_only'] == 0 for r in runs), [
        (r['geometry'], r['gamma'], r['K']) for r in runs if r['published_only']]
    for r in runs:
        if r['outcome'] == 'UNSAT_UNBOUNDED':
            assert r['published_total'] == 0
    assert any(r['h11'] == 6 for r in runs)
    assert len({r['geometry'] for r in runs}) == 68
    k2 = [r for r in runs if r['K'] == 2]
    assert sum(r['published_in_box'] for r in k2) == 9016
    k3 = [r for r in runs if r['K'] == 3]
    assert len(k3) == 60 and all(r['exact_set_equality'] for r in k3)


def test_recorded_extra_classification():
    path = ROOT / 'benchmarks/phase8-extras-classified.json'
    if not path.exists():
        pytest.skip('classification not present')
    data = json.loads(path.read_text())
    statuses = {e['status'] for e in data['extras']}
    assert statuses <= {'STABLE_CERTIFIED', 'UNSTABLE_CERTIFIED', 'NUMERIC_STABLE',
                        'NUMERIC_UNSTABLE'}
    # every certified-stable extra is an exact witness that verifies
    for e in data['extras']:
        if e['status'] == 'STABLE_CERTIFIED':
            assert e.get('kind') in ('EXACT_ALGEBRAIC', 'EXACT_RATIONAL', 'EXACT_ALGEBRAIC_SOLVE')
