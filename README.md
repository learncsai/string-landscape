# string-sm-sat

## Portfolio and working-style demo

- [Two-page Codex + Claude Code working-style demo (PDF)](application/working_style/working_style_demo.pdf)
- [Editable working-style demo (Word)](application/working_style/working_style_demo.docx)
- [Three-page research summary (PDF)](paper/summary/summary.pdf)
- [Research paper (PDF)](paper/main.pdf)
- [Original project specification](prompt.txt)
- [Research notebook and corrections](RESULTS.md)

Large benchmark artifacts use Git LFS. After cloning, run `git lfs install`
and `git lfs pull` before reproducing artifact-based tests. The source, papers,
working-style demo and smaller results are ordinary Git files.

A runnable, conservative research engine for bounded five-line-bundle heterotic
searches on favourable CICY threefolds. It uses exact ambient topology, bundle
algebra, necessary physics filters, separate reference and hierarchical searches,
and replayable JSON artifacts. It does not certify a downstairs MSSM.

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[numeric,dev]'
.venv/bin/python -m string_sm_sat.cli doctor
.venv/bin/python -m pytest -q
.venv/bin/python scripts/reproduce_known_model.py
.venv/bin/python scripts/benchmark.py --K 1 --gamma 2
```

The current workspace already has this environment. Exact core arithmetic and
basic scans need only Python; numerical witnesses and algebraic root isolation
use the optional scientific packages. Exact installed versions are recorded in
`requirements-lock.txt`. No Mathematica or external cohomology package is needed.

The golden X7447 model reproduces both indices -12, matching tangent/bundle c2,
an exact rational slope witness, and its published cohomology **for the generic
smooth family** using explicit Koszul map certificates. Recomputed topology
agrees with the published record for all 68 favourable CICYs (c2 68/68, Euler
68/68).

For X7862 with Gamma=2 the scans give 0 survivors at K=1 (`UNSAT_BOUNDED`, and
the whole 43,046,721-state domain has been replayed by an independent
enumerator), then 120 summand-canonical survivors in 5 ambient-row orbits at
K=2, 168 in 7 at K=3, and 240 in 10 at K=4, K=5, K=6 and K=7 — the same set in
all four. Every one of those orbit sets equals the published Oxford GUT catalog
exactly inside the corresponding charge box, and at K>=4 that is the complete
published catalog for this geometry and symmetry order. For Gamma=4 at K=5 the
scan reproduces all 58 published models exactly. The stability from K=4 to K=7
is recorded as empirical saturation, not as a theorem.

At h^{1,1}=5 the same machinery reproduces the X7447 catalog: K=1 is
`UNSAT_BOUNDED` (and its whole 3,486,784,401-state domain has been replayed
independently), then K=2, K=3 and K=4 give 56, 87 and 93 ambient-row orbits,
each exactly equal to the published models inside that box. All three counts
were predicted from the catalog before the runs. At K=4 that is the complete
published {7447, Gamma=2} catalog, all 93 models.

**Searches with no charge cutoff.** The slope condition forces every model into
`p^perp` for a primitive positive integer `p`, and on slices with
`(sum p)^2 > (h-1)|p|^2` the anomaly condition bounds every charge by an
explicit radius. The admissible column pool is then a finite exact set with no
`K` in it, so the search exhausts that slice over *all* integer charges:

```bash
.venv/bin/python scripts/slice_certificate.py --p 1,1,1,1 --gamma 2 --output benchmarks/x7862/slice-1111-gamma2.json
```

On X7862 with Gamma=2, 425 of the 469 such slices with `p` entries up to 10 come
back `UNSAT_SLICE_UNBOUNDED` — provably empty whatever the charges — in 37
seconds total. See `docs/exact_obstructions.md` S1-S2 for the proofs and for the
precise statement of what remains open. All five K=2 orbits have exact
interior slope witnesses; four satisfy generic upstairs full-spectrum conditions.
Equivariance, complete gauge group, and the cohomology on a specified
symmetry-invariant family remain UNKNOWN, so no model is certified.

Two slope rules are selectable. `--slope-rule box` is the published finite
coefficient-box test; `--slope-rule span` decides the same obstruction with no
coefficient bound and prunes at every branch depth. The box rule keeps exactly
one spurious ambient-row orbit at K=3 and again at K=4, which the complete rule
rejects with an explicit integer witness, so `span` is the recommended setting;
see `docs/slope_obstruction_note.md`. It is also the faster of the two once the
dual decision is used (K=4: 28.8 s span versus 36.7 s box).

**Downstairs standard models (Phase 9).** `physics/equivariance.py` and
`physics/wilson_line.py` implement the descent to the quotient `X/Gamma` and the
Wilson-line breaking `SU(5) -> SU(3)xSU(2)xU(1)`. Against the published
standard-model database (2,113 records) every upstairs quantity is recomputed and
matches, and of the 1,948 records carrying complete equivariant data all 1,948
charged downstairs spectra are reproduced exactly:

```bash
.venv/bin/python scripts/parse_standard_models.py
.venv/bin/python scripts/reproduce_standard_model.py --cicy 7862 --table
```

The Gamma-representation content of the upstairs cohomology is no longer taken
from the database: `physics/equivariant_cohomology.py` computes it from the
explicit group action, by the Gamma-equivariant Koszul alternating sum with
Bott/Kuenneth ambient characters. Checked against the published tables on all
13 geometries that carry downstairs models, comparing all four degrees of every
table: 2,012 models, **27,821 tables, all exact**. (The published tables are raw
characters of the lift; the equivariant structure enters only when the spectrum
is formed. An earlier comparison applied it to our side and misreported 694
vector-like tables as relabellings.)

```bash
.venv/bin/python scripts/parse_symmetries.py
.venv/bin/python scripts/compute_equivariant_cohomology.py --cicy 7862
```

Individual `H^q` are resolved either by the collapse of the Koszul complex or,
failing that, by equivariant map ranks — the differential preserves isotypic
components, so its rank splits character by character. That covers the
vector-like Higgs sector as well, and **all 22 published X7862 downstairs models
have their complete charged spectrum derived from first principles**.

With that, the pipeline searches rather than verifies:

```bash
.venv/bin/python scripts/search_standard_models.py --certificate benchmarks/x7862/k5-gamma4-span.json --symmetry 5
```

From the 58 ambient-row orbits of our own exhaustive `|Gamma|=4`, `K=5` scan: 26
are rejected because some `L_a` is not Gamma-equivariant, and **21 admit a
three-family, exotic-free MSSM with a Higgs doublet pair**. All 10 published
orbits are recovered; the other 11 are recorded as *candidates*, since the
published standard-model database describes itself as "a partial scan" and our
acceptance is exactly three conditions. See `docs/equivariant_cohomology.md` and
`docs/downstairs_descent.md`.

Useful commands:

```bash
.venv/bin/python -m string_sm_sat.cli search --geometry 7862 --K 3 --gamma 2 --slope-rule span --output benchmarks/x7862/k3-gamma2-span.json
.venv/bin/python scripts/independent_replay.py --geometry 7862 --K 1 --gamma 2 --compare benchmarks/x7862/k1-gamma2-box.json --output benchmarks/x7862/k1-independent-replay.json
.venv/bin/python scripts/parse_published_catalog.py
.venv/bin/python scripts/compare_catalog.py benchmarks/x7862/k3-gamma2-span.json --output benchmarks/x7862/k3-published-catalog-comparison-span.json
.venv/bin/python scripts/catalog_topology_audit.py
.venv/bin/python -m string_sm_sat.cli golden --output benchmarks/x7447/golden.json
.venv/bin/python -m string_sm_sat.cli verify-candidate benchmarks/x7447/golden.json
.venv/bin/python -m string_sm_sat.cli cohomology --geometry 7447 --charges -2 -2 2 2 0 --generic --output benchmarks/x7447/cohomology.json
.venv/bin/python -m string_sm_sat.cli verify-cohomology benchmarks/x7447/cohomology.json
.venv/bin/python scripts/benchmark.py --K 2 --gamma 2
.venv/bin/python scripts/compare_published.py benchmarks/x7862/k2-gamma2-current.json --output benchmarks/x7862/k2-comparison.json
.venv/bin/python scripts/certify_tetraquadric_stability.py
```

Checkpoints resume automatically and refuse mismatched code or data. To rerun
with changed source, choose a new CLI checkpoint/output path; retain the old
artifact. `--max-roots` stops at a deterministic checkpoint boundary. `--workers 2`
uses independent roots, with deterministic output. Larger scans require a pilot,
resource estimate and documented escalation; the benchmark wrapper stops at K=2.

Search outcomes are `SAT_BOUNDED` (never yet emitted), `UNSAT_BOUNDED`,
`UNKNOWN_BOUNDED`, and `UNSAT_UNBOUNDED`. The last is emitted only by the exact
index-divisibility obstruction, which holds for every K: for example X7447 with
|Gamma|=5 returns it immediately, and the published catalog lists no models
there either.

`verify-search` independently replays tiny domains, with a default one-million
ordered-state cap. The full tetraquadric boxes exceed that cap; the K=1 box is
instead replayed in full by `scripts/independent_replay.py`, which shares no
search logic with the package. Their search
summaries are auditable exhaustive software runs, not independently replayed
large-domain formal proofs. Tiny nonempty restricted-column domains are covered
by differential and certificate tests.

See `STATUS.md`, `RESULTS.md`, and `docs/` for precise scope, source discrepancies,
certificate semantics, mathematical derivations, remaining work and benchmarks.
Raw scientific downloads are immutable and SHA-256 manifested; `fetch_data.py`
acquires them and `convert_data.py` rebuilds selected Oxford geometry records.

**The superpotential (steps 2-6).** `physics/selection_rules.py` decides the
U(1)^4 selection rule with singlet insertions exactly — membership in the monoid
of available singlet charges, a network-flow problem with no bound on the
insertion order. It reproduces every one of the thirteen operator tables of the
published standard-model database for all 2,012 complete models (Yukawa, mu,
Higgs mass, R-parity violation, proton decay, singlet superpotential, D- and
FI-terms, and the Kahler operators), and shows 954 of 2,007 published down-type
Yukawa tables to be internally inconsistent. `physics/yukawa.py` evaluates
leading-order couplings as genuine cohomological triple products, restricted to
the Gamma-isotypic components, with an exact Gamma-covariance self-test:

```bash
.venv/bin/python scripts/yukawa_selection_benchmark.py
.venv/bin/python scripts/operator_benchmark.py
.venv/bin/python scripts/kahler_benchmark.py
.venv/bin/python scripts/leading_order_yukawa.py
```

**The eleven additional models (steps 1, 3-5).** All eleven lie outside the
published scan's own stated domain (`scripts/absence_resolution.py`). Their
Yukawa sectors and dangerous operators, over every accepted configuration, and a
logical ranking with the ten published orbits as the baseline:

```bash
.venv/bin/python scripts/audit_candidates.py --include-published --all-configurations --output benchmarks/x7862/configurations-all.json
.venv/bin/python scripts/candidate_yukawa.py --manifest benchmarks/x7862/configurations-all.json --out benchmarks/x7862/yukawa-all-configurations.json
.venv/bin/python scripts/rank_candidates.py
```

No orbit on X7862/(Z2 x Z2), published or new, is a strong candidate; see
`docs/candidate_ranking.md`. Physical Yukawas and supersymmetry breaking are
documented as open ingredients (`docs/physical_yukawas.md`,
`docs/supersymmetry_breaking_scope.md`), not computed.

**Paper.** `paper/main.tex` is a full write-up of the methods and results; build
with `tectonic paper/main.tex`.

**All 68 favourable CICYs (Phase 8).** `scripts/phase8_suite.py` runs the
exhaustive search on every (geometry, |Gamma|) key of the published GUT catalog
and compares with the catalog inside the box: 271 runs (K = 1 on all 110 keys,
K = 2 on the 101 keys with h11 <= 5, K = 3 on the 60 keys with h11 <= 4). **No published model inside a box is ever
missed**: at K = 2 all 9,016 are recovered. Extra orbits of ours occur on 11
runs, mostly on geometries with d_ijj != 0; `scripts/phase8_extras.py` classifies
them with exact tools (a Polya hierarchy of sign certificates, and an exact
Groebner/interval decision of interior slope zeros). One of them is a
poly-stable, anomaly-free, correct-index GUT model on CICY 5256 (= 5301 = 5452),
|Gamma| = 4, charges |k| <= 2, certified by an exact real-algebraic witness and
absent from the published catalog; see `docs/phase8_suite.md`.
