from dataclasses import asdict
from ..physics.structure_group import check_c1,check_structure_group
from ..physics.anomaly import check_anomaly
from ..physics.spectrum import check_indices,check_full_spectrum
from ..physics.stability import necessary_stability,exact_witness,numerical_witness
from ..physics.index import bundle_index,bundle_c2
from ..search.checkpoints import code_hash,digest

def candidate_certificate(geometry,bundle,gamma,t=None,numeric=False):
    checks=[check_c1(bundle),check_structure_group(bundle),check_anomaly(bundle,geometry),check_indices(bundle,geometry,gamma),necessary_stability(geometry,bundle.lines),check_full_spectrum(bundle,geometry,gamma)]
    if t is not None: checks.append(exact_witness(geometry,bundle,t))
    if numeric: checks.append(numerical_witness(geometry,bundle))
    return {'schema':1,'kind':'candidate','geometry':asdict(geometry),'geometry_sha256':digest(asdict(geometry)),'matrix_columns':bundle.canonical,'gamma_order':gamma,'c1':bundle.c1,'c2':bundle_c2(geometry,bundle),'index_V':bundle_index(geometry,bundle),'index_wedge2':bundle_index(geometry,bundle.wedge2()),'checks':[c.as_dict() for c in checks],'generic_spectrum':check_full_spectrum(bundle,geometry,gamma,generic=True).as_dict(),'rational_witness':None if t is None else [str(x) for x in t],'classification':'REJECTED' if any(c.outcome=='FAIL' for c in checks) else 'UNKNOWN','equivariance':'UNKNOWN','wilson_line':'UNKNOWN','additional_massless_U1':'UNKNOWN','full_structure_group':'UNKNOWN','software_source_sha256':code_hash()}
