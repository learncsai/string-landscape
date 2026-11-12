# Audit of the signed combined slope-matrix rule

Status of this document: mathematical audit requested for the rule implemented
as `signed_slope_matrices` in `physics/stability.py::necessary_stability`,
including the `coefficient_bound=1` restriction. Conclusions are stated at the
end. Nothing here is claimed as new mathematics; §5–§7 record what *is* new in
this repository.

## 1. Setting and notation

`X` is a smooth favourable CICY threefold with `h = h^{1,1}`, integral basis
`J_1..J_h` given by restricted ambient hyperplane classes, triple intersection
numbers `d_{ijl} = ∫_X J_i J_j J_l ∈ Z` (totally symmetric). A Kähler class is
`J(t) = t^i J_i`. The declared search domain restricts `t` to the **positive
ambient chamber**

    T_+ = { t ∈ R^h : t^i > 0 for every i } ,

which for a favourable CICY is contained in the Kähler cone K_X, and for the two
benchmark geometries (X7862, X7447 — both complete intersections in products of
P^1 with `cone = POSITIVE_ORTHANT` in the registry) is taken to equal K_X.

For `k ∈ Z^h` write `L = O_X(k)` and

    μ_k(t) = d_{ijl} k^i t^j t^l ,          (slope, up to the usual positive factor)
    M(k)_{jl} = d_{ijl} k^i ,               (symmetric integer matrix, Z-linear in k)
    μ_k(t) = t^T M(k) t .

`k ↦ M(k)` is a homomorphism of abelian groups: `M(k + k') = M(k) + M(k')`.

## 2. The condition the rule is testing

For `V = ⊕_{a=1}^5 L_a` with `c_1(V) = 0`, supersymmetry at the split locus
requires `V` to be poly-stable with respect to *some* Kähler class. A direct sum
of line bundles is poly-stable exactly when all summands have equal slope; since
`μ(V) = 0`, this means a **common zero of all five slopes**:

    (SZ)   ∃ t ∈ T_+ with μ_{k_a}(t) = 0 for a = 1..5.

The rule tests a family of necessary conditions for (SZ).

**Lemma 1 (sign obstruction).** Let `M ∈ Sym_h(Z)`, `M ≠ 0`, with all entries
`≥ 0` (or all `≤ 0`). Then `t^T M t ≠ 0` for every `t ∈ T_+`.

*Proof.* `t^T M t = Σ_{j,l} M_{jl} t^j t^l`. Every summand has weakly the same
sign because `t^j t^l > 0`, and at least one `M_{jl} ≠ 0` contributes strictly.∎

**Proposition 2 (necessity of the combined test).** Assume (SZ) holds with
witness `t_*`. Then for every `c ∈ R^5` the matrix
`M(c) := Σ_a c_a M(k_a) = M(Σ_a c_a k_a)` satisfies
`t_*^T M(c) t_* = Σ_a c_a μ_{k_a}(t_*) = 0`, hence by Lemma 1 `M(c)` is either
zero or has both a strictly positive and a strictly negative entry.

*Contrapositive (the pruning rule):* if for **some** `c ∈ Z^5` the matrix
`M(Σ_a c_a k_a)` is nonzero and entrywise one-signed, then (SZ) fails, and the
candidate `V` admits no poly-stable Kähler class in `T_+`. ∎

This is exactly what `necessary_stability` implements: `signed_matrix_ok`
returns `False` precisely when the matrix is nonzero and entrywise one-signed;
the `c = e_a` cases are checked first, then all `c ∈ {-1,0,1}^5` with first
nonzero entry positive (`c` and `−c` give the same obstruction).

## 3. Assumptions under which it is necessary

1. **Kähler domain.** `t ∈ T_+`, strictly. The proof uses `t^j t^l > 0`. A
   rejection is therefore a statement about the declared domain. It extends to
   the full Kähler cone only under the (declared, geometry-specific) assumption
   `K_X = T_+`. For X7862 and X7447 this is the registry's `POSITIVE_ORTHANT`
   declaration; it is an input assumption, not something the code proves.
