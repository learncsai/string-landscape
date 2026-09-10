# Status — 2026-09-10

Current stage: validated early baseline through the Phase-4 hierarchical search;
partial Phase-5 tetraquadric benchmark. General analytic-cohomology Task H remains
partial. The complete first milestone is NOT declared finished.

Completed: runnable Python package/CLI, source provenance, exact topology and
bundle algebra, constraint metadata, anomaly/subset/index tests, necessary slope
obstructions, numerical and exact rational/algebraic witnesses, conservative
Koszul cohomology, generic exact rank certificates for both benchmarks, reference
and hierarchical enumeration, checkpoint/resume, thread equality, tiny independent
certificate replay, candidate/cohomology replay, literature and scope documents.

Current verified scientific capabilities: golden X7447 c1=0; ind(V)=ind(wedge2)=-12;
c2(TX)=c2(V)=(24,24,24,24,24); exact t=(5,29,15,11,5); generic smooth-family
cohomology V=(0,12,0,0), wedge2=(0,15,3,0). X7862 K=2,Gamma=2: 120 necessary
survivors, five row orbits, all five with exact slope witnesses (three rational,
two quadratic-algebraic). Four pass and one fails generic upstairs full-spectrum
conditions. None is labeled a fully certified heterotic/MSSM model.

Tests: 71 passing before final artifact refresh; exact topology across four
geometries, Oxford data integrity, algebra/mutation tests, large integers,
Koszul/index/Serre checks, rational/modular independent matrix ranks, resultant
symbolic determinant, nonempty differential physics domains, checkpoint/resume,
threads, certificate tampering and root isolation. See benchmarks/tests.txt.

Known discrepancies: 1307.4787 Section-5 c2/ch2 sign; 2306.03147 C4' index sign
and X7447 M5 display; 1307.4787 unequal-rank tangent/bundle remark. Each is
recorded in docs/literature_notes.md. Published golden quantities agree. Full
historical catalogs and fixed-symmetry cohomology have not been reproduced.

Current benchmark: X7862 K=2,Gamma=2, GUT_FULL necessary-filter domain with pair
indices <=0 and positive ambient chamber. Initial run: 17.34 s, 38,161 complete
bundles, 120 necessary survivors. Final source-version refresh recorded separately
in RESULTS.md. K=1 runs have zero necessary survivors in their declared domains.

Candidate counts: five K=2 row orbits; zero fully certified models; surviving
model decisions UNKNOWN_BOUNDED. A complete empty K=1 domain is UNSAT_BOUNDED
only for its explicit restrictions. No unbounded inference is made.

Runtime / peak memory: see current benchmark JSON files and RESULTS.md. Initial
K=2 pilot: 0.719 s for 3/235 roots, 29,949,952-byte peak RSS. Estimated 56.3 s for
full scan; measured initial completion 17.34 s. Checkpoints validated before run.
No higher-K or X5302 escalation has occurred.

Next task: reproduce generic golden/rank certificates, then specify a free-action
subfamily and check whether rank witnesses persist there. Profile fourth-column
extensions before attempting a higher-K search.

Scientific blockers: actual holonomy/commutant classification, nonzero integral
anomaly effectivity, invariant-family cohomology, equivariance and Wilson-line
representations; generic rank-deficient cases remain UNKNOWN. Large independent
exhaustion proofs require branch-level certificates not yet implemented.
