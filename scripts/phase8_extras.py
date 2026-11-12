"""Classify every orbit our search keeps that the published GUT catalog does not.

Our survivor sets are necessary-condition survivors; the catalog is the
poly-stable stage. Where they differ (always by extra orbits of ours, never by
missing published ones), each extra is classified, strongest evidence first:

  UNSTABLE_CERTIFIED (sign/Polya)  some combination of slopes is certified
                                   positive on the open orthant (exact);
  STABLE_CERTIFIED                 exact rational or real-algebraic interior
                                   common slope zero (exact);
  UNSTABLE_CERTIFIED (solve)       all real common zeros of the zero-dimensional
                                   system lie outside the open orthant (exact);
  NUMERIC_UNSTABLE / NUMERIC_STABLE numerical evidence only, clearly labelled.

A STABLE_CERTIFIED extra satisfies every condition the catalog states
(anomaly, indices, poly-stability) and is absent from it.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from phase8_suite import configuration_automorphisms, geometry_for, run_key  # noqa: E402
from string_sm_sat.physics.stability import (decide_interior_slope_zero,  # noqa: E402
                                              polya_obstruction)

CATALOG = ROOT / 'data/processed/published_gut_models.json'
SOURCES = [ROOT / 'benchmarks/phase8-suite.json', ROOT / 'benchmarks/phase8-suite-h5-k2.json',
           ROOT / 'benchmarks/phase8-suite-k3.json']
OUT = ROOT / 'benchmarks/phase8-extras-classified.json'


def numeric_interior(geometry, columns, starts=300):
    """Best interior residual of q(t) in S^perp, and the smallest t ratio there."""
    h = geometry.h11
    d = np.array(geometry.d, float)
    K = np.array(columns, float)
    _, s, vh = np.linalg.svd(K)
    rank = int((s > 1e-9).sum())
    null = vh[rank:].T
    q = lambda t: np.einsum('ijl,j,l->i', d, t, t)
    rng = np.random.default_rng(7)
    best = None
    for _ in range(starts):
        x0 = rng.uniform(-3, 1, size=h)

        def residual(x):
            u = q(np.exp(x))
            u = u / np.linalg.norm(u)
            return u - null @ (null.T @ u)
        result = least_squares(residual, x0, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        t = np.exp(result.x)
        value = float(np.abs(residual(result.x)).max())
        if best is None or value < best[0]:
            best = (value, float(t.min() / t.max()))
    return best


def classify(geometry, columns):
    certificate = polya_obstruction(geometry, columns, max_degree=4)
    if certificate is not None:
        return {'status': 'UNSTABLE_CERTIFIED', 'method': f"Polya degree {certificate['N']}",
                'certificate': certificate}
    decision = decide_interior_slope_zero(geometry, columns)
    if decision['status'] != 'UNDECIDED':
        decision['method'] = 'exact solve'
        return decision
    residual, ratio = numeric_interior(geometry, columns)
    interior = residual < 1e-10 and ratio > 1e-6
    return {'status': 'NUMERIC_STABLE' if interior else 'NUMERIC_UNSTABLE',
            'method': 'numerical, not a proof', 'best_residual': residual,
            'ratio_at_best': ratio, 'exact_attempt': decision.get('reason')}


def main():
    catalog = json.loads(CATALOG.read_text())
    records = {r['number']: r for r in catalog['geometries']}
    differing = []
    for source in SOURCES:
        if source.exists():
            differing += [r for r in json.loads(source.read_text())['runs']
                          if not r['exact_set_equality']]
    results = []
    tally = Counter()
    for run in differing:
        record = records[run['geometry']]
        geometry = geometry_for(record)
        automorphisms = configuration_automorphisms(geometry)
        published = catalog['models'][f"{run['geometry']},{run['gamma']}"]
        full = run if 'ours_only_all' in run else run_key(record, run['gamma'], run['K'],
                                                           published, automorphisms)
        for columns in full['ours_only_all']:
            verdict = classify(geometry, [tuple(k) for k in columns])
            tally[verdict['status']] += 1
            results.append({'geometry': run['geometry'], 'gamma': run['gamma'], 'K': run['K'],
                            'columns': columns, **verdict})
            print(f"{run['geometry']} |G|={run['gamma']} K={run['K']}  {verdict['status']:20s} "
                  f"{verdict.get('method', '')}", flush=True)
    OUT.write_text(json.dumps({'tally': dict(tally), 'extras': results}, indent=1, default=str))
    print('\n', dict(tally))


if __name__ == '__main__':
    main()
