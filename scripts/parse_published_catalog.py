"""Convert the Oxford published GUT catalog (GUTall.m) to JSON.

Source: data/raw/GUTall.m.gz, the model database accompanying arXiv:1307.4787
("All heterotic line bundle SU(5) GUT models on favourable Cicys", 63,325
models on 68 favourable CICYs).

The file is Mathematica source. Only two assignments are read: `Cicys` (per
geometry metadata) and `LineBundleSums` (models keyed by
{Cicy number, symmetry order}). Raw data is never edited in place; this script
writes data/processed/published_gut_models.json and records a conversion log.

A published line bundle sum is a matrix given row by row: row r is the list of
the five charges k_a^r along ambient factor r. Our internal representation is
the tuple of five columns k_a. The conversion is a transpose, recorded here so
that the convention is auditable.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/GUTall.m.gz"
OUT = ROOT / "data/processed/published_gut_models.json"
LOG = ROOT / "data/processed/published-catalog-log.json"


def read_source():
    data = gzip.decompress(RAW.read_bytes()).decode("utf-8", "replace")
    return data


def nested_lists(text, start):
    """Parse a Mathematica nested integer list starting at text[start] == '{'."""
    assert text[start] == "{"
    stack = [[]]
    i = start + 1
    number = ""
    while stack:
        c = text[i]
        if c == "{":
            stack.append([])
        elif c in "},":
            if number.strip():
                stack[-1].append(int(number.replace(" ", "").replace("\n", "")))
                number = ""
            if c == "}":
                done = stack.pop()
                if not stack:
                    return done, i + 1
                stack[-1].append(done)
        elif c in "-0123456789" or c.isspace():
            number += c
        else:
            raise ValueError(f"unexpected character {c!r} at {i}")
        i += 1
    raise ValueError("unterminated list")


def parse_cicys(text):
    start = text.index("Cicys =")
    block_start = text.index("{", start)
    depth = 0
    for i in range(block_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                block = text[block_start:i + 1]
                break
    records = []
    for entry in re.finditer(r"Num\s*->\s*(\d+)(.*?)(?=Num\s*->|\Z)", block, re.S):
        number = int(entry.group(1))
        body = entry.group(2)
        def field(name):
            m = re.search(name + r"\s*->\s*(-?\d+)", body)
            return int(m.group(1)) if m else None
        def listfield(name):
            m = re.search(name + r"\s*->\s*\{", body)
            if not m:
                return None
            return nested_lists(body, m.end() - 1)[0]
        records.append({
            "number": number,
            "h11": field("H11"),
            "h21": field("H21"),
            "euler": field("Eta"),
            "num_projective_factors": field("NumPs"),
            "c2": listfield("C2"),
            "configuration": listfield(r"Conf"),
            "redundant_with": listfield("Redun"),
            "symmetry_orders": listfield("SymmOrder"),
            "favourable": "Favour -> True" in body,
        })
    return records


def parse_models(text):
    start = text.index("LineBundleSums =")
    out = {}
    for m in re.finditer(r"\{(\d+),\s*(\d+)\}\s*->\s*\{", text[start:]):
        number, order = int(m.group(1)), int(m.group(2))
        offset = start + m.end() - 1
        block, _ = nested_lists(text, offset)
        # block is a list of matrices, each given as a list of rows
        models = []
        for matrix in block:
            rows = [tuple(r) for r in matrix]
            columns = tuple(tuple(row[a] for row in rows) for a in range(len(rows[0])))
            models.append(columns)
        out[f"{number},{order}"] = models
    return out


def main():
    text = read_source()
    cicys = parse_cicys(text)
    models = parse_models(text)
    total = sum(len(v) for v in models.values())
    payload = {
        "schema": 1,
        "source": "data/raw/GUTall.m.gz",
        "source_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "paper": "arXiv:1307.4787",
        "acceptance_stage": ("published database description: anomaly-free, poly-stable, "
                             "correct indices; SU(5) GUT stage before Wilson lines"),
        "row_convention": "published matrices are row = ambient factor; stored here as tuples of five columns",
        "geometry_count": len(cicys),
        "model_count": total,
        "geometries": cicys,
        "models": {k: [list(map(list, m)) for m in v] for k, v in models.items()},
    }
    OUT.write_text(json.dumps(payload, indent=1) + "\n")
    LOG.write_text(json.dumps({
        "input": "data/raw/GUTall.m.gz",
        "input_sha256": payload["source_sha256"],
        "output": str(OUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "geometries": len(cicys),
        "models": total,
        "keys": sorted(models),
    }, indent=1) + "\n")
    print(json.dumps({"geometries": len(cicys), "models": total,
                      "keys_with_7862": [k for k in models if k.startswith("7862,")],
                      "counts_7862": {k: len(v) for k, v in models.items() if k.startswith("7862,")},
                      "counts_7447": {k: len(v) for k, v in models.items() if k.startswith("7447,")}},
                     indent=2))


if __name__ == "__main__":
    main()
