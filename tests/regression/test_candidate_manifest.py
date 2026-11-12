"""The frozen audit of the additional X7862 candidates.

Every condition of the Oxford heterotic standard-model construction, checked
explicitly rather than by our three-condition search shorthand.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'benchmarks/x7862/candidate-manifest.json'
pytestmark = pytest.mark.skipif(not MANIFEST.exists(), reason='manifest not built')


def manifest():
    return json.loads(MANIFEST.read_text())


def test_manifest_shape():
    data = manifest()
    assert data['frozen'] and data['geometry'] == '7862' and data['gamma_order'] == 4
    assert data['symmetry_number'] == 5
    assert len(data['candidates']) == 11
    assert len({c['candidate_id'] for c in data['candidates']}) == 11
    assert data['symmetry_realisation']['cyclic_factors'] == [2, 2]
    assert data['symmetry_realisation']['acts_freely'] == 'True'


@pytest.mark.parametrize('condition', [
    'c1_zero', 'structure_group_no_proper_zero_subset', 'anomaly_effectivity',
    'bogomolov', 'span_slope_obstruction', 'generation_index',
    'no_anti_families', 'three_families_upstairs'])
def test_every_upstairs_condition_passes(condition):
    for candidate in manifest()['candidates']:
        assert candidate['upstairs'][condition] == 'PASS', candidate['candidate_id']


def test_generation_index_and_cohomology():
    for candidate in manifest()['candidates']:
        upstairs = candidate['upstairs']
        assert upstairs['index_V'] == upstairs['index_wedge2'] == -12   # -3|Gamma|
        h = candidate['cohomology']['h_V']
        assert h == [0, 12, 0, 0]                                       # 3|Gamma|, no anti-families
        w = candidate['cohomology']['h_wedge2V']
        assert w[0] == 0 and w[3] == 0
        assert w[1] == 12 + w[2] and w[2] > 0                           # 3|Gamma| + n_h, n_h > 0


def test_poly_stability_is_an_exact_witness():
    """Never a bare optimizer result: every candidate carries an exact witness."""
    for candidate in manifest()['candidates']:
        witness = candidate['upstairs']['poly_stability_witness']
        assert witness['kind'] in ('EXACT_RATIONAL', 'EXACT_ALGEBRAIC'), candidate['candidate_id']


def test_equivariance_and_character_tables():
    for candidate in manifest()['candidates']:
        assert candidate['equivariance']['all_bundles_equivariant']
        assert not candidate['character_tables']['undetermined']


def test_downstairs_conditions():
    for candidate in manifest()['candidates']:
        downstairs = candidate['downstairs']
        assert downstairs['full_conditions_met']
        assert downstairs['accepted_count'] > 0
        for accepted in downstairs['accepted']:
            assert accepted['families'] == {'Q': 3, 'u^c': 3, 'e^c': 3, 'd^c': 3, 'L': 3}
            assert accepted['higgs_pairs'] >= 1
            assert accepted['colour_triplet_pairs'] == 0
            # the published scan used exactly this Wilson line
            assert accepted['wilson_line'] == [[0, 0], [0, 1]]


def test_none_is_in_the_published_database():
    for candidate in manifest()['candidates']:
        assert not candidate['present_in_published_sm_database']
        assert candidate['published_downstairs_matches'] == []


def test_absence_reasons_are_recorded():
    data = manifest()
    identified = [c for c in data['candidates'] if c['absence_classification'] == 'identified']
    unknown = [c for c in data['candidates'] if c['absence_classification'] == 'unknown']
    assert len(identified) == 9 and len(unknown) == 2
    assert {c['candidate_id'] for c in unknown} == {'X7862-G4-A08', 'X7862-G4-A09'}
    for candidate in identified:
        assert candidate['absence_reason'] != ['unknown']
        assert (candidate['max_abs_charge'] > 3) or (candidate['additional_massless_U1'] != 1)
