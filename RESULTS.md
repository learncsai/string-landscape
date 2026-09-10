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
