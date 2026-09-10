"""Resource-measured reproducible benchmark. CLI requires explicit small box."""
import argparse,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--K',type=int,default=1);p.add_argument('--gamma',type=int,default=2);p.add_argument('--geometry',default='7862');p.add_argument('--max-roots',type=int);a=p.parse_args()
if a.K>2: p.error('K>2 requires a separately documented profiling decision; use CLI explicitly after review')
base=ROOT/'benchmarks'/('x'+a.geometry)/f'k{a.K}-gamma{a.gamma}-current'
cmd=[sys.executable,'-m','string_sm_sat.cli','search','--geometry',a.geometry,'--K',str(a.K),'--gamma',str(a.gamma),'--checkpoint',str(base)+'.checkpoint.json','--output',str(base)+'.json']
if a.max_roots is not None:cmd+=['--max-roots',str(a.max_roots)]
result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
if result.returncode: print(result.stderr,file=sys.stderr);raise SystemExit(result.returncode)
Path(str(base)+'-output.json').write_text(result.stdout);print(result.stdout)
