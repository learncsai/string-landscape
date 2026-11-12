from fractions import Fraction
from functools import lru_cache
from itertools import combinations,product
from math import gcd
from .constraints import Check,SLOPE,SPAN_SLOPE,EXACT_SLOPE,NUMERIC_SLOPE

def slope_matrix(geometry,k):
    return tuple(sum(geometry.d[i][j][r]*k[i] for i in range(geometry.h11)) for j in range(geometry.h11) for r in range(geometry.h11))

def signed_matrix_ok(matrix):
    # The identically zero matrix imposes no constraint. Rejecting it loses valid sums.
    return not any(matrix) or min(matrix)<0<max(matrix)

# ---------------------------------------------------------------------------
# Complete form of the signed-combination obstruction (docs/slope_obstruction_note.md,
# Propositions 3-5): decide whether the span of a set of charge vectors contains
# any k with M(k) entrywise one-signed and nonzero. Exact integer arithmetic.
# ---------------------------------------------------------------------------

def slope_forms(geometry):
    """Distinct nonzero linear forms k -> M(k)_{jl}, as integer coefficient rows."""
    h=geometry.h11; rows={}
    for j in range(h):
        for r in range(j,h):
            row=tuple(geometry.d[i][j][r] for i in range(h))
            if any(row): rows[row]=None
    return tuple(rows)

def _determinant(matrix):
    """Exact integer determinant by fraction-free (Bareiss) elimination."""
    n=len(matrix)
    if n==0: return 1
    a=[list(row) for row in matrix]; sign=1; previous=1
    for k in range(n-1):
        if a[k][k]==0:
            swap=next((i for i in range(k+1,n) if a[i][k]),None)
            if swap is None: return 0
            a[k],a[swap]=a[swap],a[k]; sign=-sign
        for i in range(k+1,n):
            for j in range(k+1,n):
                a[i][j]=(a[i][j]*a[k][k]-a[i][k]*a[k][j])//previous
            a[i][k]=0
        previous=a[k][k]
    return sign*a[n-1][n-1]

