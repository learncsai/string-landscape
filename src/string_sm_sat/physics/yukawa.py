"""Holomorphic cubic superpotential couplings from bundle cohomology.

The perturbative Yukawa coupling of three matter fields living in
H^1(X, L_1), H^1(X, L_2), H^1(X, L_3) with L_1 (x) L_2 (x) L_3 = O_X is the
cup product

    H^1(X,L_1) x H^1(X,L_2) x H^1(X,L_3) -> H^3(X, O_X) = C .

For a hypersurface X = {f = 0} in a product of projective spaces the Koszul
sequence 0 -> O_A(k-q) -> O_A(k) -> O_X(k) -> 0 splits every class by *Koszul
level*:

    level 0 : the image of the ambient H^1(A, O(k));
    level 1 : the kernel of multiplication by f on H^2(A, O(k-q)).

Two facts then determine everything.

**Vanishing rule.** Cup product commutes with restriction, so if all three
classes are restrictions of ambient classes the coupling is the restriction of
an element of H^3(A, O_A). For A a product of P^1s that group vanishes, so the
coupling is identically zero. Charge conservation can therefore permit a
coupling that is exactly zero for cohomological reasons — a genuine selection
rule, not an accident of a particular complex structure.

**Level-one rule.** When exactly one class is at level 1 and two are
restrictions of ambient classes, the coupling is computed by the ambient cup
product

    H^1(A,O(k_1)) x H^1(A,O(k_2)) x H^2(A,O(k_3-q)) -> H^4(A,O(-q)) = C ,

because the connecting map delta: H^3(X,O_X) -> H^4(A,O(-q)) is an isomorphism
(H^3(A,O_A) = H^4(A,O_A) = 0) and is linear over restrictions of ambient
classes: delta(a|_X . b) = a . delta(b).

**Level sum two or more is not decided here.** The connecting map is *not*
multiplicative, so when two or three classes sit at level 1 the product is not
the naive ambient product (which would land in H^5 or H^6 of a fourfold and
vanish for degree reasons); it requires lifting through the defining
polynomial and is in general nonzero. Such couplings are returned as
UNKNOWN_HIGHER_KOSZUL_LEVEL, never as zero. (An earlier version of this module
reported them as vanishing. No coupling in any recorded artifact has level sum
two or more, so no recorded result was affected; see RESULTS.md.)

**Evaluation.** In the Cech description on the standard two-chart cover of each
P^1, H^0(P^1,O(m)) has the monomials x^i y^{m-i} with i >= 0, and H^1(P^1,O(m))
for m <= -2 has the Laurent monomials x^a y^{m-a} with a and m-a both <= -1.
Products multiply monomials factor by factor, and the generator of
H^1(P^1,O(-2)) is x^{-1} y^{-1}. The coupling of three basis elements is
therefore 1 exactly when the exponents sum to (-1,-1) in every factor, and 0
otherwise. Exponents only increase when multiplying by a polynomial monomial,
so a term reaching (-1,-1) stays inside the negative region throughout and no
projection subtlety arises.

Everything here is exact integer bookkeeping. What it does *not* do: the overall
normalisation of the trace map is not fixed, so only the zero/nonzero pattern
and the rank of a coupling matrix are meaningful; and physical (canonically
normalised) Yukawas need matter-field Kahler metrics, which are not computed.

References: Anderson, Gray, Lukas, Palti arXiv:1202.1757 Section 6;
Blesneag, Buchbinder, Candelas, Lukas arXiv:1512.05322 for the ambient-space
evaluation of holomorphic Yukawa couplings (and Blesneag, Buchbinder, Lukas
arXiv:1607.03461 for complete intersections).
"""
from dataclasses import dataclass
from itertools import product

from ..bundles.line_bundle import LineBundle
from ..cohomology.analytic import ambient_cohomology
from ..cohomology.cached import cohomology
from ..physics.constraints import Check, rule

YUKAWA = rule('holomorphic_yukawa', 'EXACT',
              '1202.1757 Section 6; 1512.05322; Koszul/Cech evaluation',
              ('hypersurface in a product of P^1 factors; trivial total line bundle; '
               'overall normalisation of the trace map not fixed',),
              False, False)


def normal_multidegree(geometry):
    """The multidegree of the single defining polynomial."""
    columns = tuple(zip(*geometry.configuration))
    if len(columns) != 1:
        raise ValueError('implemented for a single defining polynomial')
    return columns[0]


