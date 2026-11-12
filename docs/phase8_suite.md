# Phase 8: the 68 favourable CICYs at low K

The master plan (prompt Section 29) asks for an automated low-K benchmark over
the 68 favourable CICYs of the published GUT catalog, after the two benchmarks
and one h11 = 6 example work, recording per geometry the nominal search size,
retained singles, pairs and triples, complete bundles checked, counts, runtime
and memory. `scripts/phase8_suite.py` does this for every (geometry, |Gamma|) key
of the catalog and compares each survivor set with the published catalog
restricted to the same box. Artifacts: `benchmarks/phase8-suite.json` (K = 1 on
all keys, K = 2 for h11 <= 4), `benchmarks/phase8-suite-h5-k2.json` (K = 2 for
h11 = 5), `benchmarks/phase8-suite-k3.json` (K = 3 for h11 <= 4),
`benchmarks/phase8-extras-classified.json`.

## Orbits

Two charge matrices are identified under summand permutations and under
permutations of the ambient factors that preserve the configuration matrix up
to a permutation of its columns. For the benchmarks this is the identical-row
convention used elsewhere. It can be finer than the true equivalence of models
(see below), which can only make our orbit counts larger.

## Coverage and cost

| K | h11 | keys | geometries | max runtime | max RSS |
|---|---:|---:|---:|---:|---:|
| 1 | 2-5 | 101 | 60 | 2.6 s | 158 MiB |
| 1 | 6 | 9 | 8 | 484 s | 618 MiB |
| 2 | 2-4 | 60 | 37 | 19 s | 179 MiB |
| 2 | 5 | 41 | 23 | 8,794 s (7447, Gamma = Z_20) | 947 MiB |
| 3 | 2-4 | 60 | 37 | 418 s | 433 MiB |

271 runs, all 68 geometries. The h11 = 6 prerequisite of the plan is met: CICY
3413 (|Gamma| = 3) at K = 1 in 380 s, and CICY 4190 (|Gamma| = 2) at K = 1
reproduces its 11 published models in the box exactly. The cost is dominated by
the number of complete bundles materialised, which at h11 = 5, K = 2 ranges from
35,833 to 4,817,135.

## Agreement with the published catalog

| K | keys | exact orbit-set equality | published models in box | recovered | extra orbits of ours |
|---|---:|---:|---:|---:|---:|
| 1 | 110 | 109 | 40 | **40** | 1 |
| 2 | 101 | 91 | 9,016 | **9,016** | 79 |
| 3 | 60 | 60 | 342 | **342** | 0 |

**No published model inside a box is ever missed** — the soundness statement,
now verified on every geometry of the catalog. The divisibility obstruction
fires on exactly the keys where the catalog is empty ({7761, 2}, {7447, 5}).
Extra orbits occur in eleven runs (ten keys at K = 2, one at K = 1), ten of them
on geometries with d_ijj != 0, where the sign test is not exact per combination
(Proposition 4 of the slope note).

## The extra orbits

`scripts/phase8_extras.py` classifies each extra orbit, strongest evidence first
(`benchmarks/phase8-extras-classified.json`):

| verdict | count |
|---|---:|
| UNSTABLE_CERTIFIED (exact Groebner/interval decision, rank h-1) | 53 |
| STABLE_CERTIFIED (exact real-algebraic interior witness) | 9 |
| NUMERIC_UNSTABLE (rank < h-1; numerical evidence only) | 18 |

The 53 are false survivors of our necessary-only filter, now excluded exactly;
the 18 are very probably the same, but only numerically. The 9 are a single
model (one intersection fingerprint across the redundant descriptions 5256,
5301, 5452): a poly-stable, anomaly-free, correct-index SU(5) GUT model with
|Gamma| = 4 and |k| <= 2 that the published catalog does not contain, although it
lists 656 models on that key inside the same box and none with the same
invariants. Certificate: `benchmarks/phase8-new-gut-model.json`
(`scripts/new_gut_model_certificate.py`). It has no downstairs descent with
individually equivariant line bundles under the four free Z2 x Z2 actions.

The exact decision was itself validated against the published models, which are
poly-stable: it never calls one unstable (0 of 548 sampled; 214 certified
stable). A first version failed this check through two bugs, both fixed and both
now guarded by a regression test.
