# Computing the Γ-representation on H^q(X, L)

This closes the blocker the project had carried since the first session. The
descent machinery of `docs/downstairs_descent.md` needed the
Γ-representation content of the upstairs cohomology and previously read it from
a published table. It is now computed from the explicit group action.

## 1. The method

The Koszul resolution of `O_X` by `⊕_p ∧^p N^* ⊗ L` is Γ-equivariant, so in the
representation ring of Γ

    Σ_q (−1)^q [H^q(X,L)] = Σ_p (−1)^p Σ_q (−1)^q [H^q(A, L ⊗ ∧^p N^*)] .   (★)

Every term on the right is the cohomology of a line bundle on a product of
projective spaces, and its character is elementary.

**Ambient characters.** For a factor `P^n` let `M` be the group element acting on
that factor's linear forms, and `h_m` the complete homogeneous symmetric function
of its eigenvalues — computed without ever finding the eigenvalues, from the
characteristic polynomial via `h_m = Σ_i (−1)^{i−1} e_i h_{m−i}`. Then by Bott

    tr on H^0(P^n, O(m))  = h_m                       (m ≥ 0)
    tr on H^n(P^n, O(m))  = det(M)^{m+n} · h_{−m−n−1} (m ≤ −n−1)
    H^*(P^n, O(m)) = 0                                (−n ≤ m ≤ −1)

the middle case being Serre duality. Künneth multiplies across factors and the
cohomological degree is the sum of the per-factor degrees. Everything is exact:
entries are roots of unity, handled symbolically.

**The normal bundle twist.** `N = ⊕_j O(q_j)` and Γ acts on the defining
polynomials by a matrix `ρ`. A factor-preserving element can only mix
polynomials of equal multidegree, so the polynomials are grouped by multidegree
and the trace on `∧^p N^*` is a product of elementary symmetric functions
`e_{p_c}(ρ_c^{−1})` over those groups. When the polynomials are invariant this
collapses to a plain sum over subsets — but it does **not** collapse in general,
and getting it wrong is detectable (see §4).

**Decomposition.** For abelian Γ the multiplicity of a character is the finite
Fourier transform `mult(χ_c) = |Γ|^{-1} Σ_a character(a) · conj(χ_c(a))`.

## 2. Resolving the individual H^q

(★) determines the *alternating sum*. Three regimes, in increasing difficulty:

* **A collapsing Koszul complex.** When no differential can join two occupied E1
  nodes — the same bidegree-support test the non-equivariant code already uses —
  each `H^q(X,L)` is simply the sum of the E1 characters with `q − p` equal to
  that degree. This resolves every degree separately, including `H^1` and `H^2`
  of a pair bundle, which is what the vector-like Higgs sector needs.
* **A single differential between two nodes.** The differential is
  multiplication by the defining polynomial and is Γ-equivariant, so it
  preserves isotypic components: the rank splits character by character, and
  `ker` and `coker` per character give the two surviving degrees. Implemented as
  `equivariant_degrees_by_ranks` for a single defining polynomial, using a
  generic member of the published invariant family and the explicit action
  matrices of §2b. The equivariance `M ρ_src(γ) = ρ_tgt(γ) M` is *checked*, not
  assumed — it is a strong test of the action matrices, the invariant-polynomial
  parsing and the basis conventions all at once.
* **Anything more** (several differentials, higher pages) is refused.

`equivariant_cohomology` tries collapse first, then ranks.

### 2b. Explicit action matrices

For the rank path the characters are not enough; we need the operators. On a
`P^1` factor with basis `x_0^i x_1^{m−i}` (index = exponent of the first
coordinate, matching `cohomology/finite_rank.basis`):

    H^0(O(m)) :  Sym^m(B)
    H^1(O(m)) :  det(B)^{-1} · (Sym^{−m−2}(B))^{-T}      (Serre duality)

and Künneth gives the ambient action as a Kronecker product. Their traces agree
with the symmetric-function formulas of §1 — two independent computations of the
same number, checked in the test suite.

### 2c. The older, weaker statement

Before the above, only the alternating sum was available, giving:

* **A single nonzero degree.** When exactly one `H^q(X,L)` is nonzero — decided
  independently by our own exact dimension code, not assumed — the alternating
  sum *is* that representation, up to the sign `(−1)^q`. No map ranks, no
  spectral sequence.
* **Several nonzero degrees.** The individual representations are not separable
  by (★) alone. This is not a defect of the implementation: `H^1` and `H^2` of a
  pair bundle can be isomorphic as Γ-representations, in which case the
  alternating sum is zero and carries no information about either.

| sector | from the alternating sum alone | with collapse + ranks |
|---|---|---|
| **chiral** — families of `Q, u^c, e^c, d^c, L` | yes, always | yes |
| **vector-like** — Higgs doublet pairs, vector-like triplets | no | **yes** |

The chiral content is `H^1 − H^2`, exactly what (★) gives, so three families and
the absence of chiral exotics follow from the geometry, the group action and the
charges with no cohomology input at all. The vector-like sector needed §2's
finer treatment, and now has it: on the tetraquadric every bundle of every
published model is resolved, and the **complete** charged spectrum — chiral and
Higgs — is derived for all 22 of them.

## 3. The equivariance obstruction, checked not assumed

The matrices form a central extension `G` of Γ, not Γ itself. On the
tetraquadric the two generators of the `Z_2 × Z_2` do **not** commute in `GL_8`:
their commutator is `−1` on every `P^1` factor. That is trivial on the ambient
space but acts on `O(k)` by `(−1)^{Σ_i k_i}`. Hence

