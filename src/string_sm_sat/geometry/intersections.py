"""Sparse exact ambient Chow ring Z[J_r]/(J_r**(n_r+1))."""
from itertools import product

def multiply(p, q, ambient, degree=None):
    out = {}
    for a, x in p.items():
        for b, y in q.items():
            c = tuple(u+v for u,v in zip(a,b))
            if any(u>v for u,v in zip(c,ambient)) or (degree is not None and sum(c)>degree):
                continue
            out[c] = out.get(c,0) + x*y
    return {a:x for a,x in out.items() if x}

def linear(coefficients):
    h=len(coefficients)
    return {tuple(int(i==j) for i in range(h)):x for j,x in enumerate(coefficients) if x}

def fundamental_class(ambient, configuration):
    out = {(0,)*len(ambient):1}
    for column in zip(*configuration):
        out = multiply(out,linear(column),ambient)
    return out

def triple_intersections(ambient, configuration):
    h=len(ambient); fundamental=fundamental_class(ambient,configuration)
    def entry(i,j,k):
        exponent=tuple(n-(int(r==i)+int(r==j)+int(r==k)) for r,n in enumerate(ambient))
        return fundamental.get(exponent,0)
    return tuple(tuple(tuple(entry(i,j,k) for k in range(h)) for j in range(h)) for i in range(h))
