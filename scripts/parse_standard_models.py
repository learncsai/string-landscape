"""Convert the Oxford heterotic line-bundle STANDARD MODEL database to JSON.

Source: data/raw/sms202.m.gz, the downstairs database accompanying
arXiv:1106.4804 and arXiv:1202.1757. Unlike GUTall.m (the upstairs SU(5) GUT
catalog) this one carries the data Phase 9 needs:

  LineSum    upstairs line bundle sum, rows = ambient factors
  C2         c2(V)
  Coh        h^q(X, L_a) for each of the five line bundles
  Coh2       h^q(X, L_a (x) L_b) for the ten pairs
  CohSing    h^q(X, L_a (x) L_b^*) for the singlet bundles
  GCoh       the Gamma-REPRESENTATION content of Coh: for each bundle a
             a table [q][character] of multiplicities
  GCoh2      the same for the pairs, GCohSing for the singlets
  EquivStr   the chosen equivariant structure on each line bundle
  WLine      the Wilson line
  DownSpec   the published downstairs spectrum (symbolic)
  HPairs, Num5, MasslessU1, PhysHiggs, ...

Only the integer-valued fields are parsed into structure; symbolic fields
(DownSpec, FITerms, Yukawas, ...) are retained verbatim as strings so that
nothing is silently reinterpreted.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/sms202.m.gz"
OUT = ROOT / "data/processed/published_standard_models.json"
LOG = ROOT / "data/processed/published-sm-log.json"

INTEGER_FIELDS = ["LineSum", "C2", "Coh", "Coh2", "CohSing", "GCoh", "GCoh2",
                  "GCohSing", "WLine", "EquivStr", "EDownSpec", "HPairs", "Num5",
                  "MasslessU1", "ModelNumber",
                  # published superpotential data, for the Yukawa benchmark
                  "YukawaUp", "YukawaDown", "MuTerm", "SuperPotential", "RParVio"]
TEXT_FIELDS = ["DownSpec", "PhysHiggs", "IsSM", "GMTerm", "Dim4Proton", "NeutrinoKahler",
               # further published operator data, for the operator benchmark
               "Dim5Proton", "HiggsMass", "Kin5", "DTerms", "FITerms"]


def balanced(text, start):
    """Return (substring, end) for the braced expression starting at text[start]."""
    assert text[start] == "{"
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], i + 1
    raise ValueError("unbalanced")


def integer_list(text):
    """Parse a nested Mathematica list of integers; None if it is not numeric."""
    if not re.fullmatch(r"[\s{},\-0-9]*", text):
        return None
    stack = [[]]
    number = ""
    for c in text:
        if c == "{":
            stack.append([])
        elif c in "},":
            if number.strip():
                stack[-1].append(int(number.strip()))
                number = ""
            if c == "}":
                done = stack.pop()
                stack[-1].append(done)
        elif c in "-0123456789" or c.isspace():
            number += c
    return stack[0][0] if stack[0] else None


def field_value(record, name):
    match = re.search(re.escape(name) + r"\s*->\s*", record)
    if not match:
        return None
    rest = record[match.end():]
    if rest.startswith("{"):
        raw, _ = balanced(record, match.end())
        return raw
    token = re.match(r"[^,]*", rest).group(0).strip()
    return token


def parse_models(text):
    start = text.index("\nlinemodels=")
    body = text[start:]
    models = []
    for match in re.finditer(r"Num\s*->\s*\{\s*(\d+)\s*,\s*(\d+)\s*,", body):
        key_start = body.rindex("{", 0, match.end())
        head, end = balanced(body, key_start)
        # the record runs until the next "Num -> {" or the end
        nxt = body.find("Num ->", end)
        record = body[match.start():nxt if nxt != -1 else len(body)]
        key = integer_list(head)
        entry = {"cicy": int(match.group(1)), "gamma_order": int(match.group(2)),
                 "symmetry_key": key,
                 "symmetry_number": (key[2] if isinstance(key, list) and len(key) > 2
                                     and isinstance(key[2], int) else None)}
        for name in INTEGER_FIELDS:
            raw = field_value(record, name)
            if raw is None:
                continue
            if raw.startswith("{"):
                value = integer_list(raw)
                if value is None:                      # symbolic: keep it verbatim
                    value = re.sub(r"\s+", " ", raw)
            else:
                value = int(raw) if re.fullmatch(r"-?\d+", raw) else raw
            entry[name] = value
        for name in TEXT_FIELDS:
            raw = field_value(record, name)
            if raw is not None:
                entry[name] = re.sub(r"\s+", " ", raw)
        models.append(entry)
    return models


def parse_cicys(text):
    start = text.index("\ncicys=")
    block, _ = balanced(text, text.index("{", start))
    records = []
    for entry in re.finditer(r"Num\s*->\s*(\d+)(.*?)(?=Num\s*->|\Z)", block, re.S):
        body = entry.group(2)

        def field(name):
            m = re.search(name + r"\s*->\s*(-?\d+)", body)
            return int(m.group(1)) if m else None

        def listfield(name):
            m = re.search(name + r"\s*->\s*\{", body)
            if not m:
                return None
            raw, _ = balanced(body, m.end() - 1)
            return integer_list(raw)
        records.append({
            "number": int(entry.group(1)), "h11": field("H11"), "h21": field("H21"),
            "euler": field("Eta"), "c2": listfield("C2"),
            "configuration": listfield(r"Conf"),
            "has_symmetry_data": "Symmetries ->" in body,
        })
    return records


def main():
    text = gzip.decompress(RAW.read_bytes()).decode("utf-8", "replace")
    models = parse_models(text)
    cicys = parse_cicys(text)
    payload = {
        "schema": 1,
        "source": "data/raw/sms202.m.gz",
        "source_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "paper": "arXiv:1106.4804; arXiv:1202.1757",
        "acceptance_stage": ("downstairs heterotic line bundle standard models: equivariant "
                             "bundle on the quotient, Wilson line, MSSM spectrum"),
        "row_convention": "LineSum rows are ambient factors; our columns are its transpose",
        "model_count": len(models),
        "geometry_count": len(cicys),
        "geometries": cicys,
        "models": models,
    }
    OUT.write_text(json.dumps(payload, indent=1) + "\n")
    LOG.write_text(json.dumps({
        "input": "data/raw/sms202.m.gz", "input_sha256": payload["source_sha256"],
        "output": str(OUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "models": len(models), "geometries": len(cicys),
    }, indent=1) + "\n")
    from collections import Counter
    keys = Counter((m["cicy"], m["gamma_order"]) for m in models)
    print(json.dumps({"models": len(models), "geometries": len(cicys),
                      "by_(cicy,gamma)": {f"{a},{b}": n for (a, b), n in sorted(keys.items())}},
                     indent=2))


if __name__ == "__main__":
    main()
