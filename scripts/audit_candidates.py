"""Freeze and audit the additional X7862 downstairs candidates.

Every condition of the original Oxford heterotic standard-model construction is
checked explicitly, not the three-condition shorthand our search used. The
output is an immutable manifest: one record per candidate carrying the charge
matrix, the symmetry realisation, every equivariant structure and Wilson line
that works, all cohomology with its Gamma-character decomposition, the complete
downstairs spectrum, and the verdict of each individual condition.

Conditions checked, in the order of the construction:

  upstairs   c1(V) = 0
             structure group: no proper subset of the L_a has vanishing c1
             anomaly / effectivity: c2(TX) - c2(V) nonnegative against nef classes
             Bogomolov: c2(V).J >= 0 at the stable polarisation
             poly-stability: an actual common zero of all five slopes at t > 0,
                             exact where possible, never a bare optimizer failure
             generation index: ind(V) = ind(wedge^2 V) = -3|Gamma|
             no anti-families: h^0(V) = h^2(V) = h^3(V) = 0
  descent    every bundle that enters the spectrum is Gamma-equivariant
             the Wilson line is an admissible U(1)_Y embedding
  downstairs exactly three of Q, u^c, d^c, L, e^c
             no charged chiral exotics
             at least one Higgs doublet pair
             no colour-triplet Higgs
             number of additional massless U(1)s
  identity   exact deduplication against every published downstairs model

Nothing here is called new. The manifest records what each candidate is and,
separately, why it is absent from the published partial scan.
"""
import argparse
import json
from fractions import Fraction
from math import gcd
from itertools import combinations, product
from pathlib import Path

import sympy

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.cached import cohomology
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import canonical_row_orbit
from string_sm_sat.physics.anomaly import check_anomaly, check_bogomolov
from string_sm_sat.physics.equivariance import CharacterGroup
from string_sm_sat.physics.equivariant_cohomology import (cyclic_lift, equivariant_cohomology,
                                                          factor_blocks, invariant_family_coefficients,
                                                          is_equivariant, to_matrix)
from string_sm_sat.physics.index import bundle_c2, bundle_index, index
from string_sm_sat.physics.spectrum import check_indices
from string_sm_sat.physics.stability import (_integer_rref, check_span_slope, exact_witness,
                                             numerical_witness, slopes)
from string_sm_sat.physics.structure_group import check_c1, check_structure_group
from string_sm_sat.physics.wilson_line import (WilsonLine, acceptance_report,
                                               downstairs_spectrum)
from string_sm_sat.search.checkpoints import atomic_json, code_hash

ROOT = Path(__file__).resolve().parents[1]
# Every one of the 2,113 published downstairs models has max|k| <= 3, while the
# published GUT catalog reaches 10: the standard-model scan was charge-restricted.
PUBLISHED_SM_CHARGE_LIMIT = 3
# Every published X7862 model has charge-matrix rank 3, i.e. exactly one extra U(1).
PUBLISHED_EXTRA_U1 = 1
SEARCH = ROOT / "benchmarks/x7862/downstairs-search-gamma4.json"
SYMMETRIES = ROOT / "data/processed/published_symmetries.json"
PUBLISHED = ROOT / "data/processed/published_standard_models.json"


def rational_lattice_search(geometry, columns, bound=12):
    """Exhaustive search for an exact positive integral common zero of the slopes.

    Slopes are homogeneous, so only the direction matters and a primitive integer
    vector suffices. This is exact: a hit is a proof of poly-stability in the
    declared chamber, and a miss proves nothing.
    """
    bundle = BundleSum.from_columns(columns)
    for candidate in product(range(1, bound + 1), repeat=geometry.h11):
        divisor = 0
        for value in candidate:
            divisor = gcd(divisor, value)
        if divisor != 1:
            continue
        if not any(slopes(geometry, bundle, [Fraction(v) for v in candidate])):
            return [str(v) for v in candidate]
    return None


