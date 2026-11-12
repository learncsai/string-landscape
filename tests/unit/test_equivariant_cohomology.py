"""Gamma-representation on line-bundle cohomology, computed from first principles.

docs/equivariant_cohomology.md. The Koszul alternating sum turns the group action
on the ambient coordinates into the character of Gamma on H^q(X, L).
"""
import json
from itertools import combinations
from pathlib import Path

import pytest
import sympy

from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.cached import cohomology
from string_sm_sat.geometry.cicy import CICY, benchmark
from string_sm_sat.physics.equivariant_cohomology import (chiral_multiplicities,
                                                          complete_homogeneous,
                                                          cyclic_lift, decompose_abelian,
                                                          elementary_symmetric,
                                                          factor_blocks, factor_character,
                                                          is_representation,
                                                          koszul_virtual_character, to_matrix)

ROOT = Path(__file__).resolve().parents[2]
SYMMETRIES = ROOT / "data/processed/published_symmetries.json"
MODELS = ROOT / "data/processed/published_standard_models.json"


def test_bott_dimensions_on_projective_space():
    """With the identity element the characters are the honest dimensions."""
    for n, degrees, expected in ((1, range(5), [1, 2, 3, 4, 5]),
                                 (2, range(5), [1, 3, 6, 10, 15]),
                                 (3, range(4), [1, 4, 10, 20])):
        identity = sympy.eye(n + 1)
        assert [complete_homogeneous(m, identity) for m in degrees] == expected
    # top cohomology by Serre duality, and the vanishing window between
    identity = sympy.eye(3)
    assert factor_character(identity, -3) == (2, 1)
    assert factor_character(identity, -4) == (2, 3)
    assert factor_character(identity, -1)[0] is None
    assert factor_character(identity, -2)[0] is None


def test_equivariance_obstruction_is_detected():
    """O(k) descends only when the central element of the lift acts trivially."""
    from string_sm_sat.physics.equivariant_cohomology import is_equivariant
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    generators = [to_matrix(m) for m in symmetry["generators"]]
    ambient = benchmark('7862').ambient
    # the commutator acts by -1 on every factor, so O(k) descends iff sum k is even
    assert is_equivariant(generators, ambient, (1, -3, 0, 2))       # sum 0
    assert is_equivariant(generators, ambient, (2, 0, 0, 0))        # sum 2
    assert not is_equivariant(generators, ambient, (1, 0, 0, 0))    # sum 1
    assert not is_equivariant(generators, ambient, (1, 1, 1, 0))    # sum 3


def test_elementary_symmetric_of_a_matrix():
    m = sympy.Matrix([[2, 0], [0, 3]])
    assert elementary_symmetric(m, 0) == 1
    assert elementary_symmetric(m, 1) == 5      # trace
    assert elementary_symmetric(m, 2) == 6      # determinant
    assert elementary_symmetric(m, 3) == 0


def test_identity_character_reproduces_exact_dimensions():
    """The alternating sum at the identity is the holomorphic Euler characteristic."""
    from string_sm_sat.physics.index import index
    g = benchmark('7862')
    lift = {(0,): sympy.eye(8)}
    for k in [(1, -3, 0, 2), (0, 1, 0, -1), (2, 2, -2, -2), (-1, 1, 1, -1)]:
        value = koszul_virtual_character(g, k, [lift[(0,)]])[0]
        assert sympy.simplify(value - index(g, LineBundle(k))) == 0