def factor_exponents(degree, index):
    """Exponent pair of a monomial basis element of H^*(P^1, O(degree)).

    Index conventions match cohomology/finite_rank.basis: for degree >= 0 the
    index is the exponent of the first coordinate; for degree <= -2 it counts the
    Laurent monomials with both exponents at most -1.
    """
    if degree >= 0:
        return (index, degree - index)
    if degree == -1:
        raise ValueError('H^*(P^1, O(-1)) vanishes')
    return (degree + 1 + index, -1 - index)


def factor_dimension(degree):
    if degree >= 0:
        return degree + 1
    if degree == -1:
        return 0
    return -degree - 1


def ambient_basis_indices(k):
    """Index tuples for a monomial basis of the single nonzero H^q(A, O(k))."""
    if any(degree == -1 for degree in k):
        return ()
    return tuple(product(*(range(factor_dimension(degree)) for degree in k)))


def level_decomposition(geometry, k):
    """Dimensions of the level-0 and level-1 parts of H^1(X, O(k)).

    level 0 = coker(H^1(A,O(k-q)) -> H^1(A,O(k)))
    level 1 = ker  (H^2(A,O(k-q)) -> H^2(A,O(k)))
    Their sum is checked against the exact h^1(X, O(k)).
    """
    from ..cohomology.finite_rank import modular_rank, multiplication_matrix, coefficients
    q = normal_multidegree(geometry)
    shifted = tuple(a - b for a, b in zip(k, q))
    here = ambient_cohomology(geometry.ambient, tuple(k))
    below = ambient_cohomology(geometry.ambient, shifted)

    def part(target_degree):
        source = below[1] if below and below[0] == target_degree else 0
        image = here[1] if here and here[0] == target_degree else 0
        if not source or not image:
            return source, image, 0
        try:
            matrix = multiplication_matrix(tuple(k), coefficients())
        except ValueError:
            return source, image, None
        return source, image, modular_rank(matrix)

    source1, image1, rank1 = part(1)
    source2, image2, rank2 = part(2)
    level0 = image1 - (rank1 or 0) if image1 else 0
    level1 = source2 - (rank2 or 0) if source2 else 0
    dimensions = cohomology(geometry, LineBundle(tuple(k))).dimensions
    return {
        'k': list(k), 'level0': level0, 'level1': level1,
        'h1_exact': None if dimensions is None else dimensions[1],
        'consistent': dimensions is not None and level0 + level1 == dimensions[1],
        'ambient_here': list(here) if here else None,
        'ambient_shifted': list(below) if below else None,
        'ranks': {'d1': rank1, 'd2': rank2},
    }


@dataclass(frozen=True)
class TripleCoupling:
    charges: tuple
    status: str
    level_assignment: tuple | None = None
    nonzero_terms: int = 0
    tensor: tuple = ()
    dimensions: tuple = ()
    detail: str = ''

    def as_dict(self):
        return {'charges': [list(k) for k in self.charges], 'status': self.status,
                'level_assignment': self.level_assignment, 'nonzero_terms': self.nonzero_terms,
                'dimensions': list(self.dimensions), 'detail': self.detail}


def triple_coupling(geometry, k1, k2, k3):
    """The holomorphic coupling tensor for three H^1 classes, or why it vanishes."""
    charges = (tuple(k1), tuple(k2), tuple(k3))
    total = [sum(k[i] for k in charges) for i in range(geometry.h11)]
    if any(total):
        return TripleCoupling(charges, 'FORBIDDEN_BY_CHARGE',
                              detail='the three line bundles do not multiply to O_X')
    q = normal_multidegree(geometry)
    levels = [level_decomposition(geometry, k) for k in charges]
    if any(level['h1_exact'] in (None, 0) for level in levels):
        return TripleCoupling(charges, 'NO_MATTER',
                              detail='one of the bundles carries no H^1 matter')

    # which classes can sit at which level
    options = []
    for level in levels:
        available = []
        if level['level0']:
            available.append(0)
        if level['level1']:
            available.append(1)
        options.append(available)
    all_assignments = list(product(*options))
    reachable = sorted({sum(a) for a in all_assignments})
    if reachable == [0]:
        return TripleCoupling(
            charges, 'VANISHES_BY_KOSZUL_LEVEL',
            detail=('charge conservation allows it, but every class is the restriction of '
                    'an ambient class; the cup product is the restriction of a class in '
                    'H^3(A,O_A) = 0'))
    if any(s >= 2 for s in reachable):
        return TripleCoupling(
            charges, 'UNKNOWN_HIGHER_KOSZUL_LEVEL',
            detail=(f'reachable Koszul level sums {reachable}; a level sum of two or more '
                    'needs a lift through the defining polynomial and is not computed'))
    assignments = [a for a in all_assignments if sum(a) == 1]

    # evaluate the ambient product for each admissible assignment
    tensor, dimensions, nonzero = [], [], 0
    for assignment in assignments:
        shifted = []
        for level, k in zip(assignment, charges):
            shifted.append(tuple(a - b for a, b in zip(k, q)) if level else tuple(k))
        bases = [ambient_basis_indices(k) for k in shifted]
        dimensions = tuple(len(b) for b in bases)
        entries = []
        for indices in product(*[range(len(b)) for b in bases]):
            exponents = [0] * geometry.h11
            partner = [0] * geometry.h11
            for slot, index in enumerate(indices):
                basis_index = bases[slot][index]
                for factor, component in enumerate(basis_index):
                    a, b = factor_exponents(shifted[slot][factor], component)
                    exponents[factor] += a
                    partner[factor] += b
            if all(x == -1 for x in exponents) and all(y == -1 for y in partner):
                entries.append(list(indices))
        nonzero += len(entries)
        tensor.append({'level_assignment': list(assignment),
                       'dimensions': list(dimensions),
                       'nonzero_index_triples': entries})
    status = 'NONZERO' if nonzero else 'VANISHES_BY_MONOMIAL_PRODUCT'
    detail = ('' if nonzero else
              'levels can sum to one but no monomial product reaches the top class')
    return TripleCoupling(charges, status, tuple(assignments[0]), nonzero,
                          tuple(tensor), dimensions, detail)


