# Generic-rank certificates: precise statement and assumptions

This note formalises what the finite-field rank witnesses in
`cohomology/finite_rank.py` and `cohomology/codimension_two.py` actually prove.
It complements `docs/cohomology_certificates.md`, which describes *which* maps
are built; here we justify *why a modular computation licenses a
characteristic-zero statement*.

## 1. Setup

Fix the ambient space `A` (a product of projective spaces) and the multidegrees
of the defining equations. Let

    P = A^N_Z   with coordinates c = (c_1,…,c_N)

be the affine space of coefficient vectors of those equations; a point `c ∈ P`
determines a subscheme `X_c ⊆ A`. Write

    U_sm = { c ∈ P : X_c is a smooth complete intersection of the expected
             dimension }.

Fix a line bundle `L = O_A(k)` and a Koszul differential in the spectral
sequence `E_1^{-p,q} = H^q(A, L ⊗ ∧^p N^*)`. Because the differential is
induced by the defining equations themselves, and the ambient cohomology bases
(Bott/Künneth monomial bases) do **not** depend on `c`, the differential is
represented in those fixed bases by a matrix

    Φ(c) ∈ Mat_{m×n}( Z[c] ),        entries Z-**linear** in c      (A1)

with `m`, `n` determined combinatorially by `k` and the ambient dimensions.

## 2. The proposition

**Proposition R.** Let `r ≤ min(m,n)`, let `c_0 ∈ Z^N`, and let `p` be a prime.
Suppose

    rank_{F_p} ( Φ(c_0) mod p )  ≥  r.                                   (★)

Then

1. there is an `r × r` minor `δ ∈ Z[c]` of `Φ` with `δ(c_0) ≢ 0 (mod p)`; in
   particular `δ(c_0) ≠ 0` in `Z` and `δ` is **not** the zero polynomial;
2. `rank_Q Φ(c_0) ≥ r`;
3. `U_δ := { c ∈ P : δ(c) ≠ 0 }` is a nonempty Zariski-open subset of `P`, and
   `rank Φ(c) ≥ r` for every `c ∈ U_δ`, over `Q` and over `C`;
4. if `r = min(m,n)` then `rank Φ(c) = min(m,n)` for all `c ∈ U_δ`: the generic
   rank is maximal.

*Proof.* (1) A matrix over a field has rank `≥ r` iff some `r × r` minor is
nonzero. Taking minors commutes with the ring map `Z → F_p`, so the minor of
`Φ(c_0) mod p` that is nonzero in `F_p` is the reduction of an integer minor
`δ(c_0)`; hence `δ(c_0) ≠ 0` in `Z`, and a polynomial taking a nonzero value at
one point is not the zero polynomial. (2) is immediate from `δ(c_0) ≠ 0` over
`Q`. (3) `δ ≠ 0` in the integral domain `Z[c]`, so its nonvanishing locus is a
nonempty Zariski-open subset of the irreducible space `P`, and on it the same
minor is nonzero. (4) combines (3) with the structural bound
`rank Φ(c) ≤ min(m,n)`, valid for every `c`. ∎

**Corollary (simultaneous validity).** Let `δ_1,…,δ_s` be the minors certified
for finitely many line bundles/differentials. `P` is irreducible, so
`U_{δ_1} ∩ … ∩ U_{δ_s} ∩ U_sm` is again open, and it is nonempty as soon as
`U_sm ≠ ∅`. Hence all the certified dimensions hold **simultaneously** on a
dense open set of smooth members. ∎

## 3. Why no "good reduction" hypothesis is needed

The certificate uses only the implication

    (nonzero mod p)  ⟹  (nonzero in Z),

never its converse. Equivalently `rank_{F_p}(M mod p) ≤ rank_Q(M)` always holds:
reduction can only *drop* rank. Consequences:

* The prime is unconstrained. `p = 1000003` need not avoid any discriminant,
  resultant, or bad-reduction locus of the family, and `c_0` need not lie in
  `U_sm`. If `p` happened to divide every certifying minor, condition (★) would
  simply fail and the code would report `UNKNOWN` — never a wrong answer.
* Failure is inconclusive in a strong sense: neither `p | δ(c_0)` nor an
  unlucky `c_0` can be distinguished from a genuine generic rank drop. No number
  of failed samples is evidence for a rank deficiency. The implementation
  reflects this: it tries three deterministic seeds and, if none saturates the
  bound, returns `UNKNOWN` rather than an inferred smaller rank.
* Nothing is claimed about `X_c` for `c ∉ U_δ`, and cohomology genuinely jumps
  on such loci.

## 4. From rank to cohomology dimensions

Proposition R bounds a matrix rank; converting it to `h^q` needs the structural
input recorded in `docs/cohomology_certificates.md`:

* **(A4)** the code only accepts the case in which exactly **two** bidegrees are
  occupied in `E_1` and are joined by the single differential in question, so
  `E_∞` is determined by `ker` and `coker` of that one map, whose dimensions are
  `n − r` and `m − r`;
* the surviving degrees `q−p` must lie in `{0,1,2,3}` (checked; otherwise an
  `ArithmeticError` is raised);
* the resulting `(h^0,h^1,h^2,h^3)` must satisfy the exact HRR index
  `Σ(−1)^q h^q = ind(L)` (enforced in `Cohomology.validate`) and Serre duality
  against the independently computed dual bundle (enforced in
  `cohomology/cached.py`). These are independent postconditions: they do not
  enter the proof, they falsify bugs.

## 5. Assumptions to be recorded with any claim

| # | Assumption | Status |
|---|---|---|
| A1 | `Φ(c)` has entries polynomial (here linear) in `c` with integer coefficients, in `c`-independent bases | structural, by construction of the multiplication/Koszul maps |
| A2 | The parameter space `P` is irreducible | true (affine space) |
| A3 | `U_sm ≠ ∅` for the configuration | classical for both benchmarks; input assumption from the geometry registry, not proved by this code |
| A4 | Exactly two occupied `E_1` bidegrees joined by the certified differential | checked at runtime; other cases return `UNKNOWN` |
| A5 | `r = min(m,n)` when a *maximal* generic rank is claimed | checked at runtime |
| A6 | `c_0`, `p`, matrix dimensions and matrix hash are recorded so the witness is replayable | recorded in the certificate JSON |

## 6. Scope statement that must accompany results

> The certified dimensions hold for the **generic** member of the smooth family
> with the given configuration matrix — that is, on a dense Zariski-open subset
> of coefficient space. They do **not** establish the cohomology of any
> particular member, and in particular not of a member admitting a chosen freely
> acting symmetry `Γ`, whose defining equations are constrained to a proper
> closed subfamily. On such a subfamily the dimensions may jump; that case is
> reported as `UNKNOWN`.

This is exactly the wording used by the `complex_structure_scope` field of the
emitted rank certificates.

## 7. Tests exercising the proposition

* `tests/unit/test_finite_rank.py::test_modular_vs_rational_rank` — modular rank
  against an independent exact rational rank on the same integer matrix.
* `tests/unit/test_finite_rank.py::test_modular_rank_is_a_lower_bound` — the
  one-sided direction: an explicit integer matrix whose rank over `Q` exceeds
  its rank modulo a bad prime, confirming that failure mod `p` is inconclusive
  and that the certificate never uses that direction.
* `tests/unit/test_finite_rank.py::test_certified_minor_is_nonzero_over_Z` —
  extracts an `r × r` submatrix that is invertible mod `p` from a real
  certificate and checks its **integer** determinant is nonzero, i.e. step (1)
  of Proposition R on actual data.
* `tests/regression/test_certificates.py` — replay of stored rank certificates.
