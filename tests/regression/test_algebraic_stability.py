import copy
import pytest
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.certificates.algebraic_stability import verify_algebraic_witness

def fixture():
    v=BundleSum.from_columns([(-2,-1,1,1),(-1,1,-1,1),(-1,1,-1,1),(2,-2,1,-1),(2,1,0,-2)])
    w={'polynomial_ascending':[-7,0,1],'isolating_interval':[2,3],'t_coefficients_ascending':[[1],[1],['-1/3','1/3'],['-1/3','1/3']]}
    return benchmark('7862'),v,w

def test_algebraic_positive_exact():
    g,v,w=fixture();assert verify_algebraic_witness(g,v,w).outcome=='PASS'
@pytest.mark.parametrize('change',['interval','coordinate','negative'])
def test_invalid_algebraic_witness(change):
    g,v,w=fixture()
    if change=='interval':w['isolating_interval']=[3,4]
    elif change=='coordinate':w['t_coefficients_ascending'][0]=[2]
    else:w['t_coefficients_ascending'][0]=[-1]
    with pytest.raises(ValueError):verify_algebraic_witness(g,v,w)
