"""Operator-table benchmark, candidate operator analysis and the physics ranking.

Pins the published conventions established by the operator benchmark, the
equivariant-structure convention of the coupling engine, the structural
(complex-structure independent) identification of Koszul levels, the D-flat
singlet criterion, and the recorded artifacts.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from string_sm_sat.geometry.cicy import benchmark  # noqa: E402
from string_sm_sat.physics.equivariance import CharacterGroup  # noqa: E402
from string_sm_sat.physics.superpotential import (DownstairsSpectrum,  # noqa: E402
                                                  operator_table)
from string_sm_sat.physics.yukawa import structural_identification  # noqa: E402


def artifact(path):
    full = ROOT / path
    if not full.exists():
        pytest.skip(f'{path} not present')
    return json.loads(full.read_text())


# --- conventions -------------------------------------------------------------

def test_bilinear_rpv_needs_a_singlet_insertion():
    """A bare 5bar 5_H term is absent by construction; with no neutral singlet
    monomial available the bilinear is forbidden to all orders."""
    spectrum = DownstairsSpectrum((1, 2, 3), ((4, 5), (1, 2), (1, 3)), (4, 5), (1, 2), ())
    assert operator_table(spectrum)['L H_u (bilinear RPV)']['verdict'] == \
        'FORBIDDEN_BY_SELECTION_RULE'
    # a directed 2-cycle supplies neutral monomials, so the term reappears at order two
    cycle = DownstairsSpectrum((1, 2, 3), ((4, 5), (1, 2), (1, 3)), (4, 5), (1, 2),
                               ((1, 2), (2, 1)))
    assert operator_table(cycle)['L H_u (bilinear RPV)']['verdict'] == \
        'ALLOWED_BY_SELECTION_RULE'


def test_slot_label_matches_the_wilson_line_shift_convention():
    """A piece chi on a bundle with structure e sits in the unshifted component
    chi - e, which is exactly what wilson_line.shift counts."""
    from candidate_yukawa import slot_label
    group = CharacterGroup((2, 2))
    row = (5, 7, 11, 13)                      # multiplicities per label
    for piece in group.labels:
        for e in group.labels:
            shifted = group.shift(row, e)
            assert group.multiplicity(shifted, piece) == \
                group.multiplicity(row, slot_label(group, piece, e))
    z4 = CharacterGroup((4,))                 # a group where the sign matters
    row4 = (2, 3, 5, 7)
    for piece in z4.labels:
        for e in z4.labels:
            assert z4.multiplicity(z4.shift(row4, e), piece) == \
                z4.multiplicity(row4, slot_label(z4, piece, e))


def test_structural_identification():
    geometry = benchmark('7862')
    # a -1 entry kills H^*(A, O(k)): the class is level 1 for every member
    level, ambient, structural = structural_identification(geometry, (-1, 2, -5, 2))
    assert level == 1 and ambient == (-3, 0, -7, 0) and structural
    level, ambient, structural = structural_identification(geometry, (1, -2, 3, 0))
    assert level == 0 and structural


def test_d_flat_singlets_are_those_on_directed_cycles():
    from rank_candidates import cycle_edges
    assert cycle_edges(((1, 2), (2, 1), (2, 3))) == ((1, 2), (2, 1))
    assert cycle_edges(((1, 2), (2, 3), (3, 1), (4, 5))) == ((1, 2), (2, 3), (3, 1))
    assert cycle_edges(((1, 2), (3, 4))) == ()


# --- recorded artifacts ------------------------------------------------------

def test_recorded_operator_benchmark():
    summary = artifact('benchmarks/operator-benchmark-all.json')
    tally = summary['tally']
    for kind in ('SuperPotential', 'DTerms', 'FITerms'):
        assert tally[f'{kind}/tables'] == 2012
        assert tally[f'{kind}/exact'] == 2012, kind
    for kind in ('Dim4Proton', 'Dim5Proton', 'RParVio', 'HiggsMass'):
        assert tally[f'{kind}/tables'] == 2012
        # with the published conventions made explicit, everything agrees
        assert tally[f'{kind}/classes'] == tally[f'{kind}/classes_agree'], kind
        assert tally[f'{kind}/tables_classes_exact'] == 2012, kind
    assert tally['HiggsMass/cells'] == tally['HiggsMass/cells_agree'] == 18108
    assert tally['Dim5Proton/classes'] == 60360
    assert tally['Dim4Proton/classes'] == 36216
    assert summary['index_orders']['Dim5Proton'] == [3, 0, 1, 2]


def test_absence_is_explained_by_stated_scan_conditions():
    summary = artifact('benchmarks/x7862/absence-resolution.json')
    assert summary['candidates_explained'] == 11
    assert summary['published_violating_R2'] == 0
    assert summary['published_x7862_violating_R1'] == 0
    by_id = {r['candidate_id'][-3:]: r['violates'] for r in summary['candidates']}
    assert by_id['A08'] == ['R2_vector_like_pairs'] == by_id['A09']
    assert by_id['A01'] == ['R1_charge_range']
    assert not any(r['colour_triplet_higgs'] for r in summary['candidates'])


def test_candidate_yukawa_records_are_consistent():
    data = artifact('benchmarks/x7862/candidate-yukawa.json')
    for candidate in data['candidates']:
        for configuration in candidate['configurations']:
            for block in configuration['higgs_choices']:
                for name in ('Y_u', 'Y_d', 'Y_e'):
                    matrix = block[name]
                    assert 'DIMENSION_MISMATCH' not in matrix.get('notes', [])
                    if matrix.get('status') == 'COMPUTED':
                        assert matrix['complex_structure_independent'] is True
                assert 'cubic_operators' in block
    # none of the eleven has a leading-order top Yukawa
    for candidate in data['candidates']:
        ranks = {b['Y_u']['rank'] for c in candidate['configurations']
                 for b in c['higgs_choices']}
        assert ranks == {0}, candidate['candidate_id']


def test_recorded_singlet_validation():
    summary = artifact('benchmarks/x7862/singlet-spectrum-validation.json')
    assert summary['genuine_differences'] == 0
    assert summary['matches'] + summary['differ_only_on_unevaluated'] == summary['models']


def test_recorded_physics_ranking():
    summary = artifact('benchmarks/x7862/physics-ranking.json')
    orbits = summary['orbits']
    assert len(orbits) == 21
    assert sum(r['class'] == 'additional' for r in orbits) == 11
    for r in orbits:
        assert r['verdict'] in ('STRONG_CANDIDATE', 'PHENOMENOLOGICALLY_PROBLEMATIC', 'UNKNOWN')
        # a problematic verdict must rest on a recorded exact reason in every choice
        if r['verdict'] == 'PHENOMENOLOGICALLY_PROBLEMATIC':
            assert r['categories'] == {'PHENOMENOLOGICALLY_PROBLEMATIC': r['choices']}


def test_recorded_kahler_benchmark():
    """Kahler operators: exact under the reading without trivial |S|^2 factors,
    and clearly not under the other reading, so the convention is determined."""
    report = artifact('benchmarks/kahler-benchmark-all.json')
    exact = report['without |S|^2 factors']
    for kind, cells in (('GMTerm', 2012), ('NeutrinoKahler', 6036), ('Kin5', 18108)):
        assert exact[f'{kind}/tables'] == 2012
        assert exact[f'{kind}/exact'] == 2012, kind
        assert exact[f'{kind}/cells'] == exact[f'{kind}/agree'] == cells, kind
    other = report['with |S|^2 factors']
    assert other['GMTerm/exact'] < 100 and other['Kin5/exact'] == 0


def test_ranking_outcome_and_baseline():
    """No orbit on X7862/(Z2xZ2) -- published or additional -- is a strong candidate,
    and the additional orbits fail for the same kinds of reasons as the published."""
    summary = artifact('benchmarks/x7862/physics-ranking.json')
    assert summary['verdicts'] == {
        'additional:PHENOMENOLOGICALLY_PROBLEMATIC': 9, 'additional:UNKNOWN': 2,
        'published:PHENOMENOLOGICALLY_PROBLEMATIC': 7, 'published:UNKNOWN': 3}
    by_id = {r['id'][-3:]: r for r in summary['orbits']}
    assert by_id['A04']['verdict'] == by_id['A06']['verdict'] == 'UNKNOWN'
    # the only additional orbits whose up-type Yukawa can reach rank three
    assert by_id['A04']['Yu_cap'] == by_id['A06']['Yu_cap'] == [3]
    assert by_id['A04']['Yu_cap_Dflat'] == [3]
    # no additional orbit has a leading-order top Yukawa
    assert all(by_id[f'A{i:02d}']['top_leading'] == 0 for i in range(1, 12))
    # nine of eleven forbid dimension-five proton decay to all orders, everywhere
    forbid = [i for i in range(1, 12)
              if by_id[f'A{i:02d}']['QQQL_forbidden'] == by_id[f'A{i:02d}']['choices']]
    assert len(forbid) == 9
