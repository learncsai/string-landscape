"""Reproduce exact slope witnesses for the five K=2,Gamma=2 row orbits."""
import json
from pathlib import Path
from fractions import Fraction
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.physics.stability import exact_witness
from string_sm_sat.certificates.algebraic_stability import verify_algebraic_witness
from string_sm_sat.search.checkpoints import atomic_json
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'benchmarks/x7862/k2-comparison.json').read_text());g=benchmark('7862')
expected_first=[(-2,-1,1,1),(-2,-1,1,1),(-2,-1,2,2),(-2,0,0,1),(-2,0,1,2)]
rational={1:(4,4,4,1),2:(4,1,4,4),3:(4,4,4,1)}
algebraic={0:{'polynomial_ascending':[-7,0,1],'isolating_interval':[2,3],'t_coefficients_ascending':[[1],[1],['-1/3','1/3'],['-1/3','1/3']]},4:{'polynomial_ascending':[-3,0,1],'isolating_interval':[1,2],'t_coefficients_ascending':[[1],[1,1],[1],[1,1]]}}
rows=[]
for i,row in enumerate(c['candidates']):
    if tuple(row['columns'][0])!=expected_first[i]: raise ValueError('unexpected fixture ordering')
    bundle=BundleSum.from_columns(row['columns'])
    check=exact_witness(g,bundle,rational[i]) if i in rational else verify_algebraic_witness(g,bundle,algebraic[i])
    if check.outcome!='PASS': raise ArithmeticError('exact witness failed')
    rows.append({'columns':row['columns'],'stability':check.as_dict(),'generic_spectrum':row['spectrum']})
atomic_json(ROOT/'benchmarks/x7862/k2-exact-stability.json',{'geometry':'7862','K':2,'gamma':2,'exact_stability_orbits':len(rows),'candidates':rows,'scope':'exact upstairs stability; full gauge/equivariance and symmetry-subfamily cohomology UNKNOWN'})
print('Verified 3 rational and 2 real-algebraic interior slope witnesses.')
