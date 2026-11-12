# Performance and resource policy

Exact search uses Python integers, bounded LRU caches (100,000 index/pair entries),
streamed roots and deterministic atomic checkpoints. No int64 overflow is possible
in the topology/index path. Dense exact rank matrices have a 250,000-entry budget;
unsupported/larger cases return UNKNOWN. The one-line list is capped at 100,000.
These limits are conservative development guards, not mathematical bounds on K.

The first K=2,Gamma=2 pilot processed 3/235 roots in 0.719 s, with peak RSS
29,949,952 bytes. A simple root extrapolation gave 56.3 s. The completed run took
17.34 s. Unequal root sizes explain the coarse estimate. It visited 7,875,639
fourth-column extensions but materialized only 38,161 complete bundles.
No K>=3 or X5302 scan has been launched. Normal usage is far below the 8 GB target.

Counters at different depths count different objects. Ratios between depth-4
attempts and retained prefixes measure that stage; ratios between nominal ordered
matrices and canonical complete bundles also include C1 reduction and permutation
identification. They are not pure physics rejection fractions.

The principal search cost is extending fourth-column prefixes that later fail
component or pair budgets. Before higher K, profile this path and consider tighter
proven completion bounds; do not precompute a memory-heavy pair catalog blindly.
The principal scientific bottleneck is cohomology and equivariance on a specified
free-action subfamily, together with exact gauge-group interpretation.

The full suite initially spent 58 s in an independent SymPy Matrix rank check.
Using SymPy's exact polynomial-domain matrix rank implementation reduced that
same check to about 0.1 s without changing the matrices or arithmetic. No physics
pruning was altered for this optimization.


## Second session measurements

X7862, Gamma=2, GUT_FULL, positive ambient chamber, nonpositive pair indices.
Times are single-threaded on the M4 Mac mini, no checkpoint writes.

Before bitset indexing (`hierarchical_section5_conservative_v1`):

| K | rule | wall | peak RSS | 4th-column attempts | complete bundles | survivors |
|---:|---|---:|---:|---:|---:|---:|
| 1 | box | 0.10 s | 25.3 MiB | 37,761 | 713 | 0 |
| 2 | box | 15.84 s | 31.5 MiB | 7,875,639 | 38,161 | 120 |
| 2 | span | 8.72 s | 35.5 MiB | 2,693,275 | 10,097 | 120 |
| 3 | box | 120.08 s | 49.9 MiB | 64,825,851 | 146,425 | 192 |
| 3 | span | 55.69 s | 66.6 MiB | 21,041,937 | 52,800 | 168 |
| 4 | span | 204.76 s | 107.9 MiB | 85,213,846 | 118,577 | 240 |

After bitset indexing (`hierarchical_section5_indexed_v2`), identical survivor
sets in all seven re-run cases:

| K | rule | wall | peak RSS | 4th-column attempts | complete bundles | survivors |
|---:|---|---:|---:|---:|---:|---:|
| 1 | box | 0.05 s | 25.4 MiB | 4,636 | 713 | 0 |
| 1 | span | 0.09 s | 25.3 MiB | 2,535 | 334 | 0 |
| 2 | box | 4.00 s | 33.2 MiB | 420,266 | 38,161 | 120 |
| 2 | span | 3.99 s | 37.2 MiB | 170,121 | 10,097 | 120 |
| 3 | box | 15.88 s | 50.5 MiB | 2,304,135 | 146,425 | 192 |
| 3 | span | 18.42 s | 68.3 MiB | 963,549 | 52,800 | 168 |
| 4 | box | 36.65 s | 65.6 MiB | 7,147,830 | 294,130 | 264 |
| 4 | span | 43.62 s | 105.6 MiB | 3,236,246 | 118,577 | 240 |
| 5 | span | 85.44 s | 141.0 MiB | 6,537,468 | 162,761 | 240 |
| 6 | span | 118.88 s | 193.8 MiB | 10,199,673 | 206,847 | 240 |
| 7 | span | 179.15 s | 188.9 MiB | 14,516,351 | 231,946 | 240 |

