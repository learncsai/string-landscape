"""Cell-by-cell benchmark of every published superpotential operator table.

Extends the Yukawa benchmark to the remaining holomorphic operators the
standard-model database records, and to the D- and Fayet-Iliopoulos terms:

  Dim4Proton      dimension-four R-parity violation, 10 5bar 5bar
  Dim5Proton      dimension-five proton decay, 10 10 10 5bar
  RParVio         bilinear R-parity violation, 5bar 5_H
  HiggsMass       the full Higgs mass matrix over every 5_H and 5bar_H
  SuperPotential  the pure-singlet superpotential
  DTerms          the five U(1) D-terms, sum_S Q_a(S) |S|^2
  FITerms         the five Fayet-Iliopoulos terms, i.e. the slopes mu_{k_a}(t)

Everything on our side is computed from the charges (and, for the FI terms, from
our own intersection numbers); the published tables are only the comparison
target. Index orderings that the sources do not state are *fitted* on the
tetraquadric, reported, and then held fixed for the whole database.
"""
import argparse
import json
import re
import sys
from collections import Counter
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from published_table_consistency import decode_edownspec  # noqa: E402
from string_sm_sat.physics.selection_rules import (add, enumerate_monomials,  # noqa: E402
                                                   five, fivebar, residual_charge,
                                                   singlet, ten)
from yukawa_selection_benchmark import (FIELD, parse_braces, term_monomial,  # noqa: E402
                                        tokenise)

DATABASE = ROOT / 'data/processed/published_standard_models.json'


def truncation(fields):
    """Largest singlet order in the published lists: total degree <= 8, capped at 5."""
    return min(5, 8 - fields)


def higgs_lists(model):
    """(5_H pairs, 5bar_H pairs) in DownSpec order, repeated by multiplicity."""
    ups, downs = [], []
    text = model['DownSpec']
    for match in FIELD.finditer(text):
        head = match.group(1).replace(' ', '')
        if head not in ('"H"', 'OverBar["H"]'):
            continue
        pair = (int(match.group(2)), int(match.group(3)))
        prefix = text[max(0, match.start() - 12):match.start()]
        count = re.search(r'(\d+)\s*\*\s*$', prefix)
        (ups if head == '"H"' else downs).extend([pair] * (int(count.group(1)) if count else 1))
    return ups, downs


def published_tensor(value):
    """Nested lists of monomial sets; 'ALL_ZERO' for a purely numeric zero table."""
    if value is None:
        return None
    if not isinstance(value, str):
        flat = json.dumps(value)
        return 'ALL_ZERO' if set(flat) <= set('[]0, \n') else None
    text, atoms = tokenise(value)
    if not re.fullmatch(r'[\s{},0-9A*^+\-]*', text):
        return None                                  # contains conjugates or sums
    tree = parse_braces(text)
    while len(tree) == 1 and isinstance(tree[0], list):
        tree = tree[0]

    def convert(node):
        if node and all(isinstance(item, list) for item in node):
            return [convert(item) for item in node]
        return frozenset(frozenset(m.items()) for m in
                         (term_monomial(t, atoms) for t in node) if m is not None)

    return convert(tree)


def shape(tensor):
    out = []
    while isinstance(tensor, list):
        out.append(len(tensor))
        tensor = tensor[0] if tensor else None
    return tuple(out)


def cells(tensor, prefix=()):
    if isinstance(tensor, list):
        for i, item in enumerate(tensor):
            yield from cells(item, prefix + (i,))
    else:
        yield prefix, tensor


OPERATORS = {
    # name: (index families, charge builder)
    'Dim4Proton': (('tens', 'fivebars', 'fivebars'),
                   lambda a, b, c: [ten(a), fivebar(*b), fivebar(*c)]),
    'Dim5Proton': (('tens', 'tens', 'tens', 'fivebars'),
                   lambda a, b, c, d: [ten(a), ten(b), ten(c), fivebar(*d)]),
    'RParVio': (('fivebars',), None),
    'HiggsMass': (('higgs_up', 'higgs_down'),
                  lambda u, d: [five(*u), fivebar(*d)]),
}


