# string-sm-sat

A runnable, conservative research engine for bounded five-line-bundle heterotic
searches on favourable CICY threefolds. It uses exact ambient topology, bundle
algebra, necessary physics filters, separate reference and hierarchical searches,
and replayable JSON artifacts. It does not certify a downstairs MSSM.

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[numeric,dev]'
.venv/bin/python -m string_sm_sat.cli doctor
.venv/bin/python -m pytest -q
.venv/bin/python scripts/reproduce_known_model.py
.venv/bin/python scripts/benchmark.py --K 1 --gamma 2
```

The current workspace already has this environment. Exact core arithmetic and
basic scans need only Python; numerical witnesses and algebraic root isolation
use the optional scientific packages. Exact installed versions are recorded in
`requirements-lock.txt`. No Mathematica or external cohomology package is needed.

The golden X7447 model reproduces both indices -12, matching tangent/bundle c2,
an exact rational slope witness, and its published cohomology **for the generic
smooth family** using explicit Koszul map certificates. The X7862 K=2,Gamma=2
scan yields 120 summand-canonical necessary survivors, or five ambient-row orbits.
All five have exact interior slope witnesses; four satisfy generic upstairs full
spectrum conditions. Equivariance, complete gauge group, and the cohomology on a
specified symmetry-invariant family remain UNKNOWN.

Useful commands:

```bash
.venv/bin/python -m string_sm_sat.cli golden --output benchmarks/x7447/golden.json
.venv/bin/python -m string_sm_sat.cli verify-candidate benchmarks/x7447/golden.json
.venv/bin/python -m string_sm_sat.cli cohomology --geometry 7447 --charges -2 -2 2 2 0 --generic --output benchmarks/x7447/cohomology.json
.venv/bin/python -m string_sm_sat.cli verify-cohomology benchmarks/x7447/cohomology.json
.venv/bin/python scripts/benchmark.py --K 2 --gamma 2
.venv/bin/python scripts/compare_published.py benchmarks/x7862/k2-gamma2-current.json --output benchmarks/x7862/k2-comparison.json
.venv/bin/python scripts/certify_tetraquadric_stability.py
```

Checkpoints resume automatically and refuse mismatched code or data. To rerun
with changed source, choose a new CLI checkpoint/output path; retain the old
artifact. `--max-roots` stops at a deterministic checkpoint boundary. `--workers 2`
uses independent roots, with deterministic output. Larger scans require a pilot,
resource estimate and documented escalation; the benchmark wrapper stops at K=2.

`verify-search` independently replays tiny domains, with a default one-million
ordered-state cap. The full tetraquadric boxes exceed that cap. Their search
summaries are auditable exhaustive software runs, not independently replayed
large-domain formal proofs. Tiny nonempty restricted-column domains are covered
by differential and certificate tests.

See `STATUS.md`, `RESULTS.md`, and `docs/` for precise scope, source discrepancies,
certificate semantics, mathematical derivations, remaining work and benchmarks.
Raw scientific downloads are immutable and SHA-256 manifested; `fetch_data.py`
acquires them and `convert_data.py` rebuilds selected Oxford geometry records.