def check_triple(geometry, k1, k2, k3):
    coupling = triple_coupling(geometry, k1, k2, k3)
    outcome = {'NONZERO': 'PASS'}.get(coupling.status, 'FAIL')
    return Check(YUKAWA, outcome, coupling.nonzero_terms, coupling.as_dict())


# ---------------------------------------------------------------------------
# The Gamma-equivariant coupling: the actual downstairs Yukawa matrix
# ---------------------------------------------------------------------------

def koszul_pure_level(geometry, k):
    """The single Koszul level carrying H^1(X, O(k)), with its ambient multidegree.

    Returns (level, ambient multidegree, dimension).  Raises when the classes are
    spread over both levels, which the monomial evaluation below does not cover.
    """
    levels = level_decomposition(geometry, k)
    if levels['level0'] and levels['level1']:
        raise ValueError(f'H^1(X,O({k})) is spread over both Koszul levels')
    q = normal_multidegree(geometry)
    if levels['level0']:
        return 0, tuple(k), levels['level0']
    if levels['level1']:
        return 1, tuple(a - b for a, b in zip(k, q)), levels['level1']
    raise ValueError(f'H^1(X,O({k})) vanishes')


def structural_identification(geometry, k):
    """Is H^1(X, O(k)) identified with one ambient group for *every* smooth member?

    Level 0 is the cokernel of H^1(A,O(k-q)) -> H^1(A,O(k)) and level 1 the kernel
    of H^2(A,O(k-q)) -> H^2(A,O(k)). When the other end of the relevant map is a
    zero ambient group, the identification holds for every defining polynomial,
    so a coupling built from such classes is independent of complex structure.
    Returns (level, ambient multidegree, structural?).
    """
    q = normal_multidegree(geometry)
    shifted = tuple(a - b for a, b in zip(k, q))
    here = ambient_cohomology(geometry.ambient, tuple(k))
    below = ambient_cohomology(geometry.ambient, shifted)

    def degree(entry):
        return entry[0] if entry else None

    level0 = degree(here) == 1
    level1 = degree(below) == 2
    if level0 and level1:
        return None, None, False
    if level0:
        return 0, tuple(k), degree(below) != 1 and degree(below) != 2
    if level1:
        return 1, shifted, degree(here) != 2 and degree(here) != 1
    return None, None, False


def monomial_tensor(geometry, ambient_degrees):
    """The trilinear form on the monomial bases, as {(i,j,l): 1}.

    The product of three Cech monomials represents the generator of
    H^{top}(A, O(-q)) exactly when the exponents sum to (-1,-1) in every factor.
    """
    bases = [ambient_basis_indices(k) for k in ambient_degrees]
    tensor = {}
    for i, first in enumerate(bases[0]):
        for j, second in enumerate(bases[1]):
            for l, third in enumerate(bases[2]):
                left = [0] * geometry.h11
                right = [0] * geometry.h11
                for degrees, indices in zip(ambient_degrees, (first, second, third)):
                    for factor, component in enumerate(indices):
                        a, b = factor_exponents(degrees[factor], component)
                        left[factor] += a
                        right[factor] += b
                if all(x == -1 for x in left) and all(y == -1 for y in right):
                    tensor[(i, j, l)] = 1
    return tensor, [len(b) for b in bases]


