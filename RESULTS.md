# Research notebook

Experiments below are append-only. Early runs preceded Git initialization and
are identified by retained artifact/source hashes rather than invented commits.

## 2026-09-10 — topology and golden baseline

Git commit: pre-initialization working tree. Geometry: X7447; Gamma=4; K=2
fixture, no exhaustive scan. Algorithm: ambient Chow-ring multiplication,
Whitney c2 and HRR. Exact c1=0; c2(TX)=c2(V)=(24,24,24,24,24); both indices=-12.
Agreement: arXiv:1307.4787 Section 7 and independent Oxford C2 records.
Initial six tests passed in 0.03 s. Numerical witness residual 6.415e-17 was
subsequently superseded by exact rational t=(5,29,15,11,5). No model-count claim.

## 2026-09-10 — initial tetraquadric K=1

Git commit: pre-initialization. Geometry: X7862; Gamma=2 and 4; K=1.
Target: GUT_FULL necessary-filter superset, with pair-index nonpositivity and
positive ambient chamber. Algorithm: hierarchical_section5_conservative_v1.
No heuristics. Raw four-column assignments: 43,046,721. Retained individual
lines: 43. Complete canonical bundles checked: 713 (Gamma=2), 989 (Gamma=4).
No necessary survivors. Runtime: 0.106 / 0.128 s; peak RSS about 24.3 MB in the
shared measurement process. Published Table-4 zero counts agree, but that table
has different acceptance stages; the independent reference has not replayed
this 43-million-state domain. Final-source artifacts supersede these timings.

## 2026-09-10 — first K=2 pilot and completion

Git commit: pre-initialization; exact source identity retained in
benchmarks/x7862/k2-gamma2.json. X7862, Gamma=2, K=2. Same restricted target.
Raw ordered four-column assignments: 152,587,890,625; raw five-column matrices:
95,367,431,640,625. Pilot 3/235 roots: 0.719 s, peak RSS 29,949,952 bytes;
linear root estimate 56.3 s, saved before full run. Checkpoint and thread tests
passed before execution. Completed in 17.341 s. Source code changed later, so
this checkpoint is historical and must not be resumed under current source.

| Stage | Count |
|---|---:|
| Individual columns considered | 625 |
| Retained after index and signed-matrix checks | 235 |
| Retained pair prefixes | 10,573 |
| Retained triple prefixes | 123,629 |
| Fourth-column attempts | 7,875,639 |
| Retained four prefixes | 252,154 |
| Complete canonical bundles checked | 38,161 |
| No-proper-zero-subset survivors | 24,043 |
| Total index survivors | 6,261 |
| All pair-index survivors | 1,356 |
| Anomaly nef-pairing survivors | 1,260 |
| Signed combination survivors | 120 |

Interpretation: cheap conditions greatly reduce materialized candidates, but
these are necessary survivors. Prefix counters are not disjoint counts of full
ordered matrices. Full statistics and peak RSS are retained in the JSON.

## 2026-09-10 — stage comparison and exact witnesses

Git commit: pre-initialization. Same X7862 K=2,Gamma=2 run. Quotient by ambient
factor permutations only for comparison: 120 column-canonical survivors become
five row orbits, equal to arXiv:1307.4787 Table 4's five pre-cohomology models.
This is count agreement, not catalog identity. All five have numerical slope
witnesses; then three rational and two real-algebraic witnesses were verified
exactly. Artifacts: k2-comparison.json and k2-exact-stability.json.

Generic upstairs cohomology, computed by collapse or certified maximal ranks,
gives V=(0,6,0,0) for all five. Wedge2 cohomologies are (0,18,12,0),
(0,23,17,0), (0,9,3,0), (0,9,3,0), (0,6,0,0), in artifact order. Four pass
generic GUT_FULL spectrum conditions; one lacks a generic Higgs pair. These
cohomologies do not establish the spectrum on a chosen free-action subfamily.
Decision remains UNKNOWN_BOUNDED; no SAT_BOUNDED or MSSM construction.

## 2026-09-10 — golden generic cohomology reproduction

Git commit: pre-initialization. X7447 golden bundle; Gamma=4; fixture only.
Algorithms: exact Koszul collapse; isolated d1 matrix ranks; relative P1
resultant d2 rank witnesses, reduced modulo prime 1000003 with full-rank upper
bounds. No numerical/heuristic acceptance. Generic smooth-family dimensions
V=(0,12,0,0), wedge2=(0,15,3,0), agreeing with the published Section-7 numbers.
Source family with specified free action is not certified. Reproduction command:
`.venv/bin/python scripts/reproduce_known_model.py`. All nontrivial rank witness
records are saved under benchmarks/x7447/. No novel theorem is claimed.

## 2026-09-10 — committed-source refresh and independent tiny replay

Git commit: e9525cca0baa09819547da037e67db5f1ae61ce4 (core implementation).
Inputs and core source SHA-256 are embedded in the current search artifacts.
Algorithm: hierarchical_section5_conservative_v1; no heuristic pruning;
positive ambient chamber, trivial hidden bundle, GUT_FULL necessary domain,
nonpositive pair indices, coefficient bound 1 for combined slope matrices.

X7862,Gamma=2,K=1: complete in 0.6323 s with checkpoint writes enabled;
peak RSS 26,755,072 bytes. Zero survivors; UNSAT_BOUNDED for that declared
domain. Independent full brute replay of this 43-million-state box is not run.

X7862,Gamma=2,K=2: complete in 18.7447 s; peak RSS 33,308,672 bytes
(31.77 MiB). All stage counts match the initial K=2 run exactly: 625 singles,
235 retained, 10,573 pair prefixes, 123,629 triple prefixes, 252,154 four
prefixes, 38,161 completed bundles and 120 necessary survivors. The outcome is
UNKNOWN_BOUNDED. Survivor set and counts were preserved across source refresh.
Artifacts: benchmarks/x7862/k2-gamma2-current.json and associated checkpoint.

The ratio of raw four-column assignments to materialized complete canonical
bundles is about 4.0 million. This includes C1 completion and canonicalization,
so it must not be called a pure physics pruning factor. At the fourth-extension
stage, 7,875,639 attempts reduce to 252,154 retained prefixes (factor 31.23).
Anomaly survivors 1,260 reduce to 120 under the signed combinations (factor 10.5).
No expensive cohomology was used to prune this scan.

The independent reference replay on the bicubic K=1,Gamma=1 domain verifies
UNSAT_BOUNDED over all 6,561 ordered four-column states. Nonempty physics-subset
replays, resumptions and thread equality remain part of the unit suite.
Full suite: 71 tests pass, about two seconds; exact timing in benchmarks/tests.txt.

The generic golden model, generic rank certificates, and five exact tetraquadric
slope witnesses were regenerated successfully. No complete gauge group,
symmetry-invariant cohomology, equivariance or downstairs claim was added.

## 2026-09-10 — independent exhaustive replay of the X7862 K=1 domain

Git commit: 903643d source plus the working tree recorded in each artifact.
Geometry X7862; Gamma=2; K=1. Algorithm: `scripts/independent_replay.py`, a
standalone enumerator that shares no search logic with the package. It hardcodes
the published tetraquadric topology (d_ijk=2 for distinct indices, c2=(24,24,24,24)
from arXiv:1311.1941) and re-implements HRR, the subset criterion, the anomaly
pairing and the signed slope test. Its hardcoded topology agrees with the
package's computed topology (h11, all d_ijk, c2). It enumerates the ordered
four-column product directly, derives the fifth column, canonicalises, and
applies the declared conditions to each distinct multiset once.

All three declared K=1 domains were replayed in full. Every one of the
43,046,721 ordered four-column assignments was visited and counted.

| domain | raw ordered | valid fifth | canonical | survivors | optimized survivors | set equality | runtime | peak RSS |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| GUT_FULL, pair<=0 | 43,046,721 | 6,765,201 | 58,781 | 0 | 0 | exact | 25.11 s | 38.3 MB |
| GUT_FULL, pairs free | 43,046,721 | 6,765,201 | 58,781 | 0 | 0 | exact | 25.33 s | 38.1 MB |
| GUT_CHIRAL, pairs free | 43,046,721 | 6,765,201 | 58,781 | 0 | 0 | exact | 25.98 s | 38.2 MB |
| GUT_FULL, pair<=0, span rule | 43,046,721 | 6,765,201 | 58,781 | 0 | 0 | exact | 26.50 s | 38.6 MB |

