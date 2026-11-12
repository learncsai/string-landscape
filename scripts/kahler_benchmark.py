"""Benchmark of the published Kahler-potential operator tables.

The standard-model database also lists Kahler-potential operators, whose
singlet monomials may contain conjugates S^dagger_{ab} (charge -(e_a - e_b)):

  GMTerm          H_u H_d x monomial with at least one conjugate singlet
                  (the Giudice-Masiero term, arXiv:1202.1757 Section 3.1.10)
  NeutrinoKahler  L^p H_d^dagger x monomial            (Section 3.1.9)
  Kin5            5bar^p 5bar^q^dagger x monomial, the 5bar kinetic matrix

(In the paper's notation H-bar is the up-type Higgs, which is how these map to
our 5_H / 5bar_H.) The published lists stop at total singlet degree three. One
convention is not stated -- whether monomials containing both S_{ab} and its
own conjugate, i.e. a trivially neutral |S_{ab}|^2 factor, are listed -- so both
readings are compared and reported, not assumed.
"""
import argparse
import json
import re
import sys
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from operator_benchmark import families_of  # noqa: E402
from string_sm_sat.physics.selection_rules import (add, five, fivebar,  # noqa: E402
                                                   residual_charge, singlet)
from yukawa_selection_benchmark import FIELD, parse_braces  # noqa: E402

DATABASE = ROOT / 'data/processed/published_standard_models.json'
DEGREE = 3


def tokenise(text):
    atoms = {}

    def substitute(match):
        head = match.group(1).replace(' ', '')
        kind = 'Sbar' if 'SuperDagger' in head else ('S' if head == '"S"' else head)
        name = f'A{len(atoms)}'
        atoms[name] = (kind, (int(match.group(2)), int(match.group(3))))
        return name

    return FIELD.sub(substitute, text), atoms


def term(text, atoms):
    text = text.strip()
    if text in ('0', ''):
        return None
    if text == '1':
        return frozenset()
    out = Counter()
    for factor in text.split('*'):
        factor = factor.strip()
        if not factor:
            continue
        power = 1
        if '^' in factor:
            factor, exponent = factor.rsplit('^', 1)
            power = int(exponent)
            factor = factor.strip()
        atom = atoms.get(factor)
        if atom is None or atom[0] not in ('S', 'Sbar'):
            return None
        out[atom] += power
    return frozenset(out.items())


def published(value):
    if not isinstance(value, str):
        flat = json.dumps(value) if value is not None else ''
        return 'ALL_ZERO' if value is not None and set(flat) <= set('[]0, \n') else None
    text, atoms = tokenise(value)
    tree = parse_braces(text)
    while len(tree) == 1 and isinstance(tree[0], list):
        tree = tree[0]

    def convert(node):
        if node and all(isinstance(item, list) for item in node):
            return [convert(item) for item in node]
        return frozenset(t for t in (term(x, atoms) for x in node) if t is not None)

    return convert(tree)


def generators(singlets):
    out = []
    for pair in singlets:
        out.append((('S', pair), singlet(*pair)))
        out.append((('Sbar', pair), tuple(-x for x in singlet(*pair))))
    return out


def monomials(residual, singlets, need_conjugate=False, allow_square=True,
              need_holomorphic=False):
    """All monomials in S and S-bar of degree <= DEGREE with the given charge."""
    gens = generators(singlets)
    found = set()
    for degree in range(DEGREE + 1):
        for combo in combinations_with_replacement(range(len(gens)), degree):
            charge = add(*[gens[i][1] for i in combo]) if combo else (0,) * 5
            if charge != residual:
                continue
            counts = Counter(gens[i][0] for i in combo)
            if need_conjugate and not any(kind == 'Sbar' for kind, _ in counts):
                continue
            if need_holomorphic and not any(kind == 'S' for kind, _ in counts):
                continue
            if not allow_square and any(('S', p) in counts and ('Sbar', p) in counts
                                        for _, p in counts):
                continue
            found.add(frozenset(counts.items()))
    return frozenset(found)


def cells(tensor, prefix=()):
    if isinstance(tensor, list):
        for i, item in enumerate(tensor):
            yield from cells(item, prefix + (i,))
    else:
        yield prefix, tensor


def compare(model, allow_square):
    fam = families_of(model)
    if fam is None:
        return {}
    singlets = fam['singlets']
    up, down = fam['physical_up'], fam['physical_down']
    out = {}

    # GMTerm: H_u H_d with at least one conjugate singlet
    table = published(model.get('GMTerm'))
    if table is not None and up and down:
        residual = residual_charge(add(five(*up), fivebar(*down)))
        ours = (monomials(residual, singlets, need_conjugate=True, allow_square=allow_square)
                if residual is not None else frozenset())
        mine = frozenset() if table == 'ALL_ZERO' else table
        if isinstance(mine, list):
            mine = frozenset().union(*[c for _, c in cells(mine)])
        out['GMTerm'] = (1, int(ours == mine))

    # NeutrinoKahler: L^p H_d^dagger
    table = published(model.get('NeutrinoKahler'))
    if table is not None and down:
        grid = (dict(cells(table)) if table != 'ALL_ZERO'
                else {(i,): frozenset() for i in range(len(fam['fivebars']))})
        total = agree = 0
        for index, cell in grid.items():
            charge = add(fivebar(*fam['fivebars'][index[0]]),
                         tuple(-x for x in fivebar(*down)))
            residual = residual_charge(charge)
            # published convention: at least one holomorphic singlet, which the
            # paper uses as the right-handed neutrino (Section 3.1.9)
            ours = (monomials(residual, singlets, allow_square=allow_square,
                              need_holomorphic=True)
                    if residual is not None else frozenset())
            total += 1
            agree += ours == cell
        out['NeutrinoKahler'] = (total, agree)

    # Kin5: 5bar^p 5bar^q^dagger
    table = published(model.get('Kin5'))
    if table is not None:
        grid = (dict(cells(table)) if table != 'ALL_ZERO'
                else {(i, j): frozenset() for i in range(3) for j in range(3)})
        total = agree = 0
        for index, cell in grid.items():
            if len(index) != 2:
                return out
            # published indexing: K_{pq} 5bar^{p dagger} 5bar^q
            p, q = fam['fivebars'][index[0]], fam['fivebars'][index[1]]
            residual = residual_charge(add(tuple(-x for x in fivebar(*p)), fivebar(*q)))
            ours = (monomials(residual, singlets, allow_square=allow_square)
                    if residual is not None else frozenset())
            total += 1
            agree += ours == cell
        out['Kin5'] = (total, agree)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=None)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    data = json.loads(DATABASE.read_text())
    models = [m for m in data['models'] if args.cicy is None or m['cicy'] == args.cicy]
    report = {}
    for allow_square in (True, False):
        tally = Counter()
        for model in models:
            for kind, (total, agree) in compare(model, allow_square).items():
                tally[f'{kind}/tables'] += 1
                tally[f'{kind}/cells'] += total
                tally[f'{kind}/agree'] += agree
                tally[f'{kind}/exact'] += total == agree
        label = 'with |S|^2 factors' if allow_square else 'without |S|^2 factors'
        print(f'--- reading: monomials {label}')
        for kind in ('GMTerm', 'NeutrinoKahler', 'Kin5'):
            print(f'{kind:15s} tables {tally[kind + "/tables"]:5d}  exact {tally[kind + "/exact"]:5d}'
                  f'  cells {tally[kind + "/cells"]:6d}  agree {tally[kind + "/agree"]:6d}')
        report[label] = dict(tally)
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
