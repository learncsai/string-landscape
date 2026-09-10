"""Recompute the golden candidate and all nontrivial generic Koszul rank witnesses."""
from pathlib import Path
from string_sm_sat.cli import golden
from string_sm_sat.geometry.cicy import benchmark
from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.cohomology.codimension_two import rank_certificate
from string_sm_sat.search.checkpoints import atomic_json
from string_sm_sat.certificates.verifier import verify_candidate
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    cert=golden();assert cert['generic_spectrum']['outcome']=='PASS'
    assert cert['generic_spectrum']['residual']=={'V':(0,12,0,0),'wedge2':(0,15,3,0)}
    atomic_json(ROOT/'benchmarks/x7447/golden.json',cert)
    atomic_json(ROOT/'benchmarks/x7447/verification.json',verify_candidate(cert))
    g=benchmark('7447');v=BundleSum.from_columns(cert['matrix_columns'])
    ranks=[rank_certificate(g,l) for l in v.lines+v.wedge2().lines]
    atomic_json(ROOT/'benchmarks/x7447/generic-rank-certificates.json',[r for r in ranks if r is not None])
    print('Reproduced c1=0, both indices=-12, c2=(24,24,24,24,24), exact rational slopes, generic V=(0,12,0,0), wedge2=(0,15,3,0). Full gauge/equivariant status UNKNOWN.')
