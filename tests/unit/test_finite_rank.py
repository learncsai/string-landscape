from itertools import product
import pytest
import sympy
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.finite_rank import coefficients,multiplication_matrix,modular_rank,rank_certificate,generic_cohomology,PRIME

def test_prime(): assert sympy.isprime(PRIME)

def test_modular_vs_rational_rank():
    for k in [(-2,-2,2,2),(-3,2,2,2),(2,2,2,2),(-3,-2,2,3)]:
        matrix=multiplication_matrix(k,coefficients())
        assert modular_rank(matrix)==sympy.polys.matrices.DomainMatrix.from_Matrix(sympy.Matrix(matrix)).rank()

def test_monomial_dual_multiplication():
    coeff={k:0 for k in product(range(3),repeat=4)};coeff[(0,0,0,0)]=1
    matrix=multiplication_matrix((-2,-2,2,2),coeff)
    assert modular_rank(matrix)==1
    assert sum(map(sum,matrix))==1

def test_generic_rank_serre():
    g=benchmark('7862')
    for k in [(-2,-2,2,2),(-3,-2,2,3),(-2,2,2,2)]:
        l=LineBundle(k);cert=rank_certificate(g,l)
        assert cert and cert['rank']==min(cert['source_dimension'],cert['target_dimension'])
        assert generic_cohomology(g,l).dimensions==generic_cohomology(g,l.dual()).dimensions[::-1]

def test_budget_and_unsupported():
    assert rank_certificate(benchmark('7862'),LineBundle((-100,-100,100,100))) is None
    assert rank_certificate(benchmark('7447'),LineBundle((-2,-2,2,2,0))) is None
