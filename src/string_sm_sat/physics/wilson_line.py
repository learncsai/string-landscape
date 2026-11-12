"""Wilson-line breaking SU(5) -> SU(3) x SU(2) x U(1)_Y and the downstairs spectrum.

The Wilson line is a flat bundle given by a homomorphism Gamma -> U(1)_Y inside
SU(5); since Gamma is abelian this is a pair of characters, one for the colour
triplet and one for the weak doublet of the fundamental 5. Everything else
follows: 10 = wedge^2 5, and 5bar / 5 are the conjugates.

    5    = (3,1)_{-1/3} [T]  (+)  (1,2)_{1/2} [D]
    10   = (3,2)_{1/6}  [Q = T^D]  (+) (3bar,1)_{-2/3} [u^c = T^T]
           (+) (1,1)_{1} [e^c = D^D]
    5bar = (3bar,1)_{1/3} [d^c]  (+)  (1,2)_{-1/2} [L]

A multiplet piece with Wilson-line character `chi` survives the quotient with
multiplicity equal to the multiplicity of `chi` in the corresponding upstairs
cohomology, once the equivariant structure has been applied. That is the whole
content of the projection for abelian Gamma.

This module performs exact representation-theoretic bookkeeping. It takes the
Gamma-character content of the upstairs cohomologies as input; it does not
compute it. Multiplicities are therefore only as good as that input, and the
certificate records its provenance.

References: arXiv:1106.4804 Section 4; arXiv:1202.1757 Sections 2-3 and the
spectrum tables; arXiv:1307.4787 Table 2 for the upstairs assignments.
"""
from dataclasses import dataclass

from .constraints import Check, rule
from .equivariance import CharacterGroup

WILSON = rule('wilson_line_projection', 'EXACT',
              '1202.1757 Sections 2-3; 1106.4804 Section 4',
              ('abelian Gamma; Wilson line valued in U(1)_Y; the Gamma-character content '
               'of the upstairs cohomology is supplied as input',),
              False, False)

# name -> (SU(3), SU(2), 6*hypercharge, how it sits inside wedge^2 of (T, D))
TEN_PIECES = (('Q', 3, 2, 1, ('T', 'D')),
              ('u^c', 3, 1, -4, ('T', 'T')),
              ('e^c', 1, 1, 6, ('D', 'D')))
FIVEBAR_PIECES = (('d^c', 3, 1, 2, ('T',)),
                  ('L', 1, 2, -3, ('D',)))


@dataclass(frozen=True)
class WilsonLine:
    """Characters assigned to the triplet and doublet of the fundamental 5."""
    group: CharacterGroup
    triplet: tuple[int, ...]
    doublet: tuple[int, ...]

    def piece_character(self, factors, conjugate=False):
        """Character of a multiplet piece built from the listed 5-factors."""
        chi = self.group.add(*[self.triplet if f == 'T' else self.doublet for f in factors])
        return self.group.negate(chi) if conjugate else chi

    def as_dict(self):
        return {'triplet': list(self.triplet), 'doublet': list(self.doublet),
                'moduli': list(self.group.moduli)}


def ten_multiplicities(group, wilson, row, equivariant_structure=None):
    """Downstairs multiplicities of Q, u^c, e^c from one H^1(X, L_a)."""
    if equivariant_structure is not None:
        row = group.shift(row, equivariant_structure)
    return {name: group.multiplicity(row, wilson.piece_character(factors))
            for name, _, _, _, factors in TEN_PIECES}


def fivebar_multiplicities(group, wilson, row, equivariant_structure=None):
    """Downstairs multiplicities of d^c and L from one H^1(X, L_a (x) L_b)."""
    if equivariant_structure is not None:
        row = group.shift(row, equivariant_structure)
    return {name: group.multiplicity(row, wilson.piece_character(factors, conjugate=True))
            for name, _, _, _, factors in FIVEBAR_PIECES}


def group_into_multiplets(pieces, names):
    """Split multiplicities into complete SU(5) multiplets plus leftovers.

    The published spectra write a complete 5bar when a d^c and an L come
    together, and call a leftover doublet a Higgs. Same idea for the 10.
    """
    complete = min(pieces[n] for n in names)
    return complete, {n: pieces[n] - complete for n in names}


