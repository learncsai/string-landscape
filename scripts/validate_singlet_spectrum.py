"""Validate the computed downstairs singlet spectrum against the published one.

The candidate Yukawa analysis (`candidate_yukawa.py`) derives which singlets
S_{ab} survive the quotient from first principles: the Gamma-invariants of
H^1(X, L_a (x) L_b^*) after the equivariant-structure shift. Every rank verdict
that depends on the selection rule depends on that spectrum, so it is checked
here against the singlets listed in the published DownSpec of every X7862 model.
"""
import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from candidate_yukawa import setup, singlet_spectrum  # noqa: E402
from string_sm_sat.physics.equivariance import CharacterGroup  # noqa: E402
from string_sm_sat.physics.equivariant_cohomology import (equivariant_cohomology,  # noqa: E402
                                                          is_equivariant)
from yukawa_selection_benchmark import parse_spectrum  # noqa: E402

DATABASE = ROOT / 'data/processed/published_standard_models.json'
UNEVALUATED = re.compile(r'Subscript\[\s*"S"\s*,\s*(\d+)\s*,\s*(\d+)\s*\]\s*\*\s*\(')


def unevaluated_singlets(text):
    """Singlets whose published multiplicity is an unevaluated rank expression."""
    return sorted({(int(a), int(b)) for a, b in UNEVALUATED.findall(text)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=7862)
    parser.add_argument('--symmetry', type=int, default=5)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    data = json.loads(DATABASE.read_text())
    geometry, lift, factors, poly, generators, coefficients = setup(args.cicy, args.symmetry)
    group = CharacterGroup(tuple(factors))
    trivial = tuple(0 for _ in factors)

    @lru_cache(maxsize=None)
    def table(k):
        if not is_equivariant(generators, geometry.ambient, k):
            return None
        return equivariant_cohomology(geometry, k, lift, factors, poly, generators,
                                      coefficients)

    rows = []
    for model in data['models']:
        if model['cicy'] != args.cicy or model.get('symmetry_number') != args.symmetry:
            continue
        if not model.get('LineSum') or not model.get('EquivStr'):
            continue
        columns = [tuple(c) for c in zip(*model['LineSum'])]
        shift = [tuple(x) for x in model['EquivStr']]
        ours, undetermined = singlet_spectrum(columns, shift, group, trivial, table,
                                              geometry.h11)
        published = sorted({indices for (head, indices), _ in
                            parse_spectrum(model['DownSpec']).items() if head == '"S"'})
        same = sorted(ours) == published
        symbolic = unevaluated_singlets(model['DownSpec'])
        differing = sorted(set(ours) ^ set(published))
        verdict = ('match' if same else
                   'differs_only_where_published_is_unevaluated'
                   if differing and set(differing) <= set(symbolic) else 'genuine_difference')
        rows.append({'model': model['ModelNumber'], 'match': same, 'verdict': verdict,
                     'published_unevaluated': [list(s) for s in symbolic],
                     'ours': [list(s) for s in sorted(ours)],
                     'published': [list(s) for s in published],
                     'undetermined': [list(s) for s in undetermined]})
        print(f"model {model['ModelNumber']:3d}  {verdict}"
              + ('' if same else f"  ours {sorted(ours)}  published {published}"
                 f"  published-unevaluated {symbolic}"), flush=True)
    agree = sum(r['match'] for r in rows)
    unevaluated = sum(r['verdict'] == 'differs_only_where_published_is_unevaluated'
                      for r in rows)
    genuine = sum(r['verdict'] == 'genuine_difference' for r in rows)
    print(f'singlet spectra: {agree}/{len(rows)} match exactly; {unevaluated} differ only on '
          f'singlets the published data leaves unevaluated; {genuine} genuine differences')
    if args.out:
        Path(args.out).write_text(json.dumps({'cicy': args.cicy, 'symmetry': args.symmetry,
                                              'matches': agree, 'models': len(rows),
                                              'differ_only_on_unevaluated': unevaluated,
                                              'genuine_differences': genuine,
                                              'rows': rows}, indent=1))


if __name__ == '__main__':
    main()
