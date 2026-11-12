"""Step 6: the Yukawa engine against the published tables.

Covers the exact U(1)^4 selection rule, the exhaustive singlet-monomial
enumeration, the Gamma-covariance self-test of the trilinear form, and the
recorded benchmark artifacts.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from string_sm_sat.geometry.cicy import benchmark  # noqa: E402
from string_sm_sat.physics.selection_rules import (add, classify,  # noqa: E402
                                                   enumerate_monomials, five, fivebar,
                                                   monoid_membership, residual_charge,
                                                   singlet, ten)
from string_sm_sat.physics.superpotential import (DownstairsSpectrum,  # noqa: E402
                                                  mu_term, operator_table, yukawa_down,
                                                  yukawa_up)
from string_sm_sat.physics.yukawa import (contract_higgs, covariance_defect,  # noqa: E402
                                          equivariant_coupling, koszul_pure_level,
                                          monomial_tensor, triple_coupling)

SYMMETRIES = ROOT / 'data/processed/published_symmetries.json'
MODEL_16 = [(1, 0, -3, 0), (1, -2, 3, 0), (0, 0, 1, -1), (0, 0, 1, -1), (-2, 2, -2, 2)]


def product(*bundles):
    return tuple(sum(b[i] for b in bundles) for i in range(4))


def lift_for_x7862():
    from string_sm_sat.physics.equivariant_cohomology import cyclic_lift, to_matrix
    entry = json.loads(SYMMETRIES.read_text())['symmetries']['7862'][4]
    assert entry['group_order'] == 4 and entry['cyclic_factors'] == [2, 2]
    return cyclic_lift([to_matrix(m) for m in entry['generators']],
                       entry['cyclic_factors']), entry['cyclic_factors']


# --- the selection rule -----------------------------------------------------

def test_charges_live_in_the_quotient_lattice():
    assert sum(ten(3)) == 1 and sum(fivebar(1, 2)) == 2
    assert sum(five(1, 2)) == -2 and sum(singlet(1, 2)) == 0
    # a 10 5bar 5bar coupling is neutral exactly when all five indices differ
    assert residual_charge(add(ten(1), fivebar(2, 3), fivebar(4, 5))) == (0,) * 5
    assert residual_charge(add(ten(1), fivebar(1, 3), fivebar(4, 5))) != (0,) * 5
    # an entry sum that is not a multiple of five can never be fixed by singlets
    assert residual_charge(add(ten(1), ten(2))) is None


def test_monoid_membership_is_a_flow_problem():
    # 2 -> 5 is unavailable directly but reachable as 2 -> 1 -> 5
    available = [(2, 1), (1, 5)]
    feasible, insertions, monomial = monoid_membership(singlet(2, 5), available)
    assert feasible and insertions == 2
    assert dict(monomial) == {(2, 1): 1, (1, 5): 1}
    # with no path there is no monomial at any order: an exact negative
    assert monoid_membership(singlet(2, 5), [(1, 2), (5, 1)])[0] is False


def test_published_model_14_down_yukawa_monomials():
    """The exact published list, reproduced: orders 2, 4 and 5."""
    available = [(1, 2), (2, 1), (5, 1), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5)]
    residual = residual_charge(add(ten(2), fivebar(1, 2), fivebar(3, 4)))
    found = enumerate_monomials(residual, available, 5)
    assert {tuple(sorted(term)) for term in found} == {
        (((1, 2), 1), ((5, 1), 1)),
        (((1, 2), 2), ((2, 1), 1), ((5, 1), 1)),
        (((1, 2), 2), ((2, 5), 1), ((5, 1), 2)),
    }
    assert classify([ten(2), fivebar(1, 2), fivebar(3, 4)], available).insertions == 2


def test_neutral_factors_are_enumerated_too():
    """A valid monomial times a charge-neutral one is again valid."""
    available = [(2, 4), (4, 2)]
    found = enumerate_monomials((0, 0, 0, 0, 0), available, 4)
    assert frozenset() in found
    assert frozenset({((2, 4), 1), ((4, 2), 1)}) in found
    assert frozenset({((2, 4), 2), ((4, 2), 2)}) in found


def test_superpotential_tables_use_the_physical_higgs():
    spectrum = DownstairsSpectrum((1, 2, 2), ((1, 5),) * 3, (1, 2), (3, 4),
                                  ((1, 2), (2, 1), (2, 5), (5, 1)), 'x7862-16')
    up = yukawa_up(spectrum)
    assert up[0][1]['status'] == 'ALLOWED_AT_LEADING_ORDER'      # 10_1 10_2 H_12
    assert up[0][0]['minimal_insertions'] == 1                   # 10_1 10_1 H_12
    down = yukawa_down(spectrum)
    assert down[1][0]['status'] == 'ALLOWED_AT_LEADING_ORDER'    # 10_2 5bar_15 Hbar_34
    # H_12 Hbar_34 needs singlets carrying charge into bundles 3 and 4; with none
    # available the mu term is forbidden to all orders
    assert mu_term(spectrum)['status'] == 'FORBIDDEN_BY_SELECTION_RULE'
    richer = DownstairsSpectrum(spectrum.ten_families, spectrum.fivebar_families,
                                (1, 2), (3, 4),
                                spectrum.singlets + ((1, 3), (1, 4), (2, 3), (2, 4)))
    assert mu_term(richer)['minimal_insertions'] == 2


def test_operator_table_classifies_dangerous_operators():
    spectrum = DownstairsSpectrum((1, 2, 3), ((1, 2), (3, 4), (4, 5)), (1, 2), (3, 4), ())
    table = operator_table(spectrum)
    for name in ('QQQL / u^c u^c d^c e^c', 'LLe^c / LQd^c / u^c d^c d^c', 'H_u H_d'):
        assert name in table
        assert table[name]['verdict'] in ('FORBIDDEN_BY_SELECTION_RULE',
                                          'ALLOWED_BY_SELECTION_RULE')


# --- the cohomological product ---------------------------------------------

def test_koszul_levels_of_the_model_16_couplings():
    geometry = benchmark('7862')
    # the up-type coupling has all three classes at level 0, so it vanishes
    bundles = (MODEL_16[0], MODEL_16[1],
               tuple(-x for x in product(MODEL_16[0], MODEL_16[1])))
    assert [koszul_pure_level(geometry, k)[0] for k in bundles] == [0, 0, 0]
    assert triple_coupling(geometry, *bundles).status == 'VANISHES_BY_KOSZUL_LEVEL'
    # the down-type coupling has levels summing to one, so it survives
    down = (MODEL_16[1], product(MODEL_16[0], MODEL_16[4]),
            product(MODEL_16[2], MODEL_16[3]))
    assert sum(koszul_pure_level(geometry, k)[0] for k in down) == 1
    assert triple_coupling(geometry, *down).status == 'NONZERO'


@pytest.mark.skipif(not SYMMETRIES.exists(), reason='symmetry data not converted')
def test_trilinear_form_is_gamma_covariant():
    """The decisive convention check: zero covariance violations."""
    geometry = benchmark('7862')
    lift, _ = lift_for_x7862()
    degrees = [(1, -2, 3, 0), (-3, 0, -7, 0), (0, 0, 2, -2)]
    tensor, dimensions = monomial_tensor(geometry, degrees)
    assert dimensions == [8, 12, 3] and len(tensor) == 24
    assert covariance_defect(geometry, lift, degrees, tensor) == 0


@pytest.mark.skipif(not SYMMETRIES.exists(), reason='symmetry data not converted')
def test_model_16_down_yukawa_block_has_rank_two():
    """Rank 2 in the block where the published table shows a zero row."""
    geometry = benchmark('7862')
    lift, factors = lift_for_x7862()
    bundles = (MODEL_16[1], product(MODEL_16[0], MODEL_16[4]),
               product(MODEL_16[2], MODEL_16[3]))
    outcome = equivariant_coupling(geometry, lift, factors, bundles,
                                   ((0, 1), (0, 0), (0, 1)), check=True)
    assert outcome['status'] == 'COMPUTED'
    assert outcome['covariance_defect'] == 0
    # dimensions match the published character tables: 2 Q, 3 d^c, 1 Higgs
    assert outcome['dimensions'] == [2, 3, 1]
    assert contract_higgs(outcome['tensor']).rank() == 2


# --- the recorded artifacts -------------------------------------------------

def test_recorded_selection_rule_benchmark():
    artifact = ROOT / 'benchmarks/yukawa-selection-rule-all.json'
    if not artifact.exists():
        pytest.skip('artifact not present')
    summary = json.loads(artifact.read_text())['tally']
    for kind in ('YukawaUp', 'YukawaDown', 'MuTerm'):
        assert summary[f'{kind}/compared'] == 2012
        assert summary[f'{kind}/sets_equal'] == 2012, kind
        assert summary.get(f'{kind}/set_mismatch', 0) == 0
    # the one flag difference is the order-six term beyond the published cutoff
    assert summary.get('YukawaUp/differ', 0) == 1
    assert summary.get('YukawaDown/differ', 0) == 0
    assert summary.get('MuTerm/differ', 0) == 0


def test_recorded_published_table_consistency():
    artifact = ROOT / 'benchmarks/published-table-consistency.json'
    if not artifact.exists():
        pytest.skip('artifact not present')
    summary = json.loads(artifact.read_text())
    tally = summary['tally']
    assert tally['YukawaUp/checked'] == 2012
    # every published up table is a charge table; 47% of the down tables are not
    assert tally.get('YukawaUp/inconsistent', 0) == 0
    assert tally['YukawaDown/inconsistent'] == 954
    offenders = {(o['cicy'], o['model']) for o in summary['inconsistent']
                 if o['cicy'] == 7862}
    assert offenders == {(7862, 14), (7862, 16), (7862, 18), (7862, 19), (7862, 21)}


def test_recorded_leading_order_ranks():
    artifact = ROOT / 'benchmarks/x7862/leading-order-yukawa.json'
    if not artifact.exists():
        pytest.skip('artifact not present')
    records = json.loads(artifact.read_text())
    assert len(records) == 22
    agree = {'YukawaUp': 0, 'YukawaDown': 0}
    for record in records:
        for kind in agree:
            block = record[kind]
            assert block['status'] == 'COMPUTED', (record['model'], kind)
            agree[kind] += block['our_rank'] == block['published_structural_rank']
            # arXiv:1202.1757 Section 6.2: no rank-one up-type Yukawa here
            if kind == 'YukawaUp':
                assert block['our_rank'] != 1, record['model']
    assert agree == {'YukawaUp': 20, 'YukawaDown': 20}


def test_level_sum_two_is_unknown_not_zero():
    """Two classes at Koszul level 1: the connecting map is not multiplicative,
    so the naive ambient product says nothing. Must be UNKNOWN, never zero."""
    geometry = benchmark('7862')
    bundles = ((-3, -1, 2, 2), (2, -1, -3, 2), (1, 2, 1, -4))
    assert [koszul_pure_level(geometry, k)[0] for k in bundles] == [1, 1, 0]
    assert triple_coupling(geometry, *bundles).status == 'UNKNOWN_HIGHER_KOSZUL_LEVEL'
