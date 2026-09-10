from .index import bundle_c2
from .constraints import ANOMALY,Check

def check_anomaly(bundle,geometry):
    if any(bundle.c1): return Check(ANOMALY,'UNKNOWN',diagnostics='requires c1(V)=0')
    residual=tuple(a-b for a,b in zip(geometry.c2,bundle_c2(geometry,bundle)))
    if any(x<0 for x in residual): return Check(ANOMALY,'FAIL',residual)
    return Check(ANOMALY,'PASS',residual,{'effectivity':'EXACT_ZERO_CLASS' if not any(residual) else 'UNKNOWN_EFFECTIVITY','note':'nonnegative nef pairings are necessary; an integral effective representative is not constructed'})
