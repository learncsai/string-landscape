# Literature and convention ledger

Read before physics implementation: 1307.4787 Sections 2–7 and Appendix A;
1202.1757 Sections 4–5 and equivariant construction; 1106.4804 upstairs/downstairs
construction and Abelian masses; 2306.03147 C1–C5 and Appendix B. Supporting
checks use 1311.1941 and the map-rank discussion in 2606.22275. Raw HTML is
retained with hashes; derived text is convenience only. No unavailable source
is treated as evidence.

All indices below mean chi=sum_q (-1)^q h^q. J_i are ordered ambient integral
hyperplanes; d_ijk integrates J_i J_j J_k and c2_i pairs c2 with J_i. There are
no hidden factorials or floating-point topology coefficients.

| Equation / implementation | Convention and derivation | Source location | Validation |
|---|---|---|---|
| Ambient fundamental class | Product over defining equations of sum_i q_i J_i; coefficient of product J_i^n_i integrates over ambient space | Ambient complete-intersection construction, 1202.1757 §5.1; direct Chow-ring derivation | test_topology, test_oxford_topology |
| Triple intersections | Coefficient after multiplication by J_i J_j J_k; all ordered indices included | 1311.1941 (2.4), tetraquadric geometry | test_topology: tetraquadric, X7447, quintic, bicubic |
| Tangent Chern polynomial | Product (1+J_i)^(n_i+1) times product (1+sum q_i J_i)^(-1), truncated through degree 3; tangent-normal exact sequence | CICY adjunction; our explicit polynomial expansion | test_topology Euler and c2; Oxford raw C2 fields |
| c1 and tensor/dual | Column sums; tensor adds charges; dual negates | 1202.1757 (4.8), (5.1), (5.5) | test_immutable_algebra_and_large_integer; test_golden_topology_algebra |
| Line index HRR | d kkk/6+c2_i k_i/12; exact rational then integral check | 1307.4787 §5 HRR display; 2306.03147 (B.1) for tetraquadric | test_immutable_algebra_and_large_integer, test_koszul_serre_index_box |
| Sum and wedge2 index | Add individual indices; wedge2 has all ten unordered pairs, including multiplicities | 1307.4787 (4.7), §5 | test_golden_topology_algebra; test_permutation_multiplicity |
| Bundle c2 | Whitney sum over a<b k_a k_b; for c1=0 equals -1/2 sum_a k_a^2 | 1311.1941 (2.3); 1202.1757 (5.6) is ch2, not c2 | test_whitney_independent_negative_quadratic; golden c2=24 |
| Anomaly residual | c2(TX)-c2(V); negative nef pairing rejects; nonzero positive residual effectivity not proved | 1311.1941 (2.6), 1307.4787 (4.4) | test_mutated_anomaly; golden zero residual |
| Structure subset | All nonempty proper subsets must have nonzero sum | 1307.4787 (2.2), Appendix A | test_mutated_structure; no claim of exact four-dimensional holonomy torus |
| Slopes | d_ijk k^i t^j t^k, no normalization needed for exact homogeneous zero | 1311.1941 (2.7); 1307.4787 (4.5) | test_golden_rational_stability; test_algebraic_positive_exact |
| Signed matrix obstruction | Nonzero entrywise one-sign combinations cannot vanish at positive t; identically zero allowed | 1307.4787 §5 | test_zero_matrix_not_rejected; differential tests |
| Chiral target | Both indices equal -3 Gamma | 1307.4787 (4.7) | golden and index mutation |
| Full spectrum | V=(0,3 Gamma,0,0); wedge2=(0,3 Gamma+nh,nh,0), nh>0 | 1307.4787 (4.8)–(4.9), 2306.03147 C4 | test_generic_golden_spectrum |
| Single, pair, partial index budgets | Nonpositive quantities and fixed negative total imply lower bounds; GUT_FULL and pair-domain assumptions explicit | 1307.4787 §5 steps 1–6 | test_physics_sets; test_nonempty_physics_subset_and_resume |
| Component completion | Abs(partial sum)<=remaining*K | 1307.4787 §5 step 4(i), triangle inequality | test_nonempty_canonical_domains |
| Ambient cohomology | Bott binomial dimensions and Künneth; P1 negative basis is Serre dual | 1202.1757 §5.2; 1311.1941 Appendix C | test_exception_and_trivial; monomial multiplication |
| Koszul collapse | dr has bidegree (r,1-r); absence of possible arrows implies E1=Einf | 2606.22275 §2.1; 1202.1757 §5.2 | test_koszul_serre_index_box |
| Generic rank certification | Nonzero maximal minor modulo a prime proves generic full rank over Q/C | 2606.22275 rank-certificate discussion; elementary minor argument | test_modular_vs_rational_rank; test_cohomology_rank_certificate_replay |
| X7447 resultant d2 | Relative P1 Koszul complex yields f0*g1-f1*g0 when k_r=0 | Our derivation in cohomology_certificates.md from the Koszul framework | test_resultant_direct_symbolic_determinant; test_resultant_coordinates_and_dual |
| Published GUT catalog | GUTall.m parsed to data/processed/published_gut_models.json; published matrices are row = ambient factor, transposed to our column form | Oxford line bundle model database for 1307.4787 | test_catalog_totals reproduces the stated 68 geometries / 63,325 models |
| Section-5 algorithm steps | Steps 1-10 quoted in full in this file below; our hierarchy implements 1,3,4,5,6 with exact necessary conditions and defers step 2 (row-permutation reduction) to the comparison stage | 1307.4787 Section 5 | benchmarks/x7862/k*-published-catalog-comparison.json |
| ind(V)=ind(wedge2 V) | Identity for rank five with c1(V)=0; the paper states it explicitly after (4.7) | 1307.4787 after (4.7) | test_index_identity; K=1 census is exactly diagonal |
| Bogomolov pairing | c2(V).J>=0 at the stable polarization; entrywise-nonnegative sum_a q_r(k_a) rejects | 1307.4787 (4.6) | test_published_models_satisfy_bogomolov_and_anomaly |
| Index divisibility | d_X=gcd{ind(L)} must divide 3|Gamma|; unbounded in K | our derivation, docs/exact_obstructions.md P2 | test_divisibility_predictions_match_the_published_catalog |
| Published standard-model database | sms202.m parsed to data/processed/published_standard_models.json; carries free actions, EquivStr, WLine, GCoh/GCoh2/GCohSing and DownSpec | Oxford line bundle model pages for 1106.4804 / 1202.1757 | test_database_totals; 2,113 records |
| Equivariant structure | enters as a character shift of H^q: chi_a for a single bundle, chi_a+chi_b for a pair | convention pinned by fitting the published catalog, then verified | 1948/1948 with the shift vs 1503/1948 without |
| Character indexing | GCoh columns are the characters in lexicographic label order; Gamma inferred database-wide (Z_2 at order 2, Z_2xZ_2 at order 4) | convention pinned by fitting, cross-checked against group order and table width | test_character_group_arithmetic, test_infer_group_rejects_wrong_order |
| Wilson-line projection | piece with character chi survives with the multiplicity of chi upstairs; 10 = wedge^2 5 fixes Q, u^c, e^c characters | 1106.4804 Section 4; 1202.1757 Sections 2-3 | test_regular_representation_gives_three_complete_families |
| Real-algebraic stability | Reduce slopes modulo a polynomial; isolate one root and prove positivity with rational interval bounds | Our certificate specialization of (4.5); standard polynomial arithmetic | test_invalid_algebraic_witness and exact tetraquadric artifacts |

