"""Immutable, hash-checked acquisition; failed sources are recorded, never fabricated."""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = {f'arxiv_{p}.html': (f'https://arxiv.org/html/{p}', p, 'Primary paper HTML') for p in ['1106.4804','1202.1757','1307.4787','2306.03147','2606.22275','1311.1941','1808.09992']}
BASE='https://www-thphys.physics.ox.ac.uk/projects/CalabiYau/'
SOURCES.update({'cicylist.txt':(BASE+'cicylist/cicylist.txt','Candelas et al. 1988','Oxford original CICY list'), 'cicy_index.html':(BASE+'cicylist/index.html','1307.4787','Oxford index'), 'models_index.html':(BASE+'linebundlemodels/index.html','1307.4787','Oxford model database index'), 'symmetries.html':(BASE+'CICY_Symmetries/index.html','1003.3235','Oxford symmetry index')})
def fetch(item):
    name,(url,paper,desc)=item
    path=ROOT/'data/raw'/name
    row=dict(path=str(path.relative_to(ROOT)),source=url,associated_paper=paper,description=desc)
    try:
        if not path.exists():
            content=urllib.request.urlopen(url,timeout=45).read()
            path.write_bytes(content)
        row.update(retrieval_date=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,status='ACQUIRED')
    except Exception as exc: row.update(status='UNAVAILABLE',error=str(exc))
    return row
SOURCES.update({'symmetries_resolved.html':(BASE+'discretesymmetries/discretesymmetries/CICY_symmetries.html','1708.08943; 1003.3235','Oxford resolved symmetry data index'), 'quotients.html':(BASE+'CicyQuotients/Cicy_Quotients/Cicy_Quotients.html','1606.04032; 1003.3235','Oxford quotient data index'), 'cicylist.m':(BASE+'cicylist/cicylist.m','1003.3235','Oxford topology with symmetry metadata'), 'importGUT.nb':(BASE+'linebundlemodels/importGUT.nb','1307.4787','Model database field definitions')})
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(fetch,SOURCES.items()))
    dest=ROOT/'data/manifests/sources.json'
    if dest.exists():
        old={r['path']:r for r in json.loads(dest.read_text())}
        for row in rows:
            prior=old.get(row['path'])
            if prior and prior.get('sha256') and prior['sha256']!=row.get('sha256'): raise RuntimeError('Raw data changed: '+row['path'])
    dest.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
