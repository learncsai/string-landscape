"""Adjunction: expand c(TA)/c(N) exactly, through degree three."""
from math import comb
from .intersections import multiply, linear, fundamental_class

def tangent_chern(ambient, configuration):
    zero=(0,)*len(ambient); out={zero:1}
    for r,n in enumerate(ambient):
        factor={tuple(p if i==r else 0 for i in range(len(ambient))):comb(n+1,p) for p in range(min(n,3)+1)}
        out=multiply(out,factor,ambient,3)
    for column in zip(*configuration):
        q=linear(column); power={zero:1}; inverse={zero:1}
        for p in range(1,4):
            power=multiply(power,q,ambient,3)
            for m,v in power.items(): inverse[m]=inverse.get(m,0)+(-1)**p*v
        out=multiply(out,inverse,ambient,3)
    return out

def tangent_c2_pairings(ambient, configuration):
    chern={m:v for m,v in tangent_chern(ambient,configuration).items() if sum(m)==2}
    cycle=multiply(chern,fundamental_class(ambient,configuration),ambient)
    return tuple(cycle.get(tuple(n-int(i==r) for i,n in enumerate(ambient)),0) for r in range(len(ambient)))

def euler_number(ambient, configuration):
    c3={m:v for m,v in tangent_chern(ambient,configuration).items() if sum(m)==3}
    return multiply(c3,fundamental_class(ambient,configuration),ambient).get(ambient,0)
