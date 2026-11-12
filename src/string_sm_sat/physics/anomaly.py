from .index import bundle_c2
from .constraints import ANOMALY,BOGOMOLOV,Check
from ..search.filters import quadratic_form

def check_anomaly(bundle,geometry):
    if any(bundle.c1): return Check(ANOMALY,'UNKNOWN',diagnostics='requires c1(V)=0')
    residual=tuple(a-b for a,b in zip(geometry.c2,bundle_c2(geometry,bundle)))
    if any(x<0 for x in residual): return Check(ANOMALY,'FAIL',residual)
    return Check(ANOMALY,'PASS',residual,{'effectivity':'EXACT_ZERO_CLASS' if not any(residual) else 'UNKNOWN_EFFECTIVITY','note':'nonnegative nef pairings are necessary; an integral effective representative is not constructed'})


def check_bogomolov(bundle,geometry):
    """c2(V).J >= 0 for a bundle semistable at J. With c1(V)=0 this reads
    Q_r = sum_a q_r(k_a) and requires t.Q <= 0 for the stable t>0. If every
    component of Q is nonnegative and Q is nonzero, no t>0 can satisfy it."""
    if any(bundle.c1): return Check(BOGOMOLOV,'UNKNOWN',diagnostics='requires c1(V)=0')
    h=geometry.h11
    q=tuple(sum(quadratic_form(geometry,l.k)[r] for l in bundle.lines) for r in range(h))
    if all(x>=0 for x in q) and any(q): return Check(BOGOMOLOV,'FAIL',q,{'reason':'c2(V).J<0 for every t>0 in the declared chamber'})
    return Check(BOGOMOLOV,'PASS',q,{'note':'necessary only; the stable t is not constructed here'})