Gamma=4 at K=5: 236.91 s, 317.1 MiB, 1,577 singles, 359,317 complete bundles,
1,344 survivors. That is the largest run so far and the memory high-water mark.

The indexing keeps, for each retained line bundle, a bitmask of pair-index
compatible partners, and per component a pair of cumulative bitmasks
(`at_least`, `at_most`) so that the component completion bound becomes an
intersection of 2h masks. The recursion then iterates only over set bits. This
removed 92-96% of the inner-loop iterations and gave 3x to 7.5x wall-clock
speedups at identical results. Setup cost is one pass over n^2/2 pair indices
(n = retained singles), 0.4 s at n = 823.

The relative cost of the two slope rules moved twice. Before indexing, the
complete span rule was about twice as fast as the finite coefficient box because
it pruned so much more (K=3: 55.7 s vs 120.1 s). Indexing removed most of that
advantage and left only the rule's per-node cost, making it slightly slower
(K=4: 43.6 s vs 36.7 s). The dual decision then removed most of the per-node
cost, and the complete rule is faster again (K=4: 28.8 s vs 36.7 s). Throughout,
it is the default for correctness rather than speed: it is the rule whose
survivor set matches the published catalog.

The complete span rule costs about 7 microseconds per distinct subspace once the
canonical form is computed with fraction-free integer elimination; the first
implementation used `Fraction` RREF at about 27 microseconds and was slower
overall than the rule it replaced. Decisions are memoised on the canonical
primitive-integer RREF of the span, so prefixes sharing a span share the answer.

The independent replay of the full 43,046,721-state K=1 domain runs in about
25 s at 38 MB, dominated by the four-deep ordered product itself; the 6,765,201
states with an in-box fifth column reduce to 58,781 distinct canonical multisets.

Bottleneck as of this session: fourth-column generation. At K=3, 21 million
extension attempts survive to 261 thousand prefixes, so roughly 99% of the inner
loop is discarded by the component and pair-index tests. Indexing the retained
line list by component box and pair compatibility should remove most of that
without changing any result. Memory is not the constraint at this scale.


## Dual slope decision and the h^{1,1}=5 benchmark

Profiling the first X7447 K=2 scan showed the span decision consuming 90% of
wall time (36.5 s of 40.4 s over six roots), dominated by the primal extreme-ray
enumeration: for h=5 each decision enumerated C(10, r-1) subsets, each needing an
integer null vector of a 4x5 matrix. Two fixes:

* the annihilator computation was still using `Fraction` arithmetic; it now uses
  the same fraction-free elimination as the rest of the path;
* the decision itself is taken in the dual form (slope note Proposition 6),
  which projects the fixed extreme rays of P through the annihilator and asks
  whether 0 lies in the convex hull of the projections. The dual dimension is
  `h - rank`, so it *shrinks* as prefixes grow: the deep, numerous nodes cost
  O(#rays) in one dimension or an angular sweep in two. Shallow nodes with
  dual dimension >= 3 fall back to the primal enumeration.

Measured: X7862 K=4 span 43.6 s -> 28.8 s (1.5x); X7447 K=2 pilot 52.8 s -> 9.6 s
(5.5x). Survivor sets bit-identical on every re-run domain; dual and primal
differentially tested on 12,000 random column sets with no disagreement.

X7447 (h^{1,1}=5) scans, Gamma=2, complete span rule:

| K | singles | wall | peak RSS | complete bundles | survivors | row orbits |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 121 | 6.8 s | 32.6 MiB | 7,122 | 0 | 0 |
| 2 | 861 | 271.6 s | 361.6 MiB | 371,214 | 6,540 | 56 |

Memory is now the fastest-growing resource on this geometry: 362 MiB at K=2
against 34 MiB for the tetraquadric at the same K, driven by the survivor list
and the memoised span decisions. The 12 GB ceiling is still far away, but this
is the first benchmark where the trend matters.
