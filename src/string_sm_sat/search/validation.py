from itertools import combinations
from ..physics.constraints import Check,SINGLE,PAIR
from ..physics.structure_group import check_c1,check_structure_group
from ..physics.index import index
from ..physics.anomaly import check_anomaly,check_bogomolov
from ..physics.spectrum import check_indices,check_full_spectrum
from ..physics.stability import necessary_stability,exact_witness,check_span_slope

def cheap_checks(domain,bundle):
    g=domain.geometry; target=-3*domain.gamma
    yield check_c1(bundle)
    yield check_structure_group(bundle)
    yield check_indices(bundle,g,domain.gamma)
    if domain.target=='GUT_FULL':
        values=[index(g,l) for l in bundle.lines]
        yield Check(SINGLE,'PASS' if all(target<=v<=0 for v in values) else 'FAIL',values)
    if domain.pair_nonpositive:
        values=[index(g,a.tensor(b)) for a,b in combinations(bundle.lines,2)]
        yield Check(PAIR,'PASS' if all(target<=v<=0 for v in values) else 'FAIL',values)
    yield check_anomaly(bundle,g)
    yield check_bogomolov(bundle,g)
    if domain.slope_rule in ('box','both'): yield necessary_stability(g,bundle.lines,domain.slope_coefficients)
    if domain.slope_rule in ('span','both'): yield check_span_slope(g,[l.k for l in bundle.lines])

def passes_cheap(domain,bundle,counts=None):
    for check in cheap_checks(domain,bundle):
        if check.outcome=='FAIL':
            if not check.metadata.can_safely_prune: raise AssertionError('unsafe pruning attempt')
            if counts is not None: counts['reject_'+check.metadata.name]+=1
            return False
        if counts is not None: counts['pass_'+check.metadata.name]+=1
    return True

def classify(domain,bundle):
    checks=list(cheap_checks(domain,bundle))
    if any(c.outcome=='FAIL' for c in checks): return 'REJECTED',checks
    checks.append(exact_witness(domain.geometry,bundle,(1,)*domain.geometry.h11))
    if domain.target=='GUT_FULL': checks.append(check_full_spectrum(bundle,domain.geometry,domain.gamma))
    if any(c.outcome=='FAIL' for c in checks): return 'REJECTED',checks
    # No SAT label until full structure-group/holonomy and integral effectivity
    # certification are available. Passing index or fixture data cannot override this.
    return 'UNKNOWN',checks
