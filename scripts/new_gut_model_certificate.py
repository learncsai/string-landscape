"""Certificate for the GUT model on CICY 5256 absent from the published catalog.

Recomputes every condition the published GUT catalog states -- c1 = 0, the
structure-group criterion, the indices, the anomaly pairing, Bogomolov -- and
certifies poly-stability exactly (real-algebraic interior witness). Then shows it
is inequivalent to every published model on the same key by the full triple
intersection fingerprint, and records its descent status.
"""
import json
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from phase8_suite import geometry_for  # noqa: E402
from string_sm_sat.bundles.bundle_sum import BundleSum  # noqa: E402
from string_sm_sat.physics.anomaly import check_anomaly, check_bogomolov  # noqa: E402
from string_sm_sat.physics.spectrum import check_indices  # noqa: E402
from string_sm_sat.physics.structure_group import check_c1, check_structure_group  # noqa: E402
from string_sm_sat.physics.stability import decide_interior_slope_zero  # noqa: E402

CATALOG = ROOT / 'data/processed/published_gut_models.json'
COLUMNS = [(-2, 0, -1, 1, 0), (0, -1, 1, -2, 1), (0, 2, 1, 0, -1), (1, -2, 1, 0, 0),
           (1, 1, -2, 1, 0)]


def fingerprint(geometry, columns):
    h = geometry.h11
    d = geometry.d
    D = lambda a, b, c: sum(d[i][j][l] * a[i] * b[j] * c[l]
                            for i in range(h) for j in range(h) for l in range(h))
    table = {(a, b, c): D(columns[a], columns[b], columns[c])
             for a in range(5) for b in range(5) for c in range(5)}
    linear = [sum(geometry.c2[i] * k[i] for i in range(h)) for k in columns]
    return min(tuple(table[(p[a], p[b], p[c])] for a in range(5) for b in range(5)
                     for c in range(5)) + tuple(linear[p[a]] for a in range(5))
               for p in permutations(range(5)))


def main():
    catalog = json.loads(CATALOG.read_text())
    record = next(r for r in catalog['geometries'] if r['number'] == 5256)
    geometry = geometry_for(record)
    bundle = BundleSum.from_columns(COLUMNS)
    checks = {
        'c1_zero': check_c1(bundle).outcome,
        'structure_group': check_structure_group(bundle).outcome,
        'indices_minus_12': check_indices(bundle, geometry, 4).outcome,
        'anomaly_nef_pairings': check_anomaly(bundle, geometry).outcome,
        'bogomolov': check_bogomolov(bundle, geometry).outcome,
    }
    witness = decide_interior_slope_zero(geometry, COLUMNS)
    mine = fingerprint(geometry, [tuple(k) for k in COLUMNS])
    published = catalog['models']['5256,4']
    same = sum(1 for m in published if fingerprint(geometry, [tuple(k) for k in m]) == mine)
    in_box = [m for m in published if max(abs(x) for k in m for x in k) <= 2]
    descent = json.loads((ROOT / 'benchmarks/phase8-new-model-descent.json').read_text())
    result = {
        'geometry': 5256, 'redundant_descriptions': record.get('redundant_with'),
        'gamma_order': 4, 'columns': [list(k) for k in COLUMNS],
        'max_abs_charge': 2, 'conditions': checks,
        'poly_stability': witness,
        'published_models_on_key': len(published),
        'published_models_with_max_abs_charge_le_2': len(in_box),
        'published_max_abs_charge_reached': max(max(abs(x) for k in m for x in k) for m in published),
        'published_models_with_identical_intersection_fingerprint': same,
        'descent_by_individually_equivariant_line_bundles': {
            number: entry['status'] for number, entry in descent['symmetries'].items()},
    }
    out = ROOT / 'benchmarks/phase8-new-gut-model.json'
    out.write_text(json.dumps(result, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != 'poly_stability'}, indent=1))
    print('poly-stability:', witness['status'], witness.get('kind'), witness.get('root_interval'),
          witness.get('minimal_polynomial', '')[:90])


if __name__ == '__main__':
    main()
