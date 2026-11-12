"""Gamma-representation content of line-bundle cohomology, from first principles.

This is the piece the downstairs pipeline was missing. Given an explicit linear
action of a finite group on the ambient homogeneous coordinates that preserves a
complete intersection X, it computes the character of Gamma on H^q(X, L) — not
merely the dimensions — so that the descent of physics/wilson_line.py no longer
needs the answer supplied from a published table.

Method. The Koszul resolution of O_X is Gamma-equivariant, so in the
representation ring

    sum_q (-1)^q [H^q(X,L)] = sum_p (-1)^p sum_q (-1)^q [H^q(A, L (x) wedge^p N*)].

Every term on the right is ambient cohomology of a line bundle on a product of
P^1s, whose character is an elementary symmetric-function computation. When only
one H^q(X,L) is nonzero — which the exact dimension code decides independently —
the alternating sum determines that single representation completely, with no
map ranks and no spectral-sequence input.

Ambient characters. On a P^1 factor let T and D be the trace and determinant of
the group element acting on the linear forms. With h_m the complete homogeneous
symmetric function of the two eigenvalues, computed by the recursion
h_m = T h_{m-1} - D h_{m-2},

    tr on H^0(P^1, O(m)) = h_m               (m >= 0)
    tr on H^1(P^1, O(m)) = D^{m+1} h_{-m-2}  (m <= -2)
    H^*(P^1, O(-1)) = 0.

Kuenneth multiplies these across factors, and the cohomological degree is the
number of factors in the negative range. A group element that permutes the P^1
factors does not preserve a line bundle of non-symmetric multidegree; such cases
are refused rather than approximated.

Scalars. The matrices form a central extension G of Gamma: an element whose
blocks are all scalars acts trivially on the ambient space but can act
nontrivially on O(k). L is Gamma-equivariant exactly when that central subgroup
acts trivially, which is checked; the resulting character then descends to
Gamma. Different lifts differ by a character of Gamma, which is precisely the
freedom of the equivariant structure.
"""
from dataclasses import dataclass
from itertools import product

import sympy

from .constraints import Check, rule

EQUIVARIANT_COHOMOLOGY = rule(
    'equivariant_cohomology', 'EXACT',
    'Koszul resolution; Bott/Kuenneth on products of P^1; our derivation',
    ('linear action on ambient coordinates preserving X; each group element preserves '
     'every projective factor; only one H^q(X,L) nonzero, decided independently',),
    False, False)


def root_of_unity(text):
    """Interpret an entry such as 'rt[4]' or '-rt[8]' or an integer."""
    if isinstance(text, int):
        return sympy.Integer(text)
    text = str(text).replace(' ', '')
    sign = 1
    if text.startswith('-'):
        sign, text = -1, text[1:]
    if text.startswith('rt['):
        n = int(text[3:-1])
        return sign * sympy.exp(2 * sympy.pi * sympy.I / n)
    return sign * sympy.Integer(int(text))


def to_matrix(rows):
    return sympy.Matrix([[root_of_unity(x) for x in row] for row in rows])


def generate_group(generators, limit=256):
    """Close a set of matrices under multiplication."""
    identity = sympy.eye(generators[0].shape[0])
    elements = [identity]
    frontier = [identity]
    seen = {sympy.ImmutableMatrix(identity)}
    while frontier:
        current = frontier.pop()
        for g in generators:
            product_matrix = sympy.simplify(current * g)
            key = sympy.ImmutableMatrix(product_matrix)
            if key in seen:
                continue
            seen.add(key)
            elements.append(product_matrix)
            frontier.append(product_matrix)
            if len(elements) > limit:
                raise ValueError('matrix group larger than the guard')
    return elements


def factor_blocks(matrix, ambient):
    """Per-factor square blocks, or None when the element permutes factors."""
    blocks, offset = [], 0
    for n in ambient:
        size = n + 1
        block = matrix[offset:offset + size, offset:offset + size]
        outside = 0
        for i in range(offset, offset + size):
            for j in range(matrix.shape[1]):
                if not (offset <= j < offset + size) and matrix[i, j] != 0:
                    outside += 1
        if outside:
            return None
        blocks.append(block)
        offset += size
    return blocks