def parametric_rational_search(geometry, columns, bound=12):
    """Fix the trailing coordinates to small rationals and solve the rest exactly."""
    h = geometry.h11
    bundle = BundleSum.from_columns(columns)
    free = sympy.symbols(f'u1:{h - 1}', positive=True)
    for numerator in range(1, bound + 1):
        for denominator in range(1, bound + 1):
            if gcd(numerator, denominator) != 1:
                continue
            tail = [sympy.Rational(numerator, denominator), sympy.Integer(1)]
            point = list(free) + tail
            equations = [sympy.expand(sum(d * point[j] * point[k] * column[i]
                                          for i, j, k, d in geometry.nonzero_intersections))
                         for column in columns]
            try:
                solutions = sympy.solve([e for e in equations if e != 0], free, dict=True)
            except Exception:
                continue
            for solution in solutions:
                values = [solution.get(x, x) for x in free] + tail
                if any(getattr(v, 'free_symbols', set()) for v in values):
                    continue
                if not all(getattr(v, 'is_rational', False) and v > 0 for v in values):
                    continue
                multiplier = 1
                for v in values:
                    multiplier = multiplier * sympy.Rational(v).q // gcd(multiplier,
                                                                        sympy.Rational(v).q)
                integral = tuple(int(v * multiplier) for v in values)
                if exact_witness(geometry, bundle,
                                 tuple(Fraction(v) for v in integral)).outcome == 'PASS':
                    return [str(v) for v in integral]
    return None


def slope_witness(geometry, columns):
    """An actual common zero of the five slopes at t > 0, as exact as we can get."""
    bundle = BundleSum.from_columns(columns)
    equal = exact_witness(geometry, bundle, (1,) * geometry.h11)
    if equal.outcome == 'PASS':
        return {"kind": "EXACT_RATIONAL", "t": ["1"] * geometry.h11}
    lattice = rational_lattice_search(geometry, columns)
    if lattice is not None:
        return {"kind": "EXACT_RATIONAL", "t": lattice, "method": "integral lattice search"}
    numeric = numerical_witness(geometry, bundle)
    if numeric.outcome == 'PASS':
        # rationalise the numerical root by continued fractions and test exactly
        raw = numeric.diagnostics["t"]
        smallest = min(raw)
        for limit in (2, 3, 5, 7, 10, 12, 16, 20, 30, 50, 80, 120, 200, 400):
            scaled = [Fraction(v / smallest).limit_denominator(limit) for v in raw]
            if any(x <= 0 for x in scaled):
                continue
            multiplier = 1
            for x in scaled:
                multiplier = multiplier * x.denominator // gcd(multiplier, x.denominator)
            integral = tuple(int(x * multiplier) for x in scaled)
            if any(v <= 0 for v in integral):
                continue
            if exact_witness(geometry, bundle, tuple(Fraction(v) for v in integral)).outcome == 'PASS':
                return {"kind": "EXACT_RATIONAL", "t": [str(v) for v in integral],
                        "method": f"continued-fraction rationalisation, denominator limit {limit}"}
    if numeric.outcome != 'PASS':
        return {"kind": "NONE", "diagnostics": numeric.diagnostics}
    values = numeric.diagnostics["t"]
    # try to rationalise the numerical root exactly
    for denominator in (1, 2, 3, 4, 6, 8, 12, 16, 24, 48, 96, 240):
        scaled = [Fraction(round(v * denominator / max(values)), 1) for v in values]
        if any(x <= 0 for x in scaled):
            continue
        check = exact_witness(geometry, bundle, tuple(scaled))
        if check.outcome == 'PASS':
            return {"kind": "EXACT_RATIONAL", "t": [str(x) for x in scaled]}
    # when the charge matrix has rank below h-1 the solution set is a positive
    # dimensional curve, so rationalising a numerical point cannot work: a rational
    # point ON the curve is needed. Fix the last coordinates to small rationals and
    # solve the remaining system exactly.
    parametric = parametric_rational_search(geometry, columns)
    if parametric is not None:
        return {"kind": "EXACT_RATIONAL", "t": parametric,
                "method": "parametric rational search on the solution curve"}
    # otherwise solve the system symbolically and isolate a positive real root
    symbols = sympy.symbols(f't1:{geometry.h11 + 1}', positive=True)
    equations = [sympy.expand(sum(d * symbols[j] * symbols[k] * column[i]
                                  for i, j, k, d in geometry.nonzero_intersections))
                 for column in columns]
    equations.append(symbols[-1] - 1)
    try:
        solutions = sympy.solve(equations, symbols, dict=True)
    except Exception:
        solutions = []
    for solution in solutions:
        point = [solution.get(s, s) for s in symbols]
        if any(getattr(v, 'free_symbols', set()) for v in point):
            continue                                   # parametric family, not a point
        try:
            values = [complex(sympy.N(v)) for v in point]
        except (TypeError, ValueError):
            continue
        if any(abs(v.imag) > 1e-20 or v.real <= 0 for v in values):
            continue
        residual = slopes(geometry, bundle, [sympy.nsimplify(v) for v in point])
        if any(sympy.simplify(r) != 0 for r in residual):
            continue
        return {"kind": "EXACT_ALGEBRAIC",
                "t": [str(v) for v in point],
                "t_numeric": [v.real for v in values],
                "minimal_polynomials": [str(sympy.minimal_polynomial(v, sympy.Symbol('z')))
                                        for v in point]}
    return {"kind": "NUMERIC_ONLY", "t": values,
            "maximum_slope_residual": numeric.residual}


