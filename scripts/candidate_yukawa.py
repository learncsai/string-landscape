"""Yukawa sector of the eleven additional X7862 candidates.

For every frozen candidate and every accepted downstairs configuration this
computes, exactly:

  1. the singlet spectrum, from the Gamma-representation on H^1(X, L_a (x) L_b^*);
  2. the up-type, down-type and charged-lepton Yukawa matrices as tables of
     gauge-invariant singlet monomials (the U(1)^4 selection rule, exact and
     unbounded in the insertion order);
  3. the leading-order (Abelian-locus) Yukawa matrices as actual cohomological
     triple products, with their exact ranks;
  4. the dangerous and desirable operators: dimension-five proton decay,
     dimension-four R-parity violation, the mu term and the Weinberg operator.

The rank classification follows the four categories asked for:

  FULL_RANK_GENERIC   -- rank three already at the Abelian locus
  FULL_RANK_ON_LOCUS  -- rank three only once singlet vacuum expectation values
                         are switched on, i.e. the selection rule permits a
                         rank-three matrix but the Abelian-locus cohomology does
                         not reach it
  RANK_DEFICIENT      -- the selection rule itself caps the rank below three, so
                         no choice of singlet vacuum can fix it
  UNKNOWN             -- the cohomological product could not be computed (mixed
                         Koszul levels, or several Higgs states in one character)

Only zero/nonzero structure and ranks are meaningful: the normalisation of the
trace map is not fixed, and physical Yukawas would need matter-field Kahler
metrics, which are not computed anywhere in this repository.
"""
import argparse
import json
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import sympy  # noqa: E402

from leading_order_yukawa import structural_rank  # noqa: E402
from string_sm_sat.geometry.cicy import benchmark  # noqa: E402
from string_sm_sat.physics.equivariance import CharacterGroup  # noqa: E402
from string_sm_sat.physics.equivariant_cohomology import (cyclic_lift,  # noqa: E402
                                                          equivariant_cohomology,
                                                          invariant_family_coefficients,
                                                          is_equivariant, to_matrix)
from string_sm_sat.physics.superpotential import (DownstairsSpectrum,  # noqa: E402
                                                  mu_term, operator_table, yukawa_down,
                                                  yukawa_up)
from string_sm_sat.physics.yukawa import equivariant_coupling  # noqa: E402

MANIFEST = ROOT / 'benchmarks/x7862/candidate-manifest.json'
SYMMETRIES = ROOT / 'data/processed/published_symmetries.json'


def setup(cicy, symmetry_number):
    entry = json.loads(SYMMETRIES.read_text())['symmetries'][str(cicy)][symmetry_number - 1]
    factors = entry['cyclic_factors']
    generators = [to_matrix(m) for m in entry['generators']]
    lift = cyclic_lift(generators, factors)
    poly = (cyclic_lift([to_matrix(m) for m in entry['polynomial_action']], factors)
            if entry['polynomial_action'] else None)
    geometry = benchmark(str(cicy))
    coefficients = None
    if entry.get('invariants') and len(tuple(zip(*geometry.configuration))) == 1:
        coefficients = invariant_family_coefficients(
            entry['invariants'], sum(n + 1 for n in geometry.ambient))
    return geometry, lift, factors, poly, generators, coefficients


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=None)
    parser.add_argument('--only', default=None, help='comma-separated candidate ids')
    parser.add_argument('--manifest', default=str(MANIFEST),
                        help='candidate manifest (default: the frozen step-1 manifest)')
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    cicy = int(str(manifest['geometry']).lstrip('X'))
    geometry, lift, factors, poly, generators, coefficients = setup(
        cicy, manifest['symmetry_number'])
    group = CharacterGroup(tuple(factors))
    trivial = tuple(0 for _ in factors)
    h11 = geometry.h11

    def combine(*bundles):
        return tuple(sum(b[i] for b in bundles) for i in range(h11))

    def invert(bundle):
        return tuple(-x for x in bundle)

    @lru_cache(maxsize=None)
    def cohomology_table(k):
        if not is_equivariant(generators, geometry.ambient, k):
            return None
        return equivariant_cohomology(geometry, k, lift, factors, poly, generators,
                                      coefficients)

    @lru_cache(maxsize=None)
    def coupling(charges, labels):
        try:
            return equivariant_coupling(geometry, lift, factors, charges, labels)
        except ValueError as error:
            return {'status': 'REFUSED', 'detail': str(error)}

    wanted = set(args.only.split(',')) if args.only else None
    results = []
    for candidate in manifest['candidates']:
        if wanted and candidate['candidate_id'] not in wanted:
            continue
        columns = [tuple(c) for c in candidate['columns']]
        record = {'candidate_id': candidate['candidate_id'],
                  'class': candidate.get('class', 'additional'),
                  'accepted_count': candidate['downstairs']['accepted_count'],
                  'columns': [list(c) for c in columns],
                  'absence_classification': candidate['absence_classification'],
                  'additional_massless_U1': candidate['additional_massless_U1'],
                  'configurations': []}
        for configuration in candidate['downstairs']['accepted']:
            record['configurations'].append(
                analyse(configuration, columns, group, factors, trivial, combine,
                        invert, cohomology_table, coupling, h11))
        record['summary'] = summarise_candidate(record['configurations'])
        results.append(record)
        print(format_candidate(record))

    if args.out:
        Path(args.out).write_text(json.dumps(
            {'schema': 1, 'geometry': manifest['geometry'],
             'gamma_order': manifest['gamma_order'],
             'symmetry_number': manifest['symmetry_number'],
             'scope': ('holomorphic superpotential only; zero/nonzero structure and '
                       'ranks are meaningful, overall normalisation is not; physical '
                       'Yukawas need matter Kahler metrics and are not computed'),
             'candidates': results}, indent=1, default=str))


