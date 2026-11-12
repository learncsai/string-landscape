"""Search for downstairs standard models over our own exhaustive upstairs results.

This is a search, not a verification. It takes the survivor set of one of our
bounded upstairs scans, and for each candidate

  1. checks that every line bundle is Gamma-equivariant for the chosen lift
     (the central element of the matrix lift must act trivially on O(k));
  2. computes the Gamma-representation on every relevant cohomology from the
     explicit group action - collapse where the Koszul complex collapses, and
     equivariant map ranks otherwise;
  3. enumerates the allowed equivariant structures and Wilson lines;
  4. derives the downstairs spectrum and keeps those with three chiral families,
     no charged chiral exotics and at least one Higgs doublet pair.

No published cohomology, representation or model data enters the search. The
published catalog is used only afterwards, to compare.

Wilson line. In SU(5) the flat bundle is diag(chi_T, chi_T, chi_T, chi_D, chi_D)
with determinant one, so chi_T^3 chi_D^2 = 1. For a group of exponent two this
forces chi_T trivial and leaves chi_D free, which is exactly the convention the
published database uses.
"""
import argparse
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import canonical_row_orbit
from string_sm_sat.physics.equivariance import CharacterGroup
from string_sm_sat.physics.equivariant_cohomology import (cyclic_lift, equivariant_cohomology,
                                                          factor_blocks, is_equivariant,
                                                          invariant_family_coefficients,
                                                          to_matrix)
from string_sm_sat.physics.wilson_line import (WilsonLine, acceptance_report,
                                               downstairs_spectrum)
from string_sm_sat.search.checkpoints import atomic_json, code_hash

ROOT = Path(__file__).resolve().parents[1]
SYMMETRIES = ROOT / "data/processed/published_symmetries.json"
MODELS = ROOT / "data/processed/published_standard_models.json"


def wilson_lines(group):
    """Characters (chi_T, chi_D) with chi_T^3 chi_D^2 trivial and chi_D nontrivial."""
    trivial = tuple(0 for _ in group.moduli)
    out = []
    for triplet in group.labels:
        for doublet in group.labels:
            determinant = group.add(group.multiply(triplet, 3), group.multiply(doublet, 2))
            if determinant != trivial or doublet == triplet:
                continue
            out.append((triplet, doublet))
    return out