2. **Split structure group.** `V` is a sum of line bundles; poly-stability
   forces equal slopes summand by summand. If a model were allowed to use a
   non-split deformation of `V`, this necessity argument would not apply — the
   declared target is the split `S(U(1)^5)` locus.
3. **Integrality/exactness.** `d_{ijl}` and `k_a` are exact integers; the test
   is pure integer arithmetic with no tolerance.
4. Nothing else. In particular the test does not assume anything about
   cohomology, the anomaly condition, or `Γ`.

## 4. Is the coefficient restriction complete?

**No, and this is the crucial distinction.**

* *Soundness (one-sided).* Every individual rejection is a proof, by
  Proposition 2, independently of which `c` produced it. Enlarging or shrinking
  the coefficient set cannot make an emitted rejection wrong.
* *Completeness (fails).* Passing the test with `c` ranging over a finite box
  does **not** prove (SZ) is satisfiable. A candidate can be slope-infeasible
  while every `c` in the box gives an unsigned matrix. So the rule is an
  incomplete rejection test, i.e. a NECESSARY-condition filter, never a
  sufficient acceptance criterion — which is how the repository already labels
  it (`SLOPE` is `NECESSARY`, `can_certify_acceptance = False`).

Two structural remarks about the box that were not previously recorded:

* Because `Σ_a k_a = 0` on the declared domain, `M(c + λ(1,1,1,1,1)) = M(c)` for
  every `λ ∈ Z`. The test therefore depends only on `[c] ∈ Z^5 / Z·(1,…,1)`.
  The box `{-1,0,1}^5` is exactly the set of `c` with spread
  `max(c) − min(c) ≤ 2`, and the 121 vectors the implementation enumerates fall
  into only **106** distinct classes: about 13% of the work is redundant.
* Consequently "coefficient bound 1" is *not* the same as "small coefficients":
  e.g. `(2,1,0,0,0) ≡ (1,0,-1,-1,-1)` is inside the box, while
  `(2,0,0,0,-1)` (spread 3) is not.

## 5. Does an incomplete rule endanger `UNSAT_BOUNDED`?

No, provided the rule is sound. `UNSAT_BOUNDED(D)` asserts: *every state of the
finite domain `D` has been accounted for and none satisfies all declared
conditions*. A state is "accounted for" if it is enumerated and then rejected by
a condition that is **necessary** for the declared target. Incompleteness of a
necessary-condition test can only *keep* states in the survivor set — which
makes `UNSAT_BOUNDED` harder to reach, never easier. It cannot create a false
`UNSAT_BOUNDED`.

By contrast a rule that is *unsound* (rejects a state that could still be a
valid model) would invalidate `UNSAT_BOUNDED`. Proposition 2 shows this rule is
sound under the §3 assumptions, so **no reclassification is required**: the rule
may continue to contribute to `UNSAT_BOUNDED`, with the domain caveat of §3.1
carried in the certificate (`kahler_domain: positive ambient chamber`).

This conclusion is load-bearing. The independent replay of the full K=1 domain
(`benchmarks/x7862/k1-independent-replay-chiral.json`) shows that with
unrestricted pair indices **all 1,932** index- and anomaly-consistent candidates
are eliminated by this rule and by nothing else. The K=1 `UNSAT_BOUNDED` result
in the *declared GUT_FULL domain with nonpositive pair indices* does not depend
on it (the pair-index condition already empties that domain), but the stronger
GUT_CHIRAL statement does.

## 6. The complete form of the same obstruction

Proposition 2 quantifies over all `c ∈ Z^5`, but the implementation samples a
box. The quantified version is decidable exactly, in rational arithmetic, with
no coefficient bound at all.

