import copy,json
import pytest
from string_sm_sat.cli import golden
from string_sm_sat.certificates.verifier import verify_candidate,verify_search
from string_sm_sat.certificates.search_certificate import search_certificate
from string_sm_sat.search.split_search import split_search
from string_sm_sat.search.domain import Domain
from string_sm_sat.geometry.cicy import benchmark

def test_candidate_recompute_and_tamper():
    c=json.loads(json.dumps(golden()))
    assert verify_candidate(c)['verified']
    for field in ('index_V','index_wedge2'):
        bad=copy.deepcopy(c);bad[field]=99
        with pytest.raises(ValueError): verify_candidate(bad)
    bad=copy.deepcopy(c);bad['checks'][0]['outcome']='FAIL'
    with pytest.raises(ValueError): verify_candidate(bad)
    bad=copy.deepcopy(c);bad['rational_witness']=['1']*5
    with pytest.raises(ValueError): verify_candidate(bad)

def test_bounded_replay_and_partial():
    d=Domain(benchmark('bicubic'),1,1)
    cert=search_certificate(d,split_search(d))
    assert verify_search(cert)['outcome']=='UNSAT_BOUNDED'
    bad=copy.deepcopy(cert);bad['outcome']='SAT_BOUNDED'
    with pytest.raises(ValueError): verify_search(bad)
    d=Domain(benchmark('7862'),1,2)
    cert=search_certificate(d,split_search(d,max_roots=1))
    assert cert['outcome']=='UNKNOWN_BOUNDED'
    assert not verify_search(cert)['verified']

def test_reference_budget_refuses_expensive_replay():
    d=Domain(benchmark('7862'),1,2);cert=search_certificate(d,split_search(d))
    with pytest.raises(ValueError): verify_search(cert,max_states=100)

def test_cohomology_rank_certificate_replay():
    from string_sm_sat.certificates.cohomology_certificate import cohomology_certificate,verify_cohomology
    from string_sm_sat.bundles.line_bundle import LineBundle
    for geometry,k in [('7862',(-2,-2,2,2)),('7447',(-2,-2,2,2,0))]:
        cert=cohomology_certificate(benchmark(geometry),LineBundle(k),generic=True)
        assert verify_cohomology(cert)['verified']
        cert['rank_witness']['rank']-=1
        with pytest.raises(ValueError):verify_cohomology(cert)


def test_unbounded_divisibility_certificate_round_trip():
    """UNSAT_UNBOUNDED is emitted, and the verifier recomputes the obstruction."""
    from string_sm_sat.search.domain import Domain
    from string_sm_sat.search.split_search import split_search
    from string_sm_sat.certificates.search_certificate import search_certificate
    from string_sm_sat.certificates.verifier import verify_search
    d=Domain(benchmark('7447'),3,5,'GUT_FULL',True,1,'span')
    certificate=search_certificate(d,split_search(d))
    assert certificate['outcome']=='UNSAT_UNBOUNDED'
    assert certificate['unbounded_obstruction']['d_X']==2
    assert not certificate['survivors']
    checked=verify_search(json.loads(json.dumps(certificate,default=str)))
    assert checked['verified'] and checked['outcome']=='UNSAT_UNBOUNDED'
    # a domain without the obstruction must not claim it
    ok=Domain(benchmark('7447'),1,2,'GUT_FULL',True,1,'span')
    assert search_certificate(ok,split_search(ok))['unbounded_obstruction'] is None
