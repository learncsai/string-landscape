"""Slow independent reference: ordered four-column product, derive fifth, dedup."""
from itertools import product
from collections import Counter
from ..bundles.bundle_sum import BundleSum
from .validation import passes_cheap

def canonical_domain(h,K,max_states=1000000):
    if type(h) is not int or h<1 or type(K) is not int or K<0: raise ValueError('invalid finite box')
    if (2*K+1)**(4*h)>max_states: raise ValueError('reference domain exceeds explicit state budget')
    vectors=list(product(range(-K,K+1),repeat=h)); seen=set()
    for first in product(vectors,repeat=4):
        last=tuple(-sum(v[i] for v in first) for i in range(h))
        if any(abs(x)>K for x in last): continue
        seen.add(tuple(sorted((*first,last))))
    return seen

def brute_force(domain,max_states=1000000):
    h=domain.geometry.h11; K=domain.K
    if domain.as_dict()["raw_four_column_states"]>max_states: raise ValueError('reference domain exceeds explicit state budget')
    vectors=list(domain.allowed_columns) if domain.allowed_columns is not None else list(product(range(-K,K+1),repeat=h)); seen=set(); results=set(); counts=Counter()
    for first in product(vectors,repeat=4):
        counts['raw_states']+=1
        last=tuple(-sum(v[i] for v in first) for i in range(h))
        if any(abs(x)>K for x in last) or (domain.allowed_columns is not None and last not in domain.allowed_columns): continue
        counts['valid_k5']+=1
        key=tuple(sorted((*first,last)))
        if key in seen: continue
        seen.add(key); counts['canonical_states']+=1
        bundle=BundleSum.from_columns(key)
        if passes_cheap(domain,bundle,counts): results.add(key)
    counts['necessary_condition_survivors']=len(results)
    return results,dict(counts)
