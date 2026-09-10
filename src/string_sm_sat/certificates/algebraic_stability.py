"""Exact real-algebraic slope witness using a rational isolating interval.

A univariate polynomial has exactly one real root in the given rational
interval. Each t_i is a rational polynomial in that root. Slopes reduce to zero
modulo the polynomial and interval evaluation proves t_i>0. No expression eval.
"""
from fractions import Fraction
from ..physics.constraints import Check,rule
from ..physics.stability import slopes
METADATA=rule('algebraic_slope_witness','SUFFICIENT','1307.4787 (4.5); polynomial quotient-ring identity and real-root isolation',('rational polynomial, isolated real root, strictly positive interval bounds',),False,True)

def interval_multiply(a,b):
    values=[x*y for x in a for y in b]
    return min(values),max(values)

def evaluate_interval(coefficients,interval):
    out=(Fraction(0),Fraction(0))
    for coefficient in reversed(coefficients):
        out=interval_multiply(out,interval)
        out=(out[0]+coefficient,out[1]+coefficient)
    return out

def verify_algebraic_witness(geometry,bundle,witness):
    import sympy as s
    x=s.Symbol('alpha')
    def rationals(seq):
        if not isinstance(seq,(list,tuple)) or not 1<=len(seq)<=17: raise ValueError('invalid coefficient list')
        if any(type(c) not in (str,int) for c in seq): raise ValueError('rational text or integer required')
        return [Fraction(c) for c in seq]
    p=rationals(witness['polynomial_ascending'])
    if len(p)<2 or p[-1]==0: raise ValueError('nonconstant polynomial required')
    lo,hi=rationals(witness['isolating_interval'])
    if lo>=hi: raise ValueError('invalid isolating interval')
    poly=s.Poly(sum(s.Rational(c.numerator,c.denominator)*x**i for i,c in enumerate(p)),x,domain=s.QQ)
    if poly.eval(lo)==0 or poly.eval(hi)==0 or poly.count_roots(lo,hi)!=1: raise ValueError('interval must isolate exactly one root away from endpoints')
    t_coeff=[rationals(c) for c in witness['t_coefficients_ascending']]
    if len(t_coeff)!=geometry.h11: raise ValueError('wrong witness dimension')
    bounds=[evaluate_interval(c,(lo,hi)) for c in t_coeff]
    if any(a<=0 for a,b in bounds): raise ValueError('positivity not certified by interval')
    t=[sum(s.Rational(c.numerator,c.denominator)*x**i for i,c in enumerate(coeff)) for coeff in t_coeff]
    residual=[s.rem(s.Poly(v,x,domain=s.QQ),poly) for v in slopes(geometry,bundle,t)]
    if any(not v.is_zero for v in residual): raise ValueError('nonzero slope in polynomial quotient ring')
    return Check(METADATA,'PASS',[0]*len(bundle.lines),{'witness':witness,'positive_bounds':[[str(a),str(b)] for a,b in bounds],'root_count':1})
