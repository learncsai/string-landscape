from fractions import Fraction
from itertools import product
from .constraints import Check,SLOPE,EXACT_SLOPE,NUMERIC_SLOPE

def slope_matrix(geometry,k):
    return tuple(sum(geometry.d[i][j][r]*k[i] for i in range(geometry.h11)) for j in range(geometry.h11) for r in range(geometry.h11))

def signed_matrix_ok(matrix):
    # The identically zero matrix imposes no constraint. Rejecting it loses valid sums.
    return not any(matrix) or min(matrix)<0<max(matrix)

def necessary_stability(geometry,lines,coefficient_bound=1):
    if type(coefficient_bound) is not int or not 0<=coefficient_bound<=5: raise ValueError('coefficient bound must be 0..5')
    matrices=[slope_matrix(geometry,l.k) for l in lines]
    for i,m in enumerate(matrices):
        if not signed_matrix_ok(m): return Check(SLOPE,'FAIL',m,{'coefficients':[int(j==i) for j in range(len(lines))]})
    if coefficient_bound:
        for coefficients in product(range(-coefficient_bound,coefficient_bound+1),repeat=len(lines)):
            first=next((c for c in coefficients if c),0)
            if first<=0: continue # ± combinations have identical sign obstruction.
            m=tuple(sum(c*x for c,x in zip(coefficients,entries)) for entries in zip(*matrices))
            if not signed_matrix_ok(m): return Check(SLOPE,'FAIL',m,{'coefficients':coefficients})
    return Check(SLOPE,'PASS',diagnostics={'coefficient_bound':coefficient_bound,'stability':'UNKNOWN_STABILITY'})

def slopes(geometry,bundle,t):
    if len(t)!=geometry.h11: raise ValueError('dimension mismatch')
    return tuple(sum(d*l.k[i]*t[j]*t[k] for i,j,k,d in geometry.nonzero_intersections) for l in bundle.lines)

def exact_witness(geometry,bundle,t):
    if any(type(x) not in (int,Fraction) for x in t): raise TypeError('exact rational witness required')
    t=tuple(Fraction(x) for x in t)
    residual=slopes(geometry,bundle,t)
    ok=all(x>0 for x in t) and not any(residual)
    return Check(EXACT_SLOPE,'PASS' if ok else 'UNKNOWN',tuple(str(x) for x in residual),{'t':[str(x) for x in t]})

def numerical_witness(geometry,bundle,seed=0,attempts=6,tolerance=1e-9):
    import numpy as np
    from scipy.optimize import least_squares
    rng=np.random.default_rng(seed); h=geometry.h11
    matrices=np.array([slope_matrix(geometry,l.k) for l in bundle.lines],dtype=float).reshape(-1,h,h)
    scale=max(1.,float(np.max(np.abs(matrices))))
    def residual(t): return np.append(np.einsum('aij,i,j->a',matrices,t,t)/scale,t.sum()-1)
    best=None
    for attempt in range(attempts):
        initial=np.ones(h)/h if attempt==0 else rng.dirichlet(np.ones(h)*2)
        result=least_squares(residual,initial,bounds=(1e-8,1),ftol=1e-13,xtol=1e-13,gtol=1e-13,max_nfev=1500)
        t=result.x/result.x.sum(); error=float(np.max(np.abs(np.einsum('aij,i,j->a',matrices,t,t))))
        row={'t':t.tolist(),'maximum_slope_residual':error,'distance_from_boundary':float(t.min()),'solver_status':int(result.status),'message':result.message,'nfev':result.nfev,'seed':seed}
        if best is None or error<best['maximum_slope_residual']: best=row
        if error<tolerance and t.min()>1e-6: return Check(NUMERIC_SLOPE,'PASS',error,row)
    return Check(NUMERIC_SLOPE,'UNKNOWN',diagnostics={'stability':'UNKNOWN_STABILITY','best_attempt':best})
