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
