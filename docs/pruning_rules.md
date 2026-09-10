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

These are established identities or the conservative Section-5 strategy from
arXiv:1307.4787, not claimed new research. Partial slope combinations are deferred
to complete bundles; individual signed matrices are checked before recursion.
The implementation omits historical early ambient-row reduction to keep a direct
completeness argument. It therefore reproduces the hierarchy, not every historical
optimization. Filter counts at differing branch depths count prefixes, not full
states; they must not be added as if they partitioned the nominal five-column box.

Tests compare the full unfiltered canonical domains, filtered tiny geometry
boxes, and a nonempty finite subset containing a K=2 tetraquadric candidate.
Checkpoint and thread comparisons include nonempty survivor sets. No heuristic
pruning or empirical saturation inference is used.