def ours_cell(kind, labels, model_families, singlets, order, index_permutation):
    names, builder = OPERATORS[kind]
    if kind == 'RParVio':
        up = model_families['physical_up']
        charges = [fivebar(*labels[0]), five(*up)]
    else:
        if any(label is None for label in labels):
            return frozenset()                     # an empty padding slot
        # the published index order may differ from the operator's field order
        fields = [None] * len(names)
        for slot, position in enumerate(index_permutation):
            fields[position] = labels[slot]
        charges = builder(*fields)
    residual = residual_charge(add(*charges))
    if residual is None:
        return frozenset()
    return frozenset(enumerate_monomials(residual, singlets, order))


def compare_tensor(kind, model, published, index_permutation, families, singlets):
    names, _ = OPERATORS[kind]
    order = truncation(len(names) if kind != 'RParVio' else 2)
    if kind == 'RParVio':
        axes = [families['fivebars']]
    else:
        axes = [families[names[p]] for p in index_permutation]
    if published == 'ALL_ZERO':
        expected = tuple(len(a) for a in axes)
    else:
        expected = shape(published)
        if expected != tuple(len(a) for a in axes):
            return None
    total = agree = 0
    iterator = (cells(published) if published != 'ALL_ZERO'
                else ((idx, frozenset()) for idx in _grid(expected)))
    for index, cell in iterator:
        labels = [axes[i][j] for i, j in enumerate(index)]
        mine = ours_cell(kind, labels, families, singlets, order, index_permutation)
        total += 1
        agree += mine == cell
    return total, agree


def _grid(dimensions):
    if not dimensions:
        yield ()
        return
    for i in range(dimensions[0]):
        for rest in _grid(dimensions[1:]):
            yield (i,) + rest


SYMMETRIC_SLOTS = {'Dim5Proton': (1, 2, 3), 'Dim4Proton': (1, 2)}


def compare_classes(kind, published, index_permutation, families, singlets):
    """Convention-adjusted comparison, one verdict per permutation class.

    Published conventions, each established from the data and stated here:
      * Dim5Proton, Dim4Proton: the charge is invariant under permuting the
        identical-type slots, and the published tensors list an inconsistent
        subset of the permutations (for the same index shape, sometimes one of
        three orderings, sometimes two). The physical content is the class, so
        a class agrees when every nonempty published cell equals our list and
        the class is nonempty exactly when ours is.
      * Dim4Proton: an entry involving a matter 5bar from the same pair bundle
        as the physical down Higgs is not listed (it is charge-identical to a
        Yukawa coupling with H_d). Holds with no exception: 19,450 allowed cells
        without such a 5bar are all listed; all 164 with one are not.
      * RParVio: the bare bilinear (singlet order zero) is not listed; a bare
        quadratic superpotential term is absent by construction for massless
        fields (arXiv:1202.1757 Section 3.1.8).
    Returns (classes, agreeing classes).
    """
    names, _ = OPERATORS[kind]
    if kind == 'RParVio':
        axes = [families['fivebars']]
        order = truncation(2)
    else:
        axes = [families[names[p]] for p in index_permutation]
        order = truncation(len(names))
    dimensions = tuple(len(a) for a in axes)
    grid = (dict(cells(published)) if published != 'ALL_ZERO'
            else {index: frozenset() for index in _grid(dimensions)})
    symmetric = SYMMETRIC_SLOTS.get(kind, ())
    classes = {}
    for index in grid:
        key = (tuple(index[i] for i in range(len(index)) if i not in symmetric)
               + (tuple(sorted(index[i] for i in symmetric)),))
        classes.setdefault(key, []).append(index)
    down = families['physical_down']
    total = agree = 0
    for members in classes.values():
        labels = [axes[i][j] for i, j in enumerate(members[0])]
        mine = ours_cell(kind, labels, families, singlets, order, index_permutation)
        if kind == 'RParVio':
            mine = mine - {frozenset()}
        if kind == 'Dim4Proton' and down in labels[1:]:
            mine = frozenset()
        listed = [grid[i] for i in members if grid[i]]
        total += 1
        agree += all(c == mine for c in listed) and bool(listed) == bool(mine)
    return total, agree


def superpotential_benchmark(model, singlets):
    published = published_tensor(model.get('SuperPotential'))
    if published is None:
        return None
    if published == 'ALL_ZERO':
        published = frozenset()
    elif isinstance(published, list):
        published = frozenset().union(*[c for _, c in cells(published)])
    ours = frozenset(m for m in enumerate_monomials((0,) * 5, singlets, 5)
                     if sum(p for _, p in m) >= 3)
    return ours == published