def complete_homogeneous(m, block):
    """h_m of the eigenvalues of `block`: the trace on Sym^m.

    Uses h_m = sum_i (-1)^{i-1} e_i h_{m-i} with e_i the elementary symmetric
    functions read off the characteristic polynomial. Exact for any size.
    """
    if m < 0:
        return sympy.Integer(0)
    size = block.shape[0]
    lam = sympy.Symbol('_lam')
    poly = sympy.Poly(sympy.expand(block.charpoly(lam).as_expr()), lam)
    # charpoly = lam^n - e_1 lam^{n-1} + e_2 lam^{n-2} - ...
    elementary = []
    for i in range(1, size + 1):
        coefficient = poly.coeff_monomial(lam ** (size - i))
        elementary.append(sympy.expand((-1) ** i * coefficient))
    values = [sympy.Integer(1)]
    for degree in range(1, m + 1):
        total = sympy.Integer(0)
        for i in range(1, min(degree, size) + 1):
            total += (-1) ** (i - 1) * elementary[i - 1] * values[degree - i]
        values.append(sympy.expand(total))
    return values[m]


def factor_character(block, degree):
    """(cohomological degree, trace) of the action on H^*(P^n, O(degree)).

    Bott: H^0 for degree >= 0, H^n for degree <= -n-1, nothing in between.
    The top piece follows from Serre duality,
    tr on H^n(P^n, O(m)) = det^{m+n} h_{-m-n-1}.
    """
    size = block.shape[0]
    n = size - 1
    if degree >= 0:
        return 0, complete_homogeneous(degree, block)
    if degree >= -n:
        return None, sympy.Integer(0)
    return n, sympy.expand(block.det() ** (degree + n)
                           * complete_homogeneous(-degree - n - 1, block))


def ambient_character(blocks, k):
    """(q, trace) of one group element on H^q(A, O(k)); (None, 0) when it vanishes."""
    q, value = 0, sympy.Integer(1)
    for block, degree in zip(blocks, k):
        step, trace = factor_character(block, degree)
        if step is None:
            return None, sympy.Integer(0)
        q += step
        value = sympy.expand(value * trace)
    return q, value


def elementary_symmetric(matrix, p):
    """tr on wedge^p of a matrix: the p-th elementary symmetric function."""
    size = matrix.shape[0]
    if p == 0:
        return sympy.Integer(1)
    if p > size:
        return sympy.Integer(0)
    from itertools import combinations
    total = sympy.Integer(0)
    for rows in combinations(range(size), p):
        total += matrix[list(rows), list(rows)].det()
    return sympy.expand(total)


def koszul_virtual_character(geometry, k, elements, polynomial_action=None):
    """sum_q (-1)^q tr on H^q(X, O(k)), for every group element.

    The normal bundle is N = (+)_j O(q_j) and Gamma acts on the defining
    polynomials by `polynomial_action` (one matrix per element, in the same
    order as `elements`). Since a factor-preserving element can only mix
    polynomials of equal multidegree, the polynomials are grouped by multidegree
    and the trace on wedge^p N* is the product of elementary symmetric functions
    of the corresponding blocks of the inverse action. With a trivial action this
    reduces to a plain sum over subsets.
    """
    columns = tuple(zip(*geometry.configuration))
    classes = {}
    for index, column in enumerate(columns):
        classes.setdefault(column, []).append(index)
    character = []
    for position, element in enumerate(elements):
        blocks = factor_blocks(element, geometry.ambient)
        if blocks is None:
            raise ValueError('group element permutes projective factors')
        rho = None
        if polynomial_action is not None:
            rho = polynomial_action[position]
            if rho.shape[0] != len(columns):
                raise ValueError('polynomial action has the wrong size')
            rho = rho.inv()                       # the action on N* is the dual
        total = sympy.Integer(0)
        degrees = list(classes)
        for counts in product(*(range(len(classes[d]) + 1) for d in degrees)):
            weight = sympy.Integer(1)
            for degree, count in zip(degrees, counts):
                indices = classes[degree]
                if rho is None:
                    weight *= sympy.binomial(len(indices), count)
                else:
                    block = rho[indices, indices]
                    weight *= elementary_symmetric(block, count)
            if weight == 0:
                continue
            p = sum(counts)
            shifted = tuple(k[i] - sum(count * degree[i]
                                       for degree, count in zip(degrees, counts))
                            for i in range(geometry.h11))
            q, value = ambient_character(blocks, shifted)
            if q is None:
                continue
            total += (-1) ** (p + q) * weight * value
        character.append(sympy.simplify(total))
    return character


