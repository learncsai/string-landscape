"""Compare precisely identified candidate stage; do not certify model counts."""
import argparse,json
from pathlib import Path
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.geometry.symmetries import canonical_row_orbit
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.physics.stability import numerical_witness,exact_witness
from string_sm_sat.physics.spectrum import check_full_spectrum
from string_sm_sat.search.checkpoints import atomic_json
p=argparse.ArgumentParser();p.add_argument('certificate');p.add_argument('--output',required=True);a=p.parse_args()
c=json.loads(Path(a.certificate).read_text());g=benchmark(c['domain']['geometry']['identifier'])
keys=sorted({canonical_row_orbit(g,k) for k in c['enumeration']['survivors']})
rows=[]
for k in keys:
    v=BundleSum.from_columns(k)
    rows.append({'columns':k,'stability_equal_t':exact_witness(g,v,(1,)*g.h11).as_dict(),'stability_numerical':numerical_witness(g,v).as_dict(),'spectrum':check_full_spectrum(v,g,c['domain']['gamma'],generic=True).as_dict()})
reference={(1,2):0,(1,4):0,(2,2):5,(2,4):9}
result={'geometry':g.identifier,'K':c['domain']['K'],'gamma':c['domain']['gamma'],'input_complete':c['enumeration']['complete'],'summand_canonical_count':len(c['enumeration']['survivors']),'ambient_row_orbit_count':len(keys),'published_table4_count':reference.get((c['domain']['K'],c['domain']['gamma'])) if g.identifier=='7862' else None,'comparison_scope':'candidate-count comparison only: published Table 4 has explicit slope solutions before cohomology; our split run uses necessary slopes, GUT_FULL single-index range, no equivariance test. Numerical witnesses are not exact certification.','cohomology_scope':'Zariski-generic smooth family; invariant symmetry subfamily not certified','candidates':rows}
atomic_json(a.output,result);print(json.dumps({k:v for k,v in result.items() if k!='candidates'},indent=2))
