"""Fully independent exhaustive replay of a finite five-line-bundle domain.

This file deliberately shares NO search logic with the package. It imports
nothing from ``string_sm_sat`` except an optional topology cross-check at
start-up. Topology (d_ijk, c2_i), the Hirzebruch-Riemann-Roch index, the
structure-group subset test, the anomaly pairing, and the signed slope-matrix
obstruction are re-implemented here from their published definitions.

Algorithm: enumerate every ordered four-column assignment of the finite box,
derive the fifth column from c1(V)=0, canonicalize the resulting five-column
multiset, and apply the declared target conditions to every distinct multiset
exactly once. No hierarchical prefix pruning, no partial-sum budgets, no
completion bounds, no caching of partial states.

References for the reimplemented quantities:
  tetraquadric d_ijk and c2_i : arXiv:1311.1941 Section 2 / Appendix A
  HRR index                   : arXiv:1307.4787 Section 5
  no-proper-zero-subset       : arXiv:1307.4787 (2.2), Appendix A
  anomaly nef pairing         : arXiv:1311.1941 (2.3),(2.6); 1307.4787 (4.4)
  signed slope matrices       : arXiv:1307.4787 Section 5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import sys
import time
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

# ---------------------------------------------------------------- topology ---

# Published topological data, written here by hand rather than recomputed by
# the package's ambient Chow-ring code, so that agreement is a genuine
# independent cross-check.
GEOMETRIES = {
    # tetraquadric hypersurface in (P1)^4
    "7862": {
        "h11": 4,
        "d": {(i, j, k): 2 for i in range(4) for j in range(4) for k in range(4)
              if i != j and j != k and i != k},
        "c2": (24, 24, 24, 24),
        "cone": "POSITIVE_ORTHANT",
        "source": "arXiv:1311.1941 tetraquadric data; d_ijk=2 for distinct i,j,k",
    },
    # X7447 = two equations of multidegree (1,1,1,1,1) in (P1)^5
    "7447": {
        "h11": 5,
        "d": {(i, j, k): 2 for i in range(5) for j in range(5) for k in range(5)
              if i != j and j != k and i != k},
        "c2": (24, 24, 24, 24, 24),
        "cone": "POSITIVE_ORTHANT",
        "source": "arXiv:1307.4787 Section 7 / Oxford CICY record 7447",
    },
    "bicubic": {
        "h11": 2,
        "d": {(0, 0, 1): 3, (0, 1, 0): 3, (1, 0, 0): 3,
              (0, 1, 1): 3, (1, 0, 1): 3, (1, 1, 0): 3},
        "c2": (36, 36),
        "cone": "POSITIVE_ORTHANT",
        "source": "Oxford CICY record; bicubic in P2xP2",
    },
    "quintic": {
        "h11": 1,
        "d": {(0, 0, 0): 5},
        "c2": (50,),
        "cone": "POSITIVE_ORTHANT",
        "source": "quintic in P4: d=5, c2.J=50",
    },
}


def crosscheck_topology(name):
    """Compare the hand-entered data with the package's computed topology."""
    try:
        from string_sm_sat.geometry.cicy import benchmark
    except ImportError:  # pragma: no cover - replay must run standalone
        return {"available": False}
    g = benchmark(name)
    spec = GEOMETRIES[name]
    d_pkg = {(i, j, k): g.d[i][j][k] for i in range(g.h11) for j in range(g.h11)
             for k in range(g.h11) if g.d[i][j][k]}
    return {
        "available": True,
        "h11_agrees": g.h11 == spec["h11"],
        "d_agrees": d_pkg == spec["d"],
        "c2_agrees": tuple(g.c2) == spec["c2"],
    }


# ------------------------------------------------------------------ physics ---

