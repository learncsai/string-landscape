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
