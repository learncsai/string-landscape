import hashlib,json
from pathlib import Path
from string_sm_sat.geometry.cicy import benchmark
ROOT=Path(__file__).parents[2]
def test_raw_integrity():
    for row in json.loads((ROOT/'data/manifests/sources.json').read_text()):
        if row['status']=='ACQUIRED':
            assert row['sha256']==hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
            assert row['source'] and row['retrieval_date'] and row['associated_paper']
def test_oxford_topology():
    for row in json.loads((ROOT/'data/processed/geometries.json').read_text()):
        g=benchmark(row['identifier'])
        assert g.ambient==tuple(row['ambient'])
        assert g.configuration==tuple(map(tuple,row['configuration']))
        assert g.c2==tuple(row['c2'])
        assert (g.h11,g.h21)==(row['h11'],row['h21'])
