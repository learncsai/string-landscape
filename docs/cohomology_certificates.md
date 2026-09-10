# Exact cohomology coverage and rank witnesses

The primary all-smooth backend constructs E1^{-p,q}=H^q(A,L tensor wedge^p N*)
using Bott and Künneth. A differential dr has bidegree (r,1-r). When no two
occupied bidegrees can be joined by any dr, every differential is zero. Summing
dimensions by q-p gives exact cohomology. This includes the trivial bundle,
many mixed-sign bundles, and the exceptional (2,-2,0,...) case with h1=h2=3.
Index and Serre duality are mandatory postconditions, not evidence of map rank.

The generic backends build actual multiplication matrices. On P1, H0 uses
homogeneous monomial bases and H1 uses the dual bases from Serre duality.
Multiplication increases H0 exponents and decreases dual H1 exponents; terms
outside the target basis vanish. Tensor products give the ambient map.
Coefficients are deterministic small integers derived from SHA-256. Gaussian
elimination uses the prime 1000003. Only saturation of the universal rank bound
min(source dimension,target dimension) is accepted. A nonzero maximal minor
modulo this prime remains a nonzero integer minor, hence a nonzero polynomial
in the defining-equation coefficients over Q. Its nonvanishing locus meets the
smooth regular-complete-intersection locus. Finitely many such open sets have
nonempty intersection in the irreducible parameter space. Therefore all the
finite collection of certified generic dimensions can hold simultaneously.

For X7862, the hypersurface sequence has a single multiplication map. Its
kernel and cokernel determine h^q exactly when the generic maximal rank is
certified. The code does not infer maximal rank from index or repeated sampling.

For X7447, two additional cases are implemented. When E1 has exactly two
occupied bidegrees joined by d1, the appropriate horizontal/vertical pair of
multiplication maps is assembled with Koszul signs. Full rank resolves the
sequence. General multi-node complexes are not implemented.

When a line-bundle component k_r is zero, write the two equations as
f=x0 f0+x1 f1 and g=x0 g0+x1 g1 along P1_r. The relative Koszul terms along
that factor are O, O(-1)^2, O(-2). Their only nonzero derived pushforwards are
H0(O)=C and H1(O(-2))=C. Eliminating the two middle terms gives the two-term
complex on the other four P1 factors with differential f0*g1-f1*g0. This is the
2-by-2 resultant, of multidegree (2,2,2,2). It can be checked on the standard
two-affine-chart Čech resolution; the sign is irrelevant to rank. Applying
ambient cohomology gives precisely the original d2 between (p,q)=(2,q) and
(0,q-1). The implemented case requires these to be the only occupied E1 nodes.
No unspecified maximal-rank assumption or smoothness of the resultant
hypersurface is needed: the derived-pushforward calculation uses the smooth
regular complete intersection upstairs. Integer resultant coefficients are
constructed by convolution of the original two multi-affine equations.

The golden X7447 bundle is resolved by collapse, isolated d1 maps, and two
9-by-9 full-rank resultant d2 maps. This independently reproduces its published
cohomology for the generic smooth family. The exact equations defining a free
Gamma action are not supplied; specialization to that subfamily remains UNKNOWN.

References: arXiv:1202.1757 Section 5.2 and Appendix B (Koszul/cohomology);
arXiv:1311.1941 Appendix C (tetraquadric hypersurface sequence);
arXiv:2606.22275 Sections 2.1–2.3 and 4.1.3 (map ranks and generic finite-field
certification). The relative-resultant specialization above is documented as
our derivation, not attributed as a new theorem from those papers. Independent
symbolic determinant, rational-rank, permutation, duality and published-spectrum
tests exercise the implementation. This is not claimed as research novelty.