class Reference:
    """Self-contained exact evaluator for one geometry."""

    def __init__(self, name):
        spec = GEOMETRIES[name]
        self.name = name
        self.h = spec["h11"]
        self.d = spec["d"]
        self.c2 = spec["c2"]
        self.triples = tuple((i, j, k, v) for (i, j, k), v in sorted(spec["d"].items()))

    # ind(L) = d_ijk k^i k^j k^k / 6 + c2_i k^i / 12   (exact rational, must be integral)
    def index(self, k):
        cubic = sum(v * k[i] * k[j] * k[r] for i, j, r, v in self.triples)
        linear = sum(a * b for a, b in zip(self.c2, k))
        value = Fraction(cubic, 6) + Fraction(linear, 12)
        if value.denominator != 1:
            raise ArithmeticError("nonintegral HRR index")
        return value.numerator

    # (M_k)_{jr} = d_{ijr} k^i ; mu(L)(t) = t^j (M_k)_{jr} t^r
    def forms(self):
        """Distinct nonzero linear forms k -> M(k)_{jl}."""
        h = self.h; rows = {}
        for j in range(h):
            for l in range(j, h):
                row = tuple(self.d.get((i, j, l), 0) for i in range(h))
                if any(row):
                    rows[row] = None
        return tuple(rows)

    def slope_matrix(self, k):
        h = self.h
        m = [0] * (h * h)
        for i, j, r, v in self.triples:
            if k[i]:
                m[j * h + r] += v * k[i]
        return tuple(m)

    @staticmethod
    def signed(matrix):
        """True when the quadratic form is provably nonzero for all t>0."""
        lo = min(matrix)
        hi = max(matrix)
        if lo == 0 and hi == 0:
            return False          # zero matrix: no obstruction
        return lo >= 0 or hi <= 0  # entrywise one-signed and nonzero

    def bundle_c2(self, columns):
        h = self.h
        out = [0] * h
        for a, b in combinations(columns, 2):
            for i, j, r, v in self.triples:
                out[i] += v * a[j] * b[r]
        return tuple(out)


def canonical_key(columns):
    return tuple(sorted(columns))


# --------------------------------------------- independent span obstruction ---
# Same mathematical decision as physics/stability.span_slope_obstruction
# (docs/slope_obstruction_note.md Prop. 3) but by a different algorithm:
# Fourier-Motzkin elimination on the inequality system, instead of extreme-ray
# enumeration. Rational arithmetic throughout.

