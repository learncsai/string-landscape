"""Benchmark the U(1)^4 selection rule against the published operator tables.

The published standard-model database records, for every model, which
superpotential operators are allowed and with which singlet insertions.  This
script recomputes those tables from the charges alone -- our own spectrum
labels, our own monoid membership test -- and compares.

Usage:  python scripts/yukawa_selection_benchmark.py [--cicy N] [--limit N]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from string_sm_sat.physics.selection_rules import (add, classify, enumerate_monomials,  # noqa: E402
                                                   five, fivebar, residual_charge, ten)

DATABASE = ROOT / 'data/processed/published_standard_models.json'

FIELD = re.compile(r'Subscript\[\s*(OverBar\[\s*"(?:5|H)"\s*\]|SuperDagger\[\s*"S"\s*\]|"10"|"5"|"H"|"S")\s*,\s*(\d+)\s*(?:,\s*(\d+)\s*)?\]')
MULTIPLE = re.compile(r'(\d+)\s*\*\s*$')


def parse_spectrum(text):
    """Multiplicities of every downstairs field type in a DownSpec string."""
    out = Counter()
    for match in FIELD.finditer(text):
        head = match.group(1).replace(' ', '')
        indices = tuple(int(x) for x in match.groups()[1:] if x is not None)
        prefix = text[max(0, match.start() - 12):match.start()]
        count = MULTIPLE.search(prefix)
        out[(head, indices)] += int(count.group(1)) if count else 1
    return out


def singlets(spectrum):
    return sorted({indices for head, indices in spectrum if head == '"S"'})


def tens(spectrum):
    return sorted({indices[0] for head, indices in spectrum if head == '"10"'})


def fivebars(spectrum):
    return sorted({indices for head, indices in spectrum if head == 'OverBar["5"]'})


def physical_higgs(text):
    """(up-type 5 indices, down-type 5bar indices) of the designated Higgs pair."""
    if not isinstance(text, str):
        return None, None
    up = re.search(r'Subscript\[\s*"H"\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', text)
    down = re.search(r'Subscript\[\s*OverBar\[\s*"H"\s*\]\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', text)
    return (tuple(int(x) for x in up.groups()) if up else None,
            tuple(int(x) for x in down.groups()) if down else None)


def tokenise(text):
    """Replace every Subscript[...] atom by a flat token, leaving pure structure."""
    atoms = {}

    def substitute(match):
        head = match.group(1).replace(' ', '')
        indices = tuple(int(x) for x in match.groups()[1:] if x is not None)
        name = f'A{len(atoms)}'
        atoms[name] = (head, indices)
        return name

    return FIELD.sub(substitute, text), atoms


def parse_braces(text):
    """Nested lists from a brace expression whose leaves are token products."""
    stack, current, buffer = [], [], ''

    def flush():
        nonlocal buffer
        if buffer.strip():
            current.append(buffer.strip())
        buffer = ''

    for character in text:
        if character == '{':
            flush()
            stack.append(current)
            current = []
        elif character == '}':
            flush()
            finished = current
            current = stack.pop()
            current.append(finished)
        elif character == ',':
            flush()
        else:
            buffer += character
    flush()
    return current


def leaves(tree):
    """Every innermost list of the parsed structure."""
    if not isinstance(tree, list):
        return
    if not any(isinstance(item, list) for item in tree):
        yield tree
        return
    for item in tree:
        yield from leaves(item)


def term_monomial(term, atoms):
    """A term as a Counter over singlet index pairs, or None if it is not one."""
    term = term.strip()
    if term == '0':
        return None
    if term == '1':
        return Counter()
    factors = Counter()
    for factor in term.split('*'):
        factor = factor.strip()
        if not factor:
            continue
        power = 1
        if '^' in factor:
            factor, exponent = factor.rsplit('^', 1)
            power = int(exponent.strip())
            factor = factor.strip()
        atom = atoms.get(factor)
        if atom is None or atom[0] != '"S"':
            return None
        factors[atom[1]] += power
    return factors or None


def monomials(value):
    """The set of published singlet monomials of one table entry.

    Returns None when the entry is absent or unparsable, () when every entry is
    {0} (forbidden), and otherwise a set of frozensets over (index pair, power),
    with the empty frozenset standing for the leading-order term {1}.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        flat = json.dumps(value)
        if re.fullmatch(r'[\[\]0,\s]*', flat):
            return ()
        if re.fullmatch(r'[\[\]01,\s]*', flat):
            return {frozenset()}
        return None
    text, atoms = tokenise(value)
    tree = parse_braces(text)
    out = set()
    for block in leaves(tree):
        for term in block:
            monomial = term_monomial(term, atoms)
            if monomial is None:
                continue
            out.add(frozenset(monomial.items()))
    return out