def downstairs_spectrum(group, wilson, ten_rows, pair_rows_h1, pair_rows_h2,
                        equivariant=None, singlet_rows=None):
    """Assemble the full downstairs spectrum from Gamma-character tables.

    ten_rows       : per line bundle a, the H^1(X, L_a) character row
    pair_rows_h1/2 : per unordered pair (a,b), the H^1 / H^2 character rows of
                     L_a (x) L_b, in the lexicographic pair order
    equivariant    : optional per-bundle equivariant structure characters
    """
    tens, fivebars, higgs, leftovers = [], [], [], []

    for a, row in enumerate(ten_rows):
        shift = None if equivariant is None else equivariant[a]
        pieces = ten_multiplicities(group, wilson, row, shift)
        complete, leftover = group_into_multiplets(pieces, [n for n, *_ in TEN_PIECES])
        if complete:
            tens.append({'bundle': a + 1, 'multiplicity': complete})
        for name, count in leftover.items():
            if count:
                leftovers.append({'from': f'10_{a+1}', 'piece': name,
                                  'multiplicity': count, 'conjugate': False})

    pairs = [(a, b) for a in range(len(ten_rows)) for b in range(a + 1, len(ten_rows))]
    for (a, b), row1, row2 in zip(pairs, pair_rows_h1, pair_rows_h2):
        shift = None if equivariant is None else group.add(equivariant[a], equivariant[b])
        for row, conjugate in ((row1, False), (row2, True)):
            pieces = fivebar_multiplicities(group, wilson, row, shift)
            complete, leftover = group_into_multiplets(pieces, ['d^c', 'L'])
            label = '5' if conjugate else '5bar'
            if complete:
                fivebars.append({'pair': [a + 1, b + 1], 'type': label,
                                 'multiplicity': complete})
            if leftover['L']:
                higgs.append({'pair': [a + 1, b + 1],
                              'type': 'Hbar' if conjugate else 'H',
                              'multiplicity': leftover['L']})
            if leftover['d^c']:
                leftovers.append({'from': f'{label}_{a+1}{b+1}', 'piece': 'colour triplet',
                                  'multiplicity': leftover['d^c'], 'conjugate': conjugate})

    singlets = None
    if singlet_rows is not None:
        singlets = sum(sum(row) for row in singlet_rows)

    # chiral content: complete multiplets minus their conjugates
    chiral_ten = sum(t['multiplicity'] for t in tens)
    chiral_five = (sum(f['multiplicity'] for f in fivebars if f['type'] == '5bar')
                   - sum(f['multiplicity'] for f in fivebars if f['type'] == '5'))
    families = {'Q': chiral_ten, 'u^c': chiral_ten, 'e^c': chiral_ten,
                'd^c': chiral_five, 'L': chiral_five}

    # a leftover piece is vector-like when it pairs with its conjugate, chiral otherwise
    higgs_up = sum(h['multiplicity'] for h in higgs if h['type'] == 'H')
    higgs_down = sum(h['multiplicity'] for h in higgs if h['type'] == 'Hbar')
    triplet_up = sum(x['multiplicity'] for x in leftovers
                     if x['piece'] == 'colour triplet' and not x['conjugate'])
    triplet_down = sum(x['multiplicity'] for x in leftovers
                       if x['piece'] == 'colour triplet' and x['conjugate'])
    exotics = [x for x in leftovers if x['piece'] != 'colour triplet']
    if triplet_up != triplet_down:
        exotics.append({'from': 'wedge^2 V', 'piece': 'colour triplet (chiral)',
                        'multiplicity': abs(triplet_up - triplet_down)})
    return {
        'tens': tens, 'fivebars': fivebars, 'higgs': higgs, 'exotics': exotics,
        'families': families, 'higgs_pairs': min(higgs_up, higgs_down),
        'higgs_up': higgs_up, 'higgs_down': higgs_down,
        'colour_triplet_pairs': min(triplet_up, triplet_down),
        'singlets': singlets,
    }


def acceptance_report(spectrum, gamma_order, massless_u1='UNKNOWN'):
    """The Section-31 human-readable acceptance table."""
    families = spectrum['families']
    three = all(families[n] == 3 for n in ('Q', 'u^c', 'e^c', 'd^c', 'L'))
    triplets = spectrum.get('colour_triplet_pairs', 0) + sum(
        e['multiplicity'] for e in spectrum['exotics'] if 'triplet' in e['piece'])
    return {
        'three_chiral_families': three,
        'family_multiplicities': families,
        'charged_chiral_exotics': bool(spectrum['exotics']),
        'exotics': spectrum['exotics'],
        'higgs_doublet_pair': spectrum['higgs_pairs'] > 0,
        'higgs_pairs': spectrum['higgs_pairs'],
        'colour_triplet_higgs': triplets > 0,
        'additional_massless_U1': massless_u1,
        'singlets': spectrum['singlets'] if spectrum['singlets'] is not None else 'UNKNOWN',
        'gamma_order': gamma_order,
        'claim': ('representation-theoretic descent only; the Gamma-character content of the '
                  'upstairs cohomology is input, and no SUSY breaking or moduli '
                  'stabilisation is addressed'),
    }


def check_spectrum(spectrum):
    report = acceptance_report(spectrum, None)
    good = (report['three_chiral_families'] and not report['charged_chiral_exotics']
            and report['higgs_doublet_pair'])
    return Check(WILSON, 'PASS' if good else 'FAIL', report['family_multiplicities'],
                 {'exotics': spectrum['exotics'], 'higgs_pairs': spectrum['higgs_pairs']})
