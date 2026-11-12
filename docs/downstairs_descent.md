# Phase 9: the downstairs MSSM spectrum

What this implements, what it takes as input, and what it does not claim.

## 1. The construction

`X` carries a freely acting abelian `Γ`; `X̂ = X/Γ`. An equivariant structure on
each `L_a` makes `V = ⊕_a L_a` descend to `V̂` on `X̂`. A Wilson line — a flat
bundle from a homomorphism `Γ → U(1)_Y ⊂ SU(5)` — then breaks
`SU(5) → SU(3) × SU(2) × U(1)_Y`.

Since `Γ` is abelian, the Wilson line is fixed by two characters: the one
carried by the colour triplet and the one carried by the weak doublet of the
fundamental `5`. Everything else follows from `10 = ∧²5`:

| multiplet | pieces | built from | 6Y |
|---|---|---|---:|
| `5`    | `T`, `D`       | —            | −2, 3 |
| `10`   | `Q`, `u^c`, `e^c` | `T∧D`, `T∧T`, `D∧D` | 1, −4, 6 |
| `5bar` | `d^c`, `L`     | conjugates of `T`, `D` | 2, −3 |

Upstairs, `H^1(X,V)` carries the `10`s, `H^1(X,∧²V)` the `5bar`s, `H^2(X,∧²V)`
the `5`s, and `H^1(X, L_a ⊗ L_b^*)` the singlets. Each is a `Γ`-representation.
Downstairs, a piece with Wilson-line character `χ` survives with multiplicity
equal to the multiplicity of `χ` in the corresponding upstairs cohomology, after
the equivariant structure has been applied. For abelian `Γ` that is the entire
content of the projection, and it is exact integer bookkeeping.

Doublet–triplet splitting is visible directly: a pair cohomology whose character
decomposition omits the triplet character contributes a Higgs doublet and no
colour triplet.

## 2. What is input and what is computed

**Input, not computed here:** the `Γ`-representation content of the upstairs
cohomologies (`GCoh`, `GCoh2`, `GCohSing` in the published database), together
with the equivariant structures and the Wilson line. Computing that content from
first principles needs the explicit invariant defining equations of the
free-action subfamily — the repository's standing scientific blocker, recorded
since the first session.

**Recomputed here, from our own exact code:** every upstairs quantity (`c1(V)`,
`c2(V)` against the published value, both indices, the subset criterion, the
anomaly and Bogomolov conditions, the complete slope obstruction); the
consistency of the character tables against the published `h^q`; the equivariant
shift; the Wilson-line projection; the grouping into complete multiplets; the
chiral/vector-like split; and the acceptance report.

The distinction is carried in the certificates, so no reader can mistake the
descent arithmetic for a computation of equivariant cohomology.

## 3. Conventions, and how they were pinned

Two conventions are not stated unambiguously in the sources and were determined
by fitting to the published database, then verified on every record:

1. **Character indexing.** The columns of the `GCoh` tables are the characters of
   `Γ` in lexicographic order of their integer-tuple labels. `Γ` is inferred from
   the union of labels used at each order — `Z_2` at order 2, `Z_2 × Z_2` at
   order 4 — and cross-checked against both the group order and the table width.
   A single record need not exhibit every character, so the inference is made
   database-wide; doing it per record fails, and the code raises rather than
   guessing.
2. **The equivariant structure enters as a shift.** `H^q(X, L_a)` is tensored by
   the character `χ_a`, and a pair bundle `L_a ⊗ L_b` by `χ_a + χ_b`.

Convention 2 is load-bearing and was verified rather than assumed: applying the
shift reproduces **1,948 of 1,948** published charged spectra; omitting it
reproduces only **1,503**. The 445 records that distinguish the two settle the
convention. A regression test asserts the difference persists.

## 4. Results

Against the published standard-model database (`sms202.m`, arXiv:1106.4804 and
arXiv:1202.1757), 2,113 model records:

| check | result |
|---|---|
| upstairs checks all pass, `c2` matches published | **2,113 / 2,113** |
| records with complete equivariant data | 1,948 |
| character tables consistent with published `h^q` | **1,948 / 1,948** |
| charged downstairs spectrum reproduced exactly | **1,948 / 1,948** |
| Higgs-pair count matches | **1,948 / 1,948** |
| three families, no charged chiral exotics, Higgs pair | **1,948 / 1,948** |

On our two benchmark geometries the loop closes completely: all 22 published
downstairs models on X7862 and all 4 on X7447 have upstairs bundles that pass
every exact check *and* lie inside the exhaustive Γ=4 survivor set produced by
our own search.

## 5. Honest gaps

* **165 published records are incomplete** — they lack `GCoh`, `GCoh2`, `WLine`
  or `EquivStr`. They are reported `UNKNOWN_INCOMPLETE_RECORD`, never guessed.
* **The published data itself leaves 2,450 entries undetermined** across 1,197
  records: singlet multiplicities written as unevaluated rank expressions
  (`rk_1[H_4[...]]`). Our comparison is therefore exact on the *charged*
  spectrum and reports singlet counts as published-or-unknown.
* **No equivariant cohomology is computed.** Without it the engine cannot
  *discover* a downstairs model, only verify and descend one whose equivariant
  data is supplied.
* **Non-abelian `Γ` is unsupported** and refused rather than approximated.
* Nothing here addresses supersymmetry breaking, moduli stabilisation, Yukawa
  textures beyond what the database records, or the physical mass spectrum. A
  reproduced model is an `N=1` supersymmetric MSSM-like spectrum, not a claim of
  an exact Standard Model.
