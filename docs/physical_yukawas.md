# From holomorphic to physical Yukawa couplings: what is needed

Step 7 of the program asks what it would take to turn the holomorphic couplings
computed here into physical, canonically normalised Yukawa couplings — and
explicitly *not* to jump to numerical fermion masses. This note records what is
established, what each missing ingredient is, and which of them this repository
can or cannot supply.

## 1. What is established

For the tetraquadric quotient `X7862/(Z2 x Z2)`:

| quantity | status | source |
|---|---|---|
| U(1)^4 selection rule for every superpotential and Kahler operator, to all orders in singlet insertions | EXACT (monoid membership); reproduces all 13 published operator tables | `physics/selection_rules.py`, `docs/yukawa_benchmark.md` |
| zero pattern and rank of `Y_u`, `Y_d`, `Y_e` at the Abelian locus | EXACT triple products, restricted to the Gamma-isotypic components | `physics/yukawa.py` |
| dependence of those leading-order matrices on complex structure | **none**: every coupling evaluated uses Koszul identifications that hold for every smooth member of the invariant family | `structural_identification` |
| cohomological vanishing beyond the charges | Koszul level-zero vanishing; computed zeros on isotypic components | `docs/yukawa_benchmark.md` Section 4 |
| largest rank reachable with singlet vacuum values | EXACT upper bound (structural rank of the allowed pattern) | `scripts/rank_candidates.py` |
| which singlets can take a D-flat vacuum value at vanishing FI terms | EXACT (edges on directed cycles of the singlet charge graph) | `scripts/rank_candidates.py` |

## 2. The physical coupling

Schematically, for a coupling of three matter fields `C^I, C^J, C^K`,

    Y_IJK(phys) = e^{K_mod/2} (K^{-1/2})_I^{I'} (K^{-1/2})_J^{J'} (K^{-1/2})_K^{K'} lambda_{I'J'K'}(z, <S>)

with `lambda` the holomorphic superpotential coupling, `K_mod` the moduli Kahler
potential and `K_IJ` the matter-field Kahler metrics. Every factor is needed.

1. **The holomorphic coupling `lambda`, including its normalisation.** We compute
   `lambda` up to one overall constant per coupling type: the trace map
   `H^3(X,O_X) -> C` is fixed only up to normalisation of the holomorphic
   three-form Omega. Fixing it needs the period normalisation of Omega on the
   quotient, i.e. the Weil-Petersson normalisation of the complex-structure
   sector. *Not computed here.*
2. **Singlet insertions.** Most entries of the published and our own Yukawa
   tables need singlet insertions. Their size is `<S>/M` to the power of the
   insertion order, so every such entry needs the singlet vacuum values. These
   are fixed by D-flatness, F-flatness and moduli stabilisation.
   * *D-flatness* at vanishing FI terms is decided exactly here (§1). Away from
     the slope-zero locus the FI terms `FI_a(t) = mu(L_a)(t)` — which we
     reproduce for all 2,012 published models — become nonzero and more singlets
     can be switched on; that corresponds to deforming the line-bundle sum to a
     non-split bundle and is **not analysed** here (see arXiv:1311.1941 for the
     tetraquadric moduli space).
   * *F-flatness* needs the singlet superpotential. Its allowed monomials are
     reproduced exactly (the `SuperPotential` table, 2,012/2,012), but their
     coefficients are higher-order holomorphic couplings that are not triple
     products and are not computed.
   * *Moduli stabilisation*: not addressed.
3. **Matter-field Kahler metrics `K_IJ`.** These are non-holomorphic and in
   general unknown for Calabi-Yau compactifications. A localisation approach for
   line-bundle models is developed in arXiv:1801.09645; it is not implemented
   here. What *is* available is the charge-allowed structure of the kinetic
   matrix (`Kin5`, reproduced 18,108/18,108 cells), which constrains its texture
   but not its values.
4. **The moduli Kahler potential and the values of the moduli** (Kahler moduli,
   complex structure, dilaton): not addressed.
5. **Running to the electroweak scale**: standard MSSM renormalisation-group
   evolution, which needs the boundary values of 1-4 and a supersymmetry-breaking
   spectrum (step 8).

## 3. What can be said without those ingredients

Only statements that survive any choice of the missing factors:

* A coupling **forbidden by the selection rule** vanishes for any normalisation,
  metric and singlet vacuum. Exact.
* A matrix whose **structural rank is below three** has rank below three for any
  singlet vacuum and any Kahler metric (the metric factors are invertible).
  Exact, perturbatively.
* A **leading-order rank** is unchanged by the normalisation and the Kahler
  metric, since both act by invertible matrices; it is the rank of the physical
  matrix at the Abelian locus.

Anything numerical — mass ratios, mixing angles — needs items 1-5 and is **not**
attempted. In particular no fermion masses are quoted anywhere in this
repository.
