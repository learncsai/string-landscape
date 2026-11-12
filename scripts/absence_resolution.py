"""Why each additional candidate is absent from the published standard-model scan.

Resolves the step-1 absence audit using only conditions the source papers
*state* for the scan that produced the standard-model database:

  (R1) charge range -3 <= k_a^i <= 3 on h^{1,1} = 4       (arXiv:1202.1757 Sec. 5.3)
  (R2) h^1(X, L_a^* (x) L_b^*) < |Gamma| for all a < b      (arXiv:1106.4804)

(R2) was imposed "to increase the chance that the Higgs triplets can be
removed"; it is a scan restriction, not a physical requirement. Both rules are
checked against every published model, which must satisfy them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'benchmarks/x7862/candidate-manifest.json'
DATABASE = ROOT / 'data/processed/published_standard_models.json'
OUT = ROOT / 'benchmarks/x7862/absence-resolution.json'
CHARGE_LIMIT = 3


def main():
    manifest = json.loads(MANIFEST.read_text())
    gamma = manifest['gamma_order']
    rows = []
    for candidate in manifest['candidates']:
        pairs = [v for v in candidate['cohomology']['per_pair'].values() if v is not None]
        worst = max(v[2] for v in pairs)          # h^2(L_a L_b) = h^1(L_a^* L_b^*)
        reasons = []
        if candidate['max_abs_charge'] > CHARGE_LIMIT:
            reasons.append('R1_charge_range')
        if worst >= gamma:
            reasons.append('R2_vector_like_pairs')
        rows.append({'candidate_id': candidate['candidate_id'],
                     'max_abs_charge': candidate['max_abs_charge'],
                     'max_pair_h1_dual': worst,
                     'violates': reasons,
                     'colour_triplet_higgs': any(a.get('colour_triplet_pairs')
                                                 for a in candidate['downstairs']['accepted']),
                     'previous_classification': candidate['absence_classification']})
    published = json.loads(DATABASE.read_text())['models']
    checked = violating_r1 = violating_r2 = 0
    for model in published:
        c2 = model.get('Coh2')
        if not isinstance(c2, list) or not all(isinstance(r, list) for r in c2):
            continue
        checked += 1
        violating_r2 += max(r[2] for r in c2) >= model['gamma_order']
        rows_k = model.get('LineSum') or []
        if model['cicy'] == 7862 and rows_k and max(abs(x) for r in rows_k for x in r) > CHARGE_LIMIT:
            violating_r1 += 1
    summary = {'published_models_checked': checked,
               'published_violating_R2': violating_r2,
               'published_x7862_violating_R1': violating_r1,
               'candidates_explained': sum(bool(r['violates']) for r in rows),
               'candidates': rows,
               'sources': {'R1': 'arXiv:1202.1757 Section 5.3', 'R2': 'arXiv:1106.4804'}}
    OUT.write_text(json.dumps(summary, indent=1))
    for r in rows:
        print(f"{r['candidate_id']}  max|k|={r['max_abs_charge']}  max h1(La*Lb*)="
              f"{r['max_pair_h1_dual']}  violates {r['violates']}")
    print(f"published: {checked} checked, {violating_r2} violate R2, "
          f"{violating_r1} X7862 models violate R1; candidates explained "
          f"{summary['candidates_explained']}/{len(rows)}")


if __name__ == '__main__':
    main()
