import argparse,importlib.util,json,platform,shutil,subprocess,sys
from pathlib import Path
from .geometry.cicy import benchmark
from .bundles.bundle_sum import BundleSum
from .bundles.line_bundle import LineBundle
from .certificates.cohomology_certificate import cohomology_certificate,verify_cohomology
from .search.domain import Domain
from .search.split_search import split_search
from .search.checkpoints import atomic_json
from .certificates.candidate_certificate import candidate_certificate
from .certificates.search_certificate import search_certificate
from .certificates.verifier import verify_candidate,verify_search

def doctor():
    try:
        import psutil
        memory=psutil.virtual_memory().total
    except ImportError: memory=None
    return {'architecture':platform.machine(),'system':platform.platform(),'python':sys.version,'ram_bytes':memory,'tools':{x:shutil.which(x) for x in ('clang','cc','wolframscript','math','cohomCalg')},'packages':{x:importlib.util.find_spec(x) is not None for x in ('numpy','scipy','sympy','pytest','psutil')},'exact_core':'Python integers/Fraction; no numerical dependency required','external_cohomology':'NOT_CONFIGURED'}

def golden(numeric=False):
    rows=((-1,-2,1,1,1),(0,-2,-1,1,2),(0,2,-1,1,-2),(0,2,0,0,-2),(1,0,0,-2,1))
    return candidate_certificate(benchmark('7447'),BundleSum.from_rows(rows),4,(5,29,15,11,5),numeric)

def main(argv=None):
    parser=argparse.ArgumentParser(description='Exact finite-domain heterotic research engine')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    g=sub.add_parser('golden');g.add_argument('--output');g.add_argument('--numeric',action='store_true')
    scan=sub.add_parser('search');scan.add_argument('--geometry',choices=['7862','7447','quintic','bicubic'],default='7862');scan.add_argument('--K',type=int,required=True);scan.add_argument('--gamma',type=int,default=2);scan.add_argument('--target',choices=['GUT_CHIRAL','GUT_FULL'],default='GUT_FULL');scan.add_argument('--unrestricted-pair-indices',action='store_true');scan.add_argument('--checkpoint');scan.add_argument('--max-roots',type=int);scan.add_argument('--slope-rule',choices=['box','span','both'],default='box');scan.add_argument('--workers',type=int,default=1);scan.add_argument('--output',required=True)
    coh=sub.add_parser('cohomology');coh.add_argument('--geometry',required=True);coh.add_argument('--charges',type=int,nargs='+',required=True);coh.add_argument('--generic',action='store_true');coh.add_argument('--output',required=True)
    for name in ('verify-candidate','verify-search','verify-cohomology'):
        p=sub.add_parser(name);p.add_argument('certificate')
        if name=='verify-search': p.add_argument('--max-states',type=int,default=1000000)
    args=parser.parse_args(argv)
    try:
        if args.command=='doctor': result=doctor()
        elif args.command=='golden':
            result=golden(args.numeric)
            if args.output: atomic_json(args.output,result)
        elif args.command=='cohomology':
            result=cohomology_certificate(benchmark(args.geometry),LineBundle(tuple(args.charges)),args.generic);atomic_json(args.output,result)
        elif args.command=='search':
            d=Domain(benchmark(args.geometry),args.K,args.gamma,args.target,not args.unrestricted_pair_indices,1,args.slope_rule)
            run=split_search(d,checkpoint=args.checkpoint,max_roots=args.max_roots,workers=args.workers)
            cert=search_certificate(d,run);atomic_json(args.output,cert)
            result={'outcome':cert['outcome'],'domain':d.as_dict(),'counts':run['counts'],'complete':run['complete'],'elapsed_seconds':run['elapsed_seconds'],'peak_rss_bytes':run['peak_rss_bytes'],'unknown_count':cert['unknown_count'],'certificate':args.output}
        else:
            data=json.loads(Path(args.certificate).read_text())
            result=verify_candidate(data) if args.command=='verify-candidate' else (verify_cohomology(data) if args.command=='verify-cohomology' else verify_search(data,args.max_states))
        print(json.dumps(result,indent=2,default=str))
    except (ValueError,ArithmeticError,KeyError,TypeError) as exc:
        parser.exit(2,f'ERROR: {exc}\n')
if __name__=='__main__': main()
