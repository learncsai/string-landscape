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
from ..physics.index import index,index_divisibility,divisibility_obstruction
from ..physics.stability import slope_matrix,signed_matrix_ok,span_obstructed,extend_span
from .filters import single_index_range,pair_index_range,partial_index_budget,completion_bound,quadratic_form,anomaly_budget
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
    span_prefix=domain.slope_rule in ('span','both')
    from ..physics.stability import _span_obstructed
    if divisibility_obstruction(g,domain.gamma):
        # docs/exact_obstructions.md P2: no five-line-bundle sum on this geometry
        # can have ind(V) = -3|Gamma|, for any K. Enumeration is unnecessary.
        return {'survivors':[],'counts':{'necessary_condition_survivors':0,'index_divisibility':index_divisibility(g),'divisibility_obstruction':1},'complete':True,'next_root':0,'roots':0,'elapsed_seconds':time.perf_counter()-start,'peak_rss_bytes':peak_rss_bytes(),'domain':domain.as_dict(),'identity':identity(domain),'algorithm':'index_divisibility_shortcut_v1','git_commit':git_commit(),'input_hashes':input_hashes(),'unbounded_obstruction':{'rule':'index_divisibility','d_X':index_divisibility(g),'target':target,'reference':'docs/exact_obstructions.md P2'}}
    pool_size=len(domain.allowed_columns) if domain.allowed_columns is not None else (2*K+1)**g.h11
    if pool_size>100000: raise ValueError('individual list exceeds initial memory budget; benchmark before escalation')
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
    order={l.k:i for i,l in enumerate(lines)}
    forms={l.k:quadratic_form(g,l.k) for l in lines}
    maxima=tuple(max((forms[l.k][r] for l in lines),default=0) for r in range(g.h11))
    budget=tuple(-2*x for x in g.c2)
    @lru_cache(maxsize=100000)
    def pair(a,b): return ind(tuple(x+y for x,y in zip(a,b)))

    # ------------------------------------------------------------------
    # Admissibility bitsets over the retained line list. These encode the
    # component completion bound and, when the domain declares it, the pair
    # index range, so the recursion iterates only over admissible partners.
    # Purely an indexing device: the conditions are exactly those of
    # docs/pruning_rules.md rules 3 and 5, applied by construction.
    # ------------------------------------------------------------------
    n=len(lines); universe=(1<<n)-1
    at_least=[[0]*(2*K+1) for _ in range(g.h11)]; at_most=[[0]*(2*K+1) for _ in range(g.h11)]
    for i in range(g.h11):
        buckets=[0]*(2*K+1)
        for j,l in enumerate(lines): buckets[l.k[i]+K]|=1<<j
        accumulated=0
        for v in range(2*K+1):
            accumulated|=buckets[v]; at_most[i][v]=accumulated
        accumulated=0
        for v in range(2*K,-1,-1):
            accumulated|=buckets[v]; at_least[i][v]=accumulated
    def completable(partial_sum,remaining):
        """Lines l with |partial_sum_i + l_i| <= remaining*K for every i."""
        mask=universe
        for i in range(g.h11):
            low=-remaining*K-partial_sum[i]; high=remaining*K-partial_sum[i]
            if low>K or high<-K: return 0
            mask&=at_least[i][max(low,-K)+K]&at_most[i][min(high,K)+K]
            if not mask: return 0
        return mask
    if domain.pair_nonpositive:
        compatible=[0]*n
        for a in range(n):
            row=0
            for b in range(a,n):
                if pair_index_range(pair(lines[a].k,lines[b].k),target): row|=1<<b
            compatible[a]=row
        for a in range(n):
            for b in range(a+1,n):
                if compatible[a]>>b&1: compatible[b]|=1<<a
    else:
        compatible=[universe]*n
    def members(mask,start_at):
        mask>>=start_at; i=start_at
        while mask:
            shift=(mask&-mask).bit_length()-1
            i+=shift; yield i
            mask>>=shift+1; i+=1

    def root_job(root):
        counts=Counter(); results=set()
        def extend(part,start_at,mask,individual_sum,pair_sum,partial_q,partial_sum,basis):
            depth=len(part)
            if depth==4:
                counts['four_prefixes']+=1
                last=tuple(-x for x in partial_sum)
                if last<part[-1].k or last not in lookup:
                    counts['reject_derived_fifth']+=1; return
                candidate=(*part,lookup[last]); counts['complete_bundles_checked']+=1
                if passes_cheap(domain,BundleSum(candidate),counts): results.add(tuple(l.k for l in candidate))
                return
            # the next column brings the prefix to depth+1 columns, whose sum must
            # still be completable inside the box: |sum| <= (5-(depth+1))K.
            admissible=mask&completable(partial_sum,4-depth)
            for i in members(admissible,start_at):
                l=lines[i]; new=(*part,l); counts[f'depth_{depth+1}_attempted']+=1
                new_ind=individual_sum+ind(l.k)
                if domain.target=='GUT_FULL' and not partial_index_budget(new_ind,target): counts[f'depth_{depth+1}_reject_index']+=1; continue
                new_pair=pair_sum
                if domain.pair_nonpositive:
                    new_pair+=sum(pair(l.k,b.k) for b in part)
                    if not partial_index_budget(new_pair,target): counts[f'depth_{depth+1}_reject_pair_budget']+=1; continue
                new_q=tuple(partial_q[r]+forms[l.k][r] for r in range(g.h11))
                if not anomaly_budget(new_q,4-depth,maxima,budget):
                    counts[f'depth_{depth+1}_reject_anomaly_budget']+=1; continue
                new_basis=basis
                if span_prefix:
                    new_basis=extend_span(basis,l.k)
                    if _span_obstructed(g,new_basis):
                        counts[f'depth_{depth+1}_reject_span_slope']+=1; continue
                counts[f'depth_{depth+1}_retained']+=1
                extend(new,i,mask&compatible[i],new_ind,new_pair,new_q,tuple(a+b for a,b in zip(partial_sum,l.k)),new_basis)
        first=lines[root]
        extend((first,),root,compatible[root],ind(first.k),0,forms[first.k],first.k,extend_span((),first.k))
        return root,results,counts
    key=identity(domain); cursor=0; results=set(); counts=Counter(initial); previous_seconds=0.
    if checkpoint and Path(checkpoint).exists():
        saved=read_checkpoint(checkpoint,key); cursor=saved['next_root']; results={tuple(map(tuple,r)) for r in saved['survivors']}; counts=Counter(saved['counts']); previous_seconds=saved['elapsed_seconds']
        if not 0<=cursor<=len(lines): raise ValueError('invalid cursor')
    stop=len(lines) if max_roots is None else min(len(lines),cursor+max_roots)
    roots=range(cursor,stop)
    def save():
        if checkpoint: save_checkpoint(checkpoint,{'identity':key,'domain':domain.as_dict(),'algorithm':'hierarchical_section5_indexed_v2','git_commit':git_commit(),'input_hashes':input_hashes(),'random_seed':None,'next_root':cursor,'survivors':sorted(results),'counts':dict(counts),'elapsed_seconds':previous_seconds+time.perf_counter()-start})
    if workers==1:
        for root,found,delta in map(root_job,roots):
            results.update(found);counts.update(delta);cursor=root+1;save()
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for root,found,delta in pool.map(root_job,roots):
                results.update(found); counts.update(delta); cursor=root+1;save()
    save()
    counts['necessary_condition_survivors']=len(results)
    return {'survivors':sorted(results),'counts':dict(counts),'complete':cursor==len(lines),'next_root':cursor,'roots':len(lines),'elapsed_seconds':previous_seconds+time.perf_counter()-start,'peak_rss_bytes':peak_rss_bytes(),'domain':domain.as_dict(),'identity':key,'algorithm':'hierarchical_section5_indexed_v2','git_commit':git_commit(),'input_hashes':input_hashes()}