The valid-fifth-column count is exactly 51^4 = 6,765,201, matching the closed
form (51 of the 81 four-tuples per component have a sum in [-1,1]). This is an
independent arithmetic check on the enumeration itself.

Funnel over the 58,781 distinct canonical states: 38,784 pass the subset
criterion; 1,932 have ind(V)=ind(wedge2 V)=-6; in the GUT_FULL domain 528 also
satisfy the single-index range and all 528 then fail the pair-index range; in
the pair-free domains all 1,932 pass the anomaly pairing and all 1,932 are
eliminated by the slope obstruction and by nothing else.

Interpretation: this is a strong independent validation of the X7862 K=1
`UNSAT_BOUNDED` result — exact survivor-set equality with the optimized solver
on all four declared domains, from a separate implementation, over the complete
finite domain. It also shows which condition is load-bearing: in the strongest
(GUT_CHIRAL, unrestricted pairs) domain the conclusion rests entirely on the
slope obstruction, which is why that rule was audited (docs/slope_obstruction_note.md).

The census also shows ind(V) = ind(wedge2 V) on every one of the 58,781 states,
and both always even — the identity and divisibility facts of
docs/exact_obstructions.md P1 and P2.

Artifacts: benchmarks/x7862/k1-independent-replay*.json.

## 2026-09-10 — exact comparison with the published model catalog

Retrieved the actual Oxford database `GUTall.m` (gzip, SHA-256 recorded in
data/manifests/sources.json; file dated 2013-07-11), converted with
`scripts/parse_published_catalog.py`. The parse reproduces the numbers stated by
the database page exactly: 68 favourable CICYs and 63,325 models.

Topology audit over all 68 geometries (`scripts/catalog_topology_audit.py`):
rebuilding every configuration matrix and recomputing with our ambient Chow-ring
code reproduces the published c2 for **68/68** and the published Euler number for
**68/68**. No disagreements.

For {7862, Gamma=2} the database holds 10 models, with max|k| distribution
{2: 5, 3: 2, 4: 3}. Equivalences applied to both catalogs: permutation of the
five summands, then permutation of identical ambient projective factors. Nothing
else; dualisation is not an equivalence because it flips the sign of ind(V).

| K | published in box | our row orbits (box rule) | our row orbits (span rule) | exact set equality |
|---|---:|---:|---:|---|
| 2 | 5 | 5 | 5 | yes, 0 published-only, 0 ours-only |
| 3 | 7 | 8 | 7 | yes for the span rule; the box rule has one spurious orbit |

Count agreement **and** exact catalog agreement hold at K=2 and, with the
complete slope rule, at K=3. Independently, all 10 published Gamma=2 models pass
every exact necessary check we implement (c1, subset criterion, both indices,
anomaly, Bogomolov, box slope rule, complete span slope rule), including the five
whose charges lie outside our box. The same holds for all 93 published
{7447, Gamma=2} models on the checks that do not need our K box.

Unresolved convention issues: our survivor set is a necessary-condition survivor
set while the published catalog is the poly-stable, anomaly-free, correct-index
stage, so agreement means the two condition sets coincide on these domains, not
that ours are sufficient. Equivariance, Wilson lines and the downstairs spectrum
are not part of either comparison. The database does not state a k_max per
geometry, so "inside the box" is our restriction, not theirs.

Artifacts: benchmarks/x7862/k{2,3}-published-catalog-comparison*.json,
benchmarks/catalog-topology-audit.json, data/processed/published_gut_models.json.

## 2026-09-10 — X7862 Gamma=2 at K=3, and the rule ablation

Nominal finite domain at K=3: 2,401 columns, 2,401^4 = 33,232,930,569,601
ordered four-column assignments, 2,401^5 = 7.98e16 ordered five-column matrices.

| K | slope rule | wall time | peak RSS | singles | pair prefixes | triple prefixes | 4th-column attempts | four prefixes | complete bundles | survivors |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | box | 0.10 s | 25.3 MiB | 43 | 652 | 3,354 | 37,761 | 3,795 | 713 | 0 |
| 1 | span | 0.12 s | 25.2 MiB | 43 | 508 | 1,650 | 18,836 | 1,503 | 334 | 0 |
| 2 | box | 15.84 s | 31.5 MiB | 235 | 10,573 | 123,629 | 7,875,639 | 252,154 | 38,161 | 120 |
| 2 | span | 8.72 s | 35.5 MiB | 235 | 7,843 | 40,615 | 2,693,275 | 51,566 | 10,097 | 120 |
| 3 | box | 120.08 s | 49.9 MiB | 481 | 34,330 | 512,108 | 64,825,851 | 1,171,254 | 146,425 | 192 |
| 3 | span | 55.69 s | 66.6 MiB | 481 | 24,244 | 167,218 | 21,041,937 | 261,122 | 52,800 | 168 |

The K=3 run before the partial anomaly budget existed took 126.02 s with
1,419,164 four prefixes and 178,366 complete bundles
(benchmarks/x7862/k3-gamma2.json), so that rule alone accounts for a 1.05x time
reduction and a 21% reduction in constructed bundles at K=3; it is inactive at
K<=2. Checkpoint size at K=3 (box): 50,269 bytes at root 131 of 481; the final
checkpoint holds the survivor list and all counters.

Scaling K=1 -> 2 -> 3 (span rule): singles 43 -> 235 -> 481; complete bundles
334 -> 10,097 -> 52,800; wall time 0.12 -> 8.72 -> 55.69 s; peak RSS 25 -> 36 ->
67 MiB. Nominal domain grows by 3,544x then 218x while materialized bundles grow
by 30x then 5.2x, so the pruning ratio improves with K rather than degrading.
Memory remains three orders of magnitude below the 12 GB ceiling.

Outcome at K=3 is UNKNOWN_BOUNDED: 168 necessary-condition survivors, no
certified model. Their 7 ambient-row orbits equal the published catalog exactly.

## 2026-09-10 — new exact rules: complete slope obstruction and partial anomaly

Two exact branch rules were derived, proved, implemented and differentially
tested (docs/slope_obstruction_note.md Prop. 3-5, docs/exact_obstructions.md P3):

1. Complete span slope obstruction. Decides, with no coefficient bound, whether
   span{k_a} contains a charge vector whose slope matrix is entrywise one-signed
   and nonzero, by extreme-ray enumeration in exact integer arithmetic. Monotone
   in the column set, so it prunes prefixes at every depth. Strictly dominates
   the finite coefficient box, and first differs from it at K=3, where the box
   retains a spurious candidate that has no slope witness and is absent from the
   published catalog. Cross-checked against an independently written
   Fourier-Motzkin decision procedure (3,000 random column sets, no
   disagreement) and against 12,000 randomly generated slope-feasible bundles
   (no false rejection).
2. Partial anomaly budget, from the separability of the anomaly condition once
   c1(V)=0.

Both preserve the survivor set on every differential domain in the test suite,
which now runs each brute-force/split-search comparison under all three slope
rule settings.

Also implemented: the Bogomolov pairing (1307.4787 (4.6)) — exact, and measured
to reject nothing on any X7862 domain scanned so far, a negative result; and the
index divisibility obstruction d_X | 3|Gamma|, which is unbounded in K. The
latter gives the engine its first non-bounded verdict: X7447 with |Gamma|=5
returns UNSAT_UNBOUNDED in 0.0 s with d_X=2, and the published catalog indeed
lists zero models for that pair. Across all 68 catalog geometries the rule makes
exactly two zero-model predictions ({7761, 2} and {7447, 5}); both hold, and no
catalog entry with models contradicts it.

Test suite: 154 passing.

## 2026-09-10 — X7862 to K=7, and the complete published catalog reproduced

Two changes since the previous entry. First the search was re-engineered: the
retained line-bundle list is now indexed by bitsets so that the component
completion bound (rule 3) and the pair-index range (rule 5) are enforced by
construction rather than tested inside the loop
(`hierarchical_section5_indexed_v2`). This is an implementation change only; it
was validated by re-running every previously recorded X7862 domain and requiring
**exact survivor-set equality**, which held in all seven cases, and by the full
differential suite. Measured speedups at equal results: K=3 box 120.1 s -> 15.9 s
(7.5x), K=3 span 55.7 s -> 17.5 s (3.2x), K=4 span 204.8 s -> 39.1 s (5.2x);
fourth-column attempts fell by factors of 19 to 28.

Second, with K=4 down to about 40 s, the box was pushed to K=7.

