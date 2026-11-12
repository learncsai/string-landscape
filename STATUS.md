# Repository snapshot — 2026-11-12

Prepared the research code, recorded benchmark artifacts, papers, original master
prompt and two-page Codex/Claude Code demo for a private GitHub repository.
The two largest benchmark JSON files are stored with Git LFS; use `git lfs pull`
after cloning. The scientific scope and limitations recorded below are unchanged.

Validation: 254 tests passed and 1 was skipped in 24.11 seconds. The skipped
X7447 K=4 catalog regression requires `benchmarks/x7447/k4-gamma2-span.json`,
which is not on disk; its checkpoint and catalog-comparison artifact are retained.
Full output: `benchmarks/prepush-tests-2026-11-12.txt`.

---

# Status — 2026-09-26 (third session)

Current stage: the nine-step Yukawa program is complete up to the point the
program itself stops (steps 7-8 are documentation of required ingredients, by
design). A publishable write-up is in `paper/` (LaTeX, builds with `tectonic`).

Completed this session:
* **Step 6, every published operator table reproduced.** Thirteen tables of the
  standard-model database — Yukawa up/down, mu, Higgs mass, bilinear and
  dimension-four RPV, dimension-five proton decay, singlet superpotential, D- and
  FI-terms, Giudice-Masiero, neutrino Kahler, 5bar kinetic matrix — for all 2,012
  complete models, after identifying nine unstated conventions from the data.
  954 of 2,007 published down-type Yukawa tables are internally inconsistent as
  charge tables (diagnosed, not reconciled).
* **Steps 2-4, the Yukawa engine.** Exact leading-order triple products with a
  Gamma-covariance self-test (zero violations); every evaluated matrix is
  independent of complex structure; dangerous operators evaluated
  cohomologically where they are triple products. Three corrections made and
  audited (Koszul level sum >= 2 is UNKNOWN not zero; nonzero Koszul maps
  refused; equivariant structure now applied per slot) — no recorded number
  changed except the candidate rerun, whose ranks were unchanged.
* **Step 5, ranking.** All accepted configurations of the 11 additional and the
  10 published orbits through one pipeline, logical categories only. No orbit,
  published or new, is a strong candidate; additional 9 problematic / 2 unknown
  (A04, A06), published 7 / 3.
* **Step 1 closed.** All 11 absences from the published database are explained
  by conditions the published scan states (charge range; h^1(La* Lb*) < |Gamma|).
* **Singlet spectrum** from first principles: 21/22 X7862 models exact, the
  22nd differs only where the published data is unevaluated.
* **Exact fast path** for exponent-two equivariant ranks (DomainMatrix over QQ).
* **Character tables:** the published GCoh/GCoh2 tables are raw characters of
  the lift; our earlier comparison shifted the computed side, which produced the
  "694 relabellings". Compared correctly, every table agrees (see RESULTS.md).
* Steps 7-8 documented: `docs/physical_yukawas.md`,
  `docs/supersymmetry_breaking_scope.md`.

* **Phase 8 done at low K.** All 68 favourable CICYs: 271 runs (K = 1 on all
  110 keys, K = 2 on the 101 keys with h11 <= 5, K = 3 on the 60 with h11 <= 4). No published model inside a
  box is ever missed (9,016 of 9,016 at K = 2). Of 80 extra survivors, 53 are
  certified unstable and 9 certified stable by a new exact Groebner/interval
  decision (validated never to reject a published model); 18 are unstable
  numerically only (rank < h-1).
* **A poly-stable GUT model missing from the published catalog** (CICY 5256 =
  5301 = 5452, |Gamma| = 4, |k| <= 2), certified with an exact real-algebraic
  witness; it has no descent with individually equivariant line bundles.

Open: finiteness on the tetraquadric (Conjecture C1); Koszul level sum >= 2
couplings; singlet vacua beyond D-flatness at zero FI; exact decisions for
rank < h-1; the survey at larger K.

---

# Status — 2026-09-10 (second session)

