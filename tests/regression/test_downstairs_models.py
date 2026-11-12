"""Phase 9: reproduction of published downstairs heterotic standard models.

The Gamma-character content of the upstairs cohomology is input from the
published database; the descent, the Wilson-line projection and every upstairs
quantity are recomputed here.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from string_sm_sat.physics.equivariance import CharacterGroup, infer_group  # noqa: E402
from string_sm_sat.physics.wilson_line import (WilsonLine, acceptance_report,  # noqa: E402
                                               downstairs_spectrum,
                                               ten_multiplicities)

DATABASE = ROOT / 'data/processed/published_standard_models.json'
pytestmark = pytest.mark.skipif(not DATABASE.exists(), reason='SM database not converted')


def database():
    return json.loads(DATABASE.read_text())


def test_database_totals():
    data = database()
    assert data['model_count'] == 2113
    assert {m['gamma_order'] for m in data['models']} == {2, 4}


def test_character_group_arithmetic():
    g = CharacterGroup((2, 2))
    assert g.order == 4
    assert g.labels == ((0, 0), (0, 1), (1, 0), (1, 1))
    assert g.add((0, 1), (1, 1)) == (1, 0)
    assert g.negate((0, 1)) == (0, 1)          # exponent two
    assert g.multiply((1, 1), 2) == (0, 0)
    row = (5, 6, 7, 8)
    assert g.multiplicity(row, (1, 0)) == 7
    # shifting by chi then by -chi is the identity
    assert g.shift(g.shift(row, (0, 1)), g.negate((0, 1))) == row
    z4 = CharacterGroup((4,))
    assert z4.negate((1,)) == (3,) and z4.add((3,), (2,)) == (1,)


def test_infer_group_rejects_wrong_order():
    with pytest.raises(ValueError):
        infer_group([(0, 0), (0, 1)], 4)       # labels only span Z_1 x Z_2
    assert infer_group([(0, 0), (1, 1)], 4).moduli == (2, 2)


def test_regular_representation_gives_three_complete_families():
    """H^1(X, L_a) = 3 x regular representation yields exactly three 10s."""
    g = CharacterGroup((2, 2))
    wilson = WilsonLine(g, (0, 0), (0, 1))
    pieces = ten_multiplicities(g, wilson, (3, 3, 3, 3))
    assert pieces == {'Q': 3, 'u^c': 3, 'e^c': 3}


def test_wilson_line_splits_the_higgs_from_the_triplet():
    """A pair cohomology missing the triplet character gives a doublet only."""
    g = CharacterGroup((2, 2))
    wilson = WilsonLine(g, (0, 0), (0, 1))
    spectrum = downstairs_spectrum(
        g, wilson,
        [(3, 3, 3, 3)] + [(0, 0, 0, 0)] * 4,
        [(0, 1, 1, 1)] + [(0, 0, 0, 0)] * 9,
        [(0, 1, 1, 1)] + [(0, 0, 0, 0)] * 9)
    assert spectrum['higgs_pairs'] == 1
    assert not spectrum['exotics']
    assert spectrum['families']['Q'] == 3


@pytest.mark.parametrize('cicy', [7862, 7447])
def test_published_models_on_our_benchmark_geometries(cicy):
    """Every published downstairs model on a benchmark geometry is reproduced."""
    from reproduce_standard_model import infer_groups, verify
    data = database()
    models = [m for m in data['models'] if m['cicy'] == cicy]
    assert models
    groups = infer_groups(data['models'])
    complete = 0
    for record in models:
        result = verify(record, data['geometries'], True, groups)
        upstairs = result['upstairs']
        for name in ('c1_zero', 'no_proper_zero_subset', 'chiral_indices',
                     'anomaly_nef_pairings', 'bogomolov_pairing',
                     'span_slope_obstruction'):
            assert upstairs[name] == 'PASS', (cicy, name)
        assert upstairs['c2_matches_published']
        if result.get('descent') == 'UNKNOWN_INCOMPLETE_RECORD':
            continue
        complete += 1
        assert result['character_tables_consistent']
        assert result['charged_spectrum_matches'], result
        assert result['higgs_pairs_match']
        report = result['acceptance']
        assert report['three_chiral_families']
        assert not report['charged_chiral_exotics']
        assert report['higgs_doublet_pair']
    assert complete


def test_recorded_full_database_reproduction():
    """The stored artifact: the whole published catalog, reproduced."""
    artifact = ROOT / 'benchmarks/downstairs-reproduction-all.json'
    if not artifact.exists():
        pytest.skip('artifact not present')
    summary = json.loads(artifact.read_text())
    assert summary['records'] == 2113
    assert summary['upstairs_all_checks_pass'] == 2113
    complete = summary['complete_records']
    assert complete == 1948
    for key in ('character_tables_consistent', 'charged_spectrum_matches',
                'higgs_pairs_match', 'three_family_no_exotic_higgs'):
        assert summary[key] == complete, key
    assert summary['equivariant_structure_applied']


def test_equivariant_structure_is_load_bearing():
    """Dropping the equivariant-structure shift breaks the reproduction."""
    from reproduce_standard_model import infer_groups, verify
    data = database()
    groups = infer_groups(data['models'])
    models = [m for m in data['models'] if any(any(x) for x in (m.get('EquivStr') or []))]
    assert models
    disagreements = 0
    for record in models[:120]:
        with_shift = verify(record, data['geometries'], True, groups)
        without = verify(record, data['geometries'], False, groups)
        if with_shift.get('descent') == 'UNKNOWN_INCOMPLETE_RECORD':
            continue
        assert with_shift['charged_spectrum_matches']
        disagreements += not without['charged_spectrum_matches']
    assert disagreements > 0


def test_recorded_downstairs_search():
    """The search over our own upstairs survivors recovers the published models."""
    artifact = ROOT / 'benchmarks/x7862/downstairs-search-gamma4.json'
    if not artifact.exists():
        pytest.skip('search artifact not present')
    summary = json.loads(artifact.read_text())
    counters = summary['counters']
    assert counters['orbits_examined'] == 58              # our exhaustive Gamma=4 orbits
    assert counters['not_equivariant'] + counters['equivariant'] == 58
    assert counters['fully_determined'] == counters['equivariant']
    # every published orbit is found; the published database is a partial scan,
    # so finding more is expected and is not a contradiction
    assert summary['published_only'] == []
    assert summary['ours_orbits'] >= summary['published_orbits']
    assert summary['scope'].startswith('search over our own exhaustive upstairs')
