"""Certified portion of Koszul/Bott computation. Never assume maximal map rank.

E1^{-p,q}=H^q(A,L tensor wedge^p N*). All differentials have total
cohomological degree +1. If no possible differential joins occupied bidegrees, all
pages collapse and dimensions can be summed exactly. Otherwise UNKNOWN.
This works for any smooth favourable complete intersection, including
both benchmarks. It is deliberately narrower than 2306.03147 Appendix B.
"""
from itertools import combinations
from math import comb
from .interface import Cohomology,CohomologyStatus

def ambient_cohomology(ambient,k):
    q=0; dim=1
    for n,a in zip(ambient,k):
        if a>=0: dim*=comb(a+n,n)
        elif a<=-n-1: q+=n; dim*=comb(-a-1,n)
        else: return None
    return q,dim

def koszul_terms(geometry,line):
    columns=tuple(zip(*geometry.configuration)); terms=[]
    for p in range(len(columns)+1):
        for subset in combinations(columns,p):
            k=tuple(line.k[i]-sum(col[i] for col in subset) for i in range(geometry.h11))
            value=ambient_cohomology(geometry.ambient,k)
            if value is not None: terms.append((p,*value))
    return terms

def analytic_cohomology(geometry,line):
    if len(line.k)!=geometry.h11: raise ValueError('dimension mismatch')
    terms=koszul_terms(geometry,line); degrees={q-p for p,q,_ in terms}
    if any(p>pp and qq==q-(p-pp)+1 for p,q,_ in terms for pp,qq,_ in terms):
        return Cohomology(None,CohomologyStatus.UNKNOWN,'Koszul map ranks required','1202.1757 Section 5.2; 2606.22275 Section 2.1')
    if any(t<0 or t>3 for t in degrees):
        raise ArithmeticError('incompatible Koszul degrees for a smooth threefold')
    dims=tuple(sum(dim for p,q,dim in terms if q-p==i) for i in range(4))
    return Cohomology(dims,CohomologyStatus.EXACT_ANALYTIC,'Koszul collapse by degree support','1202.1757 Section 5.2; 1311.1941 Appendix C; 2606.22275 Section 2.1').validate(geometry,line)