Current stage: Phases 5 and 6 complete for Gamma=2, and Phase 9 (downstairs
MSSM) opened and reproduced against the published standard-model catalog.
Phase 8 (the 68-geometry benchmark suite) remains only partly done: topology is
verified for all 68, but the search suite has not been run over them. The complete published
catalogs of both benchmark geometries are reproduced exactly: all 10 models of
{7862, 2}, all 58 of {7862, 4}, all 93 of {7447, 2}. Both geometries have had
their smallest box independently replayed in full. The session's main new result
is a charge-unbounded (K-free) slice theorem, docs/exact_obstructions.md S1-S2. General analytic
cohomology (Task H) and everything downstairs remain partial. The first
milestone is complete except for full-spectrum coverage on a specified
free-action subfamily.

Completed since the previous status: independent exhaustive replay of the entire
X7862 K=1 domain (43,046,721 ordered assignments, four declared domains, exact
survivor-set equality); retrieval and conversion of the actual published Oxford
GUT catalog (68 geometries, 63,325 models) with provenance; exact catalog
agreement at every K scanned; a mathematical audit of the signed-combination
slope rule and its replacement by a complete, certificate-producing form; a
formal proposition for the finite-field rank certificates plus tests for its
one-sided direction; X7862 scans at K=3 through K=7 (Gamma=2) and K=5
(Gamma=4); a partial anomaly branch bound; the Bogomolov pairing; an unbounded
index-divisibility obstruction; and a bitset-indexed search core that is 3x to
7.5x faster at identical results.

Current verified scientific capabilities: golden X7447 c1=0, ind(V)=ind(wedge2)=
-12, c2(TX)=c2(V)=(24,24,24,24,24), exact rational witness t=(5,29,15,11,5),
generic smooth-family cohomology V=(0,12,0,0) and wedge2=(0,15,3,0). Topology
recomputed for all 68 favourable CICYs: 68/68 agreement with published c2 and
68/68 with published Euler numbers. X7862 Gamma=2: K=1 UNSAT_BOUNDED (replayed
independently); K=2 120 survivors / 5 orbits; K=3 168 / 7; K=4 through K=7 all
240 / 10, the survivor set being literally identical across those four boxes.
Every one of those orbit sets equals the published catalog exactly inside the
corresponding box (0 published-only, 0 ours-only). For Gamma=4 at K=5, 1,344
survivors / 58 orbits, again exactly the 58 published models. All published
{7862,2} and {7862,4} models pass every exact check we implement. X7447 with
|Gamma|=5 returns UNSAT_UNBOUNDED by divisibility.

Tests: 206 passing in about 26 s. New: slope-obstruction soundness/dominance/
monotonicity, integer-vs-rational canonical span forms, Proposition-R minor and
mod-p lower-bound tests, index identity and divisibility, partial anomaly budget
soundness, published-catalog totals and row-orbit equality at six boxes plus
Gamma=4, K=4..7 survivor-set stability, the documented spurious orbit of the
finite coefficient box, X7447 catalog agreement at K=1..3, extreme rays of the
obstruction cone, dual-versus-primal decision agreement, and an
unbounded-certificate round trip. Differential brute-force/split-search comparisons now run under all
three slope-rule settings.

Known discrepancies: 694 of 27,821 equivariant cohomology tables differ from the
published ones by a permutation of the character labels, with identical
dimensions, on eight of the thirteen geometries; cause unresolved and recorded
in docs/equivariant_cohomology.md. Separately, the K=3 box-rule run produced one
extra row orbit relative
to the published catalog; diagnosed as incompleteness of the {-1,0,1} coefficient
box, resolved by the complete span rule, and recorded in
docs/slope_obstruction_note.md Section 7. Earlier convention discrepancies
(1307.4787 Section-5 c2/ch2 sign; 2306.03147 C4' index sign and X7447 M5 display;
the unequal-rank tangent/bundle remark) remain as recorded in
docs/literature_notes.md. Published golden quantities agree.

