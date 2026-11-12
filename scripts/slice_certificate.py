"""Charge-unbounded (K-free) search of one slope slice.

Mathematics: docs/exact_obstructions.md, Propositions S1 and S2.

S1 (slice decomposition). If V = (+)_a L_a admits a common zero of all five
slopes at some t in the positive ambient chamber, then the charge vectors all
lie in p-perp for some primitive p in Z^h with strictly positive entries. The
decomposition over such p is therefore exhaustive: every slope-feasible model
belongs to exactly one slice (rank h-1) or to a smaller one.

S2 (per-slice finiteness). With c1(V) = 0, the anomaly condition is
sum_a F(k_a) <= C_X where F(k) = |k|^2 - s(k)^2, s(k) = sum_i k^i, and
C_X = (sum_r c2_r)/(h-2). On p-perp, F(k) >= |k|^2 (1 - |w_p|^2) with
|w_p|^2 = h - (sum_i p_i)^2/|p|^2. So when (sum p)^2 > h|p|^2 - |p|^2 ... more
precisely when |w_p| < 1, i.e. (sum_i p_i)^2 > (h-1)|p|^2, F is positive definite
on p-perp, every individual F(k_a) is nonnegative, hence each is at most C_X, and

    |k_a|^2  <=  C_X |p|^2 / ( (sum_i p_i)^2 - (h-1)|p|^2 )  =:  R^2(p).

The admissible column pool of that slice is therefore the finite exact set
{ k in Z^h : <k,p> = 0, F(k) <= C_X }, with no K parameter anywhere. Searching
it is an exhaustive search of the whole slice over all integer charges.

The emitted outcome is UNSAT_SLICE_UNBOUNDED or SAT_SLICE_UNBOUNDED /
UNKNOWN_SLICE_UNBOUNDED: unlike UNSAT_BOUNDED it carries no K qualifier, only the
slice, the geometry, |Gamma|, the chamber and the declared target conditions.
"""
import argparse
import json
from fractions import Fraction
from itertools import product
from math import gcd, isqrt
from pathlib import Path

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import canonical_row_orbit
from string_sm_sat.search.checkpoints import atomic_json, code_hash
from string_sm_sat.search.domain import Domain
from string_sm_sat.search.split_search import split_search
from string_sm_sat.search.validation import classify

MAX_POOL_RADIUS = 160


def positive_definite(p, h):
    """(sum p)^2 > (h-1)|p|^2, i.e. |w_p| < 1 and F is positive definite."""
    return sum(p) ** 2 > (h - 1) * sum(x * x for x in p)


def slice_radius_squared(geometry, p):
    """R^2(p) from S2; the constant C_X = (sum_r c2_r)/(h-2)."""
    h = geometry.h11
    budget = Fraction(sum(geometry.c2), h - 2)
    return budget * sum(x * x for x in p) / (sum(p) ** 2 - (h - 1) * sum(x * x for x in p))


