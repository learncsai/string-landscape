"""Independent audit of our topology against the 68 published favourable CICYs,
plus an exact index-parity analysis tested against the published model catalog.

Part 1 recomputes d_ijk, c2.J_i and the Euler number from each published
configuration matrix with our ambient Chow-ring code and compares c2 and the
Euler number with the published record.

Part 2 tests, for each geometry, whether ind(L) is even for every line bundle.
When it is, ind(V) = sum_a ind(L_a) is even, so the three-family condition
ind(V) = -3|Gamma| is unsatisfiable for odd |Gamma| at any K (see
docs/exact_obstructions.md, Proposition P). The published catalog is then used
as an independent check: every (geometry, odd |Gamma|) key of such a geometry
must carry zero models.

Parity is decided by evaluating ind on (Z/8)^h. That is conclusive: ind is an
integer-valued polynomial of degree <= 3, hence a Z-combination of products of
binomial coefficients C(k_i,a) with a <= 3, and C(k,1), C(k,2), C(k,3) have
period 2, 4, 8 modulo 2 in k.
"""
import json
from itertools import product
from pathlib import Path

from string_sm_sat.geometry.cicy import CICY
from string_sm_sat.geometry.chern import euler_number
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.physics.index import index
from string_sm_sat.search.checkpoints import atomic_json

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/processed/published_gut_models.json"


def build(record):
    configuration = tuple(tuple(row) for row in record["configuration"])
    ambient = tuple(sum(row) - 1 for row in configuration)
    return CICY(str(record["number"]), ambient, configuration,
                record["h11"], record["h21"],
                tuple(record["symmetry_orders"]), "POSITIVE_ORTHANT")


def index_always_even(geometry):
    """True iff ind(L) is even for every integral line bundle."""
    for k in product(range(8), repeat=geometry.h11):
        if index(geometry, LineBundle(k)) % 2:
            return False
    return True


def main():
    catalog = json.loads(CATALOG.read_text())
    rows, failures = [], []
    for record in catalog["geometries"]:
        entry = {"number": record["number"], "h11": record["h11"]}
        try:
            g = build(record)
        except (ValueError, TypeError) as exc:
            entry.update({"built": False, "error": str(exc)})
            rows.append(entry)
            failures.append(entry)
            continue
        c2 = list(g.c2)
        euler = euler_number(g.ambient, g.configuration)
        entry.update({
            "built": True,
            "ambient": list(g.ambient),
            "c2": c2, "published_c2": record["c2"], "c2_agrees": c2 == record["c2"],
            "euler": euler, "published_euler": record["euler"],
            "euler_agrees": euler == record["euler"],
            "index_always_even": index_always_even(g),
            "symmetry_orders": record["symmetry_orders"],
        })
        if not (entry["c2_agrees"] and entry["euler_agrees"]):
            failures.append(entry)
        rows.append(entry)

    # --- parity prediction against the published catalog ---------------------
    predictions = []
    for entry in rows:
        if not entry.get("built") or not entry.get("index_always_even"):
            continue
        for order in entry["symmetry_orders"]:
            if order % 2 == 0:
                continue
            key = f"{entry['number']},{order}"
            published = len(catalog["models"].get(key, []))
            predictions.append({"geometry": entry["number"], "gamma": order,
                                "predicted_models": 0, "published_models": published,
                                "agrees": published == 0,
                                "key_present_in_catalog": key in catalog["models"]})

    built = [r for r in rows if r.get("built")]
    result = {
        "schema": 1,
        "kind": "catalog_topology_audit",
        "catalog_sha256": catalog["source_sha256"],
        "geometries_in_catalog": len(rows),
        "geometries_built": len(built),
        "c2_agreements": sum(1 for r in built if r["c2_agrees"]),
        "euler_agreements": sum(1 for r in built if r["euler_agrees"]),
        "disagreements": failures,
        "index_always_even_count": sum(1 for r in built if r["index_always_even"]),
        "index_always_even_geometries": [r["number"] for r in built if r["index_always_even"]],
        "odd_gamma_predictions": predictions,
        "odd_gamma_prediction_agreements": sum(1 for p in predictions if p["agrees"]),
        "parity_argument": ("ind(L) even for all L implies ind(V) even, so "
                            "ind(V) = -3|Gamma| forces |Gamma| even; unbounded in K"),
        "geometries": rows,
    }
    atomic_json(ROOT / "benchmarks/catalog-topology-audit.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "geometries"}, indent=2)[:4000])


if __name__ == "__main__":
    main()
