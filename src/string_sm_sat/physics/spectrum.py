from .constraints import Check,INDEX,SPECTRUM,SPECTRUM_GENERIC
from .index import bundle_index
from ..cohomology.cached import cohomology,generic_cohomology

def check_indices(bundle,geometry,gamma):
    if type(gamma) is not int or gamma<1: raise ValueError('positive integral symmetry order required')
    values=(bundle_index(geometry,bundle),bundle_index(geometry,bundle.wedge2()))
    return Check(INDEX,'PASS' if values==(-3*gamma,)*2 else 'FAIL',values)

def sum_cohomology(geometry,bundle,generic=False):
    backend=generic_cohomology if generic else cohomology
    results=[backend(geometry,l) for l in bundle.lines]
    if any(r.dimensions is None for r in results): return None
    return tuple(map(sum,zip(*(r.dimensions for r in results))))

def check_full_spectrum(bundle,geometry,gamma,generic=False):
    metadata=SPECTRUM_GENERIC if generic else SPECTRUM
    v=sum_cohomology(geometry,bundle,generic); w=sum_cohomology(geometry,bundle.wedge2(),generic)
    if v is None or w is None: return Check(metadata,'UNKNOWN',diagnostics={'V':v,'wedge2':w})
    nh=w[2]
    good=v==(0,3*gamma,0,0) and nh>0 and w==(0,3*gamma+nh,nh,0)
    return Check(metadata,'PASS' if good else 'FAIL',{'V':v,'wedge2':w})
