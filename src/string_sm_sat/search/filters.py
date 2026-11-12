"""Named exact necessary predicates. Proofs/assumptions: docs/pruning_rules.md."""
from itertools import combinations
from ..physics.index import index
from ..physics.constraints import SINGLE,PAIR,PARTIAL,PARTIAL_ANOMALY,COMPLETION

def single_index_range(value,target): return target<=value<=0
single_index_range.metadata=SINGLE

def pair_index_range(value,target): return target<=value<=0
pair_index_range.metadata=PAIR

def partial_index_budget(value,target): return target<=value<=0
partial_index_budget.metadata=PARTIAL

def completion_bound(partial,K,h):
    remaining=5-len(partial)
    return all(abs(sum(l.k[i] for l in partial))<=remaining*K for i in range(h))
completion_bound.metadata=COMPLETION

def quadratic_form(geometry,k):
    """q_r(k) = d_{rij} k^i k^j. With c1(V)=0, c2(V)_r = -(1/2) sum_a q_r(k_a)."""
    h=geometry.h11
    return tuple(sum(geometry.d[r][i][j]*k[i]*k[j] for i in range(h) for j in range(h)) for r in range(h))

def anomaly_budget(partial_q,remaining,maxima,budget):
    """Exact: no completion can satisfy sum_a q_r(k_a) >= -2 c2_r(TX).

    partial_q  running sum of q_r over the fixed columns
    remaining  number of columns still to be chosen
    maxima     per-r maximum of q_r over the declared column pool
    budget     -2 c2_r(TX)
    """
    return all(partial_q[r]+remaining*maxima[r]>=budget[r] for r in range(len(budget)))
anomaly_budget.metadata=PARTIAL_ANOMALY