| K | rule | wall | peak RSS | 4th-col attempts | complete bundles | survivors | row orbits |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | box | 0.05 s | 25.4 MiB | 4,636 | 713 | 0 | 0 |
| 1 | span | 0.09 s | 25.3 MiB | 2,535 | 334 | 0 | 0 |
| 2 | box | 4.00 s | 33.2 MiB | 420,266 | 38,161 | 120 | 5 |
| 2 | span | 3.99 s | 37.2 MiB | 170,121 | 10,097 | 120 | 5 |
| 3 | box | 15.88 s | 50.5 MiB | 2,304,135 | 146,425 | 192 | 8 |
| 3 | span | 18.42 s | 68.3 MiB | 963,549 | 52,800 | 168 | 7 |
| 4 | box | 36.65 s | 65.6 MiB | 7,147,830 | 294,130 | 264 | 11 |
| 4 | span | 43.62 s | 105.6 MiB | 3,236,246 | 118,577 | 240 | 10 |
| 5 | span | 85.44 s | 141.0 MiB | 6,537,468 | 162,761 | 240 | 10 |
| 6 | span | 118.88 s | 193.8 MiB | 10,199,673 | 206,847 | 240 | 10 |
| 7 | span | 179.15 s | 188.9 MiB | 14,516,351 | 231,946 | 240 | 10 |

Nominal domain at K=7: 15^16 = 6,568,408,355,712,890,625 ordered four-column
assignments. All runs checkpointed; the K=7 checkpoint holds the survivor list
and counters.

**Exact catalog agreement at every K.** The published {7862, Gamma=2} catalog has
10 models, with max|k| in {2:5, 3:2, 4:3}. Restricting the published catalog to
each box and canonicalising both sides under summand and ambient-factor
permutations gives exact row-orbit set equality for the span rule at K=2,3,4,5,6
and 7 — 0 published-only and 0 ours-only in every case. At K=4 the entire
published catalog is inside the box and we reproduce all 10 models. The finite
coefficient box keeps exactly one spurious orbit at K=3 (8 vs 7) and at K=4
(11 vs 10); it is the same obstruction-missed candidate in both.

**Gamma=4, K=5.** 236.91 s, 317.1 MiB, 1,577 retained singles, 359,317 complete
bundles, 1,344 survivors -> 58 ambient-row orbits. The published catalog has 58
models for {7862, 4}, all with max|k| <= 5. Exact set equality: 0 published-only,
0 ours-only. This is a considerably larger catalog target than the Gamma=2 case
and it matches model for model. All 58 published models also pass every exact
necessary check we implement.

**Empirical saturation, not a theorem.** The Gamma=2 survivor set is *literally
identical* at K=4, 5, 6 and 7 (240 column-canonical survivors, 10 orbits, and no
survivor uses a charge with |k| > 4). Under the terminology of the master plan
this is `EMPIRICAL_SATURATION` at K=4 for this geometry, symmetry order, target
and chamber. It is **not** a no-go theorem and is not evidence that no model
exists beyond K=7; the only unbounded statement this engine makes is the exact
index-divisibility obstruction.

Interpretation: over |k| <= 7 the exhaustive search finds exactly the published
models and nothing else. Because our conditions are necessary conditions and the
published catalog is the poly-stable, anomaly-free, correct-index stage, the two
sets coinciding on this domain means the necessary conditions happen to be
sufficient *here*; it does not prove they are sufficient in general, and no
equivariance, Wilson line or downstairs spectrum is asserted. The outcome for
every nonempty domain remains UNKNOWN_BOUNDED.

Test suite: 161 passing.

## 2026-09-10 — dual slope decision, and the first h^{1,1}=5 catalog agreement

