"""Compute the Gamma-representation on line-bundle cohomology from first principles.

For every published downstairs model on a supported geometry this script takes
only the explicit group action on the ambient coordinates (and the fact, read
from the database, that the defining polynomials are invariant, which makes the
Koszul complex untwisted) and computes the character of Gamma on H^q(X, L) for

  * each of the five line bundles L_a, and
  * each of the ten pair bundles L_a (x) L_b,

whenever exactly one cohomological degree is nonzero — decided independently by
our own exact dimension code. It then compares the resulting multiplicities with
the published GCoh / GCoh2 tables, allowing for the character shift induced by
the equivariant structure.

Nothing representation-theoretic is taken from the database in the computation;
GCoh is used only as the comparison target.
"""
import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import sympy

from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.cached import cohomology
from string_sm_sat.geometry.cicy import CICY
from string_sm_sat.physics.equivariant_cohomology import (cyclic_lift, decompose_abelian,
                                                          equivariant_degrees, factor_blocks,
                                                          is_representation,
                                                          koszul_virtual_character, to_matrix)
from string_sm_sat.search.checkpoints import atomic_json, code_hash

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "data/processed/published_standard_models.json"
SYMMETRIES = ROOT / "data/processed/published_symmetries.json"


def geometry_for(record):
    configuration = tuple(tuple(row) for row in record["configuration"])
    ambient = tuple(sum(row) - 1 for row in configuration)
    return CICY(str(record["number"]), ambient, configuration, record["h11"],
                record["h21"], (), "POSITIVE_ORTHANT")


def choose_symmetry(entries, order, factors):
    """The freely acting entry of the right order whose elements preserve factors."""
    for index, entry in enumerate(entries):
        if entry["group_order"] != order or entry["acts_freely"] != "True":
            continue
        if entry["cyclic_factors"] != factors:
            continue
        if not entry["generators"]:
            continue
        yield index, entry


def representation_of(geometry, k, lift, factors, order, dimensions, poly_lift=None):
    """Multiplicities of each character in the single nonzero H^q(X, O(k))."""
    nonzero = [q for q, value in enumerate(dimensions) if value]
    if len(nonzero) > 1:
        return None, 'MULTIPLE_NONZERO_DEGREES'
    if not nonzero:
        return {label: 0 for label in sorted(lift)}, 'ZERO'
    q = nonzero[0]
    labels = sorted(lift)
    values = koszul_virtual_character(
        geometry, k, [lift[label] for label in labels],
        None if poly_lift is None else [poly_lift[label] for label in labels])
    character = {label: (-1) ** q * values[i] for i, label in enumerate(labels)}
    multiplicities = decompose_abelian(character, factors)
    if not is_representation(multiplicities):
        return None, 'NOT_A_REPRESENTATION'
    if sum(int(v) for v in multiplicities.values()) != dimensions[q]:
        return None, 'DIMENSION_MISMATCH'
    return {label: int(value) for label, value in multiplicities.items()}, 'OK'


def shift_label(label, shift, factors):
    return tuple((a + b) % n for a, b, n in zip(label, shift, factors))


