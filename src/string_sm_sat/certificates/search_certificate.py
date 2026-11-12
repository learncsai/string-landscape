from ..search.checkpoints import code_hash,digest
from ..search.validation import classify
from ..bundles.bundle_sum import BundleSum
from ..physics.constraints import RULES,SPECTRUM_GENERIC
from dataclasses import asdict

def search_certificate(domain,result):
    surviving=[]; rejected=[]
    for columns in result['survivors']:
        status,checks=classify(domain,BundleSum.from_columns(columns))
        row={'columns':columns,'classification':status,'checks':[c.as_dict() for c in checks]}
        (rejected if status=='REJECTED' else surviving).append(row)
    outcome='UNSAT_BOUNDED' if result['complete'] and not surviving else 'UNKNOWN_BOUNDED'
    if result.get('unbounded_obstruction'): outcome='UNSAT_UNBOUNDED'
    return {'schema':1,'kind':'bounded_search','outcome':outcome,'domain':domain.as_dict(),'domain_sha256':digest(domain.as_dict()),'enumeration':result,'survivors':surviving,'late_rejections':rejected,'survivor_sha256':digest(surviving),'fully_certified_count':0,'unknown_count':len(surviving),'constraints':[asdict(c) for c in (*RULES,SPECTRUM_GENERIC)],'software_source_sha256':code_hash(),'assurance':'software exhaustive enumeration with exact necessary pruning; not a formal proof assistant certificate','unbounded_obstruction':result.get('unbounded_obstruction'),'literature_comparison':'1307.4787 Table 4 precedes full cohomology filtering and quotients ambient row symmetries; our necessary survivors are not that count'}
