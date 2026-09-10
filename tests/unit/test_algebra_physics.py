import json
from pathlib import Path
from fractions import Fraction
from itertools import permutations,product
import pytest
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.line_bundle import LineBundle
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.physics.index import index,bundle_c2,bundle_index
from string_sm_sat.physics.structure_group import check_c1,check_structure_group
from string_sm_sat.physics.anomaly import check_anomaly
from string_sm_sat.physics.spectrum import check_indices
from string_sm_sat.physics.stability import exact_witness,necessary_stability,signed_matrix_ok
from string_sm_sat.physics.constraints import RULES

def golden():
    f=json.loads((Path(__file__).parents[1]/'fixtures/x7447.json').read_text())
    return benchmark('7447'),BundleSum.from_rows(f['matrix_rows'])

def test_immutable_algebra_and_large_integer():
    a=LineBundle((10**30,-2,3,4));b=LineBundle((-1,5,0,2))
    assert a.tensor(b).k==(10**30-1,3,3,6)
    assert a.tensor(a.dual()).k==(0,)*4
    assert index(benchmark('7862'),a)==2*(sum(a.k)+sum(a.k[i]*a.k[j]*a.k[k] for i,j,k in [(0,1,2),(0,1,3),(0,2,3),(1,2,3)]))
    assert index(benchmark('7862'),a.dual())==-index(benchmark('7862'),a)
    with pytest.raises(TypeError): LineBundle((1.0,2))
    with pytest.raises(ValueError): a.tensor(LineBundle((1,)))

def test_whitney_independent_negative_quadratic():
    g,v=golden()
    direct=tuple(-Fraction(sum(g.d[r][i][j]*l.k[i]*l.k[j] for l in v.lines for i in range(5) for j in range(5)),2) for r in range(5))
    assert direct==bundle_c2(g,v)==(24,)*5
    # Positive sign printed in 1307.4787 Section 5 would give -24 and must fail.
    assert tuple(-x for x in direct)!=g.c2

def test_golden_rational_stability():
    g,v=golden()
    result=exact_witness(g,v,(5,29,15,11,5))
    assert result.outcome=='PASS'
    assert necessary_stability(g,v.lines,2).outcome=='PASS'
    assert exact_witness(g,v,(0,0,0,0,0)).outcome=='UNKNOWN'
    assert exact_witness(g,v,(1,1,1,1,1)).outcome=='UNKNOWN'
    with pytest.raises(TypeError): exact_witness(g,v,(1.,)*5)

def test_zero_matrix_not_rejected():
    assert signed_matrix_ok((0,0,0))
    assert signed_matrix_ok((-1,0,1))
    assert not signed_matrix_ok((0,1,2))
    g=benchmark('quintic')
    assert necessary_stability(g,(LineBundle((1,)),)).outcome=='FAIL'

def test_permutation_multiplicity():
    g,v=golden()
    for lines in permutations(v.lines): assert BundleSum(lines).canonical==v.canonical
    w=BundleSum.from_columns([(1,)]*2+[(-1,)]*2+[(0,)])
    assert w.canonical.count((1,))==2
    assert len(w.wedge2().lines)==10

def test_mutated_c1():
    g,v=golden();k=[list(l.k) for l in v.lines];k[0][0]+=1
    bad=BundleSum.from_columns(k)
    assert check_c1(bad).outcome=='FAIL'
    assert check_anomaly(bad,g).outcome=='UNKNOWN'

def test_mutated_index_preserves_c1():
    g,v=golden(); k=[list(l.k) for l in v.lines]; k[0][0]+=1;k[1][0]-=1
    bad=BundleSum.from_columns(k)
    assert check_c1(bad).outcome=='PASS'
    assert check_indices(bad,g,4).outcome=='FAIL'

def test_mutated_anomaly():
    g,v=golden();bad=BundleSum.from_columns([tuple(2*x for x in l.k) for l in v.lines])
    assert check_c1(bad).outcome=='PASS'
    assert check_anomaly(bad,g).outcome=='FAIL'
    assert check_anomaly(bad,g).residual==(-72,)*5

def test_mutated_structure():
    g,v=golden();k=[l.k for l in v.lines];k[1]=tuple(a+b for a,b in zip(k[0],k[1]));k[0]=(0,)*5
    bad=BundleSum.from_columns(k)
    assert check_c1(bad).outcome=='PASS'
    assert check_structure_group(bad).outcome=='FAIL'

def test_constraint_metadata():
    for rule in RULES:
        assert rule.name and rule.reference and rule.input_assumptions
        if rule.mathematical_status in ('HEURISTIC','NUMERIC_WITNESS','UNKNOWN'): assert not rule.can_safely_prune
