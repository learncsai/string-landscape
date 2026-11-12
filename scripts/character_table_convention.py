"""Are the published GCoh / GCoh2 character tables stored before the equivariant shift?

Our first-principles comparison (compute_equivariant_cohomology.py) shifted the
computed tables by the equivariant structure (chi_a for L_a, chi_a + chi_b for
L_a L_b) before comparing with the published GCoh/GCoh2. That left 694 tables
agreeing only up to a relabelling of characters. This script re-runs the
comparison both ways -- shifted and unshifted -- on every table, and records
which reading the published data follows. Only tables that are *not* invariant
under their shift can discriminate, so those are counted separately.
"""
import itertools
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / 'data/processed/published_standard_models.json'
GEOMETRIES = (5256, 5452, 6732, 6770, 6777, 6784, 6828, 6890, 6947, 7435, 7447, 7487, 7862)


def main():
    data = json.loads(DATABASE.read_text())
    tally = Counter()
    for geo in GEOMETRIES:
        art = json.loads((ROOT / f'benchmarks/equivariant-cohomology-{geo}.json').read_text())
        factors = art['cyclic_factors']
        labels = list(itertools.product(*(range(n) for n in factors)))
        index = {l: i for i, l in enumerate(labels)}
        models = [m for m in data['models'] if m['cicy'] == geo and m.get('GCoh')
                  and m.get('EquivStr') and m['gamma_order'] == art['gamma_order']]
        position = 0
        for result in art['results']:
            while position < len(models) and \
                    [list(c) for c in zip(*models[position]['LineSum'])] != result['columns']:
                position += 1
            if position >= len(models):
                tally['unmatched_result'] += 1
                break
            model = models[position]
            position += 1
            structure = [tuple(x) for x in model['EquivStr']]
            columns = result['columns']
            for kind, entries in (('single', result['singles']), ('pair', result['pairs'])):
                for entry in entries:
                    k = tuple(entry['k'])
                    if kind == 'single':
                        a = next(i for i, c in enumerate(columns) if tuple(c) == k)
                        shift = structure[a]
                    else:
                        a, b = next((a, b) for a, b in combinations(range(5), 2)
                                    if tuple(x + y for x, y in zip(columns[a], columns[b])) == k)
                        shift = tuple((structure[a][i] + structure[b][i]) % factors[i]
                                      for i in range(len(factors)))
                    shifted_ok = unshifted_ok = invariant = True
                    for row in entry['degrees']:
                        computed = row['computed']            # already shifted
                        raw = [computed[index[tuple((l[i] + shift[i]) % factors[i]
                                                    for i in range(len(factors)))]]
                               for l in labels]
                        shifted_ok &= computed == row['published']
                        unshifted_ok &= raw == row['published']
                        invariant &= raw == computed
                    if invariant:
                        tally[f'{kind}/not_discriminating'] += 1
                    else:
                        tally[f'{kind}/discriminating'] += 1
                        tally[f'{kind}/discriminating/shifted_matches'] += shifted_ok
                        tally[f'{kind}/discriminating/unshifted_matches'] += unshifted_ok
                    tally[f'{kind}/total'] += 1
                    tally[f'{kind}/unshifted_matches'] += unshifted_ok
                    tally[f'{kind}/shifted_matches'] += shifted_ok
    for key in sorted(tally):
        print(f'{key:45s} {tally[key]}')
    (ROOT / 'benchmarks/character-table-convention.json').write_text(
        json.dumps(dict(tally), indent=1))


if __name__ == '__main__':
    main()
