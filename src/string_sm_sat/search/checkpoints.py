import hashlib,json,os,pathlib,subprocess
from dataclasses import asdict

def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def code_hash():
    root=pathlib.Path(__file__).resolve().parents[1]; h=hashlib.sha256()
    for p in sorted(root.rglob('*.py')):
        h.update(str(p.relative_to(root)).encode()); h.update(p.read_bytes())
    return h.hexdigest()
def identity(domain): return digest({'domain':domain.as_dict(),'source':code_hash(),'inputs':input_hashes()})
def atomic_json(path,value):
    path=pathlib.Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    with temp.open('w') as f:
        json.dump(value,f,sort_keys=True,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)
def read_checkpoint(path,key):
    value=json.loads(pathlib.Path(path).read_text())
    if value.get('identity')!=key: raise ValueError('checkpoint domain/source mismatch')
    checksum=value.pop('checksum',None)
    if checksum!=digest(value): raise ValueError('checkpoint integrity mismatch')
    return value

def save_checkpoint(path,value): atomic_json(path,{**value,'checksum':digest(value)})

def git_commit():
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=pathlib.Path(__file__).parent,stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError,subprocess.CalledProcessError): return None

def input_hashes():
    root=pathlib.Path(__file__).resolve().parents[3]
    files=[root/"data/manifests/sources.json",root/"data/processed/geometries.json"]
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}