def covariance_defect(geometry, lift, ambient_degrees, tensor):
    """How far the trilinear form is from being Gamma-covariant.

    The target H^{top}(A, O(-q)) carries the character prod_i det(B_i)^{-1}, which
    is trivial precisely when the action descends to the Calabi-Yau quotient.  A
    nonzero defect means a basis or lift convention is wrong, so this is checked
    rather than assumed.
    """
    import sympy
    from .equivariant_cohomology import ambient_action_matrix, factor_blocks
    worst = 0
    for element, matrix in lift.items():
        blocks = factor_blocks(matrix, geometry.ambient)
        top = sympy.prod([block.det() ** -1 for block in blocks])
        actions = [ambient_action_matrix(blocks, k) for k in ambient_degrees]
        for i in range(actions[0].shape[1]):
            for j in range(actions[1].shape[1]):
                for l in range(actions[2].shape[1]):
                    value = sum(actions[0][a, i] * actions[1][b, j] * actions[2][c, l]
                                for (a, b, c) in tensor)
                    if sympy.simplify(value - top * tensor.get((i, j, l), 0)) != 0:
                        worst += 1
    return worst


def equivariant_coupling(geometry, lift, factors, charges, labels, check=False):
    """The downstairs coupling tensor on the Gamma-isotypic components.

    `charges` are the three line bundles and `labels` the Gamma-characters of the
    three low-energy fields (the Wilson-line character of each multiplet piece).
    Returns the tensor in bases of the isotypic subspaces, together with their
    dimensions.  This is the actual cohomological product, not a selection rule.
    """
    import sympy
    from .equivariant_cohomology import (ambient_action_matrix, factor_blocks,
                                         isotypic_projector)
    if any(sum(k[i] for k in charges) for i in range(geometry.h11)):
        raise ValueError('the three line bundles do not multiply to O_X')
    levels, degrees, structural = [], [], []
    for k in charges:
        level, ambient, dimension = koszul_pure_level(geometry, k)
        if len(ambient_basis_indices(ambient)) != dimension:
            # a Koszul map is nonzero: H^1(X,L) is a proper quotient or subspace of
            # the ambient group and the monomial basis would mis-index families
            return {'status': 'UNKNOWN_NONZERO_KOSZUL_MAP', 'levels': None,
                    'dimensions': [0, 0, 0], 'rank': None, 'matrix': None}
        levels.append(level)
        degrees.append(ambient)
        structural.append(structural_identification(geometry, k)[2])
    if sum(levels) == 0:
        return {'status': 'VANISHES_BY_KOSZUL_LEVEL', 'levels': levels,
                'dimensions': [0, 0, 0], 'rank': 0, 'matrix': None}
    if sum(levels) >= 2:
        return {'status': 'UNKNOWN_HIGHER_KOSZUL_LEVEL', 'levels': levels,
                'dimensions': [0, 0, 0], 'rank': None, 'matrix': None}
    tensor, ambient_dimensions = monomial_tensor(geometry, degrees)
    defect = covariance_defect(geometry, lift, degrees, tensor) if check else 0
    blocks = {e: factor_blocks(m, geometry.ambient) for e, m in lift.items()}
    vectors = []
    for degree, label in zip(degrees, labels):
        actions = {e: ambient_action_matrix(b, degree) for e, b in blocks.items()}
        vectors.append(isotypic_projector(actions, factors, label).columnspace())
    dimensions = [len(v) for v in vectors]
    if not all(dimensions):
        return {'status': 'NO_MATTER_IN_THAT_CHARACTER', 'levels': levels,
                'dimensions': dimensions, 'rank': 0, 'matrix': None,
                'covariance_defect': defect}
    values = [[[sympy.simplify(sum(u[a] * v[b] * w[c] for (a, b, c) in tensor))
                for w in vectors[2]] for v in vectors[1]] for u in vectors[0]]
    return {'status': 'COMPUTED', 'levels': levels, 'dimensions': dimensions,
            'ambient_dimensions': ambient_dimensions, 'tensor': values,
            'covariance_defect': defect,
            'complex_structure_independent': all(structural)}


def contract_higgs(tensor, index=0):
    """Fix the third (Higgs) index, giving the Yukawa matrix as a sympy Matrix."""
    import sympy
    return sympy.Matrix([[row[index] for row in plane] for plane in tensor])