def dterm_benchmark(model, singlets):
    text = model.get('DTerms')
    if not isinstance(text, str):
        return None
    tokenised, atoms = tokenise(text)
    body = tokenised.strip()[1:-1]
    parts = [p for p in _split_top(body)]
    if len(parts) != 5:
        return None
    for a, part in enumerate(parts, start=1):
        published = Counter()
        for sign, token in re.findall(r'([+-]?)\s*\(?\s*(A\d+)\s*\*', part):
            head, pair = atoms[token]
            published[pair] += -1 if sign == '-' else 1
        expected = Counter()
        for pair in singlets:
            charge = singlet(*pair)[a - 1]
            if charge:
                expected[pair] = charge
        if +published != +expected or -published != -expected:
            return False
    return True


def _split_top(text):
    depth, current, out = 0, '', []
    for character in text:
        if character in '([{':
            depth += 1
        elif character in ')]}':
            depth -= 1
        if character == ',' and depth == 0:
            out.append(current)
            current = ''
        else:
            current += character
    if current.strip():
        out.append(current)
    return out


def fi_benchmark(model, geometry, columns):
    """Published FI terms against our slopes mu_{k_a}(t) = d_{ijl} k^i t^j t^l."""
    text = model.get('FITerms')
    if not isinstance(text, str):
        return None
    parts = _split_top(text.strip()[1:-1])
    if len(parts) != len(columns):
        return None
    h = geometry.h11
    d = geometry.d
    for k, part in zip(columns, parts):
        ours = Counter()
        for j in range(h):
            for l in range(h):
                coefficient = sum(d[i][j][l] * k[i] for i in range(h))
                key = tuple(sorted((j, l)))
                ours[key] += coefficient
        published = Counter()
        clean = part.replace(' ', '')
        for sign, number, monomial in re.findall(
                r'([+-]?)(\d*)\*?((?:Subscript\["t",\d+\](?:\^\d+)?\*?)+)', clean):
            value = int(number) if number else 1
            value = -value if sign == '-' else value
            indices = []
            for index, power in re.findall(r'Subscript\["t",(\d+)\](?:\^(\d+))?', monomial):
                indices.extend([int(index) - 1] * (int(power) if power else 1))
            published[tuple(sorted(indices))] += value
        ours = Counter({key: value for key, value in ours.items() if value})
        published = Counter({key: value for key, value in published.items() if value})
        if ours != published:
            return False
    return True


def higgs_slots(model):
    """The Higgs slots of EDownSpec[[2]]: alternating 5_H, 5bar_H pair indices, -1 empty.

    The published HiggsMass matrix is indexed by these slots (rows 5_H, columns
    5bar_H), padded to three with empty slots whose rows and columns vanish.
    """
    from published_table_consistency import PAIRS
    encoded = model.get('EDownSpec')
    if not encoded or len(encoded) < 2:
        return None, None
    slots = encoded[1]
    ups = [PAIRS[x] if x >= 0 else None for x in slots[0::2]]
    downs = [PAIRS[x] if x >= 0 else None for x in slots[1::2]]
    return ups, downs


def families_of(model):
    decoded = decode_edownspec(model)
    if decoded is None:
        return None
    ups, downs = higgs_slots(model)
    if ups is None:
        ups, downs = higgs_lists(model)
    return {'tens': list(decoded['tens']), 'fivebars': list(decoded['fivebars']),
            'higgs_up': ups, 'higgs_down': downs,
            'physical_up': decoded['higgs_up'], 'physical_down': decoded['higgs_down'],
            'singlets': decoded['singlets']}


