"""Section-5 hierarchical scan, conservative slope checks, lexicographic roots.

No ambient-row quotient during search. Every canonical five-column multiset
has one sorted first four and a uniquely determined last column.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from itertools import product
from pathlib import Path
import time
from ..bundles.line_bundle import LineBundle
from ..bundles.bundle_sum import BundleSum
from ..physics.index import index
from ..physics.stability import slope_matrix,signed_matrix_ok
from .filters import single_index_range,pair_index_range,partial_index_budget,completion_bound
from .validation import passes_cheap
from .checkpoints import identity,read_checkpoint,save_checkpoint,git_commit,input_hashes
from .statistics import peak_rss_bytes

def canonical_domain(h,K):
    """Independent sorted recursion, used for nonempty combinatorial differential tests."""
    vectors=list(product(range(-K,K+1),repeat=h))
    def extend(part,start):
        if len(part)==4:
            last=tuple(-sum(v[i] for v in part) for i in range(h))
            if last>=part[-1] and all(abs(x)<=K for x in last): yield (*part,last)
            return
        for i in range(start,len(vectors)):
            new=(*part,vectors[i]); remaining=5-len(new)
            if all(abs(sum(v[j] for v in new))<=remaining*K for j in range(h)): yield from extend(new,i)
    return set(extend((),0))

def split_search(domain,checkpoint=None,max_roots=None,workers=1):
    if type(workers) is not int or workers<1 or workers>4: raise ValueError('workers must be 1..4')
    if max_roots is not None and (type(max_roots) is not int or max_roots<0): raise ValueError('invalid root budget')
    start=time.perf_counter(); g=domain.geometry; K=domain.K; target=-3*domain.gamma
    if (2*K+1)**g.h11>100000: raise ValueError('individual list exceeds initial memory budget; benchmark before escalation')
    @lru_cache(maxsize=100000)
    def ind(k): return index(g,LineBundle(k))
    initial=Counter(); lines=[]
    for k in (sorted(domain.allowed_columns) if domain.allowed_columns is not None else product(range(-K,K+1),repeat=g.h11)):
        initial['individual_considered']+=1
        if domain.target=='GUT_FULL' and not single_index_range(ind(k),target):
            initial['individual_reject_index']+=1; continue
        if not signed_matrix_ok(slope_matrix(g,k)):
            initial['individual_reject_slope']+=1; continue
        lines.append(LineBundle(k))
    initial['individual_retained']=len(lines); lookup={l.k:l for l in lines}
    @lru_cache(maxsize=100000)
    def pair(a,b): return ind(tuple(x+y for x,y in zip(a,b)))
    def root_job(root):
        counts=Counter(); results=set()
        def extend(part,start_at,individual_sum,pair_sum):
            if len(part)==4:
                counts['four_prefixes']+=1
                last=tuple(-sum(l.k[j] for l in part) for j in range(g.h11))
                if last<part[-1].k or last not in lookup:
                    counts['reject_derived_fifth']+=1; return
                candidate=(*part,lookup[last]); counts['complete_bundles_checked']+=1
                if passes_cheap(domain,BundleSum(candidate),counts): results.add(tuple(l.k for l in candidate))
                return
            for i in range(start_at,len(lines)):
                l=lines[i]; new=(*part,l); depth=len(new); counts[f'depth_{depth}_attempted']+=1
                if not completion_bound(new,K,g.h11): counts[f'depth_{depth}_reject_completion']+=1; continue
                new_ind=individual_sum+ind(l.k)
                if domain.target=='GUT_FULL' and not partial_index_budget(new_ind,target): counts[f'depth_{depth}_reject_index']+=1; continue
                new_pair=pair_sum
                if domain.pair_nonpositive:
                    values=[pair(l.k,b.k) for b in part]
                    if any(not pair_index_range(x,target) for x in values): counts[f'depth_{depth}_reject_pair']+=1; continue
                    new_pair+=sum(values)
                    if not partial_index_budget(new_pair,target): counts[f'depth_{depth}_reject_pair_budget']+=1; continue
                counts[f'depth_{depth}_retained']+=1
                extend(new,i,new_ind,new_pair)
        extend((lines[root],),root,ind(lines[root].k),0)
        return root,results,counts
    key=identity(domain); cursor=0; results=set(); counts=Counter(initial); previous_seconds=0.
    if checkpoint and Path(checkpoint).exists():
        saved=read_checkpoint(checkpoint,key); cursor=saved['next_root']; results={tuple(map(tuple,r)) for r in saved['survivors']}; counts=Counter(saved['counts']); previous_seconds=saved['elapsed_seconds']
        if not 0<=cursor<=len(lines): raise ValueError('invalid cursor')
    stop=len(lines) if max_roots is None else min(len(lines),cursor+max_roots)
    roots=range(cursor,stop)
    def save():
        if checkpoint: save_checkpoint(checkpoint,{'identity':key,'domain':domain.as_dict(),'algorithm':'hierarchical_section5_conservative_v1','git_commit':git_commit(),'input_hashes':input_hashes(),'random_seed':None,'next_root':cursor,'survivors':sorted(results),'counts':dict(counts),'elapsed_seconds':previous_seconds+time.perf_counter()-start})
    if workers==1:
        for root,found,delta in map(root_job,roots):
            results.update(found);counts.update(delta);cursor=root+1;save()
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for root,found,delta in pool.map(root_job,roots):
                results.update(found); counts.update(delta); cursor=root+1;save()
    save()
    counts['necessary_condition_survivors']=len(results)
    return {'survivors':sorted(results),'counts':dict(counts),'complete':cursor==len(lines),'next_root':cursor,'roots':len(lines),'elapsed_seconds':previous_seconds+time.perf_counter()-start,'peak_rss_bytes':peak_rss_bytes(),'domain':domain.as_dict(),'identity':key,'algorithm':'hierarchical_section5_conservative_v1','git_commit':git_commit(),'input_hashes':input_hashes()}
