"""Superpotential operator tables for a downstairs line-bundle standard model.

Given the downstairs spectrum -- which line bundle each family comes from,
which pair bundle carries the physical Higgs, and which singlets are present --
this assembles the charge-level content of the perturbative superpotential:

* the up-type and down-type Yukawa matrices, entry by entry, each entry being
  the exhaustive list of singlet monomials that make the operator neutral;
* the mu term;
* the dimension-four and dimension-five operators that are dangerous for proton
  decay and for R-parity, and the Weinberg operator.

Every statement here is the U(1)^4 selection rule of `selection_rules.py`, so
every entry is **necessary only**: `FORBIDDEN_BY_SELECTION_RULE` proves the
coupling vanishes, while anything else means the charges permit it and the
actual value needs the Gamma-character rule and then the cohomological triple
product of `yukawa.py`.

Conventions, fixed by comparison with the published tables and recorded here
because they are not deducible from the physics alone:

* families are listed in order of increasing line-bundle index, repeated by
  multiplicity: a model with one 10 from L_1 and two from L_2 has family order
  (10_1, 10_2, 10_2);
* the up-type Yukawa matrix is indexed (10-family, 10-family) and is symmetric;
* the down-type Yukawa matrix is indexed (10-family, 5bar-family);
* S_{ab} carries charge e_a - e_b;
* the published tables truncate the monomial lists at total degree five.
"""
from dataclasses import dataclass, field
from itertools import combinations

from .selection_rules import (RANK, add, classify, enumerate_monomials, five,
                              fivebar, residual_charge, singlet, ten)

PUBLISHED_TRUNCATION = 5


@dataclass(frozen=True)
class DownstairsSpectrum:
    """What the superpotential needs to know about a downstairs model."""
    ten_families: tuple          # one line-bundle index per 10 family
    fivebar_families: tuple      # one unordered bundle pair per 5bar family
    higgs_up: tuple | None       # pair (a, b) of the physical 5
    higgs_down: tuple | None     # pair (a, b) of the physical 5bar
    singlets: tuple = ()         # ordered pairs (a, b) present as S_{ab}
    label: str = ''

    @property
    def generations(self):
        return len(self.ten_families)


def monomial_set(charges, singlets, max_order=PUBLISHED_TRUNCATION):
    """Every singlet monomial up to `max_order` making the operator neutral."""
    residual = residual_charge(add(*charges))
    if residual is None:
        return set()
    return enumerate_monomials(residual, singlets, max_order)


def entry(charges, singlets, max_order=PUBLISHED_TRUNCATION):
    """One table entry: the exact classification plus the truncated monomial list."""
    selection = classify(charges, singlets)
    return {'status': selection.status,
            'minimal_insertions': selection.insertions,
            'monomials': sorted(sorted(term) for term in
                                monomial_set(charges, singlets, max_order))}


def yukawa_up(spectrum, max_order=PUBLISHED_TRUNCATION):
    """Y_u: the (10, 10, 5_H) matrix over the 10 families."""
    if spectrum.higgs_up is None:
        return None
    higgs = five(*spectrum.higgs_up)
    return [[entry([ten(a), ten(b), higgs], spectrum.singlets, max_order)
             for b in spectrum.ten_families] for a in spectrum.ten_families]


def yukawa_down(spectrum, max_order=PUBLISHED_TRUNCATION):
    """Y_d (and Y_e): the (10, 5bar, 5bar_H) matrix."""
    if spectrum.higgs_down is None:
        return None
    higgs = fivebar(*spectrum.higgs_down)
    return [[entry([ten(a), fivebar(*f), higgs], spectrum.singlets, max_order)
             for f in spectrum.fivebar_families] for a in spectrum.ten_families]


def mu_term(spectrum, max_order=PUBLISHED_TRUNCATION):
    """The Higgs mass term H_u H_d."""
    if spectrum.higgs_up is None or spectrum.higgs_down is None:
        return None
    return entry([five(*spectrum.higgs_up), fivebar(*spectrum.higgs_down)],
                 spectrum.singlets, max_order)


