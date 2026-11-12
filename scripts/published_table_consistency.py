"""Internal-consistency test of the published Yukawa tables.

The published Yukawa matrices are tables of gauge-invariant singlet monomials
(arXiv:1202.1757 Section 3.1.6), so they are determined by the U(1)^4 charges
alone.  Two families that come from the *same* line bundle carry the *same*
charge, so the corresponding rows -- or columns -- of a published table must be
identical.  This script checks that, using only the published data: the family
ordering is read off the model's own EDownSpec, and no quantity computed in this
repository enters.

A violation means the published table is not a function of the charges alone.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from yukawa_selection_benchmark import (DATABASE, parse_braces,  # noqa: E402
                                        term_monomial, tokenise)

PAIRS = [(a, b) for a in range(1, 6) for b in range(a + 1, 6)]


def decode_edownspec(model):
    """(ten-family bundles, 5bar-family pairs, Higgs pairs, singlets) from EDownSpec.

    Layout, established by comparison with DownSpec across the database:
        [H_u pair index, 3 ten bundle indices, H_d pair index,
         3 fivebar pair indices, one code per singlet type]
    where a pair index is the position in lexicographic order of the ten
    unordered pairs, and a singlet code is 2 * (pair index) + direction, the
    direction being 0 for S_{ab} with a < b and 1 for S_{ba}.
    """
    encoded = model.get('EDownSpec')
    if not encoded or not isinstance(encoded, list) or len(encoded[0]) < 8:
        return None
    head = encoded[0]
    tens = tuple(index + 1 for index in head[1:4])
    fivebars = tuple(PAIRS[index] for index in head[5:8])
    singlets = []
    for code in head[8:]:
        pair = PAIRS[code // 2]
        singlets.append(pair if code % 2 == 0 else (pair[1], pair[0]))
    return {'tens': tens, 'fivebars': fivebars,
            'higgs_up': PAIRS[head[0]], 'higgs_down': PAIRS[head[4]],
            'singlets': tuple(singlets)}


def published_matrix(value):
    if not isinstance(value, str):
        flat = json.dumps(value)
        if set(flat) <= set('[]0, \n'):
            return 'ALL_ZERO'
        return None
    text, atoms = tokenise(value)
    tree = parse_braces(text)
    while len(tree) == 1 and isinstance(tree[0], list):
        tree = tree[0]

    def convert(node):
        if node and all(isinstance(item, list) for item in node):
            return [convert(item) for item in node]
        return frozenset(frozenset(m.items()) for m in
                         (term_monomial(t, atoms) for t in node) if m is not None)

    return convert(tree)


def violations(matrix, row_labels, column_labels):
    """Pairs of equal-label rows (or columns) whose published entries differ."""
    if matrix in (None, 'ALL_ZERO') or not isinstance(matrix, list):
        return []
    if not matrix or not isinstance(matrix[0], list):
        return []
    out = []
    for i in range(len(row_labels)):
        for j in range(i + 1, len(row_labels)):
            if row_labels[i] == row_labels[j] and matrix[i] != matrix[j]:
                out.append(('row', i, j, row_labels[i]))
    for i in range(len(column_labels)):
        for j in range(i + 1, len(column_labels)):
            if column_labels[i] == column_labels[j] and \
                    [r[i] for r in matrix] != [r[j] for r in matrix]:
                out.append(('column', i, j, column_labels[i]))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=None)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    data = json.loads(DATABASE.read_text())
    models = data['models']
    if args.cicy:
        models = [m for m in models if m['cicy'] == args.cicy]

    tally = Counter()
    offenders = []
    for model in models:
        decoded = decode_edownspec(model)
        if decoded is None:
            tally['no_edownspec'] += 1
            continue
        for kind, rows, columns in (('YukawaUp', decoded['tens'], decoded['tens']),
                                    ('YukawaDown', decoded['tens'], decoded['fivebars'])):
            matrix = published_matrix(model.get(kind))
            if matrix is None:
                tally[kind + '/unparsed'] += 1
                continue
            tally[kind + '/checked'] += 1
            bad = violations(matrix, rows, columns)
            if bad:
                tally[kind + '/inconsistent'] += 1
                offenders.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                  'kind': kind, 'violations': [list(map(str, v)) for v in bad],
                                  'tens': list(decoded['tens']),
                                  'fivebars': [list(f) for f in decoded['fivebars']]})
            else:
                tally[kind + '/consistent'] += 1

    for kind in ('YukawaUp', 'YukawaDown'):
        print(f'{kind:12s} checked {tally[kind + "/checked"]:5d}  charge-consistent '
              f'{tally[kind + "/consistent"]:5d}  INCONSISTENT '
              f'{tally[kind + "/inconsistent"]:4d}  unparsed {tally[kind + "/unparsed"]:4d}')
    print('models without a usable EDownSpec:', tally['no_edownspec'])
    if offenders:
        print('\nby geometry:', dict(Counter(o['cicy'] for o in offenders)))
        print('first few:')
        for row in offenders[:8]:
            print('  ', row['cicy'], row['model'], row['kind'], 'tens', row['tens'],
                  'fivebars', row['fivebars'], row['violations'])
    if args.out:
        Path(args.out).write_text(json.dumps({'tally': dict(tally),
                                              'inconsistent': offenders}, indent=1))


if __name__ == '__main__':
    main()