## Discrepancies and conservative decisions

The positive quadratic expression called c2(V) in 1307.4787 §5 is ch2(V).
We use the negative sign independently stated in 1311.1941 (2.3), derived by
Whitney multiplication, and confirmed by the Section-7 golden example.
The corresponding positive-sign pseudocode anomaly inequality is not copied.

2306.03147 C4' prints a positive chiral Euler characteristic, while its A.3
objective uses the negative target. We follow HRR and the published cohomology,
which give -3 Gamma. Appendix B's displayed fifth X7447 flop matrix is not the
factor-permuted involution suggested by the preceding matrices, and its boundary
text is garbled. These displays are not executable inputs. We use explicit
Koszul maps instead of silently correcting the formula. Older empirical
cohomology formulas are not extrapolated beyond proven domains.

1307.4787 Section 7 also describes the ranks of V and TX as equal, although they
are five and three respectively. We reproduce c2 equality, not a deformation
between unequal-rank bundles. Historical saturation is not a constructive
unbounded finiteness theorem. These are source discrepancies, not claimed
failures of the reproduced numerical data.

Table 4 in 1307.4787 precedes the no-anti-family/Higgs filters and removes
ambient-factor redundancies. It lists five X7862,Gamma=2 models at K=2. That
count agreement has since been upgraded to exact catalog agreement against the
actual published database (GUTall.m). The database holds 10 models for
{7862, 2}, of which 5 lie in the K=2 box, 7 in the K=3 box and all 10 in the
K=4 box. With the complete span slope rule our row-orbit sets equal the in-box
published sets exactly (0 published-only, 0 ours-only) at K=2, 3, 4, 5, 6 and 7.
For {7862, 4} the database holds 58 models, all with max|k| <= 5, and the K=5
scan reproduces all 58 exactly. With the finite coefficient box, K=3 and K=4 each
produce one extra spurious orbit; see docs/slope_obstruction_note.md Section 7.
All published models pass every exact necessary check we implement.