# ---------------------------------------------------------------------------
# dangerous and desirable operators
#
# Upstairs these are SU(5) operators; the charge of a low-energy field is the
# charge of the SU(5) multiplet it descends from, since the Wilson line is flat
# and carries no U(1)^4 charge.  So Q, u^c and e^c all carry the charge of their
# 10, and d^c and L both carry the charge of their 5bar.
# ---------------------------------------------------------------------------

def _ten_charges(spectrum):
    return [ten(a) for a in spectrum.ten_families]


def _fivebar_charges(spectrum):
    return [fivebar(*f) for f in spectrum.fivebar_families]


def operator_table(spectrum, max_order=PUBLISHED_TRUNCATION):
    """Dangerous and desirable operators, classified by the U(1)^4 rule."""
    tens = _ten_charges(spectrum)
    fives = _fivebar_charges(spectrum)
    hu = None if spectrum.higgs_up is None else five(*spectrum.higgs_up)
    hd = None if spectrum.higgs_down is None else fivebar(*spectrum.higgs_down)
    out = {}

    def record(name, families, comment):
        rows = []
        for charges in families:
            rows.append(entry(list(charges), spectrum.singlets, max_order))
        allowed = [r for r in rows if r['status'] != 'FORBIDDEN_BY_SELECTION_RULE']
        out[name] = {
            'comment': comment,
            'operators': len(rows),
            'allowed': len(allowed),
            'verdict': ('FORBIDDEN_BY_SELECTION_RULE' if not allowed else
                        'ALLOWED_BY_SELECTION_RULE'),
            'minimal_insertions': min((r['minimal_insertions'] for r in allowed),
                                      default=None),
            'entries': rows,
        }

    # dimension five, Delta B = Delta L = 1 : Q Q Q L and u^c u^c d^c e^c.
    # Both descend from 10 10 10 5bar, so they share one charge condition.
    record('QQQL / u^c u^c d^c e^c',
           [(x, y, z, f) for x, y, z in _triples(tens) for f in fives],
           'dimension-five proton decay, from the SU(5) operator 10 10 10 5bar')

    # dimension four R-parity violation: 10 5bar 5bar with matter 5bars
    record('LLe^c / LQd^c / u^c d^c d^c',
           [(t, f, g) for t in tens for f, g in _pairs(fives)],
           'dimension-four R-parity violation, from 10 5bar 5bar with two matter 5bars')

    if hu is not None and hd is not None:
        record('H_u H_d', [(hu, hd)], 'the mu term')
    if hu is not None:
        record('Weinberg L L H_u H_u', [(f, g, hu, hu) for f, g in _pairs(fives)],
               'dimension-five neutrino mass operator, from 5bar 5bar 5_H 5_H')
        record('L H_u (bilinear RPV)', [(f, hu) for f in fives],
               'bilinear R-parity violation, 5bar 5_H; a bare (order-zero) term is absent '
               'by construction for massless fields, so only singlet insertions count')
        bilinear = out['L H_u (bilinear RPV)']
        # a bare quadratic term cannot appear between massless fields: an allowed
        # entry needs at least one singlet insertion
        orders = [e for e in bilinear['entries']
                  if e['status'] != 'FORBIDDEN_BY_SELECTION_RULE'
                  and any(len(m) for m in e['monomials'])]
        allowed_beyond_bare = [e for e in bilinear['entries']
                               if e['status'] == 'ALLOWED_WITH_SINGLET_INSERTIONS'
                               or (e['status'] == 'ALLOWED_AT_LEADING_ORDER' and orders)]
        if not allowed_beyond_bare:
            bilinear['verdict'] = 'FORBIDDEN_BY_SELECTION_RULE'
            bilinear['allowed'] = 0
    return out


def _pairs(items):
    return [(items[i], items[j]) for i, j in combinations(range(len(items)), 2)] + \
           [(x, x) for x in items]


def _triples(items):
    out = []
    n = len(items)
    for i in range(n):
        for j in range(i, n):
            for k in range(j, n):
                out.append((items[i], items[j], items[k]))
    return out
