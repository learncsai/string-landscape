"""Generic X7447 map certificates: isolated d1 rows and zero-coordinate d2.

The d2 when k_r=0 is the resultant of the two equations linear in P1_r.
See docs/cohomology_certificates.md for the relative Koszul derivation.
"""
import hashlib
from itertools import product,combinations
from math import prod
from .analytic import analytic_cohomology,ambient_cohomology,koszul_terms
from .finite_rank import basis,modular_rank,PRIME,MAX_MATRIX_ENTRIES,multiplication_matrix
from .interface import Cohomology,CohomologyStatus

def equations(seed=0):
    return [{m:int.from_bytes(hashlib.sha256(f'x7447-v1:{seed}:{n}:{m}'.encode()).digest()[:4],'big')%101-50 for m in product(range(2),repeat=5)} for n in range(2)]

def map_block(source,target,polynomial):
    a=ambient_cohomology((1,)*5,source);b=ambient_cohomology((1,)*5,target)
    if a is None or b is None: return []
    if a[0]!=b[0] or any((x>=0)!=(y>=0) for x,y in zip(source,target)):
        return [[0]*a[1] for _ in range(b[1])]
    src=basis(source);dst=basis(target);lookup={m:i for i,m in enumerate(dst)}
    matrix=[[0]*len(src) for _ in dst]
    for j,m in enumerate(src):
        for power,value in polynomial.items():
            exponent=tuple(x+y if degree>=0 else x-y for x,y,degree in zip(m,power,target))
            i=lookup.get(exponent)
            if i is not None: matrix[i][j]+=value
    return matrix

def resultant(polynomials,coordinate):
    parts=[]
    for f in polynomials:
        parts.append([{tuple(x for i,x in enumerate(m) if i!=coordinate):v for m,v in f.items() if m[coordinate]==a} for a in (0,1)])
    out={}
    for a,x in parts[0][0].items():
        for b,y in parts[1][1].items():
            m=tuple(u+v for u,v in zip(a,b));out[m]=out.get(m,0)+x*y
    for a,x in parts[0][1].items():
        for b,y in parts[1][0].items():
            m=tuple(u+v for u,v in zip(a,b));out[m]=out.get(m,0)-x*y
    return out

def rank_certificate(geometry,line):
    if geometry.identifier!='7447' or geometry.configuration!=((1,1),)*5 or geometry.ambient!=(1,)*5:return None
    terms=koszul_terms(geometry,line)
    nodes={}
    for p,q,dim in terms:nodes[p,q]=nodes.get((p,q),0)+dim
    if len(nodes)!=2:return None
    (p,q),(pp,qq)=sorted(nodes,reverse=True)
    source_dim=nodes[p,q];target_dim=nodes[pp,qq]
    if source_dim*target_dim>MAX_MATRIX_ENTRIES:return None
    k=line.k;kind=None
    for seed in range(3):
        polys=equations(seed);matrix=None
        if p==pp+1 and q==qq:
            kind='isolated_d1'
            if p==1:
                blocks=[map_block(tuple(x-1 for x in k),k,f) for f in polys]
                matrix=[a+b for a,b in zip(*blocks)]
            elif p==2:
                # Koszul differential f wedge e1e2 = f0 e2 - f1 e1.
                blocks=[map_block(tuple(x-2 for x in k),tuple(x-1 for x in k),f) for f in polys]
                matrix=[[-x for x in row] for row in blocks[1]]+blocks[0]
        elif p==2 and pp==0 and q==qq+1 and 0 in k:
            coordinate=k.index(0);projected=tuple(x for i,x in enumerate(k) if i!=coordinate)
            kind='relative_P1_resultant_d2'
            matrix=multiplication_matrix(projected,resultant(polys,coordinate))
        if matrix is None:return None
        if len(matrix)!=target_dim or any(len(row)!=source_dim for row in matrix):raise ArithmeticError('Koszul matrix dimension mismatch')
        rank=modular_rank(matrix)
        if rank==min(source_dim,target_dim):
            return {'schema':1,'geometry':'7447','line_bundle':k,'method':kind,'prime':PRIME,'seed':seed,'coefficient_generator':'sha256-x7447-v1','matrix_sha256':hashlib.sha256(str(matrix).encode()).hexdigest(),'source_bidegree':[p,q],'target_bidegree':[pp,qq],'source_dimension':source_dim,'target_dimension':target_dim,'rank':rank,'complex_structure_scope':'generic smooth two-equation family; chosen free-action locus not certified'}
    return None

def generic_cohomology(geometry,line):
    collapsed=analytic_cohomology(geometry,line)
    if collapsed.dimensions is not None:return collapsed
    cert=rank_certificate(geometry,line)
    if cert is None:return collapsed
    p,q=cert['source_bidegree'];pp,qq=cert['target_bidegree'];rank=cert['rank'];dims=[0]*4
    for degree,value in ((q-p,cert['source_dimension']-rank),(qq-pp,cert['target_dimension']-rank)):
        if 0<=degree<4:dims[degree]+=value
        elif value:raise ArithmeticError('invalid surviving Koszul degree')
    return Cohomology(tuple(dims),CohomologyStatus.EXACT_ANALYTIC,'generic isolated Koszul map; '+cert['method'],'1202.1757 Section 5.2; 2606.22275 Section 2; docs/cohomology_certificates.md').validate(geometry,line)
