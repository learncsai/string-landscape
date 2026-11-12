"""Extract the explicit freely acting symmetries from the published database.

Each CICY record in sms202.m carries a `Symmetries` field: a list of entries, one
per symmetry, of the shape

    { freely_acting_flag,
      { { generator matrices acting on the ambient homogeneous coordinates } },
      { group order, GAP id },
      { action of each generator on the defining polynomials },
      { basis of invariant polynomials, one list per ... } }

Matrix entries may contain `rt[n]`, a primitive n-th root of unity. Everything is
kept symbolic here; interpretation happens in physics/equivariance.py.

This module only reads. It never edits the raw data.
"""
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/sms202.m.gz"
OUT = ROOT / "data/processed/published_symmetries.json"


def tokenize(text):
    for match in re.finditer(r"\{|\}|,|[^{},]+", text):
        token = match.group(0)
        if token.strip() or token in "{},":
            yield token


def parse_expression(tokens, first=None):
    """Nested Mathematica list -> nested Python list; atoms stay as trimmed text."""
    token = first if first is not None else next(tokens)
    if token != "{":
        return token.strip()
    items = []
    pending = None
    for token in tokens:
        if token == "}":
            if pending is not None:
                items.append(pending)
            return items
        if token == ",":
            if pending is not None:
                items.append(pending)
            pending = None
            continue
        pending = parse_expression(tokens, token)
    raise ValueError("unbalanced braces")


def balanced(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("unbalanced")


def numeric_matrix(rows):
    """Convert a parsed matrix to numbers/symbols, or None if it is not a matrix."""
    out = []
    for row in rows:
        if not isinstance(row, list):
            return None
        line = []
        for entry in row:
            if not isinstance(entry, str):
                return None
            entry = entry.replace(" ", "")
            if re.fullmatch(r"-?\d+", entry):
                line.append(int(entry))
            elif re.fullmatch(r"-?rt\[\d+\]", entry):
                line.append(entry)
            else:
                return None
        out.append(line)
    return out


def parse_symmetry_entry(entry):
    """One symmetry entry has the shape

        [ flag,
          [ [generator matrices], [group order, GAP id] ],
          [ acts_freely, [orders of the cyclic factors] ],
          [ action of each generator on the defining polynomials ],
          [ invariant polynomials ] ]
    """
    result = {"flag": None, "generators": [], "group_order": None, "gap_id": None,
              "acts_freely": None, "cyclic_factors": None,
              "polynomial_action": None, "invariants": None}
    if entry and isinstance(entry[0], str):
        result["flag"] = entry[0].strip()
    if len(entry) > 1 and isinstance(entry[1], list) and len(entry[1]) == 2:
        matrices = entry[1][0]
        if isinstance(matrices, list):
            parsed = [numeric_matrix(m) for m in matrices]
            if parsed and all(m is not None for m in parsed):
                result["generators"] = parsed
        label = entry[1][1]
        if isinstance(label, list) and len(label) == 2:
            result["group_order"] = int(label[0])
            result["gap_id"] = int(label[1])
    if len(entry) > 2 and isinstance(entry[2], list) and len(entry[2]) == 2:
        result["acts_freely"] = str(entry[2][0]).strip()
        factors = entry[2][1]
        if isinstance(factors, list):
            result["cyclic_factors"] = [int(x) for x in factors]
    if len(entry) > 3 and isinstance(entry[3], list):
        parsed = [numeric_matrix(m) for m in entry[3] if isinstance(m, list)]
        if parsed and all(m is not None for m in parsed):
            result["polynomial_action"] = parsed
    if len(entry) > 4 and isinstance(entry[4], list):
        result["invariants"] = [[str(x) for x in group] if isinstance(group, list) else str(group)
                                for group in entry[4]]
    return result


def symmetries_for(text, number):
    block = text[text.index("\ncicys="):text.index("\nlinebundles=")]
    start = block.index(f"Num -> {number}")
    nxt = block.find("Num ->", start + 5)
    record = block[start:nxt if nxt != -1 else len(block)]
    key = record.index("Symmetries")
    raw = balanced(record, record.index("{", key))
    parsed = parse_expression(tokenize(raw))
    return [parse_symmetry_entry(e) for e in parsed], raw


def main():
    text = gzip.decompress(RAW.read_bytes()).decode("utf-8", "replace")
    catalog = json.loads((ROOT / "data/processed/published_standard_models.json").read_text())
    wanted = sorted({m["cicy"] for m in catalog["models"]})
    out = {}
    for number in wanted:
        entries, _ = symmetries_for(text, number)
        out[str(number)] = entries
    OUT.write_text(json.dumps({"schema": 1, "source": "data/raw/sms202.m.gz",
                               "symmetries": out}, indent=1) + "\n")
    print(json.dumps({n: {"entries": len(v),
                          "orders": sorted({e["group_order"] for e in v if e["group_order"]}),
                          "free": sum(1 for e in v if e["acts_freely"] == "True"),
                          "coords": sorted({len(e["generators"][0])
                                            for e in v if e["generators"]})}
                      for n, v in out.items()}, indent=2))


if __name__ == "__main__":
    main()
