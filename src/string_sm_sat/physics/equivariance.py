"""Gamma-equivariant bookkeeping for the descent to the quotient.

Scope. This module does NOT compute equivariant cohomology. It handles the
representation theory of the descent, given the Gamma-representation content of
the upstairs cohomologies as input: which characters appear in H^q(X, L), how a
choice of equivariant structure shifts them, and which pieces survive the
projection to the quotient.

Gamma is assumed abelian, presented as a product of cyclic factors, so its
characters form the same group and are labelled by integer tuples. That covers
every case in the published standard-model database (order 2 with Z_2 labels,
order 4 with Z_2 x Z_2 labels). A non-abelian Gamma would need genuine character
tables and is not supported; the code refuses rather than guessing.

References: arXiv:1106.4804 and arXiv:1202.1757, equivariant structures and
Wilson-line breaking; arXiv:1307.4787 Section 2.3 for the upstairs spectrum.
"""
from dataclasses import dataclass
from itertools import product

from .constraints import Check, rule

EQUIVARIANT = rule('equivariant_descent', 'EXACT',
                   '1202.1757 Sections 2-3; 1106.4804 Section 4',
                   ('abelian Gamma acting freely; the Gamma-representation content of the '
                    'upstairs cohomology is supplied as input, not computed here',),
                   False, False)


@dataclass(frozen=True)
class CharacterGroup:
    """Characters of an abelian Gamma = Z_{m_1} x ... x Z_{m_r}."""
    moduli: tuple[int, ...]

    def __post_init__(self):
        if not self.moduli or any(type(m) is not int or m < 1 for m in self.moduli):
            raise ValueError('moduli must be positive integers')

    @property
    def order(self):
        result = 1
        for m in self.moduli:
            result *= m
        return result

    @property
    def labels(self):
        """All characters, in the lexicographic order used by the database tables."""
        return tuple(product(*(range(m) for m in self.moduli)))

    def index(self, chi):
        chi = self.reduce(chi)
        return self.labels.index(chi)

    def reduce(self, chi):
        if len(chi) != len(self.moduli):
            raise ValueError('character has the wrong number of components')
        return tuple(int(x) % m for x, m in zip(chi, self.moduli))

    def add(self, *characters):
        total = [0] * len(self.moduli)
        for chi in characters:
            for i, x in enumerate(self.reduce(chi)):
                total[i] += x
        return self.reduce(total)

    def negate(self, chi):
        return self.reduce([-x for x in self.reduce(chi)])

    def multiply(self, chi, n):
        return self.reduce([n * x for x in self.reduce(chi)])

    def multiplicity(self, row, chi):
        """Multiplicity of `chi` in a decomposition row indexed by self.labels."""
        if len(row) != self.order:
            raise ValueError('decomposition row length does not match the group order')
        return row[self.index(chi)]

    def shift(self, row, chi):
        """Tensoring a representation by the character `chi` permutes the row."""
        return tuple(row[self.index(self.add(label, self.negate(chi)))] for label in self.labels)


def infer_group(labels, order):
    """Infer the cyclic factors from the character labels used in a data set."""
    labels = [tuple(x) for x in labels]
    if not labels:
        raise ValueError('no character labels supplied')
    width = len(labels[0])
    if any(len(x) != width for x in labels):
        raise ValueError('inconsistent character label widths')
    moduli = tuple(max(x[i] for x in labels) + 1 for i in range(width))
    group = CharacterGroup(moduli)
    if group.order != order:
        raise ValueError(f'inferred group {moduli} has order {group.order}, not {order}')
    return group


def regular_multiple(group, row):
    """Return m when the row is m copies of the regular representation, else None."""
    values = set(row)
    return row[0] if len(values) == 1 else None


def check_descent_consistency(group, table, dimensions):
    """The character multiplicities must sum to the total cohomology dimension."""
    residuals = []
    for q, row in enumerate(table):
        total = sum(row)
        residuals.append(total - dimensions[q])
    ok = not any(residuals)
    return Check(EQUIVARIANT, 'PASS' if ok else 'FAIL', residuals,
                 {'note': 'sum of Gamma-character multiplicities equals h^q(X, L)'})