def slice_pool(geometry, p):
    """The complete admissible column pool of the slice: exact, no K cutoff.

    Enumerates the ball |k|^2 <= R^2(p) rather than a box: the first h-1
    coordinates run over the ball, the last is forced by <k,p> = 0 (and must be
    an integer), then F(k) <= C_X is applied. Every admissible column is found
    because F(k) <= C_X already implies |k|^2 <= R^2 on this slice.
    """
    h = geometry.h11
    budget = Fraction(sum(geometry.c2), h - 2)
    radius = slice_radius_squared(geometry, p)
    bound = isqrt(int(radius)) + 1
    if bound > MAX_POOL_RADIUS:
        raise ValueError(f'slice radius {bound} exceeds the enumeration guard '
                         f'{MAX_POOL_RADIUS}')
    last = p[-1]
    pool = []

    def walk(prefix, squares):
        depth = len(prefix)
        if depth == h - 1:
            residual = -sum(a * b for a, b in zip(prefix, p[:-1]))
            if residual % last:
                return
            k = (*prefix, residual // last)
            if sum(x * x for x in k) > radius:
                return
            if sum(x * x for x in k) - sum(k) ** 2 <= budget:
                pool.append(k)
            return
        span = isqrt(int(radius - squares)) if radius >= squares else -1
        for value in range(-span, span + 1):
            walk((*prefix, value), squares + value * value)

    walk((), 0)
    return tuple(pool), bound, radius, budget


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--geometry', default='7862')
    parser.add_argument('--p', required=True, help='comma separated positive primitive vector')
    parser.add_argument('--gamma', type=int, default=2)
    parser.add_argument('--target', default='GUT_FULL', choices=['GUT_FULL', 'GUT_CHIRAL'])
    parser.add_argument('--output')
    args = parser.parse_args(argv)

    g = benchmark(args.geometry)
    p = tuple(int(x) for x in args.p.split(','))
    if len(p) != g.h11 or any(x <= 0 for x in p):
        raise SystemExit('p must be a strictly positive vector of length h11')
    divisor = 0
    for x in p:
        divisor = gcd(divisor, x)
    if divisor != 1:
        raise SystemExit('p must be primitive')
    if not positive_definite(p, g.h11):
        raise SystemExit(f'F is not positive definite on p-perp for p={p}: '
                         f'(sum p)^2 = {sum(p)**2} <= (h-1)|p|^2 = '
                         f'{(g.h11-1)*sum(x*x for x in p)}. This slice is not covered '
                         f'by S2 and needs the index argument instead.')

    pool, bound, radius, budget = slice_pool(g, p)
    domain = Domain(g, bound, args.gamma, args.target, True, 1, 'span', pool)
    run = split_search(domain)
    survivors = [tuple(map(tuple, m)) for m in run['survivors']]
    orbits = sorted({canonical_row_orbit(g, s) for s in survivors})

    unknown = []
    for columns in survivors:
        status, checks = classify(domain, BundleSum.from_columns(columns))
        if status != 'REJECTED':
            unknown.append({'columns': [list(k) for k in columns], 'classification': status,
                            'checks': [c.as_dict() for c in checks]})

    outcome = ('UNSAT_SLICE_UNBOUNDED' if not unknown else 'UNKNOWN_SLICE_UNBOUNDED')
    result = {
        'schema': 1, 'kind': 'slope_slice', 'outcome': outcome,
        'geometry': g.identifier, 'gamma': args.gamma, 'target': args.target,
        'slope_direction': list(p),
        'positive_definite': True,
        'anomaly_budget_C_X': str(budget),
        'radius_squared_bound': str(radius),
        'enumeration_box_side': bound,
        'admissible_columns': len(pool),
        'claim': ('exhaustive over ALL integer charges in this slice; the pool is the '
                  'complete solution set of <k,p>=0 and F(k) <= C_X, so no K cutoff enters'),
        'counts': run['counts'],
        'elapsed_seconds': run['elapsed_seconds'],
        'peak_rss_bytes': run['peak_rss_bytes'],
        'survivors': survivors,
        'row_orbits': [list(map(list, o)) for o in orbits],
        'row_orbit_count': len(orbits),
        'unknown_candidates': unknown,
        'assumptions': [
            'positive ambient Kahler chamber; the registry declares it equal to the Kahler cone',
            'split S(U(1)^5) structure; poly-stability requires a common zero slope',
            'trivial hidden bundle; ambient hyperplanes nef (as for the anomaly rule)',
            'declared target conditions, including the nonpositive pair-index restriction',
        ],
        'software_source_sha256': code_hash(),
    }
    if args.output:
        atomic_json(args.output, result)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('survivors', 'unknown_candidates', 'counts', 'row_orbits')},
                     indent=2))
    print(f'row orbits: {len(orbits)}')
    if survivors:
        print('max |k| over survivors:',
              max(max(abs(x) for k in s for x in k) for s in survivors))
    return result


if __name__ == '__main__':
    main()
