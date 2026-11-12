# Supersymmetry breaking: scope statement

Step 8 of the program defers supersymmetry breaking and instructs that its
quantities must not be invented from generic N=1 supergravity formulas. This note
records what a genuine treatment would need, what this repository provides
towards it, and what it deliberately does not do.

## What a treatment would need

* A mechanism and its scale: gaugino condensation in the hidden E8 (here with a
  trivial hidden bundle), flux-induced or moduli-mediated breaking.
* Stabilised moduli: dilaton, Kahler and complex-structure moduli, and the
  bundle moduli (the singlets `S_{ab}`), with their F-terms.
* The moduli and matter Kahler potentials, including the matter-field Kahler
  metrics of `docs/physical_yukawas.md`.
* The resulting soft terms: gaugino masses, scalar masses, A-terms, B-mu, and
  their running.

None of these is computed here, and no soft-term formula from generic
supergravity is evaluated.

## What the repository does provide

Exact, model-specific *structural* inputs that any such treatment would use:

* the U(1)^4 charges of every field, the singlet spectrum derived from first
  principles and validated against the published spectra (21/22 exact, the
  remaining model differing only where the published data is unevaluated);
* the allowed singlet superpotential, D-terms and FI terms, each reproducing
  the published tables for all 2,012 models;
* the Giudice-Masiero operators `H_u H_d f(S, S^dagger)` that can generate a mu
  term once a singlet F-term is nonzero (2,012/2,012), and the other Kahler
  operators (`NeutrinoKahler`, `Kin5`);
* for each candidate, which singlets can take D-flat vacuum values at the
  Abelian locus.

These determine which operators *can* contribute; they do not determine any
number.
