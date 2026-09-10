import json
from pathlib import Path
import sympy as s
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.codimension_two import equations,resultant,rank_certificate
from string_sm_sat.cohomology.cached import generic_cohomology
from string_sm_sat.physics.spectrum import check_full_spectrum

def test_generic_golden_spectrum():
    fixture=json.loads((Path(__file__).parents[1]/'fixtures/x7447.json').read_text());g=benchmark('7447');v=BundleSum.from_rows(fixture['matrix_rows'])
    check=check_full_spectrum(v,g,4,generic=True)
    assert check.outcome=='PASS'
    assert check.residual=={'V':tuple(fixture['published_V_cohomology']),'wedge2':tuple(fixture['published_wedge2_cohomology'])}
    assert not check.metadata.can_safely_prune
    for line in v.lines+v.wedge2().lines:
        assert generic_cohomology(g,line).dimensions==generic_cohomology(g,line.dual()).dimensions[::-1]

def test_resultant_direct_symbolic_determinant():
    # Independent polynomial-ring determinant verifies coefficient convolution.
    f=equations();x=s.symbols('x0:5');coordinate=4
    expressions=[sum(v*s.prod(x[i]**m[i] for i in range(5)) for m,v in p.items()) for p in f]
    det=s.expand(expressions[0].coeff(x[4],0)*expressions[1].coeff(x[4],1)-expressions[0].coeff(x[4],1)*expressions[1].coeff(x[4],0))
    r=resultant(f,coordinate)
    actual=s.Poly(det,*x[:4]).as_dict()
    assert {m:v for m,v in r.items() if v}==actual

def test_resultant_coordinates_and_dual():
    g=benchmark('7447')
    for k in [(-2,-2,2,2,0),(0,2,-2,-2,2),(2,2,-2,-2,0)]:
        l=LineBundle(k);r=rank_certificate(g,l)
        assert r and r['method']=='relative_P1_resultant_d2' and r['rank']==9
        assert generic_cohomology(g,l).dimensions==(0,0,0,0)
