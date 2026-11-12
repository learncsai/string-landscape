# Certification semantics

Every physics constraint carries its name, mathematical status, reference,
input assumptions, safe-pruning flag, and acceptance flag. PASS means the
specific recorded condition passes; it does not imply that all physics passes.
EXACT arithmetic is distinct from a sufficient physical acceptance criterion.

A rational interior t with identically zero slopes is a sufficient exact
polystability witness. A floating-point root is NUMERIC_WITNESS. A failed root
search is UNKNOWN_STABILITY. A signed matrix obstruction is necessary only
inside the declared positive chamber. The zero matrix is never an obstruction.

UNSAT_UNBOUNDED is emitted only by an exact obstruction whose conclusion holds
for every K, currently only the index-divisibility rule of
docs/exact_obstructions.md P2: if d_X = gcd{ind(L)} does not divide 3|Gamma|,
no five-line-bundle sum on that geometry can have the required chiral asymmetry,
whatever the charge box. The verifier recomputes d_X rather than trusting the
claim. This is the one outcome in the vocabulary that is not domain-bounded, and
it is still restricted to the declared bundle class (five line bundles, split
S(U(1)^5), that geometry, that |Gamma|).

UNSAT_BOUNDED requires complete enumeration and exact necessary rejection of
all candidates, including any late spectrum rejections. UNKNOWN candidates
prevent this result. Incomplete scans always report UNKNOWN_BOUNDED even when
there are no survivors so far. SAT_BOUNDED is deliberately not emitted yet:
full holonomy/commutant and nonzero anomaly effectivity certification are missing.
The reserved target names cannot bypass these gates.

The search JSON records the finite domain, nominal sizes, filter counters,
source hash, input hashes, completion position, survivor hashes, and per-candidate
checks. It is an auditable software certificate, not a proof-assistant theorem.
The independent verifier replays affordable domains with the separate ordered
four-column brute-force enumerator. An explicit state limit refuses expensive
replays; increasing the limit is a computational decision, not proof evidence.
Large branch/pruning proof logs remain unimplemented. Checkpoints are restart
artifacts, not adversarial proofs; checksums detect corruption, not malicious
rewriting. Final independent replay does not trust a checkpoint.

Candidate verification recomputes topology, Chern classes, indices, exact and
necessary checks, and rational witnesses. Stored numerical diagnostics cannot
certify acceptance. Benchmark identifiers must match the vetted geometry registry.
Changing source code or data invalidates a checkpoint identity. A completed
historical artifact is retained under its original source hash.

Generic rank certificates store deterministic coefficient generation, prime,
matrix dimensions and hash. Reconstructing the integer map and finding full
rank modulo the prime proves a nonzero maximal minor over Q. This establishes
the generic rank because the same size is a universal upper bound. Failure to
reach this bound is inconclusive, regardless of how many samples fail.