def _primitive(vector):
    g=0
    for x in vector: g=gcd(g,abs(x))
    return tuple(x//g for x in vector) if g else tuple(vector)

def _null_vector(rows,h):
    """Integer generator of the kernel of an (h-1) x h matrix, or None if rank<h-1."""
    v=[]
    for i in range(h):
        minor=[[row[j] for j in range(h) if j!=i] for row in rows]
        v.append((-1)**i*_determinant(minor))
    return None if not any(v) else _primitive(v)

def _rational_rref(vectors,h):
    """Rational RREF; returns (rank, pivot columns, reduced rows)."""
    m=[[Fraction(x) for x in v] for v in vectors]; pivots=[]; r=0
    for c in range(h):
        p=next((i for i in range(r,len(m)) if m[i][c]),None)
        if p is None: continue
        m[r],m[p]=m[p],m[r]; inverse=m[r][c]; m[r]=[x/inverse for x in m[r]]
        for i in range(len(m)):
            if i!=r and m[i][c]:
                f=m[i][c]; m[i]=[a-f*b for a,b in zip(m[i],m[r])]
        pivots.append(c); r+=1
        if r==len(m): break
    return r,pivots,m[:r]

def _integral(row):
    denominator=1
    for x in row: denominator=denominator*x.denominator//gcd(denominator,x.denominator)
    return _primitive([int(x*denominator) for x in row])

def _integer_rref(rows,h):
    """Fraction-free Gauss-Jordan; rows are primitive integer multiples of the
    rational RREF rows with positive pivots, hence a canonical form for the
    Q-span. Used as the memo key for the span decision."""
    m=[list(row) for row in rows]; pivots=[]; r=0
    for c in range(h):
        p=next((i for i in range(r,len(m)) if m[i][c]),None)
        if p is None: continue
        m[r],m[p]=m[p],m[r]
        for i in range(len(m)):
            if i!=r and m[i][c]:
                a,b=m[r][c],m[i][c]
                m[i]=list(_primitive([a*x-b*y for x,y in zip(m[i],m[r])]))
        m[r]=list(_primitive(m[r]))
        pivots.append(c); r+=1
        if r==len(m): break
    out=[]
    for i,c in enumerate(pivots):
        row=_primitive(m[i])
        out.append(tuple(-x for x in row) if row[c]<0 else row)
    return tuple(out)

def span_key(columns,h):
    """Canonical primitive-integer RREF basis of span(columns). Cache key."""
    return _integer_rref([tuple(k) for k in columns],h)

def extend_span(basis,vector):
    """Canonical basis of span(basis + {vector}); for incremental recursion."""
    return _integer_rref([*basis,tuple(vector)],len(vector))

def _annihilator(basis,h):
    """Integer basis of {y : y.k = 0 for every k in span(basis)}, fraction-free."""
    rows=_integer_rref(basis,h)
    pivots=[next(c for c in range(h) if row[c]) for row in rows]
    free=[c for c in range(h) if c not in pivots]
    out=[]
    for f in free:
        # solve for the pivot entries: row_i . y = 0 with y_f = product of pivots
        scale=1
        for i,c in enumerate(pivots): scale*=rows[i][c]
        y=[0]*h; y[f]=scale
        for i,c in enumerate(pivots): y[c]=-rows[i][f]*(scale//rows[i][c])
        out.append(list(_primitive(y)))
    return out

# ---------------------------------------------------------------------------
# Dual decision. S cap P = {0} iff some functional in the annihilator of S is
# strictly positive on every extreme ray of P (separate the compact base of the
# pointed cone P from the subspace S). Projecting the rays through the
# annihilator turns this into "is 0 in the convex hull of the projected rays",
# which is O(number of rays) in one dimension and an angular-gap test in two.
# The primal extreme-ray enumeration remains the reference and the witness
# producer; the two are differentially tested against each other.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def slope_cone_rays(geometry):
    """Extreme rays of P = {k : M(k) entrywise >= 0}; None when P is not pointed."""
    h=geometry.h11; forms=slope_forms(geometry)
    if _rational_rref([list(f) for f in forms],h)[0]<h: return None
    rays={}
    for subset in combinations(range(len(forms)),h-1):
        v=_null_vector([list(forms[i]) for i in subset],h)
        if v is None: continue
        for candidate in (v,tuple(-x for x in v)):
            if all(sum(f[i]*candidate[i] for i in range(h))>=0 for f in forms):
                rays[_primitive(candidate)]=None
    return tuple(rays)

def _half(point):
    return 0 if (point[1]>0 or (point[1]==0 and point[0]>0)) else 1

def _in_open_halfplane(points):
    """True when some y satisfies <y,p> > 0 for every p (all p nonzero, in Z^2)."""
    from functools import cmp_to_key
    def compare(a,b):
        if _half(a)!=_half(b): return _half(a)-_half(b)
        cross=a[0]*b[1]-a[1]*b[0]
        return -1 if cross>0 else (1 if cross<0 else 0)
    ordered=sorted(points,key=cmp_to_key(compare))
    for i in range(len(ordered)):
        u=ordered[i]; v=ordered[(i+1)%len(ordered)]
        if u[0]*v[1]-u[1]*v[0]<0: return True      # an angular gap wider than pi
    return len(ordered)==1

def _dual_obstructed(geometry,annihilator):
    """True/False when the dual test decides, None when it defers to the primal."""
    rays=slope_cone_rays(geometry)
    if rays is None: return None
    h=geometry.h11; d=len(annihilator)
    if d==0: return True                       # the span is all of R^h, and P != {0}
    projected=[tuple(sum(a[i]*r[i] for i in range(h)) for a in annihilator) for r in rays]
    if any(not any(p) for p in projected): return True   # an extreme ray lies in the span
    if d==1:
        values=[p[0] for p in projected]
        return min(values)<0<max(values)
    if d==2:
        return not _in_open_halfplane(projected)
    return None

@lru_cache(maxsize=400000)
def _span_decision(geometry,basis):
    """Extreme-ray decision for one subspace. docs/slope_obstruction_note.md Prop. 3."""
    h=geometry.h11; forms=slope_forms(geometry); rank=len(basis)
    if rank==0: return None
    annihilator=_annihilator([list(b) for b in basis],h)
    # Pointedness guard: the span must meet ker M only at the origin.
    if _rational_rref(annihilator+[list(f) for f in forms],h)[0]<h: return 'UNKNOWN_LINEALITY'
    for subset in combinations(range(len(forms)),rank-1):
        rows=annihilator+[list(forms[i]) for i in subset]
        if len(rows)!=h-1: return 'UNKNOWN_LINEALITY'
        v=_null_vector(rows,h)
        if v is None: continue
        for candidate in (v,tuple(-x for x in v)):
            values=[sum(f[i]*candidate[i] for i in range(h)) for f in forms]
            if all(x>=0 for x in values) and any(values): return candidate
    return None

@lru_cache(maxsize=400000)
def _span_obstructed(geometry,basis):
    """Boolean form of Proposition 3, dual test first, primal as fallback."""
    if len(basis)==0: return False
    annihilator=_annihilator([list(b) for b in basis],geometry.h11)
    decided=_dual_obstructed(geometry,tuple(map(tuple,annihilator)) and annihilator)
    if decided is not None: return decided
    return _span_decision(geometry,basis) not in (None,'UNKNOWN_LINEALITY')

def span_obstructed(geometry,columns):
    """True when span(columns) carries a signed-combination obstruction."""
    return _span_obstructed(geometry,span_key(columns,geometry.h11))

def span_slope_obstruction(geometry,columns):
    """Exact witness k with M(k) one-signed nonzero inside span(columns), or None.

    Returns None when no such k exists (Proposition 3) and the string
    'UNKNOWN_LINEALITY' when the pointedness guard fails, in which case the
    caller must not prune.
    """
    return _span_decision(geometry,span_key(columns,geometry.h11))

def solve_coefficients(columns,target):
    """Exact rational c with sum_a c_a k_a = target, or None. Certificate aid."""
    h=len(target); rows=[[Fraction(k[i]) for k in columns]+[Fraction(target[i])] for i in range(h)]
    width=len(columns); pivots=[]; r=0
    for c in range(width):
        p=next((i for i in range(r,h) if rows[i][c]),None)
        if p is None: continue
        rows[r],rows[p]=rows[p],rows[r]; inverse=rows[r][c]; rows[r]=[x/inverse for x in rows[r]]
        for i in range(h):
            if i!=r and rows[i][c]:
                f=rows[i][c]; rows[i]=[a-f*b for a,b in zip(rows[i],rows[r])]
        pivots.append(c); r+=1
        if r==h: break
    if any(not any(row[:width]) and row[width] for row in rows): return None
    solution=[Fraction(0)]*width
    for i,c in enumerate(pivots): solution[c]=rows[i][width]
    return tuple(solution)

def check_span_slope(geometry,columns):
    witness=span_slope_obstruction(geometry,columns)
    if witness=='UNKNOWN_LINEALITY':
        return Check(SPAN_SLOPE,'UNKNOWN',diagnostics={'reason':'span meets ker M nontrivially; no pruning'})
    if witness is None:
        return Check(SPAN_SLOPE,'PASS',diagnostics={'stability':'UNKNOWN_STABILITY','scope':'no signed combination exists in the span'})
    coefficients=solve_coefficients(columns,witness)
    return Check(SPAN_SLOPE,'FAIL',slope_matrix(geometry,witness),{'witness_charges':list(witness),'coefficients':None if coefficients is None else [str(x) for x in coefficients],'columns':[list(k) for k in columns],'claim':'sum_a c_a k_a has an entrywise one-signed nonzero slope matrix, so no t>0 gives common zero slopes'})

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


# ---------------------------------------------------------------------------
# Polya-strengthened slope obstruction
#
# The signed-matrix test proves that sum_a c_a mu_{k_a}(t) cannot vanish on the
# open orthant when all coefficients of that quadratic form have one sign. On
# geometries with d_ijj != 0 this is weaker than positivity on the orthant
# (Proposition 4 of docs/slope_obstruction_note.md needs d_ijj = 0). Polya's
# theorem supplies the hierarchy: if (t_1 + ... + t_h)^N * q(t) has all
# coefficients >= 0 and not all zero, then q > 0 on the open orthant; and every
# form strictly positive on the closed simplex has such an N. N = 0 is the
# existing test. The coefficients are linear in k_c, so finding a certificate is
# a linear program; the certificate itself is verified in exact integers.
# ---------------------------------------------------------------------------

def _compositions_of(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions_of(total - first, parts - 1):
            yield (first,) + rest


@lru_cache(maxsize=64)
def polya_forms(geometry, N):
    """Integer linear forms k -> coefficient of t^alpha in (sum t)^N * t^T M(k) t."""
    from math import factorial
    h = geometry.h11
    d = geometry.d
    forms = {}
    for alpha in _compositions_of(N + 2, h):
        row = [0] * h
        for j in range(h):
            for l in range(h):
                beta = list(alpha)
                beta[j] -= 1
                beta[l] -= 1
                if min(beta) < 0:
                    continue
                multinomial = factorial(N)
                for b in beta:
                    multinomial //= factorial(b)
                for i in range(h):
                    row[i] += d[i][j][l] * multinomial
        if any(row):
            forms[alpha] = tuple(row)
    return tuple(forms.values())


def verify_polya_certificate(geometry, k, N):
    """Exact check: all coefficients of (sum t)^N mu_k(t) are >= 0 and not all zero."""
    values = [sum(f[i] * k[i] for i in range(geometry.h11)) for f in polya_forms(geometry, N)]
    return all(v >= 0 for v in values) and any(v > 0 for v in values)


def polya_obstruction(geometry, columns, max_degree=4):
    """Search for a Polya certificate that the slopes have no common zero in T_+.

    Returns {'N', 'k', 'c'} with an exactly verified integer combination k = sum
    c_a k_a, or None. A certificate is a proof (sound); failure to find one
    proves nothing.
    """
    from fractions import Fraction
    try:
        import numpy as np
        from scipy.optimize import linprog
    except ImportError:
        return None
    columns = [tuple(k) for k in columns]
    h = geometry.h11
    K = np.array(columns, dtype=float).T                     # h x 5
    for N in range(max_degree + 1):
        A = np.array(polya_forms(geometry, N), dtype=float)   # forms x h
        AK = A @ K                                            # forms x 5
        # find c with AK c >= 0 and sum(AK c) = 1
        result = linprog(np.zeros(len(columns)), A_ub=-AK, b_ub=np.zeros(len(AK)),
                         A_eq=AK.sum(axis=0, keepdims=True), b_eq=[1.0],
                         bounds=[(None, None)] * len(columns), method='highs')
        if not result.success:
            continue
        for limit in (10, 100, 1000, 10 ** 4, 10 ** 6):
            c = [Fraction(x).limit_denominator(limit) for x in result.x]
            denominator = 1
            for x in c:
                denominator = denominator * x.denominator // _gcd(denominator, x.denominator)
            integer_c = [int(x * denominator) for x in c]
            k = tuple(sum(integer_c[a] * columns[a][i] for a in range(len(columns)))
                      for i in range(h))
            if any(k) and verify_polya_certificate(geometry, k, N):
                return {'N': N, 'k': list(k), 'c': integer_c}
    return None


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# ---------------------------------------------------------------------------
# Exact decision of a common slope zero in the open positive orthant
#
# For a charge matrix of rank h-1 the common zeros of the five slopes form a
# finite set of rays (generically). Setting t_h = 1 -- allowed, since an interior
# point has t_h > 0 -- a lexicographic Groebner basis in shape position gives
# t_i = g_i(x) and p(x) = 0 for x = t_{h-1}. Each real root of p is isolated in
# an exact rational interval; the other coordinates are enclosed by rigorous
# interval arithmetic. A root with every coordinate positive, at which every
# slope vanishes identically modulo the minimal polynomial, is an exact
# real-algebraic witness of poly-stability. If no real root is interior, the
# bundle has no common slope zero in the open orthant: an exact proof of
# instability. Anything else (rank below h-1, no shape position, an undecidable
# sign) is UNDECIDED.
# ---------------------------------------------------------------------------

def _interval_polynomial(poly, X):
    from mpmath import iv
    result = iv.mpf(0)
    for c in poly.all_coeffs():
        result = result * X + iv.mpf(int(c.p)) / iv.mpf(int(c.q))
    return result


def _solve_over_factor(exprs, variables, x, factor):
    """Coordinates as polynomials in x modulo an irreducible factor, or None.

    Works in Q[x]/(factor): repeatedly finds a basis element that, after
    substituting the coordinates already known and reducing modulo the factor,
    is linear in a single unknown with an invertible coefficient.
    """
    import sympy
    known = {x: sympy.Poly(x, x)}
    unknown = [s for s in variables if s != x]
    progress = True
    while unknown and progress:
        progress = False
        for e in exprs:
            substituted = sympy.expand(e.subs({s: known[s].as_expr() for s in known if s != x}))
            present = [s for s in unknown if substituted.has(s)]
            if len(present) != 1:
                continue
            s = present[0]
            poly = sympy.Poly(substituted, s)
            if poly.degree() != 1:
                continue
            a = sympy.Poly(poly.coeff_monomial(s), x).rem(factor)
            b = sympy.Poly(poly.coeff_monomial(1), x).rem(factor)
            if a.is_zero:
                continue
            inverse = sympy.Poly(sympy.invert(a.as_expr(), factor.as_expr(), x), x)
            known[s] = (-b * inverse).rem(factor)
            unknown.remove(s)
            progress = True
    if unknown:
        return None
    return [known[s] for s in variables]


def decide_interior_slope_zero(geometry, columns, refinements=80):
    """STABLE_CERTIFIED / UNSTABLE_CERTIFIED / UNDECIDED, with the evidence."""
    import sympy
    h = geometry.h11
    columns = [tuple(k) for k in columns]
    matrix = sympy.Matrix([list(k) for k in columns])
    rank = matrix.rank()
    if rank != h - 1:
        return {'status': 'UNDECIDED', 'reason': f'charge matrix rank {rank} < h-1: '
                'the slope-zero locus is positive dimensional'}
    t = sympy.symbols(f't1:{h + 1}')
    slopes = [sympy.expand(sum(d * t[j] * t[k] * col[i]
                               for i, j, k, d in geometry.nonzero_intersections))
              for col in columns]
    pivots = matrix.T.rref()[1][:h - 1]
    equations = [slopes[p].subs(t[-1], 1) for p in pivots]
    outcome = _positive_search(equations, list(t[:-1]), {t[-1]: sympy.Integer(1)},
                               slopes, t, refinements)
    if outcome['status'] == 'NONE':
        return {'status': 'UNSTABLE_CERTIFIED',
                'reason': 'no common zero with all coordinates positive (t_h = 1)'}
    return outcome


def _positive_search(equations, variables, assignment, slopes, t, refinements):
    """Recursive exact search for a positive common zero.

    Returns STABLE_CERTIFIED (with a certificate), NONE (proved: no positive
    solution), or UNDECIDED. Rational roots are substituted and the smaller
    system decided recursively; irrational roots are handled in Q[x]/(f) when the
    remaining coordinates are linear there, and are otherwise UNDECIDED.
    """
    import sympy
    from mpmath import iv
    iv.dps = 80
    if not variables:
        point = [assignment[s] for s in t]
        if all(v > 0 for v in point) and all(
                sympy.expand(s.subs(assignment)) == 0 for s in slopes):
            return {'status': 'STABLE_CERTIFIED', 'kind': 'EXACT_RATIONAL',
                    't': [str(v) for v in point]}
        return {'status': 'NONE'}
    equations = [e for e in (sympy.expand(e) for e in equations) if e != 0]
    if not equations:
        return {'status': 'UNDECIDED', 'reason': 'free variables: positive-dimensional'}
    basis = sympy.groebner(equations, *variables, order='lex')
    exprs = list(basis.exprs)
    if exprs == [1]:
        return {'status': 'NONE'}
    x = variables[-1]
    univariate = [e for e in exprs if e.free_symbols <= {x} and e.free_symbols]
    if not univariate:
        return {'status': 'UNDECIDED', 'reason': 'no eliminant: positive-dimensional'}
    polynomial = sympy.Poly(univariate[0], x)
    undecided = 0
    for factor, _ in sympy.factor_list(polynomial)[1]:
        factor = sympy.Poly(factor, x)
        positive = []
        zero_is_root = factor.eval(0) == 0
        for (a, b), _ in factor.intervals():
            a, b = sympy.Rational(a), sympy.Rational(b)
            if b < 0 or (b == 0 and a == b):
                continue                          # a negative root, or the root 0
            if a == b:
                if a > 0:
                    positive.append((a, b))
                continue
            if zero_is_root and a <= 0 <= b:
                continue                          # this interval isolates the root 0
            # the isolated root is not 0: refine until the interval is off zero
            while a <= 0 < b:
                a, b = factor.refine_root(a, b, eps=(b - a) / 4)
                if a == b:
                    break
            if a > 0:
                positive.append((a, b))
        if not positive:
            continue
        if factor.degree() == 1:
            root = sympy.Rational(-factor.coeff_monomial(1), factor.coeff_monomial(x))
            sub = _positive_search([e.subs(x, root) for e in exprs], variables[:-1],
                                   {**assignment, x: root}, slopes, t, refinements)
            if sub['status'] == 'STABLE_CERTIFIED':
                return sub
            undecided += sub['status'] == 'UNDECIDED'
            continue
        coordinates = _solve_over_factor(exprs, variables, x, factor)
        if coordinates is None:
            undecided += len(positive)
            continue
        for a, b in positive:
            if any(c.is_zero or c.rem(factor).is_zero for c in coordinates):
                continue
            decided = False
            for _ in range(refinements):
                X = iv.mpf([str(a), str(b)])
                boxes = [_interval_polynomial(c, X) for c in coordinates]
                if any(box.b < 0 for box in boxes):
                    decided = True
                    break
                if all(box.a > 0 for box in boxes):
                    substitution = dict(assignment)
                    substitution.update(zip(variables, [c.as_expr() for c in coordinates]))
                    if all(sympy.Poly(sympy.expand(s.subs(substitution)), x).rem(factor).is_zero
                           for s in slopes):
                        return {'status': 'STABLE_CERTIFIED', 'kind': 'EXACT_ALGEBRAIC',
                                'minimal_polynomial': str(factor.as_expr()),
                                'variable': str(x), 'root_interval': [str(a), str(b)],
                                'fixed': {str(k): str(v) for k, v in assignment.items()},
                                'coordinates': [str(c.as_expr()) for c in coordinates],
                                't_numeric': [float(box.mid) for box in boxes]}
                    decided = True
                    break
                a, b = factor.refine_root(a, b, eps=(b - a) / 16)
            if not decided:
                undecided += 1
    if undecided:
        return {'status': 'UNDECIDED', 'reason': f'{undecided} positive roots not resolved'}
    return {'status': 'NONE'}