def is_equivariant(generators, ambient, k):
    """Does O(k) carry a Gamma-equivariant structure for this matrix lift?

    The matrices generate a central extension G of Gamma: the commutator of two
    generators may be a nonzero scalar on each projective factor, acting
    trivially on the ambient space but by a root of unity on O(k). O(k) descends
    exactly when every such central element acts trivially, i.e. when
    prod_r c_r^{k_r} = 1. Otherwise the cohomology carries only a projective
    representation and the character is not a character of Gamma.
    """
    elements = generate_group(list(generators))
    for index in central_subgroup(elements, ambient):
        blocks = factor_blocks(elements[index], ambient)
        value = sympy.Integer(1)
        for block, degree in zip(blocks, k):
            value *= block[0, 0] ** degree
        if sympy.simplify(value - 1) != 0:
            return False
    return True


def central_subgroup(elements, ambient):
    """Elements acting trivially on the ambient space: every block a scalar."""
    central = []
    for index, element in enumerate(elements):
        blocks = factor_blocks(element, ambient)
        if blocks is None:
            continue
        if all(block == block[0, 0] * sympy.eye(block.shape[0]) for block in blocks):
            central.append(index)
    return central


def equivariance_defect(elements, central, ambient, k):
    """How each central element acts on O(k); it must act trivially."""
    defects = []
    for index in central:
        blocks = factor_blocks(elements[index], ambient)
        value = sympy.Integer(1)
        for block, degree in zip(blocks, k):
            value *= block[0, 0] ** degree
        defects.append(sympy.simplify(value))
    return defects


def cyclic_lift(generators, factor_orders):
    """Group elements indexed by exponent tuples: g_1^{a_1} ... g_r^{a_r}.

    This is a *lift* of Gamma into GL, one matrix per element of
    Z_{n_1} x ... x Z_{n_r}. It need only be a homomorphism up to the central
    subgroup; whether that spoils the character is decided by
    `equivariance_defect` and, independently, by whether the decomposition comes
    out as non-negative integers.
    """
    if len(generators) != len(factor_orders):
        raise ValueError('one generator per cyclic factor is required')
    size = generators[0].shape[0]
    lift = {}
    for exponents in product(*(range(n) for n in factor_orders)):
        matrix = sympy.eye(size)
        for g, power in zip(generators, exponents):
            for _ in range(power):
                matrix = matrix * g
        lift[exponents] = sympy.expand(matrix)
    return lift


def decompose_abelian(character, factor_orders):
    """Multiplicities of each irreducible character, by the finite Fourier transform.

    `character` maps exponent tuples to trace values. The characters of
    Z_{n_1} x ... x Z_{n_r} are chi_c(a) = prod_j exp(2 pi i a_j c_j / n_j), so

        mult(chi_c) = (1/|Gamma|) sum_a character(a) conj(chi_c(a)).

    Returns a dict from character label to a sympy value; a genuine
    representation gives non-negative integers.
    """
    order = 1
    for n in factor_orders:
        order *= n
    multiplicities = {}
    for label in product(*(range(n) for n in factor_orders)):
        total = sympy.Integer(0)
        for exponents, value in character.items():
            phase = sympy.Integer(1)
            for a, c, n in zip(exponents, label, factor_orders):
                phase *= sympy.exp(-2 * sympy.pi * sympy.I * a * c / n)
            total += value * phase
        multiplicities[label] = sympy.simplify(sympy.expand(total / order))
    return multiplicities


