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
ambient-factor redundancies. It lists five X7862,Gamma=2 models at K=2. Our
120 column-canonical survivors reduce to five row orbits, each with an exact
slope witness; one fails the generic Higgs condition. This is a stage-aware
count agreement, not an equivariant-model catalog equality.

Oxford original CICY records confirm configurations, Hodge numbers, Euler
numbers and c2 for both benchmarks. The original guessed symmetry URL returned
404; resolved Oxford symmetry and quotient pages and the CICY Mathematica data
were acquired instead. The model index and import notebook were inspected;
the full historical model catalog has not been parsed or matched entry-by-entry.
