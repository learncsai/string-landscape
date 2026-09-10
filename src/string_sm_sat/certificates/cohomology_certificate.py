from dataclasses import asdict
from ..cohomology.cached import cohomology,generic_cohomology
from ..cohomology.analytic import koszul_terms
from ..cohomology.finite_rank import rank_certificate as tetra_rank
from ..cohomology.codimension_two import rank_certificate as codim_rank
from ..geometry.cicy import benchmark
from ..bundles.line_bundle import LineBundle
from ..search.checkpoints import digest

def cohomology_certificate(geometry,line,generic=False):
    result=(generic_cohomology if generic else cohomology)(geometry,line)
    rank=None
    if generic and cohomology(geometry,line).dimensions is None:
        rank=(codim_rank if geometry.identifier=='7447' else tetra_rank)(geometry,line)
    return {'schema':1,'kind':'cohomology','geometry':geometry.identifier,'geometry_sha256':digest(asdict(geometry)),'line_bundle':line.k,'generic':generic,'result':asdict(result),'koszul_E1':koszul_terms(geometry,line),'rank_witness':rank,'scope':'Zariski-generic smooth family; invariant subfamily UNKNOWN' if generic else 'smooth regular complete intersections with this configuration'}

def verify_cohomology(data):
    if data.get('kind')!='cohomology' or data.get('schema')!=1 or type(data.get('generic')) is not bool:raise ValueError('invalid cohomology certificate')
    g=benchmark(data['geometry']);l=LineBundle(tuple(data['line_bundle']))
    computed=cohomology_certificate(g,l,data['generic'])
    if digest(data)!=digest(computed):raise ValueError('cohomology replay mismatch')
    return {'verified':computed['result']['dimensions'] is not None,'status':computed['result']['status'],'dimensions':computed['result']['dimensions'],'scope':computed['scope']}
