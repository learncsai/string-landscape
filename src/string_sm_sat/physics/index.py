from fractions import Fraction
from itertools import combinations

def index(geometry, line):
    k=line.k
    if len(k)!=geometry.h11: raise ValueError('dimension mismatch')
    cubic=sum(d*k[i]*k[j]*k[r] for i,j,r,d in geometry.nonzero_intersections)
    value=Fraction(cubic,6)+Fraction(sum(a*b for a,b in zip(geometry.c2,k)),12)
    if value.denominator!=1: raise ArithmeticError('nonintegral HRR: inconsistent topology or basis')
    return value.numerator

def bundle_index(geometry,bundle): return sum(index(geometry,l) for l in bundle.lines)

def bundle_c2(geometry,bundle):
    """Whitney formula sum_{a<b} c1(La)c1(Lb), valid even if c1(V)!=0."""
    if len(bundle.c1)!=geometry.h11: raise ValueError('dimension mismatch')
    return tuple(sum(geometry.d[r][i][j]*a.k[i]*b.k[j] for a,b in combinations(bundle.lines,2) for i in range(geometry.h11) for j in range(geometry.h11)) for r in range(geometry.h11))