**Proposition 3 (exact obstruction cone).** Let `S = span_R{k_1..k_5} ⊆ R^h` and
let `P = { k ∈ R^h : M(k)_{jl} ≥ 0 for all j,l }`, a rational polyhedral cone.
Then some `c ∈ Z^5` yields a signed obstruction **iff** `S ∩ P` contains a point
`k` with `M(k) ≠ 0`.

*Proof.* `S = { Σ_a c_a k_a : c ∈ R^5 }` and `M` is linear, so `M(S)` is the set
of attainable combined matrices; `P` is the entrywise-nonnegative preimage.
`−c` covers the entrywise-nonpositive case. A rational cone point can be scaled
to an integer point, and `c` recovered by solving the (rational, consistent)
linear system `Σ_a c_a k_a = k`. ∎

For both benchmark geometries `d_{ijj} = 0`, so `M(k)` has zero diagonal, and a
symmetric matrix with zero diagonal is copositive iff its off-diagonal entries
are all `≥ 0`. Hence for X7862 and X7447:

**Proposition 4 (per-combination optimality).** For a fixed `c`, the implemented
test is *exactly* the condition "`μ_{k_c}` has no zero in `T_+`".

*Proof.* (⇐) is Lemma 1. (⇒) Suppose `M := M(k_c)` has `M_{jl} > 0` and
`M_{j'l'} < 0` for two off-diagonal positions (the diagonal vanishes). Put
`t(T)` equal to `T` in positions `j,l` and `1` elsewhere: `μ(t(T)) = 2M_{jl}T² +
O(T) → +∞`. The analogous choice at `j',l'` gives `μ → −∞`. `T_+` is connected
and `μ` continuous, so `μ` vanishes somewhere in `T_+`. Hence a `c` whose matrix
is not one-signed cannot be turned into an obstruction, no matter how the test
is strengthened. ∎

This also shows the published step-1 condition "`μ(L)=0` somewhere in the
interior of the Kähler cone" (arXiv:1307.4787 §5, step 1(ii)) is *equivalent* to
the individual signed-matrix test on these two geometries — the code decides
that step exactly, where the published scan solved it exactly or numerically.

So on these two geometries nothing is lost per coefficient vector; the only
incompleteness is the truncation of the `c`-search, and Proposition 3 removes
it. (On a geometry with `d_{ijj} ≠ 0` the entrywise test is strictly weaker than
copositivity of `M(k_c)`, and Proposition 4 fails; the rule stays sound.)

**Proposition 5 (monotonicity ⇒ branch pruning).** If `S' ⊆ S` and `S'` already
contains an obstruction point, so does `S`. Therefore the test applied to the
span of any *prefix* of columns prunes every completion of that prefix. ∎

`M(k) = 0 ⇒ k = 0` holds for both benchmarks (for the tetraquadric,
`M(k)_{jl} = 2(k^m + k^n)` over the complementary pair, and all complementary
pairwise sums vanishing forces `k = 0`), so the cone `S ∩ P` is pointed, its
nonzero points are found by extreme-ray enumeration, and Proposition 3 becomes a
finite exact integer computation. This is implemented as `span_slope_obstruction`
in `physics/stability.py`, with an explicit integer witness `k_c` in every
rejection certificate. Where the pointedness guard fails the implementation
declines to prune.

## 6b. A dual decision procedure

The primal test enumerates candidate extreme rays of `S ∩ P`, which costs
`C(#forms, r−1)` integer kernel computations per node and dominated the runtime
on `X7447` (90% of a profiled scan). The same decision has a cheaper dual form.

**Proposition 6.** Let `P` be pointed and let `r_1..r_s` be its extreme rays. Let
`A` be a basis of the annihilator `S^⊥`, `d = dim S^⊥ = h − rank S`. Then
`S ∩ P = {0}` **iff** some `φ ∈ S^⊥` satisfies `⟨φ, r_i⟩ > 0` for every `i`;
equivalently, **iff** `0 ∉ conv{ A r_1, …, A r_s } ⊂ R^d`.

