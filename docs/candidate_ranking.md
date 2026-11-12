# Physics ranking of the downstairs models on X7862 / (Z2 x Z2)

Step 5. The question: *among the additional X7862 heterotic MSSM-spectrum
candidates obtained by exhaustive descent, which possess a viable perturbative
Yukawa sector and avoid dangerous operators?* Answered here with logical
categories only — no score, no weights, no learned model — and with the ten
published orbits run through the identical pipeline as the baseline.

Scripts: `scripts/audit_candidates.py --include-published --all-configurations`,
`scripts/candidate_yukawa.py --manifest benchmarks/x7862/configurations-all.json`,
`scripts/rank_candidates.py`. Artifact: `benchmarks/x7862/physics-ranking.json`.

## Coverage

Every accepted downstairs configuration (equivariant structure and Wilson line)
of every orbit, and every choice of physical Higgs pair: 192-336 configurations
and 192-720 Higgs choices per orbit, 21 orbits. Each Yukawa matrix is checked
for consistency (isotypic dimensions must equal the family counts), and every
one evaluated is independent of complex structure.

## Categories

Evaluated per configuration and Higgs choice, then per orbit (STRONG if some
choice is; PROBLEMATIC if every choice is; otherwise UNKNOWN).

* **STRONG_CANDIDATE**: a nonzero top Yukawa at the Abelian locus, up- and
  down-type Yukawas able to reach rank three at some singlet order, and
  dimension-five proton decay, dimension-four R-parity violation and bilinear
  R-parity violation all forbidden to all orders.
* **PHENOMENOLOGICALLY_PROBLEMATIC**: an unconditional exact obstruction —
  no up-type Yukawa at any perturbative order (massless top), no down-type
  Yukawa at any perturbative order, or dimension-four R-parity violation computed
  nonzero at the Abelian locus.
* **UNKNOWN**: everything else.

Every ingredient is exact given the stated scope (holomorphic superpotential,
perturbative in the singlets, generic member of the invariant family): rank caps
are structural ranks of the exactly-decided selection-rule pattern; leading-order
couplings are triple products. All 5bar states, vector-like ones included, are
counted, which makes "forbidden" statements stronger and "allowed" ones weaker.

## Result

| orbit | published models | verdict | reason (in every choice unless noted) |
|---|---|---|---|
| A01 | — | PROBLEMATIC | no up-type Yukawa at any order |
| A02 | — | PROBLEMATIC | no up-type Yukawa; dim-4 RPV at leading order in 288/720 |
| A03 | — | PROBLEMATIC | no up-type Yukawa |
| **A04** | — | **UNKNOWN** | rank 3 reachable for Y_u and Y_d; dim-4 RPV at leading order in 288/720; bilinear RPV S L H_u nonzero at order one in 720/720 |
| A05 | — | PROBLEMATIC | no up- or down-type Yukawa |
| **A06** | — | **UNKNOWN** | rank 3 reachable for Y_u and Y_d (also with D-flat singlets only); dim-5 proton decay and dim-4 RPV charge-allowed at higher order |
| A07 | — | PROBLEMATIC | no up-type Yukawa; dim-4 RPV at leading order in 288/720 |
| A08 | — | PROBLEMATIC | no up- or down-type Yukawa |
| A09 | — | PROBLEMATIC | no up- or down-type Yukawa |
| A10 | — | PROBLEMATIC | no up- or down-type Yukawa |
| A11 | — | PROBLEMATIC | no up- or down-type Yukawa |
| P01 | 1 | PROBLEMATIC | no up- or down-type Yukawa |
| P02 | 2 | PROBLEMATIC | no down-type Yukawa (Y_u rank 2 at leading order) |
| P03 | 3-6 | PROBLEMATIC | no up-type Yukawa |
| P04 | 7 | PROBLEMATIC | no up- or down-type Yukawa |
| P05 | 8 | PROBLEMATIC | no up- or down-type Yukawa |
| P06 | 9-12 | PROBLEMATIC | no up-type Yukawa in 192/384; dim-4 RPV at leading order in 192/384 |
| P07 | 13 | PROBLEMATIC | no up- or down-type Yukawa |
| P08 | 14 | UNKNOWN | rank 3 reachable for Y_u and Y_d |
| P09 | 15-18 | UNKNOWN | mixed across choices |
| P10 | 19-22 | UNKNOWN | mixed; Y_u rank 2 at leading order in 192/384 |

**No orbit on this quotient, published or additional, is a STRONG_CANDIDATE.**
Additional: 9 PROBLEMATIC, 2 UNKNOWN. Published: 7 PROBLEMATIC, 3 UNKNOWN. The
additional orbits fail for the same kinds of reasons as the published ones, and
at a comparable rate.

Further exact facts about the additional orbits:

* None has a nonzero top Yukawa at the Abelian locus (only P02 and P10 among the
  published orbits do).
* Nine of eleven forbid dimension-five proton decay (QQQL, u^c u^c d^c e^c) to
  all orders in every configuration; A04 and A06 do not.
* A08's bilinear R-parity-violating coupling S L H_u is charge-allowed but
  **vanishes cohomologically** at order one in every configuration — the one
  "allowed but vanishing" dangerous operator found.
* A04 and A06 are the only additional orbits whose up-type Yukawa can reach rank
  three; for both the rank-three pattern survives restricting to singlets that
  can take D-flat values at vanishing FI terms.

## What would change a verdict

UNKNOWN verdicts rest on higher-order terms whose coefficients are not triple
products (singlet insertions), on singlet vacua (F-flatness, moduli
stabilisation), and on physical normalisation (`docs/physical_yukawas.md`).
PROBLEMATIC verdicts are exact in the stated scope but perturbative: masses
forbidden to all orders by the U(1)^4 symmetries can still arise
non-perturbatively where those symmetries are anomalous, which is not analysed.