def test_decomposition_of_the_regular_representation():
    """A character supported on the identity is a multiple of the regular rep."""
    character = {(0, 0): 12, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    multiplicities = decompose_abelian(character, [2, 2])
    assert is_representation(multiplicities)
    assert [int(multiplicities[l]) for l in sorted(multiplicities)] == [3, 3, 3, 3]


@pytest.mark.skipif(not SYMMETRIES.exists(), reason='symmetry data not converted')
def test_tetraquadric_group_is_a_faithful_factor_preserving_lift():
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    assert symmetry["group_order"] == 4 and symmetry["cyclic_factors"] == [2, 2]
    assert symmetry["acts_freely"] == "True"
    generators = [to_matrix(m) for m in symmetry["generators"]]
    # the generators commute only PROJECTIVELY: the commutator is a scalar on
    # each P^1 factor, so it is trivial on the ambient space but can act on O(k)
    commutator = sympy.expand(generators[0] * generators[1]
                              * (generators[1] * generators[0]).inv())
    g = benchmark('7862')
    blocks = factor_blocks(commutator, g.ambient)
    assert blocks is not None
    assert all(block == block[0, 0] * sympy.eye(2) for block in blocks)
    assert all(block[0, 0] == -1 for block in blocks)
    lift = cyclic_lift(generators, symmetry["cyclic_factors"])
    assert len(lift) == 4
    for matrix in lift.values():
        assert factor_blocks(matrix, g.ambient) is not None


@pytest.mark.skipif(not (SYMMETRIES.exists() and MODELS.exists()),
                    reason='published data not converted')
def test_first_principles_representation_matches_the_published_table():
    """The published GCoh is reproduced without using any representation data."""
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    database = json.loads(MODELS.read_text())
    models = [m for m in database["models"] if m["cicy"] == 7862 and m.get("GCoh")][:4]
    assert models
    g = benchmark('7862')
    factors = symmetry["cyclic_factors"]
    lift = cyclic_lift([to_matrix(m) for m in symmetry["generators"]], factors)
    labels = sorted(lift)
    compared = 0
    for record in models:
        columns = [tuple(r[a] for r in record["LineSum"]) for a in range(5)]
        for a, k in enumerate(columns):
            dimensions = cohomology(g, LineBundle(k)).dimensions
            if dimensions is None:
                continue
            nonzero = [q for q, v in enumerate(dimensions) if v]
            if len(nonzero) > 1:
                continue
            q = nonzero[0] if nonzero else 1
            values = koszul_virtual_character(g, k, [lift[l] for l in labels])
            character = {l: (-1) ** q * values[i] for i, l in enumerate(labels)}
            multiplicities = decompose_abelian(character, factors)
            assert is_representation(multiplicities)
            computed = [int(multiplicities[l]) for l in labels]
            assert computed == list(record["GCoh"][a][q]), (record["LineSum"], a)
            compared += 1
    assert compared >= 10


@pytest.mark.skipif(not (SYMMETRIES.exists() and MODELS.exists()),
                    reason='published data not converted')
def test_three_chiral_families_derived_from_first_principles():
    """Geometry + group action + charges -> three families, with no published input."""
    from string_sm_sat.physics.equivariance import CharacterGroup
    from string_sm_sat.physics.wilson_line import (WilsonLine, fivebar_multiplicities,
                                                   ten_multiplicities)
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    database = json.loads(MODELS.read_text())
    models = [m for m in database["models"]
              if m["cicy"] == 7862 and m.get("EquivStr") and m.get("WLine")][:3]
    assert models
    g = benchmark('7862')
    factors = symmetry["cyclic_factors"]
    lift = cyclic_lift([to_matrix(m) for m in symmetry["generators"]], factors)
    group = CharacterGroup(tuple(factors))
    for record in models:
        wilson = WilsonLine(group, tuple(record["WLine"][0]), tuple(record["WLine"][1]))
        equivariant = [tuple(x) for x in record["EquivStr"]]
        columns = [tuple(r[a] for r in record["LineSum"]) for a in range(5)]
        families = dict.fromkeys(('Q', 'u^c', 'e^c', 'd^c', 'L'), 0)
        for a, k in enumerate(columns):
            multiplicities = chiral_multiplicities(g, k, lift, factors)
            assert multiplicities is not None
            row = group.shift(tuple(multiplicities[l] for l in group.labels), equivariant[a])
            pieces = ten_multiplicities(group, wilson, row)
            for name in ('Q', 'u^c', 'e^c'):
                families[name] += pieces[name]
        for a, b in combinations(range(5), 2):
            k = tuple(x + y for x, y in zip(columns[a], columns[b]))
            multiplicities = chiral_multiplicities(g, k, lift, factors)
            assert multiplicities is not None
            shift = group.add(equivariant[a], equivariant[b])
            row = group.shift(tuple(multiplicities[l] for l in group.labels), shift)
            pieces = fivebar_multiplicities(group, wilson, row)
            families['d^c'] += pieces['d^c']
            families['L'] += pieces['L']
        assert families == {'Q': 3, 'u^c': 3, 'e^c': 3, 'd^c': 3, 'L': 3}, record["LineSum"]


@pytest.mark.skipif(not SYMMETRIES.exists(), reason='symmetry data not converted')
def test_explicit_action_matrices_agree_with_the_character_formula():
    """Two independent routes to the same trace: Kronecker matrices vs symmetric functions."""
    from string_sm_sat.physics.equivariant_cohomology import (ambient_action_matrix,
                                                              ambient_character)
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    lift = cyclic_lift([to_matrix(m) for m in symmetry["generators"]],
                       symmetry["cyclic_factors"])
    g = benchmark('7862')
    for matrix in lift.values():
        blocks = factor_blocks(matrix, g.ambient)
        for k in [(2, 2, 2, 2), (1, -3, 0, 2), (0, 2, 0, -2), (-2, -2, -2, -2), (3, 0, -4, 1)]:
            action = ambient_action_matrix(blocks, k)
            degree, character = ambient_character(blocks, k)
            if action is None:
                assert degree is None
                continue
            assert sympy.simplify(action.trace() - character) == 0


@pytest.mark.skipif(not (SYMMETRIES.exists() and MODELS.exists()),
                    reason='published data not converted')
def test_map_ranks_resolve_a_non_collapsing_bundle():
    """Where the Koszul complex does not collapse, isotypic ranks give each H^q."""
    from string_sm_sat.physics.equivariant_cohomology import (collapses, equivariant_cohomology,
                                                              invariant_family_coefficients)
    symmetry = json.loads(SYMMETRIES.read_text())["symmetries"]["7862"][4]
    database = json.loads(MODELS.read_text())
    g = benchmark('7862')
    factors = symmetry["cyclic_factors"]
    lift = cyclic_lift([to_matrix(m) for m in symmetry["generators"]], factors)
    generators = [to_matrix(m) for m in symmetry["generators"]]
    coefficients = invariant_family_coefficients(symmetry["invariants"], 8)
    labels = sorted(lift)
    checked = 0
    for record in database["models"]:
        if record["cicy"] != 7862 or not record.get("GCoh2"):
            continue
        columns = [tuple(r[a] for r in record["LineSum"]) for a in range(5)]
        equivariant = [tuple(x) for x in record["EquivStr"]]
        for index, (a, b) in enumerate(combinations(range(5), 2)):
            k = tuple(x + y for x, y in zip(columns[a], columns[b]))
            if collapses(g, k):
                continue
            tables = equivariant_cohomology(g, k, lift, factors, None, generators,
                                            coefficients)
            if tables is None:
                continue
            shift = tuple((x + y) % n for x, y, n in
                          zip(equivariant[a], equivariant[b], factors))
            for q in range(4):
                computed = tables.get(q, {label: 0 for label in labels})
                shifted = [computed[tuple((l[i] + shift[i]) % factors[i]
                                          for i in range(len(factors)))] for l in labels]
                assert shifted == list(record["GCoh2"][index][q]), (k, q)
            checked += 1
            if checked >= 8:
                return
    assert checked


def test_recorded_comparison_is_exact():
    """Every published character table agrees exactly with the computed one.

    The published GCoh/GCoh2 tables are raw characters of the lift; the
    equivariant structure enters only when the spectrum is formed. Compared raw
    against raw, every table agrees. (An earlier comparison shifted the computed
    side and misreported 694 vector-like pair tables as relabellings.) The
    tables whose shifted form differs from the raw one are exactly those that
    discriminate between the two readings, and all of them favour raw.
    """
    import glob
    artifacts = glob.glob(str(ROOT / 'benchmarks/equivariant-cohomology-*.json'))
    if not artifacts:
        pytest.skip('artifacts not present')
    seen = discriminating = 0
    for path in artifacts:
        data = json.loads(Path(path).read_text())
        for result in data['results']:
            for kind in ('singles', 'pairs'):
                for entry in result[kind]:
                    if entry.get('verdict') is None:
                        continue
                    seen += 1
                    assert entry['verdict'] == 'exact', entry
                    if entry.get('shift_invariant') is False:
                        discriminating += 1
                        assert entry['matches_if_shifted'] is False
    assert seen and discriminating
