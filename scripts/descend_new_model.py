"""Descend a GUT model found by the Phase 8 suite to the quotient, from first principles.

For each freely acting symmetry of the right order on the geometry: check that
every line bundle is equivariant, compute the Gamma-representation on the
cohomology of every L_a and L_a (x) L_b (collapse, or equivariant map ranks for
a single defining polynomial), enumerate every Wilson line and every
equivariant structure with sum e_a = 0, and keep the downstairs spectra with
three chiral families, no charged chiral exotics, a Higgs doublet pair and no
colour-triplet Higgs -- the same acceptance used for the tetraquadric.
"""
import argparse
import json
import sys
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from phase8_suite import geometry_for  # noqa: E402
from string_sm_sat.physics.equivariance import CharacterGroup  # noqa: E402
from string_sm_sat.physics.equivariant_cohomology import (cyclic_lift,  # noqa: E402
                                                          equivariant_cohomology,
                                                          factor_blocks,
                                                          invariant_family_coefficients,
                                                          is_equivariant, to_matrix)
from string_sm_sat.physics.wilson_line import (WilsonLine, acceptance_report,  # noqa: E402
                                               downstairs_spectrum)

CATALOG = ROOT / 'data/processed/published_gut_models.json'
SYMMETRIES = ROOT / 'data/processed/published_symmetries.json'


def descend(geometry, columns, entry):
    factors = entry['cyclic_factors']
    generators = [to_matrix(m) for m in entry['generators']]
    lift = cyclic_lift(generators, factors)
    if any(factor_blocks(m, geometry.ambient) is None for m in lift.values()):
        return {'status': 'PERMUTES_FACTORS'}
    poly = (cyclic_lift([to_matrix(m) for m in entry['polynomial_action']], factors)
            if entry['polynomial_action'] else None)
    coefficients = None
    if entry.get('invariants') and len(tuple(zip(*geometry.configuration))) == 1:
        coefficients = invariant_family_coefficients(entry['invariants'],
                                                     sum(n + 1 for n in geometry.ambient))
    group = CharacterGroup(tuple(factors))
    labels = group.labels
    pairs_k = [tuple(x + y for x, y in zip(columns[a], columns[b]))
               for a, b in combinations(range(5), 2)]
    needed = list(columns) + pairs_k
    if not all(is_equivariant(generators, geometry.ambient, k) for k in needed):
        return {'status': 'NOT_EQUIVARIANT'}
    tables = {}
    for k in needed:
        table = equivariant_cohomology(geometry, k, lift, factors, poly, generators, coefficients)
        if table is None:
            return {'status': 'COHOMOLOGY_UNDETERMINED', 'bundle': list(k)}
        tables[k] = table
    trivial = tuple(0 for _ in factors)
    wilson_choices = [(tr, do) for tr in labels for do in labels
                      if group.add(group.multiply(tr, 3), group.multiply(do, 2)) == trivial
                      and do != tr]
    accepted, rejected = [], {}
    for wilson_characters in wilson_choices:
        wilson = WilsonLine(group, *wilson_characters)
        for head in product(labels, repeat=4):
            equivariant = (*head, group.negate(group.add(*head)))
            tens = [group.shift(tuple(tables[k].get(1, {}).get(l, 0) for l in labels),
                                equivariant[a]) for a, k in enumerate(columns)]
            h1, h2 = [], []
            for position, (a, b) in enumerate(combinations(range(5), 2)):
                k = pairs_k[position]
                shift = group.add(equivariant[a], equivariant[b])
                h1.append(group.shift(tuple(tables[k].get(1, {}).get(l, 0) for l in labels), shift))
                h2.append(group.shift(tuple(tables[k].get(2, {}).get(l, 0) for l in labels), shift))
            spectrum = downstairs_spectrum(group, wilson, tens, h1, h2)
            report = acceptance_report(spectrum, group.order)
            failures = []
            if not report['three_chiral_families']:
                failures.append('families')
            if report['charged_chiral_exotics']:
                failures.append('chiral_exotics')
            if not report['higgs_doublet_pair']:
                failures.append('no_higgs_pair')
            if spectrum.get('colour_triplet_pairs'):
                failures.append('colour_triplet_higgs')
            if failures:
                key = ','.join(failures)
                rejected[key] = rejected.get(key, 0) + 1
                continue
            accepted.append({'wilson_line': [list(c) for c in wilson_characters],
                             'equivariant_structure': [list(e) for e in equivariant],
                             'higgs_pairs': spectrum['higgs_pairs'],
                             'tens': spectrum['tens'], 'fivebars': spectrum['fivebars'],
                             'higgs': spectrum['higgs']})
    return {'status': 'ACCEPTED' if accepted else 'NO_ACCEPTABLE_DESCENT',
            'accepted_count': len(accepted), 'rejected': rejected,
            'examples': accepted[:4]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--geometry', type=int, required=True)
    parser.add_argument('--gamma', type=int, required=True)
    parser.add_argument('--columns', required=True, help='JSON list of five charge vectors')
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text())
    record = next(r for r in catalog['geometries'] if r['number'] == args.geometry)
    geometry = geometry_for(record)
    columns = [tuple(k) for k in json.loads(args.columns)]
    entries = json.loads(SYMMETRIES.read_text())['symmetries'][str(args.geometry)]
    report = {}
    for number, entry in enumerate(entries, start=1):
        if entry['group_order'] != args.gamma or entry['acts_freely'] != 'True' or \
                not entry['generators'] or not entry['cyclic_factors']:
            continue
        result = descend(geometry, columns, entry)
        report[number] = result
        print(f"symmetry {number}: {result['status']}  accepted {result.get('accepted_count', 0)}  "
              f"rejected {result.get('rejected', {})}", flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps({'geometry': args.geometry, 'gamma': args.gamma,
                                              'columns': [list(k) for k in columns],
                                              'symmetries': report}, indent=1))


if __name__ == '__main__':
    main()