def is_representation(multiplicities):
    """True when every multiplicity is a non-negative integer."""
    for value in multiplicities.values():
        simplified = sympy.nsimplify(sympy.simplify(value))
        if not simplified.is_Integer or simplified < 0:
            return False
    return True


def check_single_degree(dimensions):
    """The alternating sum determines H^q only when a single degree is nonzero."""
    nonzero = [q for q, value in enumerate(dimensions) if value]
    ok = len(nonzero) <= 1
    return Check(EQUIVARIANT_COHOMOLOGY, 'PASS' if ok else 'UNKNOWN', nonzero,
                 {'note': 'more than one nonzero H^q needs the equivariant spectral sequence'})


def chiral_character(geometry, k, lift, poly_lift=None):
    """The virtual Gamma-character of H^*(X, O(k)), indexed by group element.

    This is what the Koszul alternating sum always determines, with no
    assumption about which cohomological degrees are nonzero. Physically it is
    exactly the chiral content: 10s come from H^1(V) and 10bars from H^2(V), so
    their difference is what the index-like alternating sum sees.
    """
    labels = sorted(lift)
    values = koszul_virtual_character(
        geometry, k, [lift[label] for label in labels],
        None if poly_lift is None else [poly_lift[label] for label in labels])
    return {label: values[i] for i, label in enumerate(labels)}


def chiral_multiplicities(geometry, k, lift, factors, poly_lift=None, sign=-1,
                          generators=None):
    """Chiral multiplicity of each Gamma-character in H^1 - H^2 of O(k).

    `sign` is -1 because sum_q (-1)^q H^q = H^0 - H^1 + H^2 - H^3 and the chiral
    matter sits in H^1; with H^0 = H^3 = 0 the chiral content is minus the
    alternating sum.
    """
    if generators is not None and not is_equivariant(generators, geometry.ambient, k):
        return None
    character = {label: sign * value
                 for label, value in chiral_character(geometry, k, lift, poly_lift).items()}
    multiplicities = decompose_abelian(character, factors)
    resolved = {}
    for label, value in multiplicities.items():
        simplified = sympy.nsimplify(sympy.simplify(value))
        if not simplified.is_Integer:
            return None
        resolved[label] = int(simplified)
    return resolved


def koszul_nodes(geometry, k, elements, polynomial_action=None):
    """Occupied Koszul E1 nodes with their Gamma-characters.

    Yields (p, q, character) where character maps the index of a group element to
    the trace on that E1 term. Same bookkeeping as `koszul_virtual_character`,
    but resolved by node instead of summed with signs.
    """
    columns = tuple(zip(*geometry.configuration))
    classes = {}
    for index, column in enumerate(columns):
        classes.setdefault(column, []).append(index)
    degrees = list(classes)
    nodes = {}
    for position, element in enumerate(elements):
        blocks = factor_blocks(element, geometry.ambient)
        if blocks is None:
            raise ValueError('group element permutes projective factors')
        rho = None
        if polynomial_action is not None:
            rho = polynomial_action[position].inv()
        for counts in product(*(range(len(classes[d]) + 1) for d in degrees)):
            weight = sympy.Integer(1)
            for degree, count in zip(degrees, counts):
                indices = classes[degree]
                if rho is None:
                    weight *= sympy.binomial(len(indices), count)
                else:
                    weight *= elementary_symmetric(rho[indices, indices], count)
            if weight == 0:
                continue
            p = sum(counts)
            shifted = tuple(k[i] - sum(count * degree[i]
                                       for degree, count in zip(degrees, counts))
                            for i in range(geometry.h11))
            q, value = ambient_character(blocks, shifted)
            if q is None or value == 0 and position == 0:
                if q is None:
                    continue
            entry = nodes.setdefault((p, q), {})
            entry[position] = sympy.expand(entry.get(position, sympy.Integer(0))
                                           + weight * value)
    return nodes


