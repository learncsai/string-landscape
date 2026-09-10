import pytest
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.search.domain import Domain
from string_sm_sat.search.brute_force import brute_force,canonical_domain as brute_domain
from string_sm_sat.search.split_search import split_search,canonical_domain as split_domain
@pytest.mark.parametrize('h,K',[(1,0),(1,1),(1,2),(2,1)])
def test_nonempty_canonical_domains(h,K):
    a=brute_domain(h,K); b=split_domain(h,K)
    assert a and a==b
    assert tuple([(0,)*h]*5) in a
@pytest.mark.parametrize('geometry,K,gamma,target,pairs',[(g,k,n,t,p) for g,k in [('quintic',1),('quintic',2),('bicubic',1)] for n in [1,2] for t in ['GUT_FULL','GUT_CHIRAL'] for p in [False,True]])
def test_physics_sets(geometry,K,gamma,target,pairs):
    d=Domain(benchmark(geometry),K,gamma,target,pairs)
    reference,_=brute_force(d)
    result=split_search(d)
    assert result['complete']
    assert reference==set(result['survivors'])

def test_checkpoint_and_threads(tmp_path):
    d=Domain(benchmark('7862'),1,2)
    full=split_search(d)
    path=tmp_path/'checkpoint.json'
    partial=split_search(d,checkpoint=path,max_roots=2)
    assert not partial['complete']
    resumed=split_search(d,checkpoint=path)
    threaded=split_search(d,workers=2)
    assert full['survivors']==resumed['survivors']==threaded['survivors']
    assert full['counts']==resumed['counts']==threaded['counts']
    with pytest.raises(ValueError): split_search(Domain(benchmark('7862'),1,4),checkpoint=path)

@pytest.mark.parametrize('target',['GUT_FULL','GUT_CHIRAL'])
def test_nonempty_physics_subset_and_resume(tmp_path,target):
    # A known K=2 tetraquadric orbit plus extra columns makes the reference
    # affordable while exercising real nonempty physics survivors.
    columns=((-2,0,0,1),(0,-1,1,0),(1,1,-2,0),(1,1,0,-1),(0,0,0,0),(1,0,0,0))
    d=Domain(benchmark('7862'),2,2,target,True,1,columns)
    reference,_=brute_force(d)
    assert reference
    full=split_search(d)
    assert set(full['survivors'])==reference
    path=tmp_path/'nonempty.json'
    split_search(d,checkpoint=path,max_roots=1)
    assert split_search(d,checkpoint=path)['survivors']==full['survivors']
    assert split_search(d,workers=2)['survivors']==full['survivors']