def singlet_spectrum(columns, shift, group, trivial, cohomology_table, h11):
    """Ordered pairs (a, b) for which a downstairs singlet S_{ab} exists.

    A singlet is an SU(5) singlet, so the Wilson line acts trivially on it and the
    surviving states are the Gamma-invariants of H^1(X, L_a (x) L_b^*), after the
    equivariant-structure shift e_a - e_b.
    """
    present, undetermined = [], []
    for a in range(5):
        for b in range(5):
            if a == b:
                continue
            k = tuple(columns[a][i] - columns[b][i] for i in range(h11))
            if not any(k):
                continue                      # L_a = L_b gives H^1(X, O_X) = 0
            table = cohomology_table(k)
            if table is None:
                undetermined.append((a + 1, b + 1))
                continue
            row = table.get(1, {})
            characters = tuple(row.get(label, 0) for label in group.labels)
            # the singlet is Wilson-line neutral; after the shift e_a - e_b the
            # invariant states have unshifted character -(e_a - e_b)
            twist = group.negate(group.add(shift[a], group.negate(shift[b])))
            if group.multiplicity(characters, twist) > 0:
                present.append((a + 1, b + 1))
    return present, undetermined


def analyse(configuration, columns, group, factors, trivial, combine, invert,
            cohomology_table, coupling, h11):
    shift = [tuple(x) for x in configuration['equivariant_structure']]
    triplet, doublet = (tuple(x) for x in configuration['wilson_line'])
    singlets, undetermined = singlet_spectrum(columns, shift, group, trivial,
                                              cohomology_table, h11)

    ten_families = []
    for item in configuration['tens']:
        ten_families.extend([item['bundle']] * item['multiplicity'])
    fivebar_families = []
    for item in configuration['fivebars']:
        if item['type'] == '5bar':
            fivebar_families.extend([tuple(item['pair'])] * item['multiplicity'])
    higgs_up = [tuple(h['pair']) for h in configuration['higgs'] if h['type'] == 'H']
    higgs_down = [tuple(h['pair']) for h in configuration['higgs'] if h['type'] == 'Hbar']

    # Gamma-characters of the low-energy fields, from the Wilson line
    def negate(chi):
        return group.negate(chi)

    chi = {'Q': group.add(triplet, doublet), 'u^c': group.add(triplet, triplet),
           'e^c': group.add(doublet, doublet), 'd^c': negate(triplet),
           'L': negate(doublet), 'H_u': doublet, 'H_d': negate(doublet)}

    out = {'equivariant_structure': [list(s) for s in shift],
           'wilson_line': [list(triplet), list(doublet)],
           'ten_families': list(ten_families),
           'fivebar_families': [list(f) for f in fivebar_families],
           'singlets': [list(s) for s in singlets],
           'singlets_undetermined': [list(s) for s in undetermined],
           'higgs_choices': []}

    for up in higgs_up or [None]:
        for down in higgs_down or [None]:
            spectrum = DownstairsSpectrum(tuple(ten_families), tuple(fivebar_families),
                                          up, down, tuple(singlets))
            block = {'higgs_up': list(up) if up else None,
                     'higgs_down': list(down) if down else None,
                     'selection': {
                         'Y_u': yukawa_up(spectrum),
                         'Y_d': yukawa_down(spectrum),
                         'mu': mu_term(spectrum)},
                     'operators': operator_table(spectrum)}
            for name, sector in (('Y_u', 'up'), ('Y_d', 'down'), ('Y_e', 'lepton')):
                block[name] = leading_order(sector, spectrum, columns, chi, combine,
                                            invert, coupling, h11, group, shift)
                block[name]['classification'] = classify_rank(
                    block[name], block['selection']['Y_u' if sector == 'up' else 'Y_d'])
            block['cubic_operators'] = cubic_operators(spectrum, columns, chi, combine, invert,
                                                       coupling, h11, group, shift)
            out['higgs_choices'].append(block)
    return out