def collapses(geometry, k):
    """True when no Koszul differential can join two occupied E1 nodes.

    Mirrors cohomology/analytic.py: d_r has bidegree (r, 1-r), so a differential
    can act only between nodes (p,q) and (p-d, q-d+1).
    """
    from ..cohomology.analytic import koszul_terms
    from ..bundles.line_bundle import LineBundle
    terms = koszul_terms(geometry, LineBundle(tuple(k)))
    return not any(p > pp and qq == q - (p - pp) + 1
                   for p, q, _ in terms for pp, qq, _ in terms)


def equivariant_degrees(geometry, k, lift, factors, poly_lift=None, generators=None):
    """Multiplicities of each Gamma-character in every H^q(X, O(k)).

    Returns {q: {character label: multiplicity}} when the Koszul complex
    collapses by bidegree support, so that each H^q is the sum of the E1 nodes
    with q - p equal to that degree, and None otherwise. This resolves H^1 and
    H^2 separately, which the alternating sum cannot do.
    """
    if generators is not None and not is_equivariant(generators, geometry.ambient, k):
        return None
    if not collapses(geometry, k):
        return None
    labels = sorted(lift)
    elements = [lift[label] for label in labels]
    poly = None if poly_lift is None else [poly_lift[label] for label in labels]
    nodes = koszul_nodes(geometry, k, elements, poly)
    by_degree = {}
    for (p, q), character in nodes.items():
        degree = q - p
        if not 0 <= degree <= 3:
            raise ArithmeticError('Koszul degree outside a threefold')
        target = by_degree.setdefault(degree, {label: sympy.Integer(0) for label in labels})
        for position, value in character.items():
            target[labels[position]] += value
    result = {}
    for degree, character in by_degree.items():
        multiplicities = decompose_abelian(character, factors)
        if not is_representation(multiplicities):
            return None
        result[degree] = {label: int(sympy.nsimplify(value))
                          for label, value in multiplicities.items()}
    return result


# ---------------------------------------------------------------------------
# Explicit action matrices, for the cases where the Koszul complex does not
# collapse and the individual H^q need the rank of the differential. Because
# the differential is Gamma-equivariant it preserves isotypic components, so
# the rank splits as a sum of ranks per character and every H^q is resolved.
# ---------------------------------------------------------------------------

def symmetric_power_matrix(block, m):
    """Matrix of Sym^m(block) on the basis x0^i x1^{m-i}, index i.

    The index convention matches cohomology/finite_rank.basis: the index is the
    exponent of the first coordinate of that factor.
    """
    if m == 0:
        return sympy.eye(1)
    x0, x1 = sympy.symbols('_x0 _x1')
    images = (block[0, 0] * x0 + block[0, 1] * x1, block[1, 0] * x0 + block[1, 1] * x1)
    columns = []
    for i in range(m + 1):
        expression = sympy.expand(images[0] ** i * images[1] ** (m - i))
        polynomial = sympy.Poly(expression, x0, x1)
        column = [polynomial.coeff_monomial(x0 ** j * x1 ** (m - j)) for j in range(m + 1)]
        columns.append(column)
    return sympy.Matrix(columns).T


def factor_action_matrix(block, degree):
    """Action on H^*(P^1, O(degree)) in the finite_rank basis; None if it vanishes."""
    if block.shape != (2, 2):
        raise ValueError('explicit action matrices are implemented for P^1 factors')
    if degree >= 0:
        return symmetric_power_matrix(block, degree)
    if degree == -1:
        return None
    # Serre duality: H^1(O(m)) = H^0(O(-m-2))^* (x) det^{-1}
    dual = symmetric_power_matrix(block, -degree - 2)
    return sympy.expand(block.det() ** -1 * dual.inv().T)


