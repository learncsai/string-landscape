"""Reproduce published downstairs heterotic standard models.

For each record of the published database this script

  1. recomputes every *upstairs* quantity with our own exact code (c1(V), c2(V),
     both indices, the subset criterion, the anomaly and Bogomolov conditions and
     the complete slope obstruction) and compares with the published values;
  2. checks the Gamma-character tables against the published cohomology
     dimensions (the multiplicities must sum to h^q);
  3. runs the equivariant/Wilson-line descent implemented in
     physics/wilson_line.py and compares the resulting downstairs spectrum with
     the published DownSpec, multiplet by multiplet.

The Gamma-representation content of the upstairs cohomology is *input* from the
published database, not computed here: computing it needs the explicit invariant
defining equations of the free-action subfamily, which remains the repository's
principal scientific blocker. Everything downstream of that input is recomputed.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from string_sm_sat.bundles.bundle_sum import BundleSum
from string_sm_sat.geometry.cicy import CICY
from string_sm_sat.physics.anomaly import check_anomaly, check_bogomolov
from string_sm_sat.physics.equivariance import CharacterGroup, infer_group
from string_sm_sat.physics.index import bundle_c2, bundle_index
from string_sm_sat.physics.spectrum import check_indices
from string_sm_sat.physics.stability import check_span_slope
from string_sm_sat.physics.structure_group import check_c1, check_structure_group
from string_sm_sat.physics.wilson_line import (WilsonLine, acceptance_report,
                                               downstairs_spectrum)
from string_sm_sat.search.checkpoints import atomic_json, code_hash

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data/processed/published_standard_models.json"


def geometry_for(record, catalog):
    configuration = tuple(tuple(row) for row in record["configuration"])
    ambient = tuple(sum(row) - 1 for row in configuration)
    return CICY(str(record["number"]), ambient, configuration, record["h11"],
                record["h21"], (), "POSITIVE_ORTHANT")


def parse_down_spec(text):
    """Published DownSpec -> multiset of (kind, indices, multiplicity).

    Singlet multiplicities are sometimes left as unevaluated rank expressions in
    the published data; those entries are reported separately as UNDETERMINED
    rather than guessed.
    """
    items, undetermined = Counter(), 0
    if not text:
        return items, undetermined
    body = text.strip()
    body = body[1:-1] if body.startswith('{') else body
    depth, current, parts = 0, '', []
    for ch in body:
        if ch in '[{(':
            depth += 1
        elif ch in ']})':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(current); current = ''
        else:
            current += ch
    parts.append(current)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if 'rk' in part or 'SuperscriptBox' in part:
            undetermined += 1
            continue
        count = 1
        head = re.match(r'(\d+)\s*\*', part)
        if head:
            count = int(head.group(1)); part = part[head.end():].strip()
        match = re.match(r'Subscript\[\s*(OverBar\[\s*"(?:5|H)"\s*\]|"10"|"5"|"H"|"S")\s*,'
                         r'\s*([\d,\s]+)\]$', part)
        if not match:
            undetermined += 1
            continue
        kind = match.group(1).replace(' ', '')
        indices = tuple(int(x) for x in match.group(2).split(','))
        items[(kind, indices)] += count
    return items, undetermined


def rebuild_spec(spectrum):
    """Our spectrum in the published notation, for comparison."""
    items = Counter()
    for entry in spectrum['tens']:
        items[('"10"', (entry['bundle'],))] += entry['multiplicity']
    for entry in spectrum['fivebars']:
        kind = 'OverBar["5"]' if entry['type'] == '5bar' else '"5"'
        items[(kind, tuple(entry['pair']))] += entry['multiplicity']
    for entry in spectrum['higgs']:
        kind = '"H"' if entry['type'] == 'H' else 'OverBar["H"]'
        items[(kind, tuple(entry['pair']))] += entry['multiplicity']
    return items


def infer_groups(models):
    """Character group per |Gamma|, from every label used anywhere in the database.

    A single record may not exhibit all characters, so the cyclic factors are
    inferred from the union of the labels at that order and cross-checked
    against the group order and the width of the GCoh tables.
    """
    groups = {}
    for order in sorted({m['gamma_order'] for m in models}):
        labels = [tuple(x) for m in models if m['gamma_order'] == order
                  for key in ('EquivStr', 'WLine') for x in m.get(key, [])]
        if not labels:
            continue
        width = len(labels[0])
        moduli = tuple(max(x[i] for x in labels) + 1 for i in range(width))
        group = CharacterGroup(moduli)
        if group.order != order:
            raise ValueError(f'labels at order {order} give {moduli}, order {group.order}')
        widths = {len(tab[0]) for m in models if m['gamma_order'] == order
                  for tab in m.get('GCoh', [])}
        if widths and widths != {order}:
            raise ValueError(f'GCoh width {widths} disagrees with |Gamma| = {order}')
        groups[order] = group
    return groups


def verify(record, catalog_geometries, shift_by_equivariant_structure, groups):
    number = record['cicy']
    geometry_record = next(r for r in catalog_geometries if r['number'] == number)
    g = geometry_for(geometry_record, catalog_geometries)
    rows = record['LineSum']
    columns = tuple(tuple(r[a] for r in rows) for a in range(len(rows[0])))
    v = BundleSum.from_columns(columns)
    gamma = record['gamma_order']

    upstairs = {
        'c1_zero': check_c1(v).outcome,
        'no_proper_zero_subset': check_structure_group(v).outcome,
        'chiral_indices': check_indices(v, g, gamma).outcome,
        'anomaly_nef_pairings': check_anomaly(v, g).outcome,
        'bogomolov_pairing': check_bogomolov(v, g).outcome,
        'span_slope_obstruction': check_span_slope(g, list(columns)).outcome,
        'c2_matches_published': list(bundle_c2(g, v)) == record['C2'],
        'index_V': bundle_index(g, v),
        'index_wedge2': bundle_index(g, v.wedge2()),
    }

    result = {'cicy': number, 'gamma_order': gamma,
              'model_number': record.get('ModelNumber'),
              'columns': [list(k) for k in columns], 'upstairs': upstairs}

    required = ('GCoh', 'GCoh2', 'Coh', 'Coh2', 'WLine', 'EquivStr')
    if any(record.get(name) is None for name in required):
        result['descent'] = 'UNKNOWN_INCOMPLETE_RECORD'
        result['missing_fields'] = [n for n in required if record.get(n) is None]
        return result

    group = groups[gamma]
    wilson = WilsonLine(group, tuple(record['WLine'][0]), tuple(record['WLine'][1]))
    equivariant = ([tuple(x) for x in record['EquivStr']]
                   if shift_by_equivariant_structure else None)

    # the character multiplicities must reproduce the published dimensions
    consistent = all(sum(row) == dim
                     for table, dims in ((record['GCoh'], record['Coh']),
                                         (record['GCoh2'], record['Coh2']))
                     for tab, dd in zip(table, dims)
                     for row, dim in zip(tab, dd))
    result['character_tables_consistent'] = consistent

    spectrum = downstairs_spectrum(
        group, wilson,
        [tab[1] for tab in record['GCoh']],
        [tab[1] for tab in record['GCoh2']],
        [tab[2] for tab in record['GCoh2']],
        equivariant,
        [row for tab in (record.get('GCohSing') or []) for row in tab[1:2]])
    published, undetermined = parse_down_spec(record.get('DownSpec', ''))
    ours = rebuild_spec(spectrum)
    charged_published = Counter({k: v for k, v in published.items() if k[0] != '"S"'})
    result.update({
        'spectrum': spectrum,
        'acceptance': acceptance_report(spectrum, gamma, record.get('MasslessU1', 'UNKNOWN')),
        'published_charged_spectrum': {f'{k[0]}{list(k[1])}': v
                                       for k, v in sorted(charged_published.items())},
        'our_charged_spectrum': {f'{k[0]}{list(k[1])}': v for k, v in sorted(ours.items())},
        'charged_spectrum_matches': ours == charged_published,
        'undetermined_published_entries': undetermined,
        'published_higgs_pairs': record.get('HPairs'),
        'higgs_pairs_match': spectrum['higgs_pairs'] == record.get('HPairs'),
    })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--cicy', type=int, help='restrict to one geometry')
    parser.add_argument('--limit', type=int, help='at most this many records')
    parser.add_argument('--no-equivariant-shift', action='store_true',
                        help='treat GCoh as already including the equivariant structure')
    parser.add_argument('--output')
    parser.add_argument('--table', action='store_true',
                        help='print the Section-31 spectrum table for each record')
    args = parser.parse_args(argv)

    database = json.loads(DATABASE.read_text())
    models = database['models']
    if args.cicy:
        models = [m for m in models if m['cicy'] == args.cicy]
    if args.limit:
        models = models[:args.limit]

    groups = infer_groups(database['models'])
    results = [verify(m, database['geometries'], not args.no_equivariant_shift, groups)
               for m in models]
    complete = [r for r in results if r.get('descent') != 'UNKNOWN_INCOMPLETE_RECORD']
    summary = {
        'schema': 1, 'kind': 'downstairs_reproduction',
        'database': database['source'], 'database_sha256': database['source_sha256'],
        'records': len(results), 'complete_records': len(complete),
        'incomplete_records': len(results) - len(complete),
        'upstairs_all_checks_pass': sum(
            1 for r in results
            if all(r['upstairs'][k] == 'PASS' for k in
                   ('c1_zero', 'no_proper_zero_subset', 'chiral_indices',
                    'anomaly_nef_pairings', 'bogomolov_pairing', 'span_slope_obstruction'))
            and r['upstairs']['c2_matches_published']),
        'character_tables_consistent': sum(1 for r in complete
                                           if r.get('character_tables_consistent')),
        'charged_spectrum_matches': sum(1 for r in complete
                                        if r.get('charged_spectrum_matches')),
        'higgs_pairs_match': sum(1 for r in complete if r.get('higgs_pairs_match')),
        'three_family_no_exotic_higgs': sum(
            1 for r in complete
            if r['acceptance']['three_chiral_families']
            and not r['acceptance']['charged_chiral_exotics']
            and r['acceptance']['higgs_doublet_pair']),
        'equivariant_structure_applied': not args.no_equivariant_shift,
        'character_groups': {str(k): list(v.moduli) for k, v in groups.items()},
        'software_source_sha256': code_hash(),
        'scope': ('the Gamma-character content of the upstairs cohomology is input from the '
                  'published database; the descent, the projection and every upstairs '
                  'quantity are recomputed here'),
    }
    if args.output:
        atomic_json(args.output, {**summary, 'results': results})
    if args.table:
        for r in results:
            if r.get('descent') != 'UNKNOWN_INCOMPLETE_RECORD':
                print(spectrum_table(r)); print('-' * 66)
    print(json.dumps(summary, indent=2))
    return summary




def spectrum_table(result):
    """Section-31 human-readable particle spectrum table."""
    a = result['acceptance']; s = result['spectrum']
    lines = [f"Downstairs spectrum  CICY {result['cicy']}  |Gamma| = {result['gamma_order']}"
             f"  model {result['model_number']}",
             f"upstairs charges (columns): {result['columns']}",
             '',
             f"{'multiplet':<14}{'SU(3)':>6}{'SU(2)':>6}{'6Y':>5}{'count':>7}"]
    from string_sm_sat.physics.wilson_line import TEN_PIECES, FIVEBAR_PIECES
    for name, c, w, y, _ in TEN_PIECES + FIVEBAR_PIECES:
        lines.append(f"{name:<14}{c:>6}{w:>6}{y:>5}{a['family_multiplicities'][name]:>7}")
    lines += [f"{'H (doublet)':<14}{1:>6}{2:>6}{3:>5}{s['higgs_up']:>7}",
              f"{'Hbar':<14}{1:>6}{2:>6}{-3:>5}{s['higgs_down']:>7}",
              f"{'singlets':<14}{'':>6}{'':>6}{'':>5}{str(a['singlets']):>7}",
              '',
              f"3 chiral families?        {'yes' if a['three_chiral_families'] else 'NO'}",
              f"charged chiral exotics?   {'YES' if a['charged_chiral_exotics'] else 'no'}",
              f"Higgs doublet pair?       {'yes' if a['higgs_doublet_pair'] else 'NO'}"
              f"  ({a['higgs_pairs']} pair(s))",
              f"colour triplet Higgs?     {'YES' if a['colour_triplet_higgs'] else 'no'}",
              f"additional massless U(1)? {a['additional_massless_U1']}",
              f"singlets                  {a['singlets']}",
              '',
              'scope: ' + a['claim']]
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