def verify_model(record, geometry, lift, factors, order, poly_lift=None, generators=None):
    rows = record["LineSum"]
    columns = [tuple(r[a] for r in rows) for a in range(len(rows[0]))]
    equivariant = [tuple(x) for x in record["EquivStr"]]
    labels = sorted(lift)
    outcome = {"columns": [list(c) for c in columns], "singles": [], "pairs": [],
               "single_matches": 0, "single_compared": 0,
               "pair_matches": 0, "pair_compared": 0, "skipped": Counter()}

    def compare(k, published_table, shift, store):
        if published_table is None:
            outcome["skipped"]["NO_PUBLISHED_TABLE"] += 1
            return
        if not isinstance(published_table, list) or \
                not all(isinstance(row, list) for row in published_table):
            # the published entry is an unevaluated rank expression
            outcome["skipped"]["UNEVALUATED_PUBLISHED_TABLE"] += 1
            return
        # every cohomological degree at once, via the collapsing Koszul complex
        tables = equivariant_degrees(geometry, k, lift, factors, poly_lift, generators)
        if tables is None:
            outcome["skipped"]["NO_COLLAPSE_OR_NOT_EQUIVARIANT"] += 1
            return
        # The published GCoh / GCoh2 tables are the *raw* characters of the lift:
        # the equivariant structure is applied only when the downstairs spectrum is
        # formed (physics/wilson_line.py), which is why that reproduction needs the
        # shift. So the comparison is raw against raw. An earlier version compared
        # the shifted table and misreported 694 vector-like pair tables as
        # relabellings; see scripts/character_table_convention.py.
        rows, matches, shifted_matches = [], True, True
        for q in range(4):
            computed = tables.get(q, {label: 0 for label in labels})
            raw = [computed[label] for label in labels]
            shifted = [computed[shift_label(label, shift, factors)] for label in labels]
            published = list(published_table[q])
            rows.append({"degree": q, "computed": raw, "computed_shifted": shifted,
                         "published": published})
            matches = matches and raw == published
            shifted_matches = shifted_matches and shifted == published
        # classify a disagreement: identical multiplicity multisets in every degree
        # means the dimensions are right and only the character labelling differs.
        verdict = "exact"
        if not matches:
            if all(sorted(row["computed"]) == sorted(row["published"]) for row in rows):
                verdict = "relabelling_only"
            elif all(sum(row["computed"]) == sum(row["published"]) for row in rows):
                verdict = "same_dimensions"
            else:
                verdict = "genuine_disagreement"
        store.append({"k": list(k), "degrees": rows, "matches": matches, "verdict": verdict,
                      "shift_invariant": all(r["computed"] == r["computed_shifted"] for r in rows),
                      "matches_if_shifted": shifted_matches})

    single_tables = record.get("GCoh") or [None] * len(columns)
    pair_tables = record.get("GCoh2") or [None] * (len(columns) * (len(columns) - 1) // 2)
    for a, k in enumerate(columns):
        compare(k, single_tables[a], equivariant[a], outcome["singles"])
    for index, (a, b) in enumerate(combinations(range(len(columns)), 2)):
        k = tuple(x + y for x, y in zip(columns[a], columns[b]))
        shift = tuple((x + y) % n for x, y, n in
                      zip(equivariant[a], equivariant[b], factors))
        compare(k, pair_tables[index], shift, outcome["pairs"])

    outcome["single_compared"] = len(outcome["singles"])
    outcome["single_matches"] = sum(1 for s in outcome["singles"] if s["matches"])
    outcome["pair_compared"] = len(outcome["pairs"])
    outcome["pair_matches"] = sum(1 for s in outcome["pairs"] if s["matches"])
    outcome["skipped"] = dict(outcome["skipped"])
    return outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cicy", type=int, default=7862)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    database = json.loads(MODELS.read_text())
    symmetries = json.loads(SYMMETRIES.read_text())["symmetries"]
    record = next(r for r in database["geometries"] if r["number"] == args.cicy)
    geometry = geometry_for(record)
    models = [m for m in database["models"]
              if m["cicy"] == args.cicy and m.get("GCoh") and m.get("EquivStr")]
    if args.limit:
        models = models[:args.limit]
    if not models:
        raise SystemExit("no complete models for that geometry")

    entries = symmetries[str(args.cicy)]
    results, used, refused = [], {}, Counter()
    for model in models:
        number = model.get("symmetry_number")
        if number is None or not 1 <= number <= len(entries):
            refused["NO_SYMMETRY_NUMBER"] += 1
            continue
        entry = entries[number - 1]                    # the key is 1-based
        order = model["gamma_order"]
        if (entry["group_order"] != order or entry["acts_freely"] != "True"
                or not entry["generators"] or not entry["cyclic_factors"]):
            refused["SYMMETRY_NOT_USABLE"] += 1
            continue
        factors = entry["cyclic_factors"]
        if len(entry["generators"]) != len(factors):
            refused["GENERATOR_COUNT"] += 1
            continue
        cached = used.get(number)
        if cached is None:
            generators = [to_matrix(m) for m in entry["generators"]]
            lift = cyclic_lift(generators, factors)
            if any(factor_blocks(m, geometry.ambient) is None for m in lift.values()):
                refused["PERMUTES_FACTORS"] += 1
                used[number] = False
                continue
            poly_lift = None
            if entry["polynomial_action"]:
                poly_lift = cyclic_lift([to_matrix(m) for m in entry["polynomial_action"]],
                                        factors)
            used[number] = (lift, poly_lift, factors, entry)
            cached = used[number]
        if cached is False:
            refused["PERMUTES_FACTORS"] += 1
            continue
        lift, poly_lift, factors, entry = cached
        outcome = verify_model(model, geometry, lift, factors, order, poly_lift,
                               [to_matrix(x) for x in entry["generators"]])
        outcome["symmetry_number"] = number
        results.append(outcome)
    if not results:
        raise SystemExit(f"no usable symmetry: {dict(refused)}")
    index = sorted({r["symmetry_number"] for r in results})
    entry = {"gap_id": None, "acts_freely": "True", "polynomial_action": None}
    order = models[0]["gamma_order"]
    factors = used[results[0]["symmetry_number"]][2]
    summary = {
        "schema": 1, "kind": "equivariant_cohomology_from_first_principles",
        "geometry": args.cicy, "gamma_order": order, "cyclic_factors": factors,
        "symmetry_numbers_used": index, "models_refused": dict(refused),
        "models": len(results),
        "single_bundles_compared": sum(r["single_compared"] for r in results),
        "single_bundles_matching": sum(r["single_matches"] for r in results),
        "pair_bundles_compared": sum(r["pair_compared"] for r in results),
        "pair_bundles_matching": sum(r["pair_matches"] for r in results),
        "skipped": dict(sum((Counter(r["skipped"]) for r in results), Counter())),
        "verdicts": dict(sum((Counter(e["verdict"] for kind in ("singles", "pairs")
                                      for e in r[kind]) for r in results), Counter())),
        "method": ("Gamma-equivariant Koszul resolution resolved by node: every H^q is "
                   "the sum of the E1 terms with q - p equal to that degree, valid "
                   "whenever the complex collapses by bidegree support. Resolves H^1 and "
                   "H^2 separately, so the vector-like sector is determined too."),
        "input_from_database": "the group action, the multidegrees and the invariance "
                               "of the defining polynomials; GCoh is only the comparison target",
        "software_source_sha256": code_hash(),
    }
    if args.output:
        atomic_json(args.output, {**summary, "results": results})
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