def bundle_shift(group, shift, kind, indices):
    """Equivariant structure of the bundle carrying a field, as a character.

    10_a on L_a: e_a.  5bar_{ab} on L_a L_b: e_a + e_b.  5_{ab} on (L_a L_b)^*:
    -(e_a + e_b).  S_{ab} on L_a L_b^*: e_a - e_b.
    """
    e = lambda a: shift[a - 1]
    if kind == 'ten':
        return e(indices)
    if kind == 'fivebar':
        return group.add(e(indices[0]), e(indices[1]))
    if kind == 'five':
        return group.negate(group.add(e(indices[0]), e(indices[1])))
    if kind == 'singlet':
        return group.add(e(indices[0]), group.negate(e(indices[1])))
    raise ValueError(kind)


def slot_label(group, piece, shift_character):
    """Upstairs (unshifted) character selected by a piece on a shifted bundle.

    wilson_line.shift permutes a decomposition row by row[label - chi], so a piece
    with Wilson-line character chi_piece on a bundle with structure e sits in the
    unshifted isotypic component chi_piece - e.
    """
    return group.add(piece, group.negate(shift_character))


def evaluate(coupling, bundles, labels):
    """NONZERO / VANISHES_* / UNKNOWN_* for one triple product."""
    outcome = coupling(tuple(bundles), tuple(labels))
    status = outcome['status']
    if status == 'COMPUTED':
        nonzero = any(value != 0 for plane in outcome['tensor'] for row in plane
                      for value in row)
        return ('NONZERO' if nonzero else 'VANISHES_ON_ISOTYPIC_COMPONENTS',
                outcome.get('complex_structure_independent'))
    if status == 'VANISHES_BY_KOSZUL_LEVEL':
        return 'VANISHES_BY_KOSZUL_LEVEL', True
    if status == 'NO_MATTER_IN_THAT_CHARACTER':
        return 'NO_STATE_IN_THAT_CHARACTER', True
    return ('UNKNOWN_' + status if not status.startswith('UNKNOWN') else status), None


def combine_verdicts(verdicts):
    if not verdicts:
        return 'NO_TERM_AT_THIS_ORDER'
    if any(v == 'NONZERO' for v in verdicts):
        return 'NONZERO'
    if any(v.startswith('UNKNOWN') for v in verdicts):
        return 'UNKNOWN'
    return 'VANISHES'