def _rref(rows, h):
    m = [[Fraction(x) for x in row] for row in rows]
    pivots = []; r = 0
    for c in range(h):
        p = next((i for i in range(r, len(m)) if m[i][c]), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inverse = m[r][c]; m[r] = [x / inverse for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                f = m[i][c]; m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        pivots.append(c); r += 1
        if r == len(m):
            break
    return m[:r]


def _fm_feasible(constraints, nvars):
    """constraints: list of (coefficients, constant) meaning coeff.x + const >= 0."""
    rows = [(tuple(c), k) for c, k in constraints]
    for v in range(nvars - 1, -1, -1):
        positive = [(c, k) for c, k in rows if c[v] > 0]
        negative = [(c, k) for c, k in rows if c[v] < 0]
        neutral = [(c[:v] + c[v + 1:], k) for c, k in rows if c[v] == 0]
        combined = set(neutral)
        for cp, kp in positive:
            for cn, kn in negative:
                a, b = cp[v], -cn[v]
                coeffs = tuple(b * x + a * y for x, y in
                               zip(cp[:v] + cp[v + 1:], cn[:v] + cn[v + 1:]))
                combined.add((coeffs, b * kp + a * kn))
        rows = list(combined)
    return all(k >= 0 for _, k in rows)


def span_obstruction_fm(forms, columns, h):
    """True when span(columns) contains k with M(k) entrywise one-signed, nonzero."""
    basis = _rref([tuple(k) for k in columns], h)
    r = len(basis)
    if r == 0:
        return False
    matrix = [[sum(Fraction(f[i]) * basis[a][i] for i in range(h)) for a in range(r)]
              for f in forms]
    for j in range(r):
        for sign in (Fraction(1), Fraction(-1)):
            constraints = [(tuple(row[:j] + row[j + 1:]), row[j] * sign) for row in matrix]
            if _fm_feasible(constraints, r - 1):
                return True
    return False


# ---------------------------------------------------------------- the replay ---

def replay(name, K, gamma, target="GUT_FULL", pair_nonpositive=True,
           coefficient_bound=1, allowed_columns=None, progress=None,
           require_index_target=True, census=False, slope_rule="box"):
    ref = Reference(name)
    h = ref.h
    target_index = -3 * gamma
    vectors = (sorted(tuple(v) for v in allowed_columns) if allowed_columns is not None
               else [tuple(v) for v in product(range(-K, K + 1), repeat=h)])
    allowed = set(vectors) if allowed_columns is not None else None
    slope_cache = {v: ref.slope_matrix(v) for v in vectors}
    index_cache = {v: ref.index(v) for v in vectors}

    forms = ref.forms()
    coefficient_vectors = []
    if coefficient_bound and slope_rule in ("box", "both"):
        for c in product(range(-coefficient_bound, coefficient_bound + 1), repeat=5):
            first = next((x for x in c if x), 0)
            if first > 0:                      # c and -c give the same obstruction
                coefficient_vectors.append(c)

    counts = Counter()
    index_census = Counter()
    seen = set()
    survivors = set()
    start = time.perf_counter()

    # Explicit ordered four-column product; every assignment is visited and counted.
    for a in vectors:
        for b in vectors:
            for c in vectors:
                for e in vectors:
                    counts["raw_ordered_states"] += 1
                    last = tuple(-(a[i] + b[i] + c[i] + e[i]) for i in range(h))
                    if allowed is None:
                        if any(x > K or x < -K for x in last):
                            continue
                    elif last not in allowed:
                        continue
                    counts["valid_fifth_column"] += 1
                    key = canonical_key((a, b, c, e, last))
                    if key in seen:
                        continue
                    seen.add(key)
                    counts["distinct_canonical_states"] += 1

                    # ---- declared target conditions, in the package's order ----
                    if any(sum(col[i] for col in key) for i in range(h)):
                        counts["reject_c1_zero"] += 1
                        continue
                    counts["pass_c1_zero"] += 1

                    bad = False
                    for n in range(1, 5):
                        for subset in combinations(range(5), n):
                            if not any(sum(key[x][i] for x in subset) for i in range(h)):
                                bad = True
                                break
                        if bad:
                            break
                    if bad:
                        counts["reject_no_proper_zero_subset"] += 1
                        continue
                    counts["pass_no_proper_zero_subset"] += 1

                    singles = [index_cache[v] if v in index_cache else ref.index(v) for v in key]
                    pairs = [ref.index(tuple(x + y for x, y in zip(u, v)))
                             for u, v in combinations(key, 2)]
                    if census:
                        index_census[(sum(singles), sum(pairs))] += 1
                    if require_index_target and (sum(singles) != target_index
                                                 or sum(pairs) != target_index):
                        counts["reject_chiral_indices"] += 1
                        continue
                    counts["pass_chiral_indices"] += 1

                    if target == "GUT_FULL":
                        if any(not (target_index <= v <= 0) for v in singles):
                            counts["reject_single_index_range"] += 1
                            continue
                        counts["pass_single_index_range"] += 1

                    if pair_nonpositive:
                        if any(not (target_index <= v <= 0) for v in pairs):
                            counts["reject_pair_index_range"] += 1
                            continue
                        counts["pass_pair_index_range"] += 1

                    residual = tuple(x - y for x, y in zip(ref.c2, ref.bundle_c2(key)))
                    if any(x < 0 for x in residual):
                        counts["reject_anomaly_nef_pairings"] += 1
                        continue
                    counts["pass_anomaly_nef_pairings"] += 1

                    matrices = [slope_cache[v] if v in slope_cache else ref.slope_matrix(v)
                                for v in key]
                    obstructed = any(ref.signed(m) for m in matrices)
                    if not obstructed and slope_rule in ("span", "both"):
                        obstructed = span_obstruction_fm(forms, key, h)
                    if not obstructed:
                        for coeffs in coefficient_vectors:
                            combo = tuple(sum(x * m[t] for x, m in zip(coeffs, matrices))
                                          for t in range(h * h))
                            if ref.signed(combo):
                                obstructed = True
                                break
                    if obstructed:
                        counts["reject_signed_slope_matrices"] += 1
                        continue
                    counts["pass_signed_slope_matrices"] += 1

                    survivors.add(key)
                if progress and counts["raw_ordered_states"] % progress < len(vectors):
                    print(f"  ... {counts['raw_ordered_states']:,} ordered states, "
                          f"{len(survivors)} survivors, "
                          f"{time.perf_counter() - start:.1f}s", flush=True)

    counts["final_survivors"] = len(survivors)
    elapsed = time.perf_counter() - start
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "kind": "independent_replay",
        "schema": 1,
        "implementation": "scripts/independent_replay.py (no shared search logic)",
        "geometry": name,
        "topology_source": GEOMETRIES[name]["source"],
        "topology_crosscheck": crosscheck_topology(name),
        "K": K,
        "gamma": gamma,
        "target": target,
        "pair_nonpositive": pair_nonpositive,
        "coefficient_bound": coefficient_bound,
        "slope_rule": slope_rule,
        "slope_algorithm": ("finite coefficient box" if slope_rule == "box" else
                            "Fourier-Motzkin decision of the span cone (independent algorithm)"),
        "allowed_columns": None if allowed_columns is None else sorted(map(tuple, allowed_columns)),
        "nominal_ordered_four_column_states": len(vectors) ** 4,
        "require_index_target": require_index_target,
        "counts": dict(sorted(counts.items())),
        "index_census": (None if not census else
                         {f"{a},{b}": n for (a, b), n in sorted(index_census.items())}),
        "survivors": sorted(survivors),
        "survivor_sha256": hashlib.sha256(
            json.dumps(sorted(survivors), separators=(",", ":")).encode()).hexdigest(),
        "elapsed_seconds": elapsed,
        "peak_rss_bytes": int(rss if platform.system() == "Darwin" else rss * 1024),
        "python": sys.version,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--geometry", default="7862", choices=sorted(GEOMETRIES))
    p.add_argument("--K", type=int, required=True)
    p.add_argument("--gamma", type=int, default=2)
    p.add_argument("--target", default="GUT_FULL", choices=["GUT_FULL", "GUT_CHIRAL"])
    p.add_argument("--unrestricted-pair-indices", action="store_true")
    p.add_argument("--coefficient-bound", type=int, default=1)
    p.add_argument("--slope-rule", default="box", choices=["box", "span", "both"])
    p.add_argument("--drop-index-equality", action="store_true",
                   help="control run: keep every other declared condition but do not "
                        "require ind(V)=ind(wedge2 V)=-3|Gamma|")
    p.add_argument("--census", action="store_true",
                   help="record the joint (ind V, ind wedge2 V) distribution over all "
                        "canonical states passing c1=0 and the subset criterion")
    p.add_argument("--progress", type=int, default=0,
                   help="print progress every N ordered states (0 = silent)")
    p.add_argument("--compare", help="optimized search certificate JSON to compare against")
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)

    result = replay(args.geometry, args.K, args.gamma, args.target,
                    not args.unrestricted_pair_indices, args.coefficient_bound,
                    progress=args.progress or None,
                    require_index_target=not args.drop_index_equality,
                    census=args.census, slope_rule=args.slope_rule)

    if args.compare and args.drop_index_equality:
        raise SystemExit("ERROR: a control run must not be compared to a declared-domain certificate")
    if args.compare:
        data = json.loads(Path(args.compare).read_text())
        domain = data["domain"]
        mismatch = [k for k, v in (("K", args.K), ("gamma", args.gamma),
                                   ("target", args.target),
                                   ("pair_nonpositive", not args.unrestricted_pair_indices),
                                   ("slope_coefficients", args.coefficient_bound),
                                   ("slope_rule", args.slope_rule))
                    if domain[k] != v]
        if mismatch or domain["geometry"]["identifier"] != args.geometry:
            raise SystemExit(f"ERROR: compared certificate has a different domain: {mismatch}")
        if not data["enumeration"]["complete"]:
            raise SystemExit("ERROR: compared search is incomplete")
        optimized = {tuple(map(tuple, row)) for row in data["enumeration"]["survivors"]}
        equal = optimized == set(map(tuple, result["survivors"]))
        result["comparison"] = {
            "certificate": args.compare,
            "optimized_survivor_count": len(optimized),
            "reference_survivor_count": len(result["survivors"]),
            "exact_set_equality": equal,
            "optimized_only": sorted(optimized - set(map(tuple, result["survivors"]))),
            "reference_only": sorted(set(map(tuple, result["survivors"])) - optimized),
            "outcome_recorded": data["outcome"],
        }
        if not equal:
            Path(args.output).write_text(json.dumps(result, indent=2, default=str) + "\n")
            raise SystemExit("ERROR: survivor sets differ; artifact written for inspection")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, default=str) + "\n")
    summary = {k: v for k, v in result.items()
               if k not in ("survivors", "allowed_columns", "python", "index_census")}
    if result.get("index_census"):
        summary["index_census_entries"] = len(result["index_census"])
    print(json.dumps(summary, indent=2, default=str))
    return result


if __name__ == "__main__":
    main()
