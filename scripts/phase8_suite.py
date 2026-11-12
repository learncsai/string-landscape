"""Phase 8: an automated low-K benchmark over the 68 favourable CICYs.

For every (geometry, |Gamma|) key of the published GUT catalog this runs the
exhaustive search at small charge bounds with the complete slope rule and
records, per the master plan (prompt Section 29): h11, Gamma, K, the nominal
search size, retained single columns, retained pair and triple prefixes,
complete bundles checked, survivors, runtime and peak memory. It then compares
the survivor set, as orbits under the symmetries of the configuration matrix,
with the published catalog restricted to the same box.

Orbits. Two charge matrices are identified when they differ by a permutation of
the five summands or by a permutation of the ambient factors that preserves the
configuration matrix up to a permutation of its columns (a relabelling of the
defining equations). For the two benchmarks this reduces to permuting identical
rows, the convention used elsewhere in the repository.

Usage:  python scripts/phase8_suite.py --K 1 [--max-h11 6] [--keys 7862,2 ...]
"""
import argparse
import json
import sys
import time
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from string_sm_sat.certificates.search_certificate import search_certificate  # noqa: E402
from string_sm_sat.geometry.cicy import CICY  # noqa: E402
from string_sm_sat.search.domain import Domain  # noqa: E402
from string_sm_sat.search.split_search import split_search  # noqa: E402

CATALOG = ROOT / 'data/processed/published_gut_models.json'
OUT = ROOT / 'benchmarks/phase8-suite.json'


def geometry_for(record):
    configuration = tuple(tuple(row) for row in record['configuration'])
    ambient = tuple(sum(row) - 1 for row in configuration)
    return CICY(str(record['number']), ambient, configuration, record['h11'],
                record['h21'], (), 'POSITIVE_ORTHANT')


def configuration_automorphisms(geometry):
    """Row permutations preserving the configuration up to a column permutation."""
    rows = geometry.configuration
    columns = sorted(zip(*rows))
    out = []
    for p in permutations(range(geometry.h11)):
        if any(geometry.ambient[p[i]] != geometry.ambient[i] for i in range(geometry.h11)):
            continue
        permuted = [rows[p[i]] for i in range(geometry.h11)]
        if sorted(zip(*permuted)) == columns:
            out.append(p)
    return out


def canonical(columns, automorphisms):
    return min(tuple(sorted(tuple(k[p[i]] for i in range(len(k))) for k in columns))
               for p in automorphisms)


def run_key(record, gamma, K, published, automorphisms):
    geometry = geometry_for(record)
    domain = Domain(geometry, K, gamma, 'GUT_FULL', True, 1, 'span')
    start = time.time()
    run = split_search(domain)
    certificate = search_certificate(domain, run)
    elapsed = time.time() - start
    counts = run['counts']
    survivors = [tuple(tuple(k) for k in s) for s in run['survivors']]
    ours = {canonical(s, automorphisms) for s in survivors}
    in_box = [m for m in published if max(abs(x) for k in m for x in k) <= K]
    theirs = {canonical(tuple(tuple(k) for k in m), automorphisms) for m in in_box}
    return {
        'geometry': record['number'], 'h11': record['h11'], 'gamma': gamma, 'K': K,
        'outcome': certificate['outcome'],
        'nominal_four_column_states': (2 * K + 1) ** (4 * record['h11']),
        'individual_considered': counts.get('individual_considered'),
        'individual_retained': counts.get('individual_retained'),
        'pairs_retained': counts.get('depth_2_retained'),
        'triples_retained': counts.get('depth_3_retained'),
        'complete_bundles_checked': counts.get('complete_bundles_checked'),
        'survivors': len(survivors),
        'orbits': len(ours),
        'published_in_box': len(theirs),
        'published_total': len(published),
        'published_only': len(theirs - ours),
        'ours_only': len(ours - theirs),
        'exact_set_equality': ours == theirs,
        'automorphisms': len(automorphisms),
        'runtime_seconds': round(elapsed, 2),
        'peak_rss_mib': round(run['peak_rss_bytes'] / 2 ** 20, 1),
        'unbounded_obstruction': certificate.get('unbounded_obstruction'),
        'ours_only_examples': [list(map(list, o)) for o in sorted(ours - theirs)[:3]],
        'ours_only_all': [list(map(list, o)) for o in sorted(ours - theirs)],
        'd_ijj_nonzero': any(geometry.d[i][j][j] for i in range(geometry.h11)
                             for j in range(geometry.h11)),
        'published_only_examples': [list(map(list, o)) for o in sorted(theirs - ours)[:3]],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--K', type=int, nargs='+', default=[1])
    parser.add_argument('--max-h11', type=int, default=6)
    parser.add_argument('--keys', nargs='*', default=None)
    parser.add_argument('--out', default=str(OUT))
    args = parser.parse_args()

    catalog = json.loads(CATALOG.read_text())
    records = {r['number']: r for r in catalog['geometries']}
    out_path = Path(args.out)
    results = json.loads(out_path.read_text()) if out_path.exists() else {'runs': []}
    done = {(r['geometry'], r['gamma'], r['K']) for r in results['runs']}
    keys = args.keys or list(catalog['models'])
    for key in keys:
        number, gamma = (int(x) for x in key.split(','))
        record = records[number]
        if record['h11'] > args.max_h11:
            continue
        automorphisms = configuration_automorphisms(geometry_for(record))
        published = catalog['models'][key]
        for K in args.K:
            if (number, gamma, K) in done:
                continue
            row = run_key(record, gamma, K, published, automorphisms)
            results['runs'].append(row)
            out_path.write_text(json.dumps(results, indent=1))
            n = lambda key: row[key] if row[key] is not None else 0
            print(f"{number:5d} h11={row['h11']} |G|={gamma:2d} K={K}  {row['outcome']:16s} "
                  f"singles {n('individual_retained'):5d}  bundles {n('complete_bundles_checked'):8d}  "
                  f"orbits {row['orbits']:4d}  published-in-box {row['published_in_box']:4d}  "
                  f"{'EXACT' if row['exact_set_equality'] else 'DIFFER'}  "
                  f"{row['runtime_seconds']:8.1f}s  {row['peak_rss_mib']:6.1f} MiB", flush=True)


if __name__ == '__main__':
    main()