def cubic_operators(spectrum, columns, chi, combine, invert, coupling, h11, group, shift):
    """Operators that are genuine triple products, evaluated cohomologically.

    * dimension-four R-parity violation at singlet order zero, 10 5bar 5bar with
      both 5bars matter: its three pieces Q L d^c, L L e^c and u^c d^c d^c;
    * the mu term generated at order one, S H_u H_d;
    * bilinear R-parity violation generated at order one, S L H_u.
    Anything at higher order is not a cup product and is left to the selection
    rule, where it can only be FORBIDDEN or UNKNOWN.
    """
    neutral = lambda bs: not any(sum(b[i] for b in bs) for i in range(h11))
    bundle = {
        'ten': lambda a: columns[a - 1],
        'fivebar': lambda p: combine(columns[p[0] - 1], columns[p[1] - 1]),
        'five': lambda p: invert(combine(columns[p[0] - 1], columns[p[1] - 1])),
        'singlet': lambda p: tuple(x - y for x, y in zip(columns[p[0] - 1], columns[p[1] - 1])),
    }
    label = lambda piece, kind, idx: slot_label(group, chi[piece] if piece else
                                                tuple(0 for _ in chi['Q']),
                                                bundle_shift(group, shift, kind, idx))
    out = {}

    # dimension-four R-parity violation, order zero
    verdicts, independent = [], []
    fives = sorted(set(spectrum.fivebar_families))
    for a in sorted(set(spectrum.ten_families)):
        for i, q in enumerate(fives):
            for r in fives[i:]:
                bs = (bundle['ten'](a), bundle['fivebar'](q), bundle['fivebar'](r))
                if not neutral(bs):
                    continue
                for pieces in (('Q', 'L', 'd^c'), ('Q', 'd^c', 'L'), ('e^c', 'L', 'L'),
                               ('u^c', 'd^c', 'd^c')):
                    labels = (label(pieces[0], 'ten', a), label(pieces[1], 'fivebar', q),
                              label(pieces[2], 'fivebar', r))
                    v, ind = evaluate(coupling, bs, labels)
                    verdicts.append(v)
                    independent.append(ind)
    out['dim4_RPV_order0'] = {'verdict': combine_verdicts(verdicts),
                              'couplings_evaluated': len(verdicts),
                              'complex_structure_independent': all(x for x in independent)
                              if independent else None}

    for name, legs in (('mu_order1', ('H_u', 'H_d')), ('bilinear_RPV_order1', ('L', 'H_u'))):
        verdicts, independent = [], []
        if spectrum.higgs_up is None or (name == 'mu_order1' and spectrum.higgs_down is None):
            out[name] = {'verdict': 'NO_HIGGS'}
            continue
        seconds = ([spectrum.higgs_up] if name == 'mu_order1'
                   else sorted(set(spectrum.fivebar_families)))
        for s in spectrum.singlets:
            for second in seconds:
                if name == 'mu_order1':
                    bs = (bundle['singlet'](s), bundle['five'](spectrum.higgs_up),
                          bundle['fivebar'](spectrum.higgs_down))
                    labels = (label(None, 'singlet', s), label('H_u', 'five', spectrum.higgs_up),
                              label('H_d', 'fivebar', spectrum.higgs_down))
                else:
                    bs = (bundle['singlet'](s), bundle['fivebar'](second),
                          bundle['five'](spectrum.higgs_up))
                    labels = (label(None, 'singlet', s), label('L', 'fivebar', second),
                              label('H_u', 'five', spectrum.higgs_up))
                if not neutral(bs):
                    continue
                v, ind = evaluate(coupling, bs, labels)
                verdicts.append(v)
                independent.append(ind)
        out[name] = {'verdict': combine_verdicts(verdicts),
                     'couplings_evaluated': len(verdicts),
                     'complex_structure_independent': all(x for x in independent)
                     if independent else None}
    return out