def ambient_action_matrix(blocks, k):
    """Action on H^q(A, O(k)) as a Kronecker product over the factors."""
    matrix = sympy.eye(1)
    for block, degree in zip(blocks, k):
        piece = factor_action_matrix(block, degree)
        if piece is None:
            return None
        matrix = sympy.Matrix(sympy.kronecker_product(matrix, piece))
    return matrix


def isotypic_projector(actions, factors, label):
    """(1/|Gamma|) sum_g conj(chi(g)) rho(g), the projector onto the chi-isotypic part."""
    order = 1
    for n in factors:
        order *= n
    size = next(iter(actions.values())).shape[0]
    projector = sympy.zeros(size, size)
    for exponents, matrix in actions.items():
        phase = sympy.Integer(1)
        for a, c, n in zip(exponents, label, factors):
            phase *= sympy.exp(-2 * sympy.pi * sympy.I * a * c / n)
        projector += phase * matrix
    return sympy.expand(projector / order)


def isotypic_ranks(source_actions, target_actions, differential, factors):
    """Rank of an equivariant map restricted to each isotypic component."""
    labels = list(product(*(range(n) for n in factors)))
    ranks = {}
    for label in labels:
        source = isotypic_projector(source_actions, factors, label)
        target = isotypic_projector(target_actions, factors, label)
        restricted = sympy.expand(target * differential * source)
        ranks[label] = restricted.rank()
    return ranks


def _rational_isotypic_ranks(source_actions, target_actions, differential, factors):
    """Exact isotypic ranks in rational arithmetic, when that is possible.

    For a group of exponent two every character takes values +-1, and the
    action matrices of a signed-permutation lift are integral, so the projectors
    (1/|G|) sum_g chi(g) rho(g) are rational and every rank is a rank over Q.
    That is computed exactly with DomainMatrix over QQ -- the same answer as the
    symbolic path, far faster. Returns the ranks; False if the differential is
    not equivariant; None when the fast path does not apply (then the caller
    falls back to the symbolic computation).
    """
    from sympy.polys.domains import QQ
    from sympy.polys.matrices import DomainMatrix
    if any(n > 2 for n in factors):
        return None
    matrices = list(source_actions.values()) + list(target_actions.values()) + [differential]
    if not all(entry.is_Rational for matrix in matrices for entry in matrix):
        return None

    def domain(matrix):
        return DomainMatrix.from_Matrix(matrix).convert_to(QQ)

    d = domain(differential)
    src = {label: domain(m) for label, m in source_actions.items()}
    tgt = {label: domain(m) for label, m in target_actions.items()}
    for label in src:
        if (d * src[label] - tgt[label] * d).to_Matrix().is_zero_matrix is not True:
            return False
    order = 1
    for n in factors:
        order *= n
    labels = list(product(*(range(n) for n in factors)))
    ranks = {}
    for label in labels:
        def projector(actions):
            total = None
            for exponents, matrix in actions.items():
                sign = (-1) ** sum(a * c for a, c in zip(exponents, label))
                term = matrix * QQ(sign, order)
                total = term if total is None else total + term
            return total
        ranks[label] = (projector(tgt) * d * projector(src)).rank()
    return ranks


