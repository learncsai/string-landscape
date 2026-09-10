"""Named exact necessary predicates. Proofs/assumptions: docs/pruning_rules.md."""
from itertools import combinations
from ..physics.index import index
from ..physics.constraints import SINGLE,PAIR,PARTIAL,COMPLETION

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
