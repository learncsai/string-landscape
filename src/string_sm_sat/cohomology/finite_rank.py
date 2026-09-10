"""Generic tetraquadric cohomology via a replayable full-rank minor witness.

An integer polynomial specialization whose matrix has maximal rank modulo a
prime proves that a maximal minor is a nonzero polynomial over Q. Thus the
map has this rank on a Zariski-open subset of the smooth family. Rank failure
at sampled coefficients proves nothing and returns UNKNOWN. No floating point.

References: 1311.1941 Appendix C; 2606.22275 Sections 2.1 and 4.1.3.
"""
from itertools import product
from math import prod
import hashlib
from .analytic import ambient_cohomology,analytic_cohomology
from .interface import Cohomology,CohomologyStatus

PRIME=1000003
MAX_MATRIX_ENTRIES=250000

def coefficients(seed=0):
    return {m:int.from_bytes(hashlib.sha256(f'tetraquadric-v1:{seed}:{m}'.encode()).digest()[:4],'big')%101-50 for m in product(range(3),repeat=4)}

def basis(k):
    if any(a==-1 for a in k): return ()
    return tuple(product(*(range(a+1) if a>=0 else range(-a-1) for a in k)))

def multiplication_matrix(k,coeffs):
    source=tuple(a-2 for a in k)
    if any((a>=0)!=(b>=0) for a,b in zip(source,k)): raise ValueError('map does not preserve ambient cohomology pattern')
    sizes=[prod(a+1 if a>=0 else -a-1 for a in w) for w in (source,k)]
    if sizes[0]*sizes[1]>MAX_MATRIX_ENTRIES: raise ValueError('exact rank matrix budget exceeded')
    src=basis(source);dst=basis(k);lookup={m:i for i,m in enumerate(dst)}
    matrix=[[0]*len(src) for _ in dst]
    for j,monomial in enumerate(src):
        for power,value in coeffs.items():
            # H0 polynomial multiplication; H1 dual multiplication decreases
            # dual monomial exponents. Both homogeneous exponents must fit.
            target=tuple(a+b if degree>=0 else a-b for a,b,degree in zip(monomial,power,k))
            i=lookup.get(target)
            if i is not None: matrix[i][j]+=value
    return matrix

def modular_rank(matrix,prime=PRIME):
    """Exact Gaussian elimination in F_p (prime fixed/vetted by caller)."""
    if not matrix: return 0
    a=[[v%prime for v in row] for row in matrix]; n=len(a); m=len(a[0]); r=0
    if any(len(row)!=m for row in a): raise ValueError('ragged matrix')
    for col in range(m):
        pivot=next((i for i in range(r,n) if a[i][col]),None)
        if pivot is None: continue
        a[r],a[pivot]=a[pivot],a[r];inv=pow(a[r][col],-1,prime)
        a[r]=[(v*inv)%prime for v in a[r]]
        for i in range(r+1,n):
            factor=a[i][col]
            if factor: a[i]=[(x-factor*y)%prime for x,y in zip(a[i],a[r])]
        r+=1
        if r==n: break
    return r

def rank_certificate(geometry,line):
    if geometry.identifier!='7862' or geometry.ambient!=(1,)*4 or geometry.configuration!=((2,),)*4: return None
    k=line.k; source=tuple(a-2 for a in k)
    a=ambient_cohomology(geometry.ambient,source); b=ambient_cohomology(geometry.ambient,k)
    if a is None or b is None or a[0]!=b[0]: return None
    if any((x>=0)!=(y>=0) for x,y in zip(source,k)): return None
    if a[1]*b[1]>MAX_MATRIX_ENTRIES: return None
    for seed in range(3):
        matrix=multiplication_matrix(k,coefficients(seed)); rank=modular_rank(matrix)
        if rank==min(a[1],b[1]):
            return {'schema':1,'geometry':'7862','line_bundle':k,'prime':PRIME,'coefficient_generator':'sha256-tetraquadric-v1','seed':seed,'source_dimension':a[1],'target_dimension':b[1],'rank':rank,'ambient_degree':a[0],'complex_structure_scope':'Zariski-generic smooth family; not every specialization or invariant subfamily','matrix_sha256':hashlib.sha256(str(matrix).encode()).hexdigest()}
    return None

def generic_cohomology(geometry,line):
    collapsed=analytic_cohomology(geometry,line)
    if collapsed.dimensions is not None: return collapsed
    cert=rank_certificate(geometry,line)
    if cert is None: return collapsed
    q=cert['ambient_degree']; r=cert['rank'];dims=[0]*4
    for degree,value in ((q,cert['target_dimension']-r),(q-1,cert['source_dimension']-r)):
        if 0<=degree<4: dims[degree]+=value
        elif value: raise ArithmeticError('nonzero cohomology outside threefold degrees')
    return Cohomology(tuple(dims),CohomologyStatus.EXACT_ANALYTIC,'generic Koszul rank: replay finite-field maximal minor','1311.1941 Appendix C; 2606.22275 Sections 2.1,4.1.3').validate(geometry,line)
