"""Rebuild selected topology records from immutable Oxford data; preserve row order."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def convert():
    raw=ROOT/'data/raw/cicylist.txt'; records=[]
    for block in re.split(r'(?=Num\s+:)',raw.read_text()):
        m=re.search(r'^Num\s+: (\d+)',block)
        if not m or int(m[1]) not in (7447,7862): continue
        fields={k:v.strip() for k,v in re.findall(r'^(\w+)\s+: (.+)$',block,re.M)}
        rows=[tuple(map(int,re.findall(r'\d+',line))) for line in block.splitlines() if line.startswith('{')]
        records.append(dict(identifier=m[1],ambient=[sum(row)-1 for row in rows],configuration=rows,h11=int(fields['H11']),h21=int(fields['H21']),c2=list(map(int,re.findall(r'\d+',fields['C2']))),euler=int(fields['Eta']),source_sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
    dest=ROOT/'data/processed/geometries.json'; dest.write_text(json.dumps(records,indent=2)+'\n')
    return records
if __name__=='__main__': print(json.dumps(convert(),indent=2))