def leading_order(sector, spectrum, columns, chi, combine, invert, coupling, h11,
                  group=None, shift=None):
    """The Abelian-locus Yukawa matrix as an exact cohomological product.

    Each slot projects onto the Wilson-line character of its piece minus the
    equivariant structure of the bundle carrying it (see slot_label).
    """
    if shift is None:
        shift = [tuple(0 for _ in chi['Q'])] * 5
    lab = lambda piece, kind, idx: (chi[piece] if group is None else
                                    slot_label(group, chi[piece],
                                               bundle_shift(group, shift, kind, idx)))
    if sector == 'up':
        if spectrum.higgs_up is None:
            return {'status': 'NO_HIGGS'}
        rows = spectrum.ten_families
        others = spectrum.ten_families
        higgs = invert(combine(columns[spectrum.higgs_up[0] - 1],
                               columns[spectrum.higgs_up[1] - 1]))
        pieces = ('Q', 'u^c', 'H_u')
        kinds = ('ten', 'ten', 'five')
        higgs_index = spectrum.higgs_up
    else:
        if spectrum.higgs_down is None:
            return {'status': 'NO_HIGGS'}
        rows = spectrum.ten_families
        others = spectrum.fivebar_families
        higgs = combine(columns[spectrum.higgs_down[0] - 1],
                        columns[spectrum.higgs_down[1] - 1])
        pieces = (('Q', 'd^c', 'H_d') if sector == 'down' else ('e^c', 'L', 'H_d'))
        kinds = ('ten', 'fivebar', 'fivebar')
        higgs_index = spectrum.higgs_down

    def slot(items):
        seen, out = {}, []
        for item in items:
            index = seen.get(item, 0)
            seen[item] = index + 1
            out.append((item, index))
        return out

    row_slots, column_slots = slot(rows), slot(others)
    matrix = sympy.zeros(len(row_slots), len(column_slots))
    notes = set()
    independent = []
    for i, (a, row_index) in enumerate(row_slots):
        for j, (other, column_index) in enumerate(column_slots):
            second = (columns[other - 1] if sector == 'up'
                      else combine(columns[other[0] - 1], columns[other[1] - 1]))
            bundles = (columns[a - 1], second, higgs)
            if any(sum(b[i2] for b in bundles) for i2 in range(h11)):
                continue                                  # not neutral: zero here
            labels = (lab(pieces[0], kinds[0], a), lab(pieces[1], kinds[1], other),
                      lab(pieces[2], kinds[2], higgs_index))
            outcome = coupling(bundles, labels)
            if outcome['status'] == 'COMPUTED':
                independent.append(outcome.get('complex_structure_independent'))
            if outcome['status'] in ('UNKNOWN_HIGHER_KOSZUL_LEVEL',
                                     'UNKNOWN_NONZERO_KOSZUL_MAP'):
                notes.add(outcome['status'])
                continue
            if outcome['status'] == 'REFUSED':
                notes.add('REFUSED:' + outcome.get('detail', '')[:60])
                continue
            if outcome['status'] != 'COMPUTED':
                continue
            if outcome['dimensions'][2] != 1:
                notes.add(f"HIGGS_MULTIPLICITY_{outcome['dimensions'][2]}")
                continue
            # the isotypic dimension of each matter slot must equal the number of
            # families the spectrum assigns to that bundle; otherwise the labels
            # (Wilson line minus equivariant structure) are inconsistent
            if (outcome['dimensions'][0] != rows.count(a)
                    or outcome['dimensions'][1] != others.count(other)):
                notes.add('DIMENSION_MISMATCH')
                continue
            tensor = outcome['tensor']
            if row_index >= len(tensor) or column_index >= len(tensor[row_index]):
                notes.add('FAMILY_INDEX_OUT_OF_RANGE')
                continue
            matrix[i, j] = tensor[row_index][column_index][0]
    blocked = any(n.startswith(('REFUSED', 'HIGGS_MULTIPLICITY', 'FAMILY_INDEX', 'UNKNOWN_', 'DIMENSION'))
                  for n in notes)
    return {'status': 'UNKNOWN' if blocked else 'COMPUTED',
            'rank': None if blocked else matrix.rank(),
            'shape': [matrix.rows, matrix.cols],
            'support': [[int(bool(matrix[i, j])) for j in range(matrix.cols)]
                        for i in range(matrix.rows)],
            'entries': [[str(matrix[i, j]) for j in range(matrix.cols)]
                        for i in range(matrix.rows)],
            'complex_structure_independent': all(x for x in independent) if independent
            else True,
            'notes': sorted(notes)}


def classify_rank(leading, selection_table):
    """FULL_RANK_GENERIC / FULL_RANK_ON_LOCUS / RANK_DEFICIENT / UNKNOWN."""
    if leading.get('status') != 'COMPUTED':
        return 'UNKNOWN'
    generations = min(leading['shape'])
    if leading['rank'] == generations:
        return 'FULL_RANK_GENERIC'
    if selection_table is None:
        return 'UNKNOWN'
    allowed = [[int(cell['status'] != 'FORBIDDEN_BY_SELECTION_RULE') for cell in row]
               for row in selection_table]
    if structural_rank(allowed) == generations:
        return 'FULL_RANK_ON_LOCUS'
    return 'RANK_DEFICIENT'


def summarise_candidate(configurations):
    tally = Counter()
    for configuration in configurations:
        for block in configuration['higgs_choices']:
            for name in ('Y_u', 'Y_d', 'Y_e'):
                tally[f"{name}:{block[name]['classification']}"] += 1
    best = {}
    order = ['FULL_RANK_GENERIC', 'FULL_RANK_ON_LOCUS', 'RANK_DEFICIENT', 'UNKNOWN']
    for name in ('Y_u', 'Y_d', 'Y_e'):
        for label in order:
            if tally.get(f'{name}:{label}'):
                best[name] = label
                break
        best.setdefault(name, 'UNKNOWN')
    return {'counts': dict(tally), 'best_over_configurations': best}


def format_candidate(record):
    best = record['summary']['best_over_configurations']
    return (f"{record['candidate_id']}  configurations "
            f"{len(record['configurations']):2d}  "
            f"Y_u {best['Y_u']:18s} Y_d {best['Y_d']:18s} Y_e {best['Y_e']:18s}")


if __name__ == '__main__':
    main()
