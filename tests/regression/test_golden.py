import json
from pathlib import Path
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.physics.index import bundle_index,bundle_c2

def golden():
    f=json.loads((Path(__file__).parents[1]/'fixtures/x7447.json').read_text())
    return benchmark('7447'),BundleSum.from_rows(f['matrix_rows']),f

def test_golden_topology_algebra():
    g,v,f=golden()
    assert v.c1==(0,)*5
    assert bundle_index(g,v)==bundle_index(g,v.wedge2())==-12
    assert bundle_c2(g,v)==g.c2==tuple(f['published_c2'])
    assert sum((-1)**i*x for i,x in enumerate(f['published_V_cohomology']))==-12
    assert sum((-1)**i*x for i,x in enumerate(f['published_wedge2_cohomology']))==-12