The published database description states the catalog stage: anomaly-free,
poly-stable, correct indices. Our survivor sets are necessary-condition survivor
sets, so agreement means the two condition sets happen to coincide on these
domains; it is not a proof that our conditions are sufficient.

The published catalog also carries per-geometry topology for all 68 favourable
CICYs. Rebuilding each configuration matrix and recomputing with our ambient
Chow-ring code reproduces the published c2 for 68/68 and the published Euler
number for 68/68 (benchmarks/catalog-topology-audit.json). This extends the
earlier four-geometry cross-check considerably.

**Symmetry-order discrepancy for X7447.** The GUTall.m catalog record lists
`SymmOrder -> {2, 4, 5, 10, 20}` for CICY 7447, while our geometry registry,
populated from the Oxford freely-acting-symmetry pages, carries {2, 4, 10}. The
catalog also emits model keys for orders 5 and 20, both with zero models. We do
not silently reconcile these: the registry field is informational only (the
search takes |Gamma| from the declared domain, not from the registry), and no
result in this repository depends on it. Note that order 5 is independently
excluded by the index-divisibility obstruction (d_X = 2 does not divide 15), so
the empty catalog entry there is expected whichever list is correct; order 20 is
not excluded by divisibility and simply has no models in the published range.
Resolving which symmetry list is authoritative requires the underlying
free-action data, which we have not reproduced.

Oxford original CICY records confirm configurations, Hodge numbers, Euler
numbers and c2 for both benchmarks. The original guessed symmetry URL returned
404; resolved Oxford symmetry and quotient pages and the CICY Mathematica data
were acquired instead. The model index and import notebook were inspected;
the full historical model catalog has not been parsed or matched entry-by-entry.


The published standard-model database leaves 2,450 entries across 1,197 records
as unevaluated rank expressions (`rk_1[H_4[...]]`) - undetermined singlet
multiplicities in the source itself. A further 165 records lack the equivariant
fields entirely. Neither is reconstructed here; both are reported as unknown.

## The published scanning algorithm (arXiv:1307.4787 Section 5), quoted

1. assemble List_1 of line bundles with (i) -3|Gamma| <= ind(L) <= 0 and
   (ii) mu(L)=0 somewhere in the interior of the Kahler cone;
2. remove redundant line bundles using ambient row permutations;
3. pairs: (i) -3|Gamma| <= ind(L1)+ind(L2); (ii) -3|Gamma| <= ind(L1 x L2) <= 0;
   (iii) mu(L1)=mu(L2)=0 somewhere in the interior of the Kahler cone;
4. triples: (i) component bound |sum of three c1| <= 2 k_max; (ii) partial index
   budget; (iii) pair indices in range; (iv) wedge2 partial index <= 0;
   (v) mu(L1)=mu(L2)=mu(L3)=0 somewhere in the interior;
5. fourth column, with the fifth derived: (i) component bound; (ii) index range;
   (iii) mu(L5)=0 somewhere in the interior;
6. complete check: (i) total index = -3|Gamma|; (ii) wedge2 index = -3|Gamma|;
   (iii) remaining pair indices <= 0; (iv) common slope zero for all five;
   (v) the anomaly inequality 2 d_rst c2^st(TX) >= d_rst sum_a c1^s c1^t;
7. remove redundant line bundle sums;
8. check stability by explicitly finding points in the Kahler cone where all
   line bundles have slope zero;
9. eliminate models with anti-families; 10. eliminate models with no 5-5bar pairs.

Conventions we deliberately differ on, and why:
steps 1(ii), 3(iii), 4(v), 5(iii), 6(iv) ask for actual common slope zeros; the
published scan solved these exactly where possible and numerically otherwise.
We never accept a numerical root as a certificate. Instead we test an exactly
decidable necessary condition (docs/slope_obstruction_note.md Prop. 3), which on
these geometries is equivalent to the published condition for a single line
bundle (Prop. 4) and strictly weaker for the joint system. Step 2/7 row-permutation
reduction is applied only in the comparison stage, so that our enumeration keeps a
direct completeness argument.