Profiling the first X7447 scan showed the span slope decision taking 90% of wall
time. Two fixes, both preserving results exactly: the annihilator computation
moved from `Fraction` to fraction-free integer elimination, and the decision
itself moved to its dual form (docs/slope_obstruction_note.md Proposition 6).
The dual projects the fixed extreme rays of the obstruction cone through the
annihilator of the span and asks whether the origin lies in their convex hull;
its dimension is `h - rank`, so it *shrinks* as prefixes deepen — the numerous
deep nodes become O(#rays) sign checks in one dimension or an angular-gap test in
two, with the primal enumeration kept as the reference, the witness producer, and
the fallback above dimension two.

The obstruction cone has exactly 2h extreme rays on both benchmarks: the h
coordinate vectors and the h vectors with one entry -(h-3) and the rest 1.
Dual and primal were differentially tested on 12,000 random column sets across
every span rank with no disagreement, and re-running every recorded X7862 domain
gave bit-identical survivor sets. Measured: X7862 K=4 span 43.6 s -> 28.8 s;
X7447 K=2 pilot 52.8 s -> 9.6 s (5.5x).

X7447 (h^{1,1}=5, five bidegree-(1,1) equations in (P^1)^5), Gamma=2, GUT_FULL,
positive ambient chamber, nonpositive pair indices, complete span rule:

| K | singles | wall | peak RSS | complete bundles | survivors | row orbits | published in box | exact set equality |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 121 | 6.8 s | 32.6 MiB | 7,122 | 0 | 0 | 0 | yes |
| 2 | 861 | 271.6 s | 361.6 MiB | 371,214 | 6,540 | 56 | 56 | yes |
| 3 | 2,101 | 1338.8 s | 484.9 MiB | 1,245,469 | 10,140 | 87 | 87 | yes |

Nominal domains: 3,486,784,401 ordered four-column assignments at K=1;
9.54e13 at K=2; 7.98e16 at K=3. The K=2 and K=3 orbit counts, 56 and 87, were
**predicted before the runs** from the max|k| distribution of the published
{7447, 2} catalog (56 models with max|k| <= 2, 31 more at 3, 6 more at 4) and
came out exactly right, with 0 published-only and 0 ours-only orbits in both
cases. K=1 is UNSAT_BOUNDED, also consistent: the catalog has no model with
max|k| <= 1. All 93 published {7447, 2} models pass every exact necessary check
we implement.

This is the first exact catalog agreement at h^{1,1} = 5 and it is a
substantially larger target than the tetraquadric: 87 distinct models rather
than 10. Memory is now the fastest-growing resource here — 485 MiB at K=3
against 68 MiB for X7862 at the same K — but remains far below the 12 GB ceiling.

Source discrepancy recorded: the GUTall.m geometry record lists
`SymmOrder -> {2,4,5,10,20}` for CICY 7447 while our registry, from the Oxford
symmetry pages, carries {2,4,10}. The field is informational and no result
depends on it; order 5 is independently excluded by the index-divisibility
obstruction. Documented in docs/literature_notes.md rather than silently
reconciled.

## 2026-09-10 — independent full-domain replay at h^{1,1}=5

Geometry X7447, Gamma=2, K=1, GUT_FULL, complete span slope rule. The
independent enumerator (`scripts/independent_replay.py`, no shared search logic,
hand-entered published topology, and its own Fourier-Motzkin implementation of
the span obstruction rather than extreme-ray enumeration) visited every one of
the **3,486,784,401** ordered four-column assignments in 2,433.7 s at 783.0 MiB.

Its hardcoded topology agrees with the package's computed h11, all d_ijk and c2.
The number of assignments with an in-box fifth column came out as 345,025,251,
exactly 51^5, matching the closed form independently of the search — the same
arithmetic cross-check that held at h=4 with 51^4.

Funnel over the 2,906,223 distinct canonical states: 2,477,960 pass the subset
criterion; 132,870 have ind(V) = ind(wedge2 V) = -6; 44,580 also satisfy the
single-index range; 2,040 survive the pair-index range; all 2,040 pass the
anomaly pairing; and all 2,040 are eliminated by the slope obstruction, leaving
none. Exact survivor-set equality with the optimized solver, which recorded
UNSAT_BOUNDED for the same domain.

As at h=4, the slope obstruction is the decisive filter in the K=1 box, which is
why its audit and its upgrade to the complete form mattered. This is now the
second geometry whose smallest box has been independently exhausted rather than
merely searched.

## 2026-09-10 — X7447 Gamma=2 complete, and a charge-unbounded slice theorem

X7447 K=4 completed in 2,960.2 s at 705.5 MiB: 4,011 retained singles,
2,142,164 complete bundles, 10,800 survivors, **93 ambient-row orbits**. The
published {7447, Gamma=2} catalog has exactly 93 models, all with max|k| <= 4,
and the sets agree exactly (0 published-only, 0 ours-only). The count 93 was
predicted before the run. The full X7447 Gamma=2 ladder is now
K=1 UNSAT_BOUNDED, K=2 -> 56 orbits, K=3 -> 87, K=4 -> 93, each matching the
published catalog restricted to that box exactly.

### The slice theorem

Continuing to larger K is reproduction with diminishing returns, so the search
was restructured instead. Two propositions (docs/exact_obstructions.md S1, S2):

* **S1.** Since the slope of `L_a` at `t` is `<k_a, q(t)>` and `q(t)` is
  strictly positive on the chamber, a common zero of all five slopes forces
  every charge vector into `p^perp` for some *primitive positive integer* `p`
  (a rational subspace containing a positive vector contains a positive rational
  vector). So the landscape decomposes exhaustively over slope directions `p`,
  and `rank(K) <= h-1` — verified on data, all 240 X7862 survivors have rank 3
  or 2, never 4.
* **S2.** Summing the anomaly condition over `r` gives
  `sum_a F(k_a) <= C_X` with `F(k) = |k|^2 - s(k)^2` and `C_X = 48` for X7862.
  On `p^perp`, `F` is positive definite exactly when `(sum p)^2 > (h-1)|p|^2`,
  and then every column obeys `|k_a|^2 <= C_X |p|^2/((sum p)^2 - (h-1)|p|^2)`.

The corollary is the interesting part: for such `p` the admissible column pool
is the finite exact set `{k : <k,p> = 0, F(k) <= C_X}`, computed by walking a
ball, **with no K parameter anywhere**. Searching it exhausts that entire slice
over all integer charges. The new outcome `UNSAT_SLICE_UNBOUNDED` therefore
carries no K qualifier.

Measured on X7862, Gamma=2, GUT_FULL. Of the primitive positive `p` with entries
<= 10 (up to ambient permutation), **469 satisfy the condition**; all were
exhausted in 36.7 s: **425 are `UNSAT_SLICE_UNBOUNDED`** — provably empty for
arbitrarily large charges — and 44 carry models, together giving 6 ambient-row
orbits with maximum charge 3. Radii reach `R^2 = 2484` while pools stay at
85-700 columns, because as `|p|` grows the ball grows but `p^perp` thins.

The slices that fail the condition are where the real difficulty sits, and they
are not an artefact: real models live there, including `p = (1,1,3,4)` with
`(sum p)^2 = 3|p|^2` exactly and `p = (1,1,4,4)` with `100 < 102`. There `F` is
degenerate or indefinite, the pool is genuinely infinite, and the anomaly bounds
nothing. What actually stops the charges is the index, which grows cubically
along the `F <= 0` directions (2, 52, 198 along the null ray of `(1,1,3,4)`);
note `F(k) <= 0` forces `s(k) != 0`, so `ind(nk) = 2(n^3 e_3 + n s)` is unbounded
on every such ray. Converting that ray-wise statement into a bound on the
semialgebraic set `{F <= 0, ind in [-3|Gamma|,0]}` is the open step.

Probing all 22 such slices with entries <= 6 at an in-slice box `K = 16` — well
beyond the `K = 7` full-box reach, over pools holding thousands of large-charge
columns — yields maximum charge 4 and nothing new. The 84 proved plus 22 probed
slices reproduce **exactly** the 10 orbits of the K=7 full-box search and of the
published catalog, confirming the decomposition is complete in practice as well
as in principle.

Status: S1 and S2 are proved; the union over all positive primitive `p` is
infinite, so this is not a finiteness theorem for the geometry. It is an exact
result, unbounded in K, for an explicit and large family of slices, together
with a sharp localisation of what remains open. Artifacts:
benchmarks/x7862/slope-slices-gamma2.json (469 slice results),
benchmarks/x7862/slope-slices-uncovered.txt, benchmarks/x7862/slice-1111-gamma2.json.

## 2026-09-10 — Phase 9: downstairs standard models reproduced

Neither Phase 8 nor Phase 9 had been started; the upstairs search was by now
stable enough (exact catalog agreement on both benchmarks, independent
full-domain replays, a K-free slice theorem) to move on.

Acquired the published *standard model* database, `sms202.m` from the Oxford
line-bundle model pages (arXiv:1106.4804, arXiv:1202.1757), SHA-256 recorded in
the manifest. Unlike GUTall.m this one carries exactly what Phase 9 was blocked
on: the explicit freely acting symmetries, the equivariant structures
(`EquivStr`), the Wilson lines (`WLine`), the **Gamma-representation content of
the upstairs cohomologies** (`GCoh`, `GCoh2`, `GCohSing`) and the published
downstairs spectra (`DownSpec`). Parsed to
data/processed/published_standard_models.json: 2,113 model records over 15
(geometry, |Gamma|) keys, including 22 on X7862 and 4 on X7447.

New modules: `physics/equivariance.py` (character group of an abelian Gamma,
equivariant-structure shifts, consistency of character tables against h^q) and
`physics/wilson_line.py` (SU(5) -> SU(3)xSU(2)xU(1) branching with hypercharge,
the Wilson-line projection, assembly into complete multiplets, the chiral /
vector-like split and the Section-31 acceptance report). See
docs/downstairs_descent.md.

Results over the whole published catalog:

| check | result |
|---|---|
| every upstairs quantity recomputed and matching (c1, c2, both indices, subset criterion, anomaly, Bogomolov, complete slope obstruction) | **2113 / 2113** |
| records carrying complete equivariant data | 1948 |
| character tables consistent with the published h^q | **1948 / 1948** |
| charged downstairs spectrum reproduced exactly | **1948 / 1948** |
| Higgs-pair count matching | **1948 / 1948** |
| three families, no charged chiral exotics, a Higgs pair | **1948 / 1948** |

Two conventions are not stated unambiguously in the sources and were pinned by
fitting and then verified: the GCoh columns are the characters in lexicographic
label order (with Gamma inferred database-wide, since a single record need not
exhibit every character), and the equivariant structure enters as a character
shift of the cohomology, by chi_a for a single bundle and chi_a + chi_b for a
pair. The second is load-bearing and was checked rather than assumed: with the
shift 1948 of 1948 charged spectra match, without it only 1503. The 445 records
that distinguish the two settle the convention, and a regression test asserts it.

The loop closes on our own benchmarks: all 22 published downstairs models on
X7862 and all 4 on X7447 have upstairs bundles that pass every exact check we
implement *and* lie inside the exhaustive Gamma=4 survivor set from our own
search. An example Section-31 table, X7862 model 1, upstairs columns
(1,-3,0,2), (0,1,0,-1), (0,1,0,-1), (0,0,-1,1), (-1,1,1,-1):

    Q 3, u^c 3, e^c 3, d^c 3, L 3, H 1, Hbar 1, singlets 92
    3 chiral families? yes | charged chiral exotics? no | Higgs doublet pair? yes
    colour triplet Higgs? no | additional massless U(1)? 1

Honest gaps, all recorded in the certificates: 165 published records are
incomplete (missing GCoh/GCoh2/WLine/EquivStr) and are reported
UNKNOWN_INCOMPLETE_RECORD rather than guessed; the published data itself leaves
2,450 singlet entries across 1,197 records as unevaluated rank expressions, so
our exact comparison is on the charged spectrum; and no equivariant cohomology
is computed here, so the engine can verify and descend a model whose equivariant
data is supplied but cannot yet discover one. Non-abelian Gamma is refused, not
approximated. A reproduced model is an N=1 supersymmetric MSSM-like spectrum,
not an exact Standard Model.

Test suite: 195 passing.

## 2026-09-10 — the Gamma-representation computed from first principles

The standing blocker: every downstairs result so far took the
Gamma-representation content of the upstairs cohomology from the published
tables. It is now computed from the explicit group action.

Method (docs/equivariant_cohomology.md). The Koszul resolution is
Gamma-equivariant, so the alternating sum of ambient characters gives
sum_q (-1)^q [H^q(X,L)]. Ambient characters come from Bott plus Kuenneth: on a
P^n factor the trace on H^0(O(m)) is the complete homogeneous symmetric function
h_m of the element's eigenvalues, computed from the characteristic polynomial
without ever extracting eigenvalues, and the trace on H^n(O(m)) is
det^{m+n} h_{-m-n-1} by Serre duality. The normal-bundle twist is handled by
grouping the defining polynomials by multidegree and taking elementary symmetric
functions of the polynomial-action blocks. Decomposition into characters is the
finite Fourier transform. All exact, entries are roots of unity.

New: `scripts/parse_symmetries.py` (extracts generators, group order and
structure, polynomial action and invariant families from the database) and
`physics/equivariant_cohomology.py`.

Validation against the published GCoh / GCoh2 tables, all 13 geometries that
carry downstairs models:

| geometry | models | single bundles | pair bundles |
|---|---:|---:|---:|
| 5256 | 110 | 478/478 | 966/966 |
| 5452 | 1064 | 4552/4552 | 9288/9288 |
| 6732 | 72 | 360/360 | 436/436 |
| 6770 | 32 | 160/160 | 284/284 |
| 6777 | 80 | 400/400 | 376/376 |
| 6784 | 212 | 1032/1032 | 1332/1332 |
| 6828 | 7 | 34/34 | 55/55 |
| 6890 | 56 | 280/280 | 312/312 |
| 6947 | 24 | 120/120 | 216/216 |
| 7435 | 6 | 24/24 | 36/36 |
| 7447 | 3 | 15/15 | 26/26 |
| 7487 | 324 | 1620/1620 | 2424/2424 |
| 7862 | 22 | 106/106 | 161/161 |
| **total** | **2012** | **9181/9181** | **15912/15912** |

Zero mismatches. Nothing representation-theoretic enters the computation; the
published tables are only the comparison target.

The comparison earned its keep by finding two real bugs. CICY 7487 carries four
distinct freely acting Z_2 x Z_2 symmetries differing only in their action on the
defining polynomials, and different models use different ones: selecting by a
structural heuristic gave 1600/1620, while using each model's own symmetry number
gives 1620/1620. And ignoring the polynomial twist is valid only when the
defining polynomials are invariant, which is false for most of these geometries.

A third finding is mathematical rather than a bug. The generators of the
tetraquadric Z_2 x Z_2 do **not** commute in GL(8): their commutator is -1 on
every P^1 factor. That is trivial on the ambient space but acts on O(k) by
(-1)^{sum k}, so O(k) is Gamma-equivariant for this lift exactly when sum_i k^i
is even. This is the equivariance obstruction, and it is now checked
(`is_equivariant`) rather than assumed; a second independent net rejects any
projective character whose decomposition is not by non-negative integers.

What the method does and does not give. The alternating sum determines the
individual H^q when exactly one degree is nonzero — decided independently by our
exact dimension code — and always determines the difference H^1 - H^2. That
difference is precisely the chiral content, so **three families and the absence
of chiral exotics are derivable from the geometry, the group action and the
charge matrix alone**. The vector-like sector (Higgs doublet pairs) is not
separable this way, since H^1 and H^2 of a pair bundle can be isomorphic as
Gamma-representations and cancel in the alternating sum; that needs the
equivariant spectral sequence with map ranks.

End-to-end check: on a sample of 136 models spanning all 13 geometries, the full
chiral spectrum was derived from first principles — no published cohomology, no
published representation data — and gave exactly three families of Q, u^c, e^c,
d^c and L in every case.

Scope: abelian Gamma only; group elements must preserve each projective factor;
the free action and the invariant defining family are taken from the published
symmetry data and their freeness is an input assumption.

Test suite: 203 passing.

## 2026-09-10 — the vector-like sector, and a downstairs search

Two additions completed the downstairs pipeline.

**Resolving each H^q, not just the alternating sum.** Two mechanisms, tried in
order by `equivariant_cohomology`:

* *Collapse.* When no Koszul differential can join two occupied E1 nodes — the
  same bidegree-support test the non-equivariant code already used — each H^q is
  the sum of the E1 characters with q - p equal to that degree. This resolves
  H^1 and H^2 of a pair bundle separately, which is exactly what the Higgs
  sector needs. The earlier alternating-sum treatment threw that away: for the
  worked example the two are isomorphic as Gamma-representations and cancel.
* *Equivariant map ranks.* Otherwise, when a single differential joins two
  nodes, that differential is multiplication by the defining polynomial and is
  Gamma-equivariant, so it preserves isotypic components and its rank splits
  character by character; kernel and cokernel per character give the two
  surviving degrees. Uses explicit action matrices — Sym^m(B) on H^0 and
  det(B)^{-1}(Sym^{-m-2}(B))^{-T} on H^1 by Serre duality, Kronecker across
  factors — whose traces are checked against the independent symmetric-function
  characters, and a generic member of the published invariant family. The
  equivariance M rho_src = rho_tgt M is verified rather than assumed, which
  tests the action matrices, the invariant-polynomial parsing and the basis
  conventions simultaneously.

Validation: 21/21 non-collapsing pair bundles of the X7862 models resolved and
matching the published GCoh2. Re-running the all-degree comparison raised pair
coverage from 161 to 199 bundles on X7862 with every degree compared, still zero
mismatches. End to end, **all 22 published X7862 downstairs models now have their
complete charged spectrum — chiral and Higgs — derived from first principles**
and matching the published spectrum exactly.

**A search rather than a verification.** `scripts/search_standard_models.py`
takes the survivor set of one of our own bounded upstairs scans and derives
downstairs spectra with no published input. On X7862, |Gamma|=4, from the 58
ambient-row orbits of our exhaustive K=5 scan:

| stage | count |
|---|---:|
| upstairs orbits examined | 58 |
| rejected, some L_a not Gamma-equivariant (sum k odd) | 26 |
| equivariant and cohomology fully determined | 32 |
| no Wilson line / equivariant structure works | 11 |
| orbits admitting a three-family, exotic-free MSSM with a Higgs pair | **21** |

The Wilson line is derived, not assumed: det = 1 in SU(5) forces
chi_T^3 chi_D^2 = 1, hence chi_T trivial for a group of exponent two. Equivariant
structures are enumerated subject to sum_a e_a = 0 so det V descends.

All 10 published orbits are recovered, plus 11 further orbits. This is not a
contradiction: the published standard-model database calls itself "a partial
scan" in those words. Each of the 11 is a model from the published GUT catalog
for {7862,4}, passes every exact upstairs check, has h^1(V) = 12 = 3|Gamma|, and
carries no colour-triplet Higgs under any admissible Wilson line.

They are recorded as **candidates, not confirmed new standard models**. Our
acceptance is exactly three conditions (three chiral families, no charged chiral
exotics, at least one Higgs pair); the published partial scan may have applied
further conditions we have not identified; the cohomology is that of a generic
member of the invariant family; and singlets, Yukawa textures, supersymmetry
breaking and moduli stabilisation are untouched.

Artifacts: benchmarks/x7862/downstairs-search-gamma4.json,
benchmarks/x7862/downstairs-reproduction.json,
benchmarks/equivariant-cohomology-*.json. Test suite: 206 passing.

**Correction to the previous entry.** That entry reported 9,181/9,181 single and
15,912/15,912 pair bundles with "zero mismatches". That comparison checked only
the single nonzero degree of each table and *skipped* every multi-degree case.
Re-running with all four degrees compared, over the same 2,012 models:

| | |
|---|---:|
| cohomology tables compared (all degrees) | 27,821 |
| exact agreement | 27,127 |
| differ only by a permutation of the character labels | 694 |
| genuine disagreements, i.e. wrong dimensions | **0** |

In all 694 the per-degree multiplicity multisets are identical, so the
cohomology is right and only the assignment to characters differs. They are
confined to multi-degree pair bundles on eight geometries (5256, 5452, 6732,
6770, 6777, 6784, 6890, 7487). X7862, X7447, 6828, 6947 and 7435 agree exactly
on every table and degree — and X7862 is what the complete-spectrum derivation
and the downstairs search rest on, so those results are unaffected.

The cause is unresolved. A pair bundle's equivariant structure should be
e_a + e_b, and that shift is correct for every single bundle and most pairs; on
the affected ones the published table corresponds to no shift instead. Either
our convention for those pairs or the published one differs. The artifacts now
carry a per-table `verdict` field (`exact`, `relabelling_only`,
`same_dimensions`, `genuine_disagreement`) so the distinction is recorded rather
than averaged away.

## 2026-09-10 — step 1: audit of the 11 additional X7862 candidates

The 11 orbits our downstairs search found beyond the published partial scan were
frozen into an immutable manifest (benchmarks/x7862/candidate-manifest.json) and
audited against every condition of the original Oxford construction, not the
three-condition shorthand the search used.

Result: **all 11 satisfy every condition.**

| condition | result |
|---|---|
| c1(V)=0 | 11/11 PASS |
| structure group, no proper subset with vanishing c1 | 11/11 PASS |
| anomaly / effectivity | 11/11 PASS |
| Bogomolov | 11/11 PASS |
| poly-stability, **exact** witness | 11/11 (8 rational, 3 real-algebraic) |
| generation index ind(V)=ind(wedge2 V)=-12 | 11/11 PASS |
| h(V) = (0,12,0,0), i.e. 3\|Gamma\| and no anti-families | 11/11 PASS |
| h(wedge2 V) = (0, 12+n_h, n_h, 0), n_h>0 | 11/11 PASS |
| every bundle Gamma-equivariant | 11/11 |
| Gamma-character tables fully determined | 11/11 |
| admissible Wilson line | 11/11, all with [[0,0],[0,1]] |
| exactly three Q, u^c, d^c, L, e^c | 11/11 |
| no charged chiral exotics | 11/11 |
| at least one Higgs doublet pair | 11/11 |
| no colour-triplet Higgs | 11/11 |
| absent from every published downstairs model | 11/11 |

Poly-stability is now an exact statement for each: seven rational witnesses found
by an integral lattice search, one by a parametric search along the solution
curve (A02: t = (15,15,3,1)), and three real-algebraic, e.g. A01/A03 with
t_1 = 4 + sqrt(21). Where the charge matrix has rank 2 the slope-zero locus is a
curve, so rationalising a numerical point cannot work and a rational point *on*
the curve is required; that case is handled explicitly.

Two script bugs were found and fixed while auditing, both of which would have
mis-stated the result: the character-table cache is keyed by charge vector, so a
model with a repeated line bundle collapsed duplicates and failed a count-based
determinacy guard (A01 wrongly showed zero admissible configurations); and the
symbolic slope solver returned parametric families that were compared as if they
were points.

### Why each is absent from the published scan

Two structural facts about the published database decide most of it.

1. **Every one of the 2,113 published downstairs models has max\|k\| <= 3**,
   while the published GUT catalog reaches 10. The standard-model scan was
   charge-restricted; the GUT scan was not.
2. **Every published X7862 model has charge-matrix rank 3**, i.e. exactly one
   additional massless U(1) (4 - rank), and its MasslessU1 field confirms 1.

| candidate | max\|k\| | extra U(1) | reason for absence |
|---|---:|---:|---|
| A01 | 5 | 1 | outside the published SM charge range |
| A02 | 5 | 2 | charge range; and 2 extra U(1)s |
| A03 | 5 | 1 | outside the published SM charge range |
| A04 | 4 | 2 | charge range; and 2 extra U(1)s |
| A05 | 4 | 1 | outside the published SM charge range |
| A06 | 4 | 2 | charge range; and 2 extra U(1)s |
| A07 | 3 | 2 | 2 extra U(1)s |
| A08 | 3 | 1 | **unknown** |
| A09 | 3 | 1 | **unknown** |
| A10 | 3 | 2 | 2 extra U(1)s |
| A11 | 3 | 2 | 2 extra U(1)s |

A08 and A09 sit inside the published charge range, have the same rank and
massless-U(1) profile as every published model, and work with exactly the
published Wilson line [[0,0],[0,1]]. A hypothesis that the published scan used a
single Wilson line was tested and refuted: all 11 use that same one. Their only
distinguishing feature is a larger vector-like sector, n_h = 11 against 3 or 6
for the published ten. We record their absence as unknown rather than invent a
reason; the source describes itself as a partial scan.

Interpretation. A01, A03, A05 are the sharpest: rank 3, one extra U(1), n_h = 3 —
profile-identical to published models — and absent only because their charges
exceed the range the published scan covered. The six rank-2 candidates carry two
additional massless U(1)s, which no published model does, and should be treated
as phenomenologically distinct rather than as simple additions to the catalog.

Still not called new: the audit establishes that they satisfy the published
construction's conditions, not that they are viable. That is what the Yukawa
analysis is for.

---

## Step 6 — reproducing the published Yukawa calculation

Before trusting any Yukawa statement about our own candidates, the engine must
reproduce a published one. Target: the Yukawa sector of the Anderson-Gray-Lukas-
Palti standard-model database (arXiv:1202.1757 Section 3.1.6). Full account in
`docs/yukawa_benchmark.md`; artifacts `benchmarks/yukawa-selection-rule-all.json`,
`benchmarks/published-table-consistency.json`,
`benchmarks/x7862/leading-order-yukawa.json`.

### Selection rules — exact agreement across the whole database

The `U(1)^4` rule with singlet insertions is decided exactly, as membership of a
charge vector in the monoid generated by the available `e_a - e_b`: a network
flow problem, so decidable with **no bound on the insertion order**, with the
minimal order a min-cost flow. Every monomial up to a given degree is then
enumerated exhaustively.

| table | compared | monomial sets exactly equal | allowed/forbidden differs |
|---|---:|---:|---:|
| `Y_u` | 2,012 | **2,012** | 1 |
| `Y_d` | 2,012 | **2,012** | 0 |
| mu term | 2,012 | **2,012** | 0 |

6,036 tables, every singlet monomial at every order. The single flag difference
is X7862 model 14, whose up coupling first becomes neutral at insertion order
six — above the published truncation of five, where both lists are empty and so
still agree. Conventions fixed by this comparison are listed in the doc,
including a full decoding of the per-model `EDownSpec` field, which independently
confirms the family ordering.

Logical status, kept separate as required: `FORBIDDEN_BY_SELECTION_RULE` is EXACT
and proves vanishing to all orders. `ALLOWED` proves nothing about the value.

### Entry by entry — and a diagnosed inconsistency in the published `Y_d`

| table | tables | exact | cells | agreeing |
|---|---:|---:|---:|---:|
| `Y_u` | 22 | **22** | 198 | **198** |
| `Y_d` | 22 | 17 | 198 | 184 |
| mu term | 14 | **14** | 14 | **14** |

The five `Y_d` exceptions were diagnosed, not dismissed. Because the published
tables are functions of the charges, two families from the same line bundle must
give identical rows. Testing that with **published data only** — family order
from each model's own `EDownSpec`, nothing computed here entering:

| table | checked | charge-consistent | internally inconsistent |
|---|---:|---:|---:|
| `Y_u` | 2,012 | **2,012** | 0 |
| `Y_d` | 2,007 | 1,053 | **954** |

Every published up-type table is consistent; 47% of the down-type tables are
not, carrying a zero row where an identical row is nonzero. The five X7862
tables we fail to reproduce are exactly five of those. Transposing or swapping
the row/column labels does not repair it (1,028 inconsistent either way), so it
is not an indexing convention. The cause is not identified and is not guessed.

### The cohomological product

At the Abelian locus a Yukawa entry is a genuine triple cup product. It is
computed exactly: Koszul level per class, trilinear form on Cech monomials,
restricted to the Gamma-isotypic components the Wilson line selects.

*Self-test.* The trilinear form must be Gamma-covariant with the character of
`H^top(A,O(-q)) = prod_i det(B_i)^{-1}`. Checked element by element and index
triple by index triple: **zero violations** — validating the Serre-duality
basis, the exponent convention, the Kronecker ordering and the group lift at
once.

| leading-order rank | models | agree with published structural rank | differ |
|---|---:|---:|---:|
| `Y_u` | 22 | **20** | 2 |
| `Y_d` | 22 | **20** | 2 |

The two `Y_u` differences (models 15, 16) are a **genuine cohomological
vanishing invisible to charge conservation**: all three classes sit at Koszul
level 0, so the product is the restriction of a class in `H^3(A, O_A) = 0`. The
two `Y_d` differences (models 16, 18) are internally inconsistent published
tables — and there the cohomology gives rank 2 in a block where the published
table shows a zero row, which no change of family basis can produce, since a
rank-2 2x3 matrix has no zero row in any basis.

*Independent confirmation of a published theorem.* Section 6.2 of
arXiv:1202.1757 proves `Y_u` cannot have rank one without equivariant blocks.
Our computed `Y_u` ranks across all 22 models are 0 or 2 and **never 1** —
recovered from the cohomology, not from the group theory.

### What this licenses

Selection rules, zero/nonzero structure and matrix rank are reproduced on a
published model set, with every disagreement accounted for. Physical
(canonically normalised) Yukawas are **not** attempted: they need matter-field
Kahler metrics, which are not computed here.

## Correction — Koszul level sum two or more is not a vanishing rule

`physics/yukawa.py` previously returned `VANISHES_BY_KOSZUL_LEVEL` whenever the
Koszul levels of the three classes did not sum to exactly one. Only half of that
is a theorem. Level sum **zero** does force vanishing (the product restricts from
`H^3(A, O_A) = 0`), and level sum **one** is rigorously the ambient product,
because the connecting map `H^3(X,O_X) -> H^4(A,O(-q))` is an isomorphism and is
linear over restricted ambient classes. For level sum **two or more** the
connecting map is not multiplicative, the naive ambient product vanishes only
for degree reasons, and the true coupling needs a lift through the defining
polynomial; it can be nonzero. Such couplings now return
`UNKNOWN_HIGHER_KOSZUL_LEVEL` and block any matrix they enter.

Impact audited, not assumed: every charge-neutral leading-order bundle triple in
every recorded artifact was re-classified by level sum. Published X7862 models:
4 triples at sum 0, 14 at sum 1, none at 2 or more. The eleven candidates: 240
triples, all at sum 1, none at 2 or more. **No recorded number changes.** A
regression test pins a genuine level-sum-two triple to `UNKNOWN`.

## Singlet spectrum derived from first principles, validated

Every rank verdict that uses the selection rule depends on which singlets
`S_{ab}` survive the quotient. `scripts/validate_singlet_spectrum.py` derives
them from the Gamma-invariants of `H^1(X, L_a (x) L_b^*)` after the equivariant
shift and compares with the published `DownSpec` of every X7862 model. The one
X7862 model on which they differ (model 2) differs only on `S_{24}`, `S_{42}`,
whose published multiplicities are unevaluated rank expressions
(`-32 + rk_1[...]`): the database never evaluated them. Our equivariant map-rank
computation evaluates them to zero at a generic member of the invariant family —
determined here, left open there. Artifact:
benchmarks/x7862/singlet-spectrum-validation.json.

## Every published operator table reproduced

The Yukawa benchmark covered three of the database's operator tables. The other
ten are now benchmarked too (`scripts/operator_benchmark.py`,
`scripts/kahler_benchmark.py`; `docs/yukawa_benchmark.md` Sections 6-7), over all
2,012 complete models:

| table | unit | agree |
|---|---|---:|
| HiggsMass (full Higgs mass matrix) | cells | 18,108 / 18,108 |
| SuperPotential (pure singlet) | tables | 2,012 / 2,012 |
| DTerms | tables | 2,012 / 2,012 |
| FITerms (= slopes, an independent check of d_ijk on 13 geometries) | tables | 2,012 / 2,012 |
| RParVio (bilinear RPV) | cells | 6,036 / 6,036 |
| Dim4Proton | permutation classes | 36,216 / 36,216 |
| Dim5Proton | permutation classes | 60,360 / 60,360 |
| GMTerm (Giudice-Masiero) | tables | 2,012 / 2,012 |
| NeutrinoKahler | cells | 6,036 / 6,036 |
| Kin5 (5bar kinetic matrix) | cells | 18,108 / 18,108 |

Nine published conventions were needed and each was established by a failing
comparison, not assumed; raw agreement is kept in the artifacts. The notable
ones: `Dim5Proton` lists an inconsistent subset of index permutations, so only
the permutation class is meaningful; `Dim4Proton` omits entries with a matter
5bar in the physical down-Higgs bundle (19,450 vs 164, no exceptions);
`RParVio` omits the bare bilinear; Kahler lists never contain a trivial
`|S_ab|^2` factor. One apparent failure (8/22 GM tables) was our own bug —
using the first Higgs slot instead of `PhysHiggs` — and is recorded as such.

## The absences of the eleven candidates, resolved from stated conditions

`scripts/absence_resolution.py`, artifact `benchmarks/x7862/absence-resolution.json`.
The published standard-model database was built (arXiv:1202.1757 Sec. 5.3) from
a GUT scan over `-3 <= k <= 3` on h11 = 4, which demanded (arXiv:1106.4804)
`h^1(L_a^* (x) L_b^*) < |Gamma|` for every pair. All 2,111 published models with
readable cohomology satisfy the second; A01-A06 violate the first and A02,
A04, A06-A11 the second (max value 8 >= 4). **All 11 absences are explained by
stated scan conditions**, including A08 and A09 which the step-1 audit had to
leave as unknown. The candidates are outside the published scan's declared
domain, not missed by it. The bound was imposed "to increase the chance that the
Higgs triplets can be removed"; all eleven are triplet-free anyway.

## Yukawa engine: three further corrections, audited

1. *Equivariant structure.* The leading-order coupling code projected onto
   Wilson-line characters without subtracting each bundle's equivariant
   structure. Fixed; now enforced by a blocking check that every slot's
   isotypic dimension equals the family count the spectrum assigns. Published
   X7862 models all have zero shift (benchmark unaffected, regenerated,
   identical); the candidates were recomputed and their ranks did not change.
2. *Nonzero Koszul maps* are now refused rather than evaluated. Audit: all 774
   bundle slots ever evaluated have ambient space equal to H^1(X, L), and every
   identification is structural, so every leading-order matrix computed is
   **independent of complex structure**: no rank-drop loci at leading order.
3. *Fast exact ranks.* For exponent-two groups the equivariant map ranks are
   computed over QQ with DomainMatrix; identical to the symbolic path wherever
   both were run; the largest singlet bundles went from unfinished after an hour
   to under a second.

With (3) the singlet-spectrum validation completed: **21/22 X7862 models match
exactly; model 2 differs only on S_24, S_42, whose published multiplicities are
unevaluated rank expressions; 0 genuine differences.**

## Steps 3-5 — Yukawa matrices, dangerous operators and a logical ranking, all configurations

The step-1 manifest froze only the first 8 accepted configurations per
candidate. The analysis now covers **every** accepted configuration
(192-336 per orbit) and every physical-Higgs choice, for the 11 additional orbits
**and the 10 published orbits as controls**, through the identical pipeline
(`benchmarks/x7862/configurations-all.json`,
`benchmarks/x7862/yukawa-all-configurations.json`).

New exact evaluations beyond the Yukawa matrices: operators that are genuine
triple products — dimension-four R-parity violation at singlet order zero
(its Q L d^c, L L e^c and u^c d^c d^c pieces), the mu term S H_u H_d and
bilinear R-parity violation S L H_u at singlet order one.

Findings for the additional orbits:

* no leading-order top Yukawa in any configuration (all Y_u leading ranks 0);
* up-type Yukawa forbidden to **all** perturbative orders in 9 of 11 (rank cap
  0); only A04 and A06 can reach rank three, and for both the rank-three pattern
  survives restricting to singlets that can take D-flat values at zero FI terms;
* dimension-five proton decay forbidden to all orders in 9 of 11;
* dimension-four RPV computed nonzero at the Abelian locus in 288/720 Higgs
  choices of A02, A04 and A07;
* bilinear RPV S L H_u nonzero at order one in all choices of A04 and A07, and
  charge-allowed but **cohomologically vanishing** in all choices of A08;
* every leading-order matrix is independent of complex structure; no
  dimension-consistency check fails.

Step 5 (`scripts/rank_candidates.py`, `docs/candidate_ranking.md`): logical
categories, no score. STRONG requires a leading-order top Yukawa, rank-three
reachability for Y_u and Y_d, and dimension-five proton decay, dimension-four and
bilinear RPV all forbidden to all orders. PROBLEMATIC requires an unconditional
exact obstruction (no up- or no down-type Yukawa at any order, or
dimension-four RPV at the Abelian locus).

| | STRONG | PROBLEMATIC | UNKNOWN |
|---|---:|---:|---:|
| additional orbits (11) | 0 | 9 | 2 (A04, A06) |
| published orbits (10) | 0 | 7 | 3 |

**No orbit on this quotient, published or new, is a strong candidate**, and the
additional orbits fail for the same kinds of reasons, at a comparable rate, as
the published ones. That is the answer to the question posed for this stage.
The PROBLEMATIC verdicts are perturbative statements; non-perturbative effects
violating the anomalous U(1)s are not analysed. UNKNOWN verdicts rest on
higher-order coefficients, singlet vacua and normalisation, which are
documented as open ingredients in `docs/physical_yukawas.md`.

Engine limits met on the way, reported rather than hidden: some order-one
couplings with a singlet leg on published controls are UNKNOWN because the
singlet's H^1 is spread over both Koszul levels, or sits at level one with a
nonzero Koszul map; none of the additional orbits hits either case.

Test suite: 246 passing.

## Correction — the "694 relabelled character tables" were our comparison error

Earlier entries reported that 694 of 27,821 published character tables agree
with ours only up to a permutation of the character labels, and left the cause
open. The cause is now established, and it is ours.

The published `GCoh` / `GCoh2` tables are the **raw** characters of the lift. The
equivariant structure is applied only when the downstairs spectrum is formed —
which is why the spectrum reproduction (1,948/1,948) needs the shift. Our
comparison script instead shifted the computed table by the equivariant
structure before comparing. Most tables are invariant under their shift, so the
error was invisible there; exactly the tables that are *not* invariant expose it.

Recompared raw against raw (`scripts/compute_equivariant_cohomology.py`, all 13
geometries regenerated; `scripts/character_table_convention.py`):

| | |
|---|---:|
| character tables compared (9,181 single + 18,640 pair, all four degrees) | 27,821 |
| **exact agreement** | **27,821** |
| tables not invariant under their shift (the only ones that discriminate) | 694 |
| of those, matching the raw computation | **694** |
| of those, matching the shifted computation | 0 |

So the 694 were precisely the discriminating tables, and they decide the
convention unanimously. There is no discrepancy in the published data. The
comparison script now compares raw to raw and records the shifted table and a
`shift_invariant` flag alongside; the unit test that tolerated `relabelling_only`
now requires `exact` for every table. While regenerating, 640 published pair
entries that are unevaluated rank expressions are recorded as
`UNEVALUATED_PUBLISHED_TABLE` instead of crashing the comparison.

Phase 8 (the 68-geometry suite, `scripts/phase8_suite.py`) was started; its
first h11 = 6 run, CICY 3413 with |Gamma| = 3 at K = 1, completed in 380 s:
UNSAT_BOUNDED, 267 retained single columns, 92,466 complete bundles.

## Correction — description of X7447

Entries above describe X7447 as "five bidegree-(1,1) equations in (P^1)^5". The
published configuration (and our registry) is five P^1 rows by **two** columns:
X7447 is cut out by **two equations of multidegree (1,1,1,1,1)**. Only the prose
was wrong; every computation used the correct configuration, and the
intersection numbers (d_ijl = 2 for distinct indices, 0 otherwise) and
c2 = (24,...,24) are those of the true geometry.

## Phase 8 — all 68 favourable CICYs, and a GUT model missing from the catalog

`scripts/phase8_suite.py`, `docs/phase8_suite.md`. For every (geometry, |Gamma|)
key of the published GUT catalog: the exhaustive search at small K with the
complete slope rule, per-run statistics as the master plan asks, and orbit-set
comparison with the catalog inside the box. Orbits are taken under summand
permutations and ambient-factor permutations preserving the configuration
matrix up to column permutations.

| K | h11 | keys | geometries | exact equality | published in box | recovered | extra orbits |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | 2-6 | 110 | 68 | 109 | 40 | 40 | 1 |
| 2 | 2-5 | 101 | 60 | 91 | 9,016 | 9,016 | 79 |

211 runs; the longest (7447, |Gamma| = 20, K = 2) took 8,794 s and 947 MiB. The
h11 = 6 prerequisite is met (3413 at K = 1 in 380 s; 4190 reproduces its 11
in-box models). **No published model inside a box is ever missed.** The
divisibility obstruction fires exactly on the empty keys.

### The 80 extra orbits, classified exactly where possible

Our survivor sets are necessary-condition survivors; the catalog is the
poly-stable stage. `scripts/phase8_extras.py` classifies every extra:

| verdict | count | method |
|---|---:|---|
| UNSTABLE_CERTIFIED | 53 | exact Groebner/interval decision (rank h-1) |
| STABLE_CERTIFIED | 9 | exact real-algebraic interior witness |
| NUMERIC_UNSTABLE | 18 | rank < h-1; numerical only, not a proof |

Two new exact tools, both in `physics/stability.py` (slope note Section 9): a
Polya hierarchy of sign certificates (which, measured, adds nothing on these
geometries for small charges — the obstruction is joint, not a single positive
combination) and an exact decision of interior common slope zeros for rank h-1
(recursive lexicographic Groebner basis, rational-root substitution,
linear solve in Q[x]/(f), rigorous interval positivity, exact vanishing modulo
the minimal polynomial).

**Two bugs in the decision were caught by testing it against the published
models**, which are poly-stable and must never be called unstable. A first
version rejected 91 of 548 sampled published models: a positive root whose
isolating interval started at 0 was dropped, and a polynomial remainder was
taken in the wrong order (`factor.rem(c)` for `c.rem(factor)`), which declared
every constant coordinate zero. After both fixes: 0 of 548 rejected (214
certified stable, 334 undecided, mostly rank < h-1). This check is now a
regression test. The classification above was rerun afterwards.

### A poly-stable GUT model absent from the published catalog

All nine certified-stable extras are one model: they share one full triple-
intersection fingerprint (invariant under every lattice automorphism preserving
d_ijk) across CICYs 5256, 5301 and 5452, which the catalog records as redundant
descriptions of the same manifold. On 5256 with |Gamma| = 4:

    columns (-2,0,-1,1,0), (0,-1,1,-2,1), (0,2,1,0,-1), (1,-2,1,0,0), (1,1,-2,1,0)

c1 = 0, structure group, both indices = -12, anomaly pairings and Bogomolov all
PASS; poly-stability certified by an exact real-algebraic witness (t4 the root in
[642595/64736, 769226/77493] of an irreducible degree-12 integer polynomial, all
coordinates positive by interval arithmetic, all five slopes vanishing modulo
it); the Kahler class has t_max/t_min ~ 231. The published catalog for this key
holds 2,128 models reaching |k| = 6, 656 of them inside our |k| <= 2 box, and
**none** shares the model's fingerprint. It satisfies every condition the
catalog states and is not in it. We do not know why; a stability search
confined to moderate Kahler ratios would miss it. It does not descend with
individually equivariant line bundles under any of the four Z2 x Z2 actions on
5256 (`benchmarks/phase8-new-gut-model.json`), so it is a new GUT model, not a
new downstairs model.

Test suite: 255 passing.

Addendum: K = 3 on the 60 keys with h11 <= 4 — **all 60 exact**, 342 published
models in box, all recovered, no extra orbits (longest run 418 s, 433 MiB). The
survey now stands at 271 runs.

## 2026-10-07 — three-page summary; citation check

Added `paper/summary/summary.tex` (3 pages, `tectonic -X compile summary.tex`):
summary of the work, the new parts of the algorithm, results with their logical
status, and an outlook on Type IIB (magnetised D7-branes, closed-string flux),
F-theory and Type IIA intersecting branes. All 22 references in it were checked
against the arXiv API record (authors, title, arXiv number, journal reference).

Citation corrections from that check:
- `paper/references.bib`: BBCL2016 (1512.05322) and BBL2017 (1607.03461) match
  their arXiv records; their "NOT VERIFIED LOCALLY" marks are replaced.
- `src/string_sm_sat/physics/yukawa.py` cited "Blesneag, Buchbinder, Candelas,
  Lukas arXiv:1706.07688" for holomorphic Yukawa couplings. arXiv:1706.07688 is
  in fact Braun, Brodie, Lukas, "Heterotic Line Bundle Models on Elliptically
  Fibered Calabi-Yau Three-folds". The citation now reads arXiv:1512.05322 (and
  1607.03461 for complete intersections). Docstring and rule metadata only; no
  computed value changes.

Correction to the entry above: the suite is 255 tests, 254 passing and 1
skipped (`test_x7447_catalog_agreement[K=4]`, because
`benchmarks/x7447/k4-gamma2-span.json` is not on disk; only its checkpoint and
the catalog comparison, which records exact agreement, are). The skip predates
this entry.


## 2026-11-12 — private repository preparation

Included the existing Codex baseline and subsequent Claude Code research work,
plus the original master prompt and two-page working-style demo. Git LFS stores
the two benchmark JSON files exceeding 50 MiB; local scientific artifacts were
not recomputed or changed. No additional scientific conclusion is drawn here.

Validation before push: 254 passed, 1 skipped in 24.11 s. The skip is the existing
X7447 K=4 catalog test because its full search JSON is absent; the checkpoint and
comparison remain available. Output: `benchmarks/prepush-tests-2026-11-12.txt`.
