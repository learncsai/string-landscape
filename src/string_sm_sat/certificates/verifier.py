"""Recompute quantities and replay domains; never trust stored verdicts."""
from fractions import Fraction
from ..geometry.cicy import CICY,benchmark
from ..bundles.bundle_sum import BundleSum
from ..search.domain import Domain
from ..search.brute_force import brute_force
from ..search.checkpoints import digest
from ..search.validation import classify
from ..physics.index import index_divisibility,divisibility_obstruction
from .candidate_certificate import candidate_certificate

def geometry_from_dict(data):
    g=CICY(data['identifier'],tuple(data['ambient']),tuple(map(tuple,data['configuration'])),data['h11'],data['h21'],tuple(data['symmetry_orders']),data['cone'],data['basis'])
    # Benchmark names cannot be used to substitute unrelated intersection data.
    if g!=benchmark(g.identifier): raise ValueError('geometry differs from vetted benchmark registry')
    return g

def verify_candidate(data):
    if data.get('kind')!='candidate' or data.get('schema')!=1: raise ValueError('unsupported certificate')
    g=geometry_from_dict(data['geometry']); v=BundleSum.from_columns(data['matrix_columns'])
    t=None if data['rational_witness'] is None else tuple(Fraction(x) for x in data['rational_witness'])
    computed=candidate_certificate(g,v,data['gamma_order'],t)
    for key in ['geometry_sha256','c1','c2','index_V','index_wedge2','classification','generic_spectrum']:
        if digest(data[key])!=digest(computed[key]): raise ValueError('candidate field mismatch: '+key)
    # Recompute exact/necessary checks, excluding explicitly noncertifying numeric diagnostics.
    stored=[c for c in data['checks'] if c['metadata']['mathematical_status']!='NUMERIC_WITNESS']
    if digest(stored)!=digest(computed['checks']): raise ValueError('candidate check mismatch')
    return {'verified':True,'classification':computed['classification'],'checks':computed['checks'],'claim':'exact recorded quantities verified; no MSSM or full-model certificate'}

def verify_search(data,max_states=1000000):
    if data.get('kind')!='bounded_search' or data.get('schema')!=1: raise ValueError('unsupported certificate')
    raw=data['domain'];g=geometry_from_dict(raw['geometry']);d=Domain(g,raw['K'],raw['gamma'],raw['target'],raw['pair_nonpositive'],raw['slope_coefficients'],raw.get('slope_rule','box'),None if raw.get('allowed_columns') is None else tuple(map(tuple,raw['allowed_columns'])))
    if digest(d.as_dict())!=data['domain_sha256']: raise ValueError('domain hash mismatch')
    if not data['enumeration']['complete']: return {'verified':False,'outcome':'UNKNOWN_BOUNDED','reason':'partial search'}
    if data.get('unbounded_obstruction'):
        # Recompute the divisibility obstruction independently of the stored claim.
        if not divisibility_obstruction(g,d.gamma): raise ValueError('claimed unbounded obstruction does not hold')
        if data['outcome']!='UNSAT_UNBOUNDED' or data['survivors']: raise ValueError('inconsistent unbounded certificate')
        return {'verified':True,'outcome':'UNSAT_UNBOUNDED','d_X':index_divisibility(g),'target':-3*d.gamma,'claim':'no five-line-bundle sum on this geometry has ind(V)=-3|Gamma| for any K','domain':d.as_dict()}
    reference,counts=brute_force(d,max_states=max_states)
    if reference!={tuple(map(tuple,k)) for k in data['enumeration']['survivors']}: raise ValueError('independent survivor replay mismatch')
    surviving=[]
    for columns in sorted(reference):
        status,checks=classify(d,BundleSum.from_columns(columns))
        if status!='REJECTED': surviving.append({'columns':columns,'classification':status,'checks':[c.as_dict() for c in checks]})
    expected='UNSAT_BOUNDED' if not surviving else 'UNKNOWN_BOUNDED'
    if data['outcome']!=expected or digest(surviving)!=data['survivor_sha256'] or digest(data['survivors'])!=digest(surviving): raise ValueError('search conclusion/hash mismatch')
    return {'verified':True,'outcome':expected,'independent_reference_counts':counts,'domain':d.as_dict()}