> `O(k)` carries a Γ-equivariant structure for this lift exactly when every
> central element of `G` acts trivially on it — for the tetraquadric, when
> `Σ_i k_i` is even.

When it fails the cohomology carries only a *projective* representation and the
computed function is not a character of Γ. `is_equivariant` performs this check
and the computation refuses rather than returning a meaningless decomposition;
`is_representation` is a second, independent net (a projective character
decomposes into non-integral or negative multiplicities).

Different lifts differ by a character of Γ — precisely the freedom recorded as
`EquivStr` in the published data, and the reason comparisons are made up to that
shift.

## 4. Validation

Against the published `GCoh` / `GCoh2` tables of the standard-model database,
across **all 13 geometries** carrying downstairs models, comparing **all four
cohomological degrees** of every table:

| | |
|---|---|
| models | 2,012 |
| cohomology tables compared (9,181 single + 18,640 pair) | 27,821 |
| **exact agreement** | **27,821** |

Nothing representation-theoretic enters the computation; the published tables
are only the comparison target.

**The convention that made this exact.** The published tables are the *raw*
characters of the lift: the equivariant structure (`chi_a` for `L_a`,
`chi_a + chi_b` for a pair) is applied only when the downstairs spectrum is
formed, which is why that reproduction needs the shift. The comparison is
therefore raw against raw. Only tables that are not invariant under their shift
can tell the two readings apart; there are 694 of them, all vector-like pair
bundles, and all 694 match the raw computation while none matches the shifted
one. An earlier version of this document compared the shifted table and
reported those 694 as unexplained "relabellings"; that was our error, not a
discrepancy in the published data. 640 published pair entries that are
unevaluated rank expressions are recorded separately and not compared.

Two bugs were found and fixed by this comparison, which is the point of doing it:

1. **Choosing the symmetry.** CICY 7487 carries four distinct freely acting
   `Z_2 x Z_2` symmetries differing only in their action on the defining
   polynomials, and different models use different ones. Picking one by a
   structural heuristic gave 1600/1620; using each model's own symmetry number
   from its database key gives 1620/1620.
2. **The polynomial twist.** Ignoring `rho` is correct only when the defining
   polynomials are invariant. It is not, for most geometries here.

Beyond the tables, the end-to-end chiral derivation was run on a sample of 136
models spanning all 13 geometries: in every case the full chiral spectrum is
derived from first principles and gives exactly three families of `Q, u^c, e^c,
d^c` and `L`.

## 5. Scope and limits

* **Abelian Γ only.** Non-abelian groups need genuine character tables; refused,
  not approximated.
* **Factor-preserving elements only.** An element permuting projective factors
  does not preserve a line bundle of non-symmetric multidegree, so such a bundle
  is not equivariant at all; refused.
* **The rank path is implemented for a single defining polynomial** (one Koszul
  step), which covers the tetraquadric but not the codimension-two geometries;
  there only the collapsing cases are resolved.
* **A generic member of the invariant family** is used for the rank
  computation, so the answers are the generic ones; cohomology can jump on
  special members, exactly as for the non-equivariant rank certificates.
* The free action itself and the invariant defining family are taken from the
  published symmetry data; the smoothness and freeness of the action are input
  assumptions, not re-derived here.
* Nothing here addresses supersymmetry breaking or moduli stabilisation.

## 6. A downstairs search, not a verification

With the complete spectrum derivable, the pipeline can be pointed at our own
exhaustive upstairs results instead of at published models
(`scripts/search_standard_models.py`). On X7862 with `|Γ| = 4`, starting from the
58 ambient-row orbits of our exhaustive `K = 5` scan:

| stage | count |
|---|---:|
| upstairs orbits examined | 58 |
| rejected: some `L_a` not Γ-equivariant (`Σ k` odd) | 26 |
| equivariant, cohomology fully determined | 32 |
| no Wilson line / equivariant structure works | 11 |
| **orbits admitting a three-family, exotic-free MSSM with a Higgs pair** | **21** |

The Wilson line is not guessed: in `SU(5)` the flat bundle is
`diag(χ_T,χ_T,χ_T,χ_D,χ_D)` with determinant one, so `χ_T^3 χ_D^2 = 1`, which for
a group of exponent two forces `χ_T` trivial and leaves `χ_D` free — exactly the
convention the published database uses. Equivariant structures are enumerated
subject to `Σ_a e_a = 0` so that `det V` descends.

**All 10 published orbits are recovered, and 11 further orbits are found.** That
is not a contradiction: the published standard-model database describes itself as
*"a partial scan"*, in those words. Every one of the 11 is a model from the
published *GUT* catalog for `{7862, 4}`, passes every exact upstairs check, has
`h^1(V) = 12 = 3|Γ|`, and carries no colour-triplet Higgs.

They should be called *candidates*, not confirmed new standard models. Our
acceptance is exactly three conditions — three chiral families, no charged chiral
exotics, at least one Higgs doublet pair — and the published scan may have
applied further conditions we have not identified. The cohomology is that of a
generic member of the invariant family. Singlet sectors, Yukawa textures,
supersymmetry breaking and moduli stabilisation are untouched.

## 7. What this changes

The pipeline no longer needs published representation data at all: geometry,
group action, invariant defining family and charge matrix suffice to produce a
complete charged downstairs spectrum. That is the difference between verifying
published models and searching for them.
