"""Leading-order (Abelian-locus) Yukawa matrices from the cohomological product.

At the Abelian locus, where all singlet vacuum expectation values vanish, a
Yukawa entry is a genuine triple cup product

    H^1(X, L_1) x H^1(X, L_2) x H^1(X, L_3) -> H^3(X, O_X) = C ,

restricted to the Gamma-isotypic components picked out by the Wilson line.  This
computes those matrices exactly -- no charge argument, no truncation -- and
compares their ranks with the published tables' leading-order support.

The published table gives only which entries are allowed, so the fair comparison
is our exact rank against the published *structural* rank (the largest rank any
matrix with that support can have).  Our rank exceeding the structural rank is a
contradiction; our rank falling below it means extra cohomological vanishing.
"""
import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import sympy  # noqa: E402

from published_table_consistency import (DATABASE, decode_edownspec,  # noqa: E402
                                         published_matrix)
from string_sm_sat.geometry.cicy import benchmark  # noqa: E402
from string_sm_sat.physics.equivariant_cohomology import cyclic_lift, to_matrix  # noqa: E402
from string_sm_sat.physics.equivariance import CharacterGroup  # noqa: E402
from string_sm_sat.physics.yukawa import contract_higgs, equivariant_coupling  # noqa: E402

SYMMETRIES = ROOT / 'data/processed/published_symmetries.json'


def structural_rank(support):
    """Largest rank attainable by a matrix with the given boolean support."""
    rows = len(support)
    columns = len(support[0]) if rows else 0
    match = [-1] * columns

    def augment(row, seen):
        for column in range(columns):
            if support[row][column] and not seen[column]:
                seen[column] = True
                if match[column] == -1 or augment(match[column], seen):
                    match[column] = row
                    return True
        return False

    return sum(augment(row, [False] * columns) for row in range(rows))


