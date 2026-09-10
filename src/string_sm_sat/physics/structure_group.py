from itertools import combinations
from .constraints import Check,C1,STRUCTURE

def check_c1(bundle): return Check(C1,'PASS' if len(bundle.lines)==5 and not any(bundle.c1) else 'FAIL',bundle.c1)

def check_structure_group(bundle):
    if len(bundle.lines)!=5: return Check(STRUCTURE,'FAIL',diagnostics='rank must be five')
    for n in range(1,5):
        for subset in combinations(range(5),n):
            if not any(sum(bundle.lines[a].k[i] for a in subset) for i in range(len(bundle.c1))):
                return Check(STRUCTURE,'FAIL',subset)
    return Check(STRUCTURE,'PASS',diagnostics='Published subset criterion only; repeated summands and exact holonomy need separate interpretation.')