def fit_permutations(models):
    """Pick, for each operator, the index ordering that best matches X7862."""
    chosen = {}
    for kind, (names, _) in OPERATORS.items():
        if kind == 'RParVio':
            chosen[kind] = (0,)
            continue
        scores = Counter()
        candidates = sorted(set(permutations(range(len(names)))))
        for permutation in candidates:
            for model in models:
                families = families_of(model)
                published = published_tensor(model.get(kind))
                if families is None or published is None:
                    continue
                outcome = compare_tensor(kind, model, published, permutation, families,
                                         families['singlets'])
                if outcome:
                    scores[permutation] += outcome[1]
        chosen[kind] = max(candidates, key=lambda p: scores[p])
        print(f'fitted index order for {kind}: {chosen[kind]} '
              f'(cells agreeing per ordering: {dict(scores)})')
    return chosen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=None)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    data = json.loads(DATABASE.read_text())
    models = data['models']
    if args.cicy:
        models = [m for m in models if m['cicy'] == args.cicy]

    permutations_used = fit_permutations([m for m in data['models'] if m['cicy'] == 7862])

    from compute_equivariant_cohomology import geometry_for
    geometries = {r['number']: geometry_for(r) for r in data['geometries']}

    tally = Counter()
    failures = []
    for model in models:
        families = families_of(model)
        if families is None:
            tally['no_edownspec'] += 1
            continue
        singlets = families['singlets']
        for kind in OPERATORS:
            published = published_tensor(model.get(kind))
            if published is None:
                tally[f'{kind}/skipped'] += 1
                continue
            outcome = compare_tensor(kind, model, published, permutations_used[kind],
                                     families, singlets)
            if outcome is None:
                tally[f'{kind}/shape_mismatch'] += 1
                failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                 'kind': kind, 'reason': 'shape'})
                continue
            total, agree = outcome
            classes, classes_agree = compare_classes(kind, published, permutations_used[kind],
                                                     families, singlets)
            tally[f'{kind}/classes'] += classes
            tally[f'{kind}/classes_agree'] += classes_agree
            tally[f'{kind}/tables_classes_exact'] += classes == classes_agree
            tally[f'{kind}/tables'] += 1
            tally[f'{kind}/cells'] += total
            tally[f'{kind}/cells_agree'] += agree
            if total == agree:
                tally[f'{kind}/exact'] += 1
            else:
                failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                 'kind': kind, 'cells': total, 'agree': agree})
        for kind, check in (('SuperPotential', lambda: superpotential_benchmark(model, singlets)),
                            ('DTerms', lambda: dterm_benchmark(model, singlets))):
            result = check()
            if result is None:
                tally[f'{kind}/skipped'] += 1
            else:
                tally[f'{kind}/tables'] += 1
                tally[f'{kind}/exact'] += bool(result)
                if not result:
                    failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                     'kind': kind})
        geometry = geometries.get(model['cicy'])
        if geometry is not None and model.get('LineSum'):
            columns = [tuple(c) for c in zip(*model['LineSum'])]
            result = fi_benchmark(model, geometry, columns)
            if result is None:
                tally['FITerms/skipped'] += 1
            else:
                tally['FITerms/tables'] += 1
                tally['FITerms/exact'] += bool(result)
                if not result:
                    failures.append({'cicy': model['cicy'], 'model': model['ModelNumber'],
                                     'kind': 'FITerms'})

    kinds = list(OPERATORS) + ['SuperPotential', 'DTerms', 'FITerms']
    for kind in kinds:
        line = (f'{kind:15s} tables {tally[kind + "/tables"]:5d}  exact '
                f'{tally[kind + "/exact"]:5d}')
        if tally[kind + '/cells']:
            line += f'  | cells {tally[kind + "/cells"]:7d}  agree {tally[kind + "/cells_agree"]:7d}'
        if tally[kind + '/classes']:
            line += (f'  || convention-adjusted: tables {tally[kind + "/tables_classes_exact"]:5d}'
                     f'  classes {tally[kind + "/classes"]:6d}  agree {tally[kind + "/classes_agree"]:6d}')
        line += (f'  | shape mismatch {tally[kind + "/shape_mismatch"]:4d}  '
                 f'skipped {tally[kind + "/skipped"]:4d}')
        print(line)
    if failures:
        print('\nfailures by (kind, geometry):',
              dict(Counter((f['kind'], f['cicy']) for f in failures)))
        for row in failures[:10]:
            print('  ', row)
    if args.out:
        Path(args.out).write_text(json.dumps(
            {'tally': dict(tally), 'index_orders': {k: list(v) for k, v in
                                                     permutations_used.items()},
             'failures': failures}, indent=1))


if __name__ == '__main__':
    main()