*Proof.* `P` pointed means its base `B = conv{r_i}` is compact and `0 ∉ B`. If
`S ∩ P = {0}` then `S ∩ B = ∅`, and a compact convex set can be strictly
separated from the closed subspace `S`: the separating functional must vanish on
`S` (a subspace), so it lies in `S^⊥` and is strictly positive on `B`, hence on
every `r_i`. Conversely such a `φ` vanishes on `S` and is positive on `P \ {0}`,
so the two meet only at the origin. The reformulation is Gordan's alternative
applied to the projected points `A r_i`. ∎

Two consequences make this fast exactly where the search spends its time.
`d` *shrinks* as a prefix grows, so the deepest and most numerous nodes are the
cheapest: `d = 1` reduces to "do the projected scalars take both signs", `O(s)`;
`d = 2` is an angular-gap test, `O(s log s)`. For `h = 5` the depth-3 and
depth-4 nodes have `d = 2` and `d = 1`. Larger `d` (shallow nodes) falls back to
the primal enumeration, which also remains the reference implementation and the
producer of the integer witness recorded in certificates.

The extreme rays are computed once per geometry: `2h` of them for both
benchmarks — the `h` coordinate vectors `e_i`, and the `h` vectors with a single
entry `−(h−3)` and the rest `1` (`(1,1,1,−1)` for X7862, `(1,1,1,1,−2)` for
X7447). Dual and primal are differentially tested against each other on 12,000
random column sets across every span rank, with no disagreement, and the search
re-run on every recorded domain produced bit-identical survivor sets. Measured
effect: 1.5× on X7862 (K=4 span 43.6 s → 28.8 s) and 5.5× on X7447.

## 7. Measured consequences

| Population | box `c ∈ {-1,0,1}^5` | box bound 2 | complete cone (Prop. 3) |
|---|---:|---:|---:|
| X7862 K=1 Γ=2 GUT_CHIRAL, index+anomaly survivors (1,932) | 0 survive | 0 | 0 |
| X7862 K=2 Γ=2, candidates passing all other declared conditions (1,260) | 120 survive | 120 | 120 |
| X7862 K=3 Γ=2, same stage | **192 survive** | 192 | **168** |
| X7862 K=4 Γ=2, same stage | **264 survive** | — | **240** |

At K ≤ 2 the truncation is lossless, verified rather than assumed. **At K = 3 it
is not.** The box retains 24 column-canonical candidates (one extra ambient-row
orbit) that the complete test rejects, among them

    ((−3,−1,1,2), (0,1,−1,0), (0,1,−1,0), (1,1,−1,−1), (2,−2,2,−1)),

for which the complete test returns the explicit integer witness
`k_c = (1,0,0,0)`, whose slope matrix is entrywise nonnegative and nonzero.
That candidate does not appear in the published catalogue either; with the
complete test our K=3 orbit set equals the published one exactly (7 orbits).
So the coefficient box is a genuine weakness that first shows up at K=3, and the
earlier K ≤ 2 agreement was luck rather than a property of the truncation.

None of the K=2 or K=3 survivors — the ones carrying exact rational or
real-algebraic slope witnesses, and all 10 published Γ=2 models — is rejected by
the complete test, as soundness requires.

As a *branch* rule (Prop. 5) the complete test removes 2,730 of 10,573 retained
depth-2 prefixes at K=2 and cuts completed canonical bundles from 146,425 to
52,800 at K=3 and from 294,130 to 118,577 at K=4.

Wall-clock comparison against the finite box moved twice as the engine changed:
the complete rule was faster before bitset indexing (K=3: 55.7 s vs 120.1 s),
slower just after it (K=4: 43.6 s vs 36.7 s), and faster again once the dual
decision of §6b landed (K=4: 28.8 s vs 36.7 s). None of that changes why it is
the default: it is the rule whose survivor set matches the published catalog.

## 8. Verdict

1. Exact condition tested: Proposition 2 with `c ∈ {-1,0,1}^5`.
2. Necessary for a valid model: yes, under §3 (positive ambient chamber, split
   `S(U(1)^5)` structure, exact integer topology).
