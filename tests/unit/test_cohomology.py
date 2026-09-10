from itertools import product
import pytest
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.cohomology.cached import cohomology
from string_sm_sat.cohomology.interface import Cohomology,CohomologyStatus
from string_sm_sat.physics.index import index
@pytest.mark.parametrize('name,h',[('7862',4),('7447',5)])
def test_koszul_serre_index_box(name,h):
    g=benchmark(name); known=0; unknown=0
    for k in product(range(-1,2),repeat=h):
        l=LineBundle(k);r=cohomology(g,l);s=cohomology(g,l.dual())
        if r.dimensions is None: unknown+=1;continue
        known+=1
        assert r.dimensions==s.dimensions[::-1]
        assert sum((-1)**i*x for i,x in enumerate(r.dimensions))==index(g,l)
    assert known>0

@pytest.mark.parametrize('name,h',[('7862',4),('7447',5)])
def test_exception_and_trivial(name,h):
    g=benchmark(name)
    assert cohomology(g,LineBundle((0,)*h)).dimensions==(1,0,0,1)
    assert cohomology(g,LineBundle((2,-2)+(0,)*(h-2))).dimensions==(0,3,3,0)
    assert cohomology(g,LineBundle((-1,)+(0,)*(h-1))).dimensions==(0,0,0,2)

def test_unknown_maps_not_maximal_rank_assumption():
    assert cohomology(benchmark('7447'),LineBundle((-2,-2,2,2,0))).status=='UNKNOWN'

def test_inconsistent_backend_raises():
    with pytest.raises(ArithmeticError): Cohomology((1,0,0,0),CohomologyStatus.EXACT_EXTERNAL,'bad fixture','none').validate(benchmark('7862'),LineBundle((0,)*4))
