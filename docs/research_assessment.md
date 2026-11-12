# Research assessment

Reproduction and validation work is now substantially stronger than in the first
session, and there is one genuinely new algorithmic result. Novelty is assessed
against the primary references, not against this repository's own history.

## What is reproduction

Exact topology (now cross-checked against the published record for all 68
favourable CICYs: c2 68/68, Euler numbers 68/68), the golden X7447 model, the
Section-5 hierarchy, the analytic/Koszul cohomology backends, and the X7862
scans. The exact agreement with the published Oxford catalog — the same models,
not merely the same count, at every box from K=2 to K=7 for Γ=2 and at K=5 for
Γ=4 (all 58 models) — is a validation result, not a new finding. What it does
establish is that the pipeline reproduces a published exhaustive scan
model-for-model rather than statistically.

## What is new here

**A complete, certificate-producing form of the slope obstruction**
(`docs/slope_obstruction_note.md` Propositions 3–5). The published scan needs
"μ(L_a)=0 somewhere in the interior of the Kähler cone" at several stages and
obtains it by solving the system exactly where possible and numerically
otherwise. The earlier implementation replaced this with a finite coefficient
box, which is sound but incomplete. The new rule decides, in exact integer
arithmetic and with no coefficient bound, whether the span of the charge vectors
contains a vector whose slope matrix is entrywise one-signed — the exactly
optimal single-combination obstruction on these geometries (Proposition 4) — and
returns an explicit integer witness when it does. Because the condition is
monotone in the column set it prunes at every branch depth.

Measured on X7862, Γ=2: complete bundles constructed fall from 146,425 to 52,800
at K=3 and from 294,130 to 118,577 at K=4, and the rule removes exactly one
spurious ambient-row orbit at K=3 and again at K=4, bringing the orbit sets into
exact agreement with the published catalog at every box scanned.

That last point is the substance: the rule corrected a result rather than merely
accelerating one. Its wall-clock advantage did not survive the subsequent bitset
re-engineering of the search core (the indexing removes the same work more
cheaply), so the honest summary is that it buys correctness, not speed.

Separately, the bitset-indexed core is a straightforward engineering result:
3x to 7.5x faster with bit-identical survivor sets on all seven re-run domains,
which is what made K=5, K=6, K=7 and the Γ=4 catalog affordable at all.

Secondary new items, all elementary but not previously implemented here: the
separable partial anomaly budget (a genuine branch bound, active from K=3), the
Bogomolov pairing from (4.6) (exact, and measured to prune nothing on these
domains — a negative result), and the index-divisibility obstruction
`d_X | 3|Γ|`, which is the repository's only verdict that holds for every K and
which correctly predicts two zero entries of the published catalog.

## What is not new, and is not claimed

The identity ind(V) = ind(∧²V) is stated in arXiv:1307.4787. The finiteness
discussion of §6 there already bounds the topology of poly-stable bundles; our
charge inequality `Σ_a(|k_a|² − s_a²) ≤ C_X` is that anomaly bound rewritten, and
the accompanying bound on `Σ_a|k_a|²` degenerates at the Kähler-cone boundary, so
no finiteness theorem is claimed (`docs/exact_obstructions.md` C1).

**A charge-unbounded slice theorem** (`docs/exact_obstructions.md` S1-S2). This
is the strongest result of the session. The slope condition forces every model
into `p^⊥` for a primitive positive integer `p`, decomposing the landscape
exhaustively over slope directions; and on any slice with
`(Σp)² > (h−1)|p|²` the summed anomaly condition becomes a positive definite
quadratic form, bounding every charge by an explicit radius. The admissible
column pool of such a slice is then a finite exact set carrying **no K
parameter**, so searching it exhausts the slice over all integer charges. 425 of
the 469 slices with `p` entries ≤ 10 on X7862 come back provably empty, in 37
seconds total. This is the repository's first family of results that are not
bounded-domain, other than the divisibility rule, and it converts part of the
empirical saturation into proof.

Its limits are equally clear, which is what makes it usable: the union over all
positive primitive `p` is infinite, and the slices failing the criterion are
genuinely different — real models live there, the pool is infinite, and only the
index (cubic) can bound the charges. That is a sharply stated open problem
rather than a vague gap.

## An empirical-saturation observation, carefully labelled

The Γ=2 survivor set is identical at K=4, 5, 6 and 7, and no survivor uses a
charge above 4. Per Rule 3 of the master plan this is `EMPIRICAL_SATURATION`,
not a no-go theorem. The slice theorem above upgrades part of it to proof — on
469 slope directions the saturation is now a theorem rather than an observation
— and localises the rest to slices where `F` fails to be positive definite. The
remaining open step is precise: bound the semialgebraic set
`{k : F(k) ≤ 0, ind(k) ∈ [−3|Γ|, 0]}`. Ray-wise it is bounded (`F(k) ≤ 0` forces
`s(k) ≠ 0`, so the index is unbounded along every such ray); the uniform
statement is not yet proved.

## Where the remaining cost is

The fourth-column generation loop, previously dominant, has been indexed away.
What remains at K=7 is the depth-3 to depth-4 transition (14.5 million admissible
extensions) and the per-node span decision. Beyond that, the next real test is
h^{1,1}=5 (X7447), where the published catalog offers 93 models at Γ=2 and 430 at
Γ=4, and where the combinatorics are genuinely harder.

The dominant *scientific* gap is unchanged: cohomology and equivariance on an
explicitly specified free-action subfamily, without which nothing can be
promoted from `UNKNOWN_BOUNDED` to `SAT_BOUNDED`.