def structures(group, count=5):
    """Equivariant structures on the five summands with trivial total, so det V descends."""
    trivial = tuple(0 for _ in group.moduli)
    for head in product(group.labels, repeat=count - 1):
        last = group.negate(group.add(*head)) if head else trivial
        yield (*head, last)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--certificate", required=True, help="our upstairs search artifact")
    parser.add_argument("--symmetry", type=int, required=True, help="1-based symmetry number")
    parser.add_argument("--limit", type=int, help="at most this many upstairs orbits")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    run = json.loads(Path(args.certificate).read_text())
    identifier = run["domain"]["geometry"]["identifier"]
    gamma = run["domain"]["gamma"]
    g = benchmark(identifier)
    entry = json.loads(SYMMETRIES.read_text())["symmetries"][identifier][args.symmetry - 1]
    if entry["group_order"] != gamma or entry["acts_freely"] != "True":
        raise SystemExit("symmetry does not match the certificate's |Gamma|, or is not free")

    factors = entry["cyclic_factors"]
    generators = [to_matrix(m) for m in entry["generators"]]
    lift = cyclic_lift(generators, factors)
    if any(factor_blocks(m, g.ambient) is None for m in lift.values()):
        raise SystemExit("this symmetry permutes projective factors")
    poly_lift = (cyclic_lift([to_matrix(m) for m in entry["polynomial_action"]], factors)
                 if entry["polynomial_action"] else None)
    coefficients = None
    if entry.get("invariants") and len(tuple(zip(*g.configuration))) == 1:
        coefficients = invariant_family_coefficients(entry["invariants"],
                                                     sum(n + 1 for n in g.ambient))
    group = CharacterGroup(tuple(factors))
    labels = group.labels

    # one representative per ambient-row orbit of our exhaustive survivor set
    survivors = [tuple(map(tuple, m)) for m in run["enumeration"]["survivors"]]
    orbits = {}
    for columns in survivors:
        orbits.setdefault(canonical_row_orbit(g, columns), columns)
    candidates = list(orbits.values())
    if args.limit:
        candidates = candidates[:args.limit]

    counters = Counter()
    found = []
    for columns in candidates:
        counters["orbits_examined"] += 1
        if not all(is_equivariant(generators, g.ambient, k) for k in columns):
            counters["not_equivariant"] += 1
            continue
        counters["equivariant"] += 1
        tables, ok = {}, True
        needed = list(columns) + [tuple(x + y for x, y in zip(columns[a], columns[b]))
                                  for a, b in combinations(range(5), 2)]
        for k in needed:
            table = equivariant_cohomology(g, k, lift, factors, poly_lift, generators,
                                           coefficients)
            if table is None:
                ok = False
                break
            tables[k] = table
        if not ok:
            counters["cohomology_undetermined"] += 1
            continue
        counters["fully_determined"] += 1
        pairs = [(a, b) for a, b in combinations(range(5), 2)]
        accepted = []
        for wilson_characters in wilson_lines(group):
            wilson = WilsonLine(group, *wilson_characters)
            for equivariant in structures(group):
                tens = []
                for a, k in enumerate(columns):
                    row = tuple(tables[k].get(1, {}).get(l, 0) for l in labels)
                    tens.append(group.shift(row, equivariant[a]))
                h1, h2 = [], []
                for a, b in pairs:
                    k = tuple(x + y for x, y in zip(columns[a], columns[b]))
                    shift = group.add(equivariant[a], equivariant[b])
                    h1.append(group.shift(tuple(tables[k].get(1, {}).get(l, 0)
                                                for l in labels), shift))
                    h2.append(group.shift(tuple(tables[k].get(2, {}).get(l, 0)
                                                for l in labels), shift))
                spectrum = downstairs_spectrum(group, wilson, tens, h1, h2)
                report = acceptance_report(spectrum, gamma)
                if (report["three_chiral_families"] and not report["charged_chiral_exotics"]
                        and report["higgs_doublet_pair"]):
                    accepted.append({
                        "wilson_line": [list(wilson_characters[0]), list(wilson_characters[1])],
                        "equivariant_structure": [list(e) for e in equivariant],
                        "higgs_pairs": spectrum["higgs_pairs"],
                    })
        if accepted:
            counters["orbits_with_a_standard_model"] += 1
            counters["standard_models"] += len(accepted)
            found.append({"columns": [list(k) for k in columns],
                          "models": len(accepted), "examples": accepted[:4]})
        else:
            counters["no_wilson_line_works"] += 1

    # compare with the published catalog, after the fact
    published = json.loads(MODELS.read_text())
    published_orbits = {canonical_row_orbit(g, tuple(tuple(r[a] for r in m["LineSum"])
                                                     for a in range(5)))
                        for m in published["models"]
                        if m["cicy"] == int(identifier) and m["gamma_order"] == gamma}
    ours = {canonical_row_orbit(g, tuple(map(tuple, f["columns"]))) for f in found}
    summary = {
        "schema": 1, "kind": "downstairs_search",
        "geometry": identifier, "gamma_order": gamma,
        "symmetry_number": args.symmetry, "cyclic_factors": factors,
        "upstairs_certificate": str(args.certificate),
        "upstairs_domain": run["domain"],
        "counters": dict(counters),
        "orbits_with_a_standard_model": sorted(map(lambda o: [list(k) for k in o], ours)),
        "published_orbits": len(published_orbits),
        "ours_orbits": len(ours),
        "exact_orbit_set_equality": ours == published_orbits,
        "published_only": sorted(map(lambda o: [list(k) for k in o], published_orbits - ours)),
        "ours_only": sorted(map(lambda o: [list(k) for k in o], ours - published_orbits)),
        "wilson_lines_tried": len(wilson_lines(group)),
        "equivariant_structures_tried": len(list(structures(group))),
        "scope": ("search over our own exhaustive upstairs survivor set; no published "
                  "cohomology, representation or model data enters the search"),
        "software_source_sha256": code_hash(),
    }
    if args.output:
        atomic_json(args.output, {**summary, "found": found})
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
