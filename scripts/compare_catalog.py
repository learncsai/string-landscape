"""Exact catalog comparison against the published Oxford GUT model database.

Compares the survivor set of one of our bounded searches with the published
models for the same (geometry, |Gamma|), restricted to the same finite box.

Equivalence conventions applied, separately reported:
  (1) permutation of the five line-bundle summands  (columns);
  (2) permutation of identical ambient projective factors (rows);
  (3) nothing else. Dualisation V -> V* is NOT an equivalence here: it flips
      the sign of ind(V) and would violate the three-family condition.

Every published model is also re-validated with our own exact checks, which is
an independent cross-check in both directions.
"""
import argparse
import json
from itertools import permutations
from pathlib import Path

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import ambient_relabelings
from string_sm_sat.physics.anomaly import check_anomaly
from string_sm_sat.physics.index import bundle_index
from string_sm_sat.physics.spectrum import check_indices
from string_sm_sat.physics.stability import (necessary_stability, check_span_slope,
                                             exact_witness, numerical_witness)
from string_sm_sat.physics.structure_group import check_c1, check_structure_group
from string_sm_sat.search.checkpoints import atomic_json

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/processed/published_gut_models.json"


def column_canonical(columns):
    return tuple(sorted(tuple(k) for k in columns))


def row_orbit(geometry, columns):
    relabelings = ambient_relabelings(geometry)
    return min(tuple(sorted(tuple(k[i] for i in p) for k in columns)) for p in relabelings)


def validate(geometry, columns, gamma):
    v = BundleSum.from_columns(columns)
    checks = {
        "c1_zero": check_c1(v).outcome,
        "no_proper_zero_subset": check_structure_group(v).outcome,
        "chiral_indices": check_indices(v, geometry, gamma).outcome,
        "anomaly_nef_pairings": check_anomaly(v, geometry).outcome,
        "signed_slope_box1": necessary_stability(geometry, v.lines, 1).outcome,
        "span_slope_obstruction": check_span_slope(geometry, [l.k for l in v.lines]).outcome,
    }
    numeric = numerical_witness(geometry, v)
    return {
        "checks": checks,
        "index_V": bundle_index(geometry, v),
        "index_wedge2": bundle_index(geometry, v.wedge2()),
        "max_abs_charge": max(abs(x) for k in columns for x in k),
        "equal_t_witness": exact_witness(geometry, v, (1,) * geometry.h11).outcome,
        "numerical_slope_witness": numeric.outcome,
        "numerical_residual": (numeric.residual if numeric.outcome == "PASS"
                               else numeric.diagnostics["best_attempt"]["maximum_slope_residual"]),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("certificate", help="our bounded-search certificate JSON")
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)

    ours = json.loads(Path(args.certificate).read_text())
    domain = ours["domain"]
    identifier = domain["geometry"]["identifier"]
    gamma, K = domain["gamma"], domain["K"]
    g = benchmark(identifier)

    catalog = json.loads(CATALOG.read_text())
    key = f"{identifier},{gamma}"
    published_all = [tuple(map(tuple, m)) for m in catalog["models"].get(key, [])]

    # --- geometry cross-check against the published record -------------------
    record = next((r for r in catalog["geometries"] if r["number"] == int(identifier)), None)
    geometry_check = None
    if record is not None:
        geometry_check = {
            "published_c2": record["c2"], "our_c2": list(g.c2),
            "c2_agrees": list(g.c2) == record["c2"],
            "published_h11": record["h11"], "h11_agrees": record["h11"] == g.h11,
            "published_h21": record["h21"], "h21_agrees": record["h21"] == g.h21,
            "published_configuration": record["configuration"],
            "configuration_agrees": [list(r) for r in g.configuration] == record["configuration"],
            "published_symmetry_orders": record["symmetry_orders"],
            "symmetry_orders_agree": list(g.symmetry_orders) == record["symmetry_orders"],
            "published_favourable": record["favourable"],
        }

    inside = [m for m in published_all if max(abs(x) for k in m for x in k) <= K]
    outside = [m for m in published_all if max(abs(x) for k in m for x in k) > K]

    ourset = [tuple(map(tuple, m)) for m in ours["enumeration"]["survivors"]]

    published_columns = {column_canonical(m) for m in inside}
    our_columns = {column_canonical(m) for m in ourset}
    published_rows = {row_orbit(g, m) for m in inside}
    our_rows = {row_orbit(g, m) for m in ourset}

    validations = [{"columns": [list(k) for k in m],
                    "in_box": max(abs(x) for k in m for x in k) <= K,
                    **validate(g, m, gamma)} for m in published_all]

    result = {
        "schema": 1,
        "kind": "published_catalog_comparison",
        "geometry": identifier,
        "gamma": gamma,
        "K": K,
        "our_certificate": str(args.certificate),
        "our_domain": domain,
        "catalog_source": catalog["source"],
        "catalog_sha256": catalog["source_sha256"],
        "catalog_acceptance_stage": catalog["acceptance_stage"],
        "geometry_record_crosscheck": geometry_check,
        "published_models_total": len(published_all),
        "published_models_inside_box": len(inside),
        "published_models_outside_box": len(outside),
        "published_charge_range": (max((max(abs(x) for k in m for x in k) for m in published_all),
                                       default=None)),
        "count_agreement": {
            "published_inside_box_column_canonical": len(published_columns),
            "our_column_canonical": len(our_columns),
            "published_inside_box_row_orbits": len(published_rows),
            "our_row_orbits": len(our_rows),
            "row_orbit_counts_agree": len(published_rows) == len(our_rows),
        },
        "exact_catalog_agreement": {
            "column_canonical_set_equal": published_columns == our_columns,
            "row_orbit_set_equal": published_rows == our_rows,
            "published_only_row_orbits": sorted(map(list, map(lambda o: list(map(list, o)),
                                                             published_rows - our_rows))),
            "ours_only_row_orbits": sorted(map(list, map(lambda o: list(map(list, o)),
                                                        our_rows - published_rows))),
            "published_only_column_canonical_count": len(published_columns - our_columns),
            "ours_only_column_canonical_count": len(our_columns - published_columns),
        },
        "published_model_validation": validations,
        "validation_summary": {
            name: sorted({v["checks"][name] for v in validations})
            for name in validations[0]["checks"]} if validations else {},
        "notes": [
            "Our survivor set is a necessary-condition survivor set, not a certified model list.",
            "The published catalog is the final SU(5) GUT stage of arXiv:1307.4787.",
            "Published models outside the box are excluded by the box, not by physics.",
        ],
    }
    atomic_json(args.output, result)
    printable = {k: v for k, v in result.items()
                 if k not in ("published_model_validation", "our_domain")}
    print(json.dumps(printable, indent=2))
    return result


if __name__ == "__main__":
    main()