def main():
    global slot_label, bundle_shift
    from candidate_yukawa import bundle_shift, slot_label
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=7862)
    parser.add_argument('--symmetry', type=int, default=5)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    data = json.loads(DATABASE.read_text())
    entry = json.loads(SYMMETRIES.read_text())['symmetries'][str(args.cicy)][args.symmetry - 1]
    factors = entry['cyclic_factors']
    lift = cyclic_lift([to_matrix(m) for m in entry['generators']], factors)
    geometry = benchmark(str(args.cicy))
    h11 = geometry.h11

    def combine(*bundles):
        return tuple(sum(b[i] for b in bundles) for i in range(h11))

    def invert(bundle):
        return tuple(-x for x in bundle)

    @lru_cache(maxsize=None)
    def coupling(charges, labels):
        try:
            return equivariant_coupling(geometry, lift, factors, charges, labels)
        except ValueError as error:
            return {'status': 'REFUSED', 'detail': str(error), 'dimensions': [0, 0, 0]}

    results = []
    for model in data['models']:
        if model['cicy'] != args.cicy or model.get('symmetry_number') != args.symmetry:
            continue
        decoded = decode_edownspec(model)
        if decoded is None or not model.get('LineSum'):
            continue
        columns = list(zip(*model['LineSum']))           # L_a = column a
        wilson = model['WLine']
        triplet, doublet = tuple(wilson[0]), tuple(wilson[1])
        add = lambda *cs: tuple(sum(c[i] for c in cs) % factors[i] for i in range(len(factors)))
        chi_Q = add(triplet, doublet)
        chi_uc = add(triplet, triplet)
        chi_Hu = doublet
        chi_dc = tuple(-x % factors[i] for i, x in enumerate(triplet))
        chi_Hd = tuple(-x % factors[i] for i, x in enumerate(doublet))

        group = CharacterGroup(tuple(factors))
        shift = [tuple(x) for x in (model.get('EquivStr') or [[0] * len(factors)] * 5)]
        record = {'cicy': args.cicy, 'model': model['ModelNumber'],
                  'tens': list(decoded['tens']),
                  'fivebars': [list(f) for f in decoded['fivebars']],
                  'higgs_up': list(decoded['higgs_up']),
                  'higgs_down': list(decoded['higgs_down'])}

        # each family carries (bundle, index of that family within its bundle)
        def enumerate_families(labels):
            seen, out = {}, []
            for label in labels:
                index = seen.get(label, 0)
                seen[label] = index + 1
                out.append((label, index))
            return out

        ten_families = enumerate_families(decoded['tens'])
        five_families = enumerate_families(decoded['fivebars'])

        for kind in ('YukawaUp', 'YukawaDown'):
            others = ten_families if kind == 'YukawaUp' else five_families
            pair = decoded['higgs_up' if kind == 'YukawaUp' else 'higgs_down']
            higgs = invert(combine(columns[pair[0] - 1], columns[pair[1] - 1])) \
                if kind == 'YukawaUp' else combine(columns[pair[0] - 1], columns[pair[1] - 1])
            labels = ((chi_Q, chi_uc, chi_Hu) if kind == 'YukawaUp'
                      else (chi_Q, chi_dc, chi_Hd))
            matrix = sympy.zeros(len(ten_families), len(others))
            notes = set()
            for p_index, (a, row_slot) in enumerate(ten_families):
                for q_index, (other, column_slot) in enumerate(others):
                    second = (columns[other - 1] if kind == 'YukawaUp'
                              else combine(columns[other[0] - 1], columns[other[1] - 1]))
                    bundles = (columns[a - 1], second, higgs)
                    if any(sum(b[i] for b in bundles) for i in range(h11)):
                        continue                       # forbidden at leading order
                    # project each slot onto (Wilson-line character) minus (the
                    # equivariant structure of its bundle), as candidate_yukawa does
                    if kind == 'YukawaUp':
                        slot_labels = (
                            slot_label(group, labels[0], bundle_shift(group, shift, 'ten', a)),
                            slot_label(group, labels[1], bundle_shift(group, shift, 'ten', other)),
                            slot_label(group, labels[2], bundle_shift(group, shift, 'five', pair)))
                    else:
                        slot_labels = (
                            slot_label(group, labels[0], bundle_shift(group, shift, 'ten', a)),
                            slot_label(group, labels[1], bundle_shift(group, shift, 'fivebar', other)),
                            slot_label(group, labels[2], bundle_shift(group, shift, 'fivebar', pair)))
                    outcome = coupling(bundles, slot_labels)
                    if outcome['status'] in ('UNKNOWN_HIGHER_KOSZUL_LEVEL',
                                             'UNKNOWN_NONZERO_KOSZUL_MAP'):
                        notes.add(outcome['status'])
                        continue
                    if outcome['status'] == 'REFUSED':
                        notes.add('REFUSED:' + outcome.get('detail', '')[:40])
                        continue
                    if outcome['status'] != 'COMPUTED':
                        continue
                    if outcome['dimensions'][2] != 1:
                        notes.add(f"HIGGS_MULTIPLICITY_{outcome['dimensions'][2]}")
                        continue
                    tensor = outcome['tensor']
                    if row_slot >= len(tensor) or column_slot >= len(tensor[row_slot]):
                        notes.add('FAMILY_INDEX_OUT_OF_RANGE')
                        continue
                    matrix[p_index, q_index] = tensor[row_slot][column_slot][0]
            record[kind] = summarise(matrix, model.get(kind), sorted(notes))
        results.append(record)
        print(format_row(record))

    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=1, default=str))


def summarise(matrix, published, notes):
    """Exact rank of our leading-order matrix against the published support."""
    if notes and any(n.startswith(('REFUSED', 'HIGGS_MULTIPLICITY', 'FAMILY_INDEX', 'UNKNOWN_')) for n in notes):
        return {'status': 'INCOMPLETE', 'notes': notes}
    support = [[int(bool(matrix[i, j])) for j in range(matrix.cols)]
               for i in range(matrix.rows)]
    result = {'status': 'COMPUTED', 'our_rank': matrix.rank(),
              'our_support': support, 'notes': notes,
              'entries': [[str(matrix[i, j]) for j in range(matrix.cols)]
                          for i in range(matrix.rows)]}
    table = published_matrix(published)
    if table == 'ALL_ZERO':
        result['published_leading_support'] = [[0] * matrix.cols for _ in range(matrix.rows)]
        result['published_structural_rank'] = 0
    elif isinstance(table, list) and table and isinstance(table[0], list):
        published_support = [[int(frozenset() in cell) for cell in row] for row in table]
        result['published_leading_support'] = published_support
        result['published_structural_rank'] = structural_rank(published_support)
        result['support_matches'] = published_support == support
    else:
        result['published_structural_rank'] = None
    return result


def format_row(record):
    out = [f"model {record['model']:3d} tens {record['tens']}"]
    for kind in ('YukawaUp', 'YukawaDown'):
        block = record[kind]
        if block.get('status') != 'COMPUTED':
            out.append(f"{kind[6:]:5s} {block.get('status')} {block.get('notes')}")
            continue
        out.append(f"{kind[6:]:5s} rank {block['our_rank']} vs published structural "
                   f"{block['published_structural_rank']}")
    return '  | '.join(out)


if __name__ == '__main__':
    main()