def invariant_family_coefficients(invariants, coordinates, seed=0):
    """A generic member of the Gamma-invariant defining family.

    `invariants` is the published basis of invariant polynomials. The result is
    the coefficient dictionary used by cohomology/finite_rank: keyed by the
    exponent of the first coordinate of each projective factor. Coefficients are
    deterministic small integers derived from SHA-256, so the member is
    reproducible; cohomology of a *generic* invariant member is what the
    published tables record, and special members can jump.
    """
    import hashlib
    symbols = sympy.symbols(f'x1:{coordinates + 1}')
    coefficients = {}
    for index, entry in enumerate(invariants):
        text = entry[0] if isinstance(entry, list) else entry
        if str(text).strip() == '0':
            continue
        weight = int.from_bytes(hashlib.sha256(f'inv:{seed}:{index}'.encode()).digest()[:4],
                                'big') % 101 - 50
        polynomial = sympy.Poly(sympy.sympify(str(text).replace('^', '**')), *symbols)
        for monomial, coefficient in polynomial.terms():
            key = tuple(monomial[2 * r] for r in range(coordinates // 2))
            coefficients[key] = coefficients.get(key, 0) + weight * int(coefficient)
    return coefficients


def equivariant_degrees_by_ranks(geometry, k, lift, factors, coefficients,
                                 poly_lift=None, generators=None):
    """Resolve H^q when a single Koszul differential joins two E1 nodes.

    The differential is multiplication by the defining polynomial and is
    Gamma-equivariant, so it preserves isotypic components and its rank splits
    character by character. Kernel and cokernel then give the two surviving
    degrees, resolved as Gamma-representations. Implemented for a single
    defining polynomial (one Koszul step).
    """
    from ..bundles.line_bundle import LineBundle
    from ..cohomology.analytic import koszul_terms
    from ..cohomology.finite_rank import multiplication_matrix
    if generators is not None and not is_equivariant(generators, geometry.ambient, k):
        return None
    if len(tuple(zip(*geometry.configuration))) != 1:
        return None
    nodes = {(p, q) for p, q, _ in koszul_terms(geometry, LineBundle(tuple(k)))}
    if len(nodes) != 2:
        return None
    (p_high, q_high), (p_low, q_low) = sorted(nodes, reverse=True)
    if not (p_high == p_low + 1 and q_high == q_low):
        return None
    source = tuple(v - column for v, column in
                   zip(k, tuple(zip(*geometry.configuration))[0]))
    try:
        differential = sympy.Matrix(multiplication_matrix(tuple(k), coefficients))
    except ValueError:
        return None
    labels = sorted(lift)
    source_actions, target_actions = {}, {}
    for label in labels:
        blocks = factor_blocks(lift[label], geometry.ambient)
        if blocks is None:
            return None
        a = ambient_action_matrix(blocks, source)
        b = ambient_action_matrix(blocks, tuple(k))
        if a is None or b is None:
            return None
        source_actions[label], target_actions[label] = a, b
    fast = _rational_isotypic_ranks(source_actions, target_actions, differential, factors)
    if fast is False:
        return None                          # the differential is not equivariant
    if fast is not None:
        ranks = fast
    else:
        for label in labels:
            residual = differential * source_actions[label] - target_actions[label] * differential
            if sympy.simplify(residual.norm()) != 0:
                return None                  # the differential must be equivariant
        ranks = isotypic_ranks(source_actions, target_actions, differential, factors)

    def dimensions(actions):
        out = {}
        for label in ranks:
            total = sympy.Integer(0)
            for exponents, matrix in actions.items():
                phase = sympy.Integer(1)
                for a, c, n in zip(exponents, label, factors):
                    phase *= sympy.exp(-2 * sympy.pi * sympy.I * a * c / n)
                total += phase * matrix.trace()
            out[label] = int(sympy.nsimplify(sympy.simplify(total / len(labels))))
        return out

    source_dimensions, target_dimensions = dimensions(source_actions), dimensions(target_actions)
    kernel = {label: source_dimensions[label] - ranks[label] for label in ranks}
    cokernel = {label: target_dimensions[label] - ranks[label] for label in ranks}
    return {q_high - p_high: kernel, q_low - p_low: cokernel}


def equivariant_cohomology(geometry, k, lift, factors, poly_lift=None, generators=None,
                           coefficients=None):
    """Gamma-representation on every H^q(X, O(k)): collapse first, then map ranks."""
    result = equivariant_degrees(geometry, k, lift, factors, poly_lift, generators)
    if result is not None:
        return result
    if coefficients is None:
        return None
    return equivariant_degrees_by_ranks(geometry, k, lift, factors, coefficients,
                                        poly_lift, generators)