Current benchmark: X7862, GUT_FULL necessary-filter domain, positive ambient
chamber, nonpositive pair indices, complete span slope rule. Gamma=2 runs:
K=4 43.6 s / 105.6 MiB, K=5 85.4 s / 141.0 MiB, K=6 118.9 s / 193.8 MiB,
K=7 179.2 s / 188.9 MiB, all with 240 survivors. Gamma=4 at K=5: 236.9 s /
317.1 MiB / 1,344 survivors. Full table in RESULTS.md. With the bitset-indexed
core the finite-box rule is now marginally faster than the complete rule
(K=4: 36.7 s vs 43.6 s) but retains a spurious orbit, so the complete rule is
the default recommendation.

Candidate counts: 0 fully certified models. Every nonempty domain is
UNKNOWN_BOUNDED, and 425 slope slices are UNSAT_SLICE_UNBOUNDED; the K=1 domains are UNSAT_BOUNDED for their explicit
restrictions; (X7447, |Gamma|=5) is UNSAT_UNBOUNDED for the five-line-bundle
class on that geometry. No other unbounded inference is made.

Runtime / peak memory: see the table in RESULTS.md. The nominal K=7 domain is
15^16 = 6.57e18 ordered four-column assignments; the hierarchy materialises
231,946 complete canonical bundles from it. Peak RSS 317 MiB at the largest run
(Gamma=4, K=5), still well below the 12 GB ceiling, so memory is not the binding
constraint at this scale.

Empirical saturation: the Gamma=2 survivor set is identical at K=4, 5, 6 and 7,
and no survivor uses a charge above 4. Recorded as EMPIRICAL_SATURATION(K=4) for
this geometry, symmetry order, target and chamber. This is not a no-go theorem
and no unbounded inference is drawn from it.

Long-run policy record: every escalation this session was piloted first and the
estimate written down before launching. K=4 pilot (8 roots, 4.37 s) predicted
110-450 s against an actual 204.8 s pre-indexing; the K=4 prediction that the
run must yield exactly 10 orbits, because all 10 published models have
max|k| <= 4, was stated in advance and confirmed. K=5 pilot (20 roots, 2.14 s)
predicted 32-130 s against an actual 85.4 s. Gamma=4 K=5 pilot (20 roots,
5.02 s) predicted 99-396 s against an actual 236.9 s.

X7447 (h^{1,1}=5), Gamma=2, complete span rule: K=1 UNSAT_BOUNDED in 6.8 s;
K=2 271.6 s / 361.6 MiB / 6,540 survivors / 56 orbits; K=3 1338.8 s / 484.9 MiB
/ 10,140 survivors / 87 orbits. The orbit counts 56 and 87 were predicted before
the runs from the published catalog's max|k| distribution and both came out
exactly, with 0 published-only and 0 ours-only. K=4 (predicted 93 orbits, the
complete published {7447,2} catalog) is running; the pilot estimate recorded
before launch was 23-93 min.

Next task: (a) finish X7447 K=4 and compare; (b) X7862 Gamma=8 (64 published
models, max|k|=7), whose wider index window makes it the heaviest tetraquadric
case; (c) X7447 Gamma=4, whose catalog has 430 models — the largest comparison
target available at h11<=5; (d) memory is now the fastest-growing resource on
X7447 (485 MiB at K=3), so measure before escalating to h11=6.

Scientific blockers: the downstairs pipeline is no longer blocked on either
sector. What remains: the rank path handles one defining polynomial, so
codimension-two geometries are only partly covered; the free actions and the
invariant defining families are taken from published symmetry data rather than
classified here; the cohomology is that of a generic member of the invariant
family; and nothing addresses supersymmetry breaking or moduli stabilisation; holonomy/commutant classification, integral anomaly effectivity,
and Wilson-line representation theory remain unimplemented. The conjectural
charge bound of docs/exact_obstructions.md C1 degenerates near the Kähler-cone
boundary and is not a finiteness theorem.

Source of record: benchmarks/*.json carry the domain, counters, input hashes and
source hash of each run; docs/ carries the proofs and assumptions for every rule
that is allowed to prune.