3. Coefficient restriction `{-1,0,1}`: **not** complete as a decision procedure;
   sound as a rejection rule; on the benchmark geometries it is optimal per
   coefficient vector (Prop. 4) and its truncation was empirically lossless on
   every domain scanned so far (§7).
4. Safe for certified exhaustive search: **yes** — an incomplete but sound
   necessary condition can only retain states, never wrongly discard them.
   No reclassification is required; the rule keeps `can_safely_prune = True`
   and `can_certify_acceptance = False`, and the certificates continue to
   record the Kähler-domain assumption.
5. Superseded in strength by the complete cone form (Prop. 3), which is now the
   default and additionally prunes at every branch depth (Prop. 5).

## 9. Beyond the signed test: a Polya hierarchy and an exact decision

Section 4 showed the coefficient test is exact per combination only when
`d_ijj = 0`. On other geometries, and even on `d_ijj = 0` geometries when no
single combination is one-signed, a bundle can pass every sign test yet have no
common slope zero in the open orthant. The 68-geometry suite (Phase 8) meets
such bundles. Two exact tools, both in `physics/stability.py`:

**Proposition 7 (Polya certificates).** If `(t_1+...+t_h)^N * sum_a c_a mu_{k_a}(t)`
has all coefficients `>= 0` and not all zero, the slopes have no common zero in
`T_+`. Every form strictly positive on the closed simplex has such an `N`
(Polya's theorem); `N = 0` is the signed test. The coefficients are linear in
`k_c`, so a certificate is found by a linear program and verified in exact
integers (`polya_obstruction`, `verify_polya_certificate`).

*Measured.* On the catalog geometries tested (5256, 6804, 5273, 7447 and the
tetraquadric) no charge vector with entries in `[-2,2]` gains a certificate at
`N <= 4` that it lacked at `N = 0`. On `d_ijj = 0` geometries this is a theorem
(Proposition 4); on the others it is an observation. Consistently, none of the
suite's extra survivors gets a Polya certificate: their obstruction, where it
exists, is *joint* (no simultaneous zero), not a single positive combination.

**Proposition 8 (exact decision for rank h-1).** If the charge matrix has rank
`h-1`, set `t_h = 1` (allowed at interior points) and compute a lexicographic
Groebner basis of `h-1` independent slopes. In shape position this gives
`t_i = g_i(x)` and a univariate `p(x)`; each real root of each irreducible factor
of `p` is isolated in an exact rational interval, the other coordinates are
enclosed by rigorous interval arithmetic, and the slopes are checked to vanish
identically modulo the factor. An interior root is an exact real-algebraic
witness (`STABLE_CERTIFIED`); if no real root is interior, there is no common
zero in the open orthant (`UNSTABLE_CERTIFIED`). Bases not in shape position are handled factor by factor: factors of `p` with no positive real root are discarded, a rational root is substituted and the smaller system decided recursively, and over an irrational factor `f` the remaining coordinates are solved linearly in `Q[x]/(f)`. Positive-dimensional zero sets (rank below `h-1`) are
`UNDECIDED` (`decide_interior_slope_zero`).

Validated on the tetraquadric: the published model with witness `t=(1,1,1,1)`
is certified stable with exactly that witness; the spurious K=3 candidate has a
positive-dimensional zero set (UNDECIDED here) and is excluded by the signed
test at `N = 0`, so the tools are complementary.

**Soundness validation.** Published catalog models are poly-stable, so the
decision must never call one unstable. On 548 published models across ten keys
it certifies 214 stable and calls none unstable (the rest are undecided, mostly
rank < h-1). A first implementation failed this check on 91 models through two
bugs — a positive root whose isolating interval began at zero was dropped, and a
remainder was taken in the wrong order so that constant coordinates looked like
zeros — both fixed and guarded by `tests/unit/test_slope_certificates.py`.
