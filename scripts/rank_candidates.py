"""Step 5: a logical physics ranking of the downstairs models on X7862 / (Z2 x Z2).

No score, no weights, no learned model. Each category is a logical condition on
exact or explicitly necessary facts, evaluated for every accepted configuration
and every choice of physical Higgs pair, then aggregated per upstairs orbit. The
same rules are applied to the 11 additional candidates and to the 10 published
orbits, so the published models are the baseline, not an assumption.

Per configuration and Higgs choice:

  top_leading      Y_u has nonzero rank at the Abelian locus (exact triple product)
  Yu_cap, Yd_cap   largest rank the U(1)^4 selection rule allows at ANY singlet
                   order (exact: structural rank of the allowed pattern)
  Yu_cap_Dflat     the same, using only singlets that can take a vacuum value in
                   a D-flat direction at vanishing FI terms, i.e. singlets on a
                   directed cycle of the singlet charge graph (exact)
  QQQL_forbidden   dimension-five proton decay forbidden to all orders (exact)
  RPV4_forbidden   dimension-four R-parity violation forbidden to all orders (exact)
  RPV4_leading     dimension-four RPV computed NONZERO at singlet order zero
  RPV2_order1      bilinear RPV S L H_u computed NONZERO at singlet order one

Categories (per choice):

  STRONG_CANDIDATE   top_leading and Yu_cap = Yd_cap = 3 and QQQL_forbidden and
                     RPV4_forbidden and bilinear RPV forbidden to all orders
  PHENOMENOLOGICALLY_PROBLEMATIC
                     an unconditional exact obstruction: Yu_cap = 0 (no up-type
                     mass at any perturbative order, so a massless top quark), or
                     Yd_cap = 0 (no down-type quark or charged-lepton mass at any
                     perturbative order), or RPV4_leading (dimension-four RPV
                     present at the Abelian locus)
  UNKNOWN            anything else

Per orbit: STRONG if some choice is STRONG; PROBLEMATIC if every choice is;
otherwise UNKNOWN.

Scope: holomorphic superpotential, perturbative in the singlets, generic member
of the invariant family, all 5bar states counted (vector-like ones included,
which makes "forbidden" statements stronger and "allowed" statements weaker).
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

from leading_order_yukawa import structural_rank  # noqa: E402
from string_sm_sat.physics.superpotential import (DownstairsSpectrum,  # noqa: E402
                                                  operator_table, yukawa_down, yukawa_up)

SOURCE = ROOT / 'benchmarks/x7862/yukawa-all-configurations.json'


def cycle_edges(singlets):
    """Singlet edges lying on a directed cycle: those that can take a D-flat value.

    At vanishing FI terms the D-terms read sum_S Q_a(S) |s|^2 = 0 with |s|^2 >= 0,
    i.e. a non-negative circulation on the directed graph a -> b for each S_{ab}.
    An edge carries positive flow in some circulation iff it lies on a directed
    cycle, i.e. both endpoints are in one strongly connected component.
    """
    nodes = range(1, 6)
    reach = {a: {a} for a in nodes}
    changed = True
    while changed:
        changed = False
        for a, b in singlets:
            for x in nodes:
                if a in reach[x] and b not in reach[x]:
                    reach[x].add(b)
                    changed = True
    return tuple(sorted((a, b) for a, b in singlets if a in reach[b]))


def cap(table):
    if table is None:
        return None
    return structural_rank([[int(c['status'] != 'FORBIDDEN_BY_SELECTION_RULE') for c in row]
                            for row in table])


def facts(configuration, block):
    tens = tuple(configuration['ten_families'])
    fives = tuple(tuple(f) for f in configuration['fivebar_families'])
    singlets = tuple(tuple(s) for s in configuration['singlets'])
    up = tuple(block['higgs_up']) if block['higgs_up'] else None
    down = tuple(block['higgs_down']) if block['higgs_down'] else None
    flat = cycle_edges(singlets)
    flat_spectrum = DownstairsSpectrum(tens, fives, up, down, flat)
    # recomputed from the charges with the current operator table (cheap and
    # exact), so every recorded run is ranked by the same rules
    ops = operator_table(DownstairsSpectrum(tens, fives, up, down, singlets))
    cubic = block['cubic_operators']
    bilinear = ops.get('L H_u (bilinear RPV)', {}).get('verdict')
    return {
        'top_leading': (block['Y_u'].get('rank') or 0) >= 1,
        'Yu_leading_rank': block['Y_u'].get('rank'),
        'Yd_leading_rank': block['Y_d'].get('rank'),
        'Yu_cap': cap(block['selection']['Y_u']),
        'Yd_cap': cap(block['selection']['Y_d']),
        'Yu_cap_Dflat': cap(yukawa_up(flat_spectrum)),
        'Yd_cap_Dflat': cap(yukawa_down(flat_spectrum)),
        'QQQL_forbidden': ops['QQQL / u^c u^c d^c e^c']['verdict'] == 'FORBIDDEN_BY_SELECTION_RULE',
        'RPV4_forbidden': ops['LLe^c / LQd^c / u^c d^c d^c']['verdict'] == 'FORBIDDEN_BY_SELECTION_RULE',
        'RPV4_leading': cubic['dim4_RPV_order0']['verdict'] == 'NONZERO',
        'RPV2_forbidden': bilinear == 'FORBIDDEN_BY_SELECTION_RULE',
        'RPV2_order1': cubic['bilinear_RPV_order1']['verdict'],
        'mu_forbidden': ops.get('H_u H_d', {}).get('verdict') == 'FORBIDDEN_BY_SELECTION_RULE',
        'weinberg_forbidden': ops.get('Weinberg L L H_u H_u', {}).get('verdict')
        == 'FORBIDDEN_BY_SELECTION_RULE',
        'singlets': len(singlets), 'singlets_Dflat': len(flat),
    }


def category(f):
    if (f['top_leading'] and f['Yu_cap'] == 3 and f['Yd_cap'] == 3 and f['QQQL_forbidden']
            and f['RPV4_forbidden'] and f['RPV2_forbidden']):
        return 'STRONG_CANDIDATE'
    if f['Yu_cap'] == 0 or f['Yd_cap'] == 0 or f['RPV4_leading']:
        return 'PHENOMENOLOGICALLY_PROBLEMATIC'
    return 'UNKNOWN'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=str(SOURCE))
    parser.add_argument('--out', default=str(ROOT / 'benchmarks/x7862/physics-ranking.json'))
    args = parser.parse_args()
    data = json.loads(Path(args.source).read_text())

    rows = []
    for candidate in data['candidates']:
        per_choice = []
        for configuration in candidate['configurations']:
            for block in configuration['higgs_choices']:
                f = facts(configuration, block)
                f['category'] = category(f)
                per_choice.append(f)
        categories = Counter(f['category'] for f in per_choice)
        if categories.get('STRONG_CANDIDATE'):
            verdict = 'STRONG_CANDIDATE'
        elif categories.get('PHENOMENOLOGICALLY_PROBLEMATIC') == len(per_choice):
            verdict = 'PHENOMENOLOGICALLY_PROBLEMATIC'
        else:
            verdict = 'UNKNOWN'

        def share(key):
            return sum(bool(f[key]) for f in per_choice)

        reasons = Counter()
        for f in per_choice:
            if f['Yu_cap'] == 0:
                reasons['no up-type Yukawa at any order'] += 1
            if f['Yd_cap'] == 0:
                reasons['no down-type Yukawa at any order'] += 1
            if f['RPV4_leading']:
                reasons['dimension-four RPV at the Abelian locus'] += 1
        rows.append({
            'id': candidate['candidate_id'], 'class': candidate.get('class'),
            'choices': len(per_choice), 'verdict': verdict, 'categories': dict(categories),
            'reasons': dict(reasons),
            'top_leading': share('top_leading'),
            'Yu_cap': sorted({f['Yu_cap'] for f in per_choice}),
            'Yd_cap': sorted({f['Yd_cap'] for f in per_choice}),
            'Yu_cap_Dflat': sorted({f['Yu_cap_Dflat'] for f in per_choice}),
            'Yd_cap_Dflat': sorted({f['Yd_cap_Dflat'] for f in per_choice}),
            'Yu_leading_rank': sorted({f['Yu_leading_rank'] for f in per_choice
                                       if f['Yu_leading_rank'] is not None}),
            'Yd_leading_rank': sorted({f['Yd_leading_rank'] for f in per_choice
                                       if f['Yd_leading_rank'] is not None}),
            'QQQL_forbidden': share('QQQL_forbidden'),
            'RPV4_forbidden': share('RPV4_forbidden'),
            'RPV4_leading': share('RPV4_leading'),
            'RPV2_forbidden': share('RPV2_forbidden'),
            'RPV2_order1': dict(Counter(f['RPV2_order1'] for f in per_choice)),
            'mu_forbidden': share('mu_forbidden'),
            'weinberg_forbidden': share('weinberg_forbidden'),
        })

    header = (f"{'orbit':14s} {'class':10s} {'choices':>7s}  {'verdict':30s} "
              f"{'top@LO':>6s} {'Yu cap':>7s} {'Yd cap':>7s} {'QQQL=0':>7s} {'RPV4=0':>7s} "
              f"{'RPV4 LO':>7s} {'RPV2=0':>7s}")
    print(header)
    for r in rows:
        print(f"{r['id']:14s} {r['class'] or '':10s} {r['choices']:7d}  {r['verdict']:30s} "
              f"{r['top_leading']:6d} {str(r['Yu_cap']):>7s} {str(r['Yd_cap']):>7s} "
              f"{r['QQQL_forbidden']:7d} {r['RPV4_forbidden']:7d} {r['RPV4_leading']:7d} "
              f"{r['RPV2_forbidden']:7d}")
    tally = Counter((r['class'], r['verdict']) for r in rows)
    print('\nverdicts:', dict(tally))
    Path(args.out).write_text(json.dumps({'definitions': __doc__, 'orbits': rows,
                                          'verdicts': {f'{a}:{b}': v for (a, b), v in
                                                       tally.items()}}, indent=1))


if __name__ == '__main__':
    main()