def entry_charge(kind, model):
    """Charges of the three fields of an operator, given the model's Higgs choice."""
    spectrum = parse_spectrum(model['DownSpec'])
    up, down = physical_higgs(model.get('PhysHiggs'))
    if kind == 'YukawaUp':
        if up is None:
            return None
        return [[ten(a), ten(b), five(*up)] for a in tens(spectrum) for b in tens(spectrum)]
    if kind == 'YukawaDown':
        if down is None:
            return None
        return [[ten(a), fivebar(*f), fivebar(*down)]
                for a in tens(spectrum) for f in fivebars(spectrum)]
    if kind == 'MuTerm':
        if up is None or down is None:
            return None
        return [[five(*up), fivebar(*down)]]
    return None


PUBLISHED_TRUNCATION = 5   # the published lists contain no monomial of higher order


def compare(model, kind, max_order=PUBLISHED_TRUNCATION):
    published = monomials(model.get(kind))
    if published is None:
        return None
    operators = entry_charge(kind, model)
    if operators is None:
        return None
    available = singlets(parse_spectrum(model['DownSpec']))
    rows = [classify(charges, available) for charges in operators]
    predicted_allowed = any(s.allowed for s in rows)
    published_allowed = bool(published)

    ours = set()
    for charges in operators:
        residual = residual_charge(add(*charges))
        if residual is None:
            continue
        ours |= enumerate_monomials(residual, available, max_order)

    order = (lambda term: sum(c for _, c in term))
    minimal = min((order(t) for t in ours), default=None)
    published_min = min((order(t) for t in published), default=None)
    published_max = max((order(t) for t in published), default=None)
    return {
        'kind': kind,
        'published_allowed': published_allowed,
        'predicted_allowed': predicted_allowed,
        'agree': predicted_allowed == published_allowed,
        'our_minimal_order': minimal,
        'published_minimal_order': published_min,
        'published_max_order': published_max,
        'orders_agree': minimal == published_min,
        'sets_equal': ours == set(published),
        'published_subset': set(published) <= ours,
        'extra': len(ours - set(published)),
        'missing': len(set(published) - ours),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicy', type=int, default=None)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    data = json.loads(DATABASE.read_text())
    models = data['models']
    if args.cicy:
        models = [m for m in models if m['cicy'] == args.cicy]
    if args.limit:
        models = models[:args.limit]

    tally = Counter()
    disagreements = []
    orders = Counter()
    for model in models:
        for kind in ('YukawaUp', 'YukawaDown', 'MuTerm'):
            result = compare(model, kind)
            if result is None:
                tally[kind + '/skipped'] += 1
                continue
            tally[kind + '/compared'] += 1
            tally[kind + ('/agree' if result['agree'] else '/differ')] += 1
            if result['sets_equal']:
                tally[kind + '/sets_equal'] += 1
            elif result['published_subset']:
                tally[kind + '/superset_only'] += 1
            else:
                tally[kind + '/set_mismatch'] += 1
            if result['published_max_order'] is not None:
                orders[result['published_max_order']] += 1
            if not result['agree'] or not result['sets_equal']:
                disagreements.append({'cicy': model['cicy'],
                                      'model': model['ModelNumber'], **result})
    print('published monomial orders seen:',
          ' '.join(f'{k}:{v}' for k, v in sorted(orders.items())))
    for kind in ('YukawaUp', 'YukawaDown', 'MuTerm'):
        compared = tally[kind + '/compared']
        print(f'{kind:12s} compared {compared:5d}  allowed/forbidden agree '
              f'{tally[kind + "/agree"]:5d}  differ {tally[kind + "/differ"]:4d} | '
              f'monomial sets equal {tally[kind + "/sets_equal"]:5d}  '
              f'ours-a-superset {tally[kind + "/superset_only"]:4d}  '
              f'mismatch {tally[kind + "/set_mismatch"]:4d} | skipped {tally[kind + "/skipped"]:4d}')
    if disagreements:
        print('\nfirst disagreements:')
        for row in disagreements[:15]:
            print('  cicy {cicy} model {model:4d} {kind:11s} published_allowed={published_allowed}'
                  ' predicted={predicted_allowed} our_min={our_minimal_order}'
                  ' pub_min={published_minimal_order} extra={extra} missing={missing}'.format(**row))
        buckets = Counter((r['kind'], r['published_allowed'], r['extra'], r['missing'])
                          for r in disagreements)
        print('\n(kind, published_allowed, our minimal order) -> count')
        for key, count in sorted(buckets.items(), key=lambda x: -x[1])[:20]:
            print('  ', key, count)
    if args.out:
        Path(args.out).write_text(json.dumps(
            {'tally': dict(tally), 'orders': dict(orders),
             'disagreements': disagreements}, indent=1))


if __name__ == '__main__':
    main()
