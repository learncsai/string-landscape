# Pruning statements and proofs

1. C1 completion: the fifth column is minus the first four. Each component must
   lie in [-K,K]. This is equivalent to C1=0 in the finite domain.
2. Canonical order: each five-column multiset has one sorted representation;
   its first four determine the fifth. Recursion permits equal column indices,
   so repeated line bundles are retained.
3. Partial component bound: with m columns fixed, each component of their sum
   has absolute value at most (5-m)K in any completion. This follows from the
   triangle inequality. Violation safely rejects the branch.
4. Single-index budget, GUT_FULL only: at common slope zero a nontrivial line
   bundle has h0=h3=0. No anti-families requires every h2=0, so each index is
   nonpositive. Since their sum is -3 Gamma, every partial sum is between that
   target and zero. The structure criterion excludes trivial summands.
5. Pair-index budget: the domain explicitly requires all pair indices <=0.
   Their total must equal -3 Gamma; therefore each pair and each partial sum
   of pair indices is >=-3 Gamma. Without the domain restriction this pruning
   is disabled. This is not claimed necessary for all upstairs GUT spectra.
6. Anomaly: an effective curve has nonnegative intersection with every nef
   hyperplane. Negative residual intersection therefore obstructs the declared
   trivial-hidden-bundle completion. Positive residuals do not certify effectivity.
7. Signed slope matrices: if a nonzero symmetric slope matrix, or an integer
   linear combination of such matrices, is entrywise nonnegative (or
   nonpositive), its quadratic form is strictly signed for t_i>0. It cannot
   vanish. Zero matrices impose no condition. Testing finitely many coefficient
   vectors weakens the obstruction but never makes it unsafe.

8. Partial anomaly budget: with `c1(V)=0` the anomaly condition is separable,
   `sum_a q_r(k_a) >= -2 c2_r(TX)` with `q_r(k)=d_rij k^i k^j`. If the partial
   sum over a prefix plus `(5-m)` times the pool maximum of `q_r` already falls
   below the budget, no completion can satisfy it. Exact; requires that every
   completion's columns come from the declared pool. Proof and measurements:
   docs/exact_obstructions.md P3.
9. Span slope obstruction: `span{k_a}` must not contain a `k` whose slope matrix
   is entrywise one-signed and nonzero. This is the complete (unbounded
   coefficient) form of rule 7, decided exactly by extreme-ray enumeration, and
   is monotone in the column set, so it prunes prefixes. Every rejection carries
   an explicit integer witness `k_c` and its rational coefficients. Proof:
   docs/slope_obstruction_note.md Propositions 3-5. It strictly dominates rule 7
   and first differs from it at K=3 on X7862.
10. Bogomolov pairing: `c2(V).J >= 0` at the stable polarization; if every
   component of `sum_a q_r(k_a)` is nonnegative and not all zero, no `t>0`
   satisfies it. Published necessary condition, 1307.4787 (4.6). Measured to
   reject nothing on the X7862 domains scanned so far.
11. Index divisibility: `d_X = gcd{ind(L)}` must divide `3|Gamma|`, otherwise no
   five-line-bundle sum has the required chiral asymmetry **at any K**. Exact,
   and the only rule here whose conclusion is not bounded-domain.
   docs/exact_obstructions.md P2.

These are established identities or the conservative Section-5 strategy from
arXiv:1307.4787, not claimed new research. Under the `box` slope rule partial slope combinations are deferred to complete
bundles and only individual signed matrices are checked before recursion; under
the `span` rule the complete obstruction is tested at every prefix depth.
The implementation omits historical early ambient-row reduction to keep a direct
completeness argument. It therefore reproduces the hierarchy, not every historical
optimization. Filter counts at differing branch depths count prefixes, not full
states; they must not be added as if they partitioned the nominal five-column box.

Counter semantics changed with the indexed engine
(`hierarchical_section5_indexed_v2`). Rules 3 (component completion) and 5 (pair
index range) are now applied by *construction*: the retained line list is indexed
by bitsets, so the recursion iterates only over lines already satisfying them.
Consequently `depth_N_reject_completion` and `depth_N_reject_pair` no longer
appear, and `depth_N_attempted` counts admissible partners rather than every line
in the list. `depth_N_retained` and every later counter keep their meaning, and
the survivor set is unchanged - verified by re-running every recorded X7862
domain and requiring exact set equality, and by the differential test suite.

Rules 8-11 are re-derived here; rules 9 and 10 correspond to published
requirements (Section-5 steps 3(iii)/4(v)/5(iii) and (4.6) respectively) that the
earlier implementation only approximated. Rule 9's per-coefficient optimality on
these two geometries is Proposition 4 of the slope note.

Tests compare the full unfiltered canonical domains, filtered tiny geometry
boxes, and a nonempty finite subset containing a K=2 tetraquadric candidate.
Every differential test is run for each declared slope rule (box, span, both).
Checkpoint and thread comparisons include nonempty survivor sets. No heuristic
pruning or empirical saturation inference is used.