ALL_CONFIGURATIONS = False


def audit(columns, geometry, lift, factors, generators, coefficients, group, published_models):
    columns = tuple(tuple(k) for k in columns)
    bundle = BundleSum.from_columns(columns)
    labels = group.labels
    record = {"columns": [list(k) for k in columns],
              "max_abs_charge": max(abs(x) for k in columns for x in k)}

    rank = len(_integer_rref([list(k) for k in columns], geometry.h11))
    record["charge_matrix_rank"] = rank
    record["additional_massless_U1"] = geometry.h11 - rank

    # ---------------- upstairs conditions ----------------
    anomaly = check_anomaly(bundle, geometry)
    upstairs = {
        "c1_zero": check_c1(bundle).outcome,
        "structure_group_no_proper_zero_subset": check_structure_group(bundle).outcome,
        "anomaly_effectivity": anomaly.outcome,
        "anomaly_residual": list(anomaly.residual),
        "bogomolov": check_bogomolov(bundle, geometry).outcome,
        "span_slope_obstruction": check_span_slope(geometry, list(columns)).outcome,
        "generation_index": check_indices(bundle, geometry, 4).outcome,
        "index_V": bundle_index(geometry, bundle),
        "index_wedge2": bundle_index(geometry, bundle.wedge2()),
        "c2_V": list(bundle_c2(geometry, bundle)),
    }
    upstairs["poly_stability_witness"] = slope_witness(geometry, columns)

    # ---------------- cohomology ----------------
    singles = [cohomology(geometry, LineBundle(k)).dimensions for k in columns]
    pairs_k = [tuple(x + y for x, y in zip(columns[a], columns[b]))
               for a, b in combinations(range(5), 2)]
    pairs = [cohomology(geometry, LineBundle(k)).dimensions for k in pairs_k]
    singlet_k = [tuple(x - y for x, y in zip(columns[a], columns[b]))
                 for a in range(5) for b in range(5) if a != b]
    singlets = [cohomology(geometry, LineBundle(k)).dimensions for k in singlet_k]
    total = lambda rows: [sum(r[q] for r in rows if r is not None) for q in range(4)]
    record["cohomology"] = {
        "h_V": total(singles), "h_wedge2V": total(pairs),
        "per_bundle": {str(list(k)): list(d) if d else None for k, d in zip(columns, singles)},
        "per_pair": {str(list(k)): list(d) if d else None for k, d in zip(pairs_k, pairs)},
        "singlet_total": total(singlets),
        "any_unknown": any(d is None for d in singles + pairs + singlets),
        "unknown_bundles": [list(k) for k, d in
                            list(zip(columns, singles)) + list(zip(pairs_k, pairs))
                            + list(zip(singlet_k, singlets)) if d is None][:8],
        "unknown_only_in_singlets": all(d is not None for d in singles + pairs),
    }
    h_v = record["cohomology"]["h_V"]
    upstairs["no_anti_families"] = "PASS" if (h_v[0] == 0 and h_v[2] == 0 and h_v[3] == 0) else "FAIL"
    upstairs["three_families_upstairs"] = "PASS" if h_v[1] == 12 else "FAIL"
    record["upstairs"] = upstairs

    # ---------------- equivariance of every bundle ----------------
    needed = list(columns) + pairs_k + singlet_k
    not_equivariant = [list(k) for k in needed if not is_equivariant(generators, geometry.ambient, k)]
    record["equivariance"] = {
        "all_bundles_equivariant": not not_equivariant,
        "non_equivariant_bundles": not_equivariant[:6],
        "criterion": "central element of the lift acts trivially on O(k); for this lift, sum_i k^i even",
    }

    # ---------------- Gamma-character tables ----------------
    tables, undetermined = {}, []
    for k in list(columns) + pairs_k:
        table = equivariant_cohomology(geometry, k, lift, factors, None, generators, coefficients)
        if table is None:
            undetermined.append(list(k))
        else:
            tables[k] = table
    record["character_tables"] = {
        "determined": len(tables), "distinct_bundles": len(set(list(columns) + pairs_k)),
        "needed": len(columns) + len(pairs_k),
        "undetermined": undetermined,
        "tables": {str(list(k)): {str(q): [v[l] for l in labels] for q, v in t.items()}
                   for k, t in tables.items()},
    }

    # ---------------- downstairs: every admissible choice ----------------
    trivial = tuple(0 for _ in factors)
    wilson_choices = []
    for triplet in labels:
        for doublet in labels:
            determinant = group.add(group.multiply(triplet, 3), group.multiply(doublet, 2))
            if determinant == trivial and doublet != triplet:
                wilson_choices.append((triplet, doublet))
    accepted, rejected_reasons = [], {}
    if not undetermined:
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
                report = acceptance_report(spectrum, 4, geometry.h11 - rank)
                failures = []
                if not report["three_chiral_families"]:
                    failures.append("families")
                if report["charged_chiral_exotics"]:
                    failures.append("chiral_exotics")
                if not report["higgs_doublet_pair"]:
                    failures.append("no_higgs_pair")
                if spectrum.get("colour_triplet_pairs"):
                    failures.append("colour_triplet_higgs")
                if failures:
                    rejected_reasons[",".join(failures)] = rejected_reasons.get(",".join(failures), 0) + 1
                    continue
                accepted.append({
                    "wilson_line": [list(wilson_characters[0]), list(wilson_characters[1])],
                    "equivariant_structure": [list(e) for e in equivariant],
                    "families": report["family_multiplicities"],
                    "higgs_pairs": spectrum["higgs_pairs"],
                    "colour_triplet_pairs": spectrum.get("colour_triplet_pairs", 0),
                    "tens": spectrum["tens"], "fivebars": spectrum["fivebars"],
                    "higgs": spectrum["higgs"],
                })
    record["downstairs"] = {
        "admissible_wilson_lines": [[list(a), list(b)] for a, b in wilson_choices],
        "accepted_count": len(accepted),
        "rejection_reasons": rejected_reasons,
        "accepted": accepted if ALL_CONFIGURATIONS else accepted[:8],
        "full_conditions_met": bool(accepted),
    }

    # ---------------- identity against every published downstairs model ----------------
    orbit = canonical_row_orbit(geometry, columns)
    matches = []
    for model in published_models:
        rows = model.get("LineSum")
        if not rows or len(rows) != geometry.h11:
            continue
        other = tuple(tuple(r[a] for r in rows) for a in range(len(rows[0])))
        if len(other) != 5:
            continue
        if model["cicy"] == int(geometry.identifier) and canonical_row_orbit(geometry, other) == orbit:
            matches.append({"cicy": model["cicy"], "gamma": model["gamma_order"],
                            "symmetry_number": model.get("symmetry_number"),
                            "model_number": model.get("ModelNumber")})
        elif tuple(sorted(other)) == tuple(sorted(columns)):
            matches.append({"cicy": model["cicy"], "gamma": model["gamma_order"],
                            "note": "same charge multiset on a different geometry"})
    record["published_downstairs_matches"] = matches
    record["present_in_published_sm_database"] = bool(matches)

    # ---------------- why is it absent from the published partial scan ----------------
    reasons = []
    if record["max_abs_charge"] > PUBLISHED_SM_CHARGE_LIMIT:
        reasons.append(f"outside_published_sm_charge_range(max|k|={record['max_abs_charge']}"
                       f" > {PUBLISHED_SM_CHARGE_LIMIT})")
    if record["additional_massless_U1"] != PUBLISHED_EXTRA_U1:
        reasons.append(f"different_massless_U1_content({record['additional_massless_U1']}"
                       f" vs {PUBLISHED_EXTRA_U1} in every published X7862 model)")
    record["absence_reason"] = reasons or ["unknown"]
    record["absence_classification"] = ("identified" if reasons else "unknown")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default=str(ROOT / "benchmarks/x7862/candidate-manifest.json"))
    parser.add_argument("--include-published", action="store_true",
                        help="audit the 10 published orbits as a control")
    parser.add_argument("--all-configurations", action="store_true",
                        help="store every accepted downstairs configuration, not the first 8")
    args = parser.parse_args(argv)
    global ALL_CONFIGURATIONS
    ALL_CONFIGURATIONS = args.all_configurations

    search = json.loads(SEARCH.read_text())
    geometry = benchmark(search["geometry"])
    entry = json.loads(SYMMETRIES.read_text())["symmetries"][search["geometry"]][
        search["symmetry_number"] - 1]
    factors = entry["cyclic_factors"]
    generators = [to_matrix(m) for m in entry["generators"]]
    lift = cyclic_lift(generators, factors)
    coefficients = invariant_family_coefficients(entry["invariants"],
                                                 sum(n + 1 for n in geometry.ambient))
    group = CharacterGroup(tuple(factors))
    published = json.loads(PUBLISHED.read_text())["models"]

    additional = [tuple(map(tuple, o)) for o in search["ours_only"]]
    records = []
    for position, columns in enumerate(additional, start=1):
        record = audit(columns, geometry, lift, factors, generators, coefficients, group,
                       published)
        record["candidate_id"] = f"X7862-G4-A{position:02d}"
        record["class"] = "additional"
        records.append(record)
        print(f"  audited {record['candidate_id']}  max|k|={record['max_abs_charge']}  "
              f"accepted choices={record['downstairs']['accepted_count']}  "
              f"published={record['present_in_published_sm_database']}", flush=True)

    if args.include_published:
        seen = {canonical_row_orbit(geometry, tuple(map(tuple, r["columns"]))) for r in records}
        controls = []
        for model in published:
            if model["cicy"] != 7862 or model["gamma_order"] != 4:
                continue
            columns = tuple(tuple(r[a] for r in model["LineSum"]) for a in range(5))
            orbit = canonical_row_orbit(geometry, columns)
            if orbit in seen:
                continue
            seen.add(orbit)
            controls.append(columns)
        for position, columns in enumerate(controls, start=1):
            record = audit(columns, geometry, lift, factors, generators, coefficients, group,
                           published)
            record["candidate_id"] = f"X7862-G4-P{position:02d}"
            record["class"] = "published"
            records.append(record)
            print(f"  audited {record['candidate_id']} (control)  "
                  f"accepted choices={record['downstairs']['accepted_count']}", flush=True)

    manifest = {
        "schema": 1, "kind": "candidate_manifest", "frozen": True,
        "geometry": search["geometry"], "gamma_order": search["gamma_order"],
        "symmetry_number": search["symmetry_number"],
        "symmetry_realisation": {
            "cyclic_factors": factors, "gap_id": entry["gap_id"],
            "acts_freely": entry["acts_freely"],
            "generators": entry["generators"],
            "polynomial_action": entry["polynomial_action"],
            "invariant_family_size": len([x for x in entry["invariants"]
                                          if str(x).strip() not in ("['0']", "0")]),
        },
        "upstairs_certificate": search["upstairs_certificate"],
        "candidates": records,
        "conditions_checked": [
            "c1(V)=0", "structure group subset criterion", "anomaly effectivity",
            "Bogomolov", "poly-stability witness", "generation index",
            "no anti-families", "equivariance of every bundle",
            "admissible Wilson line", "three of each SM multiplet",
            "no charged chiral exotics", "at least one Higgs doublet pair",
            "no colour-triplet Higgs", "additional massless U(1) count",
            "deduplication against every published downstairs model",
        ],
        "software_source_sha256": code_hash(),
    }
    atomic_json(args.output, manifest)
    print(json.dumps({"candidates": len(records),
                      "additional": sum(1 for r in records if r["class"] == "additional"),
                      "output": args.output}, indent=2))
    return manifest


if __name__ == "__main__":
    main()
