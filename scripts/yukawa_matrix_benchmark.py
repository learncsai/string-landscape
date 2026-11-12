"""Entry-by-entry reproduction of the published Yukawa matrices.

`yukawa_selection_benchmark.py` checks the operator tables as sets.  This goes
further: it rebuilds each published 3x3 Yukawa matrix entry by entry from our
own spectrum bookkeeping and compares every cell's full singlet-monomial list.

That tests three things at once -- the U(1)^4 selection rule, the assignment of
each family to its line bundle, and the family ordering convention.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from yukawa_selection_benchmark import (DATABASE, parse_braces, parse_spectrum,  # noqa: E402
                                        physical_higgs, term_monomial, tokenise)
from string_sm_sat.physics.superpotential import (DownstairsSpectrum,  # noqa: E402
                                                  PUBLISHED_TRUNCATION, mu_term,
                                                  yukawa_down, yukawa_up)


def spectrum_from_model(model):
    """Our DownstairsSpectrum, built only from the published spectrum listing."""
    counts = parse_spectrum(model['DownSpec'])
    tens, fivebars, singlets = [], [], []
    for (head, indices), multiplicity in sorted(counts.items()):
        if head == '"10"':
            tens.extend([indices[0]] * multiplicity)
        elif head == 'OverBar["5"]':
            fivebars.extend([indices] * multiplicity)
        elif head == '"S"':
            singlets.append(indices)
    up, down = physical_higgs(model.get('PhysHiggs'))
    return DownstairsSpectrum(tuple(sorted(tens)), tuple(sorted(fivebars)),
                              up, down, tuple(sorted(set(singlets))),
                              f"{model['cicy']}-{model['ModelNumber']}")


def published_matrix(value):
    """A published table as nested lists of monomial sets, or None."""
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
        out = set()
        for term in node:
            monomial = term_monomial(term, atoms)
            if monomial is not None:
                out.add(frozenset(monomial.items()))
        return out

    return convert(tree)


def ours_matrix(table):
    if table is None:
        return None
    return [[{frozenset(tuple(pair) for pair in
                        [(tuple(f), int(p)) for f, p in cell_term])
              for cell_term in cell['monomials']}
             for cell in row] for row in table]


def cell_sets(table):
    """Our table as nested sets of frozensets, matching published_matrix."""
    if table is None:
        return None
    def convert(cell):
        return {frozenset((tuple(pair), power) for pair, power in term)
                for term in [[(tuple(p), int(c)) for p, c in monomial]
                             for monomial in cell['monomials']]}
    if isinstance(table, dict):
        return convert(table)
    return [[convert(cell) for cell in row] for row in table]


def compare_matrix(ours, published):
    """(cells, agreeing cells) or None when the shapes do not line up."""
    if published == 'ALL_ZERO':
        flat = ours if isinstance(ours, list) else [[ours]]
        cells = sum(len(row) for row in flat)
        agree = sum(1 for row in flat for cell in row if not cell)
        return cells, agree
    if isinstance(published, set):
        return 1, int(published == ours)
    if not isinstance(ours, list) or len(ours) != len(published):
        return None
    cells = agree = 0
    for our_row, published_row in zip(ours, published):
        if isinstance(published_row, set):
            cells += 1
            agree += int(published_row == our_row)
            continue
        if len(our_row) != len(published_row):
            return None
        for our_cell, published_cell in zip(our_row, published_row):
            cells += 1
            agree += int(our_cell == published_cell)
    return cells, agree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=None)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    data = json.loads(DATABASE.read_text())
    models = data['models']
    if args.cicy:
        models = [m for m in models if m['cicy'] == args.cicy]
    if args.limit:
        models = models[:args.limit]

    tally = Counter()
    failures = []
    for model in models:
        spectrum = spectrum_from_model(model)
        builders = {'YukawaUp': yukawa_up, 'YukawaDown': yukawa_down, 'MuTerm': mu_term}
        for kind, builder in builders.items():
            published = published_matrix(model.get(kind))
            if published is None:
                tally[kind + '/skipped'] += 1
                continue
            ours = cell_sets(builder(spectrum))
            if ours is None:
                tally[kind + '/skipped'] += 1
                continue
            outcome = compare_matrix(ours, published)
            if outcome is None:
                tally[kind + '/shape_mismatch'] += 1
                failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                 'kind': kind, 'reason': 'shape'})
                continue
            cells, agree = outcome
            tally[kind + '/cells'] += cells
            tally[kind + '/cells_agree'] += agree
            tally[kind + '/tables'] += 1
            if cells == agree:
                tally[kind + '/tables_exact'] += 1
            else:
                failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                 'kind': kind, 'cells': cells, 'agree': agree})

    for kind in ('YukawaUp', 'YukawaDown', 'MuTerm'):
        print(f'{kind:12s} tables {tally[kind + "/tables"]:5d}  exact '
              f'{tally[kind + "/tables_exact"]:5d} | cells {tally[kind + "/cells"]:6d}  '
              f'agree {tally[kind + "/cells_agree"]:6d} | shape mismatch '
              f'{tally[kind + "/shape_mismatch"]:4d}  skipped {tally[kind + "/skipped"]:4d}')
    if failures:
        print(f'\n{len(failures)} tables not exact; first few:')
        for row in failures[:12]:
            print('  ', row)
        print('\nby geometry:', dict(Counter(f['cicy'] for f in failures)))
    if args.out:
        Path(args.out).write_text(json.dumps(
            {'tally': dict(tally), 'failures': failures,
             'truncation': PUBLISHED_TRUNCATION}, indent=1))


if __name__ == '__main__':
    main()
