# Mathematical scope

This engine searches five integral ambient line bundles on explicitly named,
favourable smooth CICY threefolds. Smoothness and favourability are input
assumptions checked against published benchmark records, not decided from a
configuration matrix. Charges are measured in the ordered integral ambient
hyperplane basis. Intersection and Chern computations use arbitrary precision.

The domain fixes geometry, positive ambient Kähler chamber, symmetry **order**,
K, target, and whether every pair index is nonpositive. An optional finite
allowed-column set intersects the box; this is used for nonempty independent
regression tests and is recorded in certificates. Permutations of summands are
identified, preserving repeated columns. Ambient-factor relabelings are used
only in the separate published-count comparison.

Targets are GUT_CHIRAL, GUT_FULL, DOWNSTAIRS_MSSM, and the reserved
STRICT_NON_SUSY_SM. Only the first two have search implementations. GUT_FULL
adds no anti-families and a positive number of vectorlike 5 pairs. Pair index
nonpositivity is an explicit historical restriction, not inferred from arbitrary
GUT_FULL spectra. Single-index bounds are never applied to unrestricted
GUT_CHIRAL. Numerical optimizer failures never reject candidates.

The no-proper-zero-subset criterion is checked exactly, following the historical
scan. It is not a proof that the connection has four independent U(1) holonomies.
The golden matrix itself has rank three. Repeated summands and other integral
relations can reduce the actual holonomy torus; a separate commutant analysis
is required before certifying the complete gauge group. Additional massless U(1)
factors are UNKNOWN. No equivariance follows from a group order or divisibility.

Anomaly testing computes c2(TX)-c2(V) paired with nef hyperplanes. A negative
component excludes effectivity. A nonnegative vector passes this necessary test;
a nonzero integral effective representative is not constructed. Zero residual
is exactly the zero class in the assumed favourable dual basis.

The default cohomology backend computes only Koszul spectral sequences that
provably collapse by bidegree support. These answers hold for smooth regular
complete intersections, without a maximal-rank assumption. A separate optional
tetraquadric backend proves maximal ranks on a Zariski-open subset by finite-field
minor witnesses. Its results concern the generic smooth family, not every
complex-structure specialization or the subfamily admitting a chosen free action.
It is not used to eliminate generic-unknown cases from an all-moduli search.

No bundle, quotient, or SUSY-breaking construction in this repository is called
an exact Standard Model. No ML, flux scan, unbounded no-go, or new finiteness
claim is implemented.
