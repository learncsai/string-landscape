from dataclasses import dataclass,asdict
from enum import StrEnum
class MathematicalStatus(StrEnum):
    EXACT='EXACT'; NECESSARY='NECESSARY'; SUFFICIENT='SUFFICIENT'; HEURISTIC='HEURISTIC'; NUMERIC_WITNESS='NUMERIC_WITNESS'; UNKNOWN='UNKNOWN'
class Target(StrEnum):
    GUT_CHIRAL='GUT_CHIRAL'; GUT_FULL='GUT_FULL'; DOWNSTAIRS_MSSM='DOWNSTAIRS_MSSM'; STRICT_NON_SUSY_SM='STRICT_NON_SUSY_SM'
@dataclass(frozen=True)
class Constraint:
    name: str
    mathematical_status: MathematicalStatus
    reference: str
    input_assumptions: tuple[str,...]
    can_safely_prune: bool
    can_certify_acceptance: bool
@dataclass(frozen=True)
class Check:
    metadata: Constraint
    outcome: str
    residual: object = None
    diagnostics: object = None
    def as_dict(self): return asdict(self)

def rule(name,status,reference,assumptions=(),prune=True,accept=False):
    return Constraint(name,MathematicalStatus(status),reference,tuple(assumptions),prune,accept)
C1=rule('c1_zero','EXACT','1307.4787 (4.2)',('rank five integral bundle',),accept=True)
STRUCTURE=rule('no_proper_zero_subset','EXACT','1307.4787 (2.2), Appendix A',('nonempty proper subsets; torsion-free Picard group; criterion only, not full holonomy classification',),accept=True)
ANOMALY=rule('anomaly_nef_pairings','NECESSARY','1311.1941 (2.3),(2.6); 1307.4787 (4.4)',('trivial hidden bundle; ambient hyperplanes nef',))
INDEX=rule('chiral_indices','EXACT','1307.4787 (4.7)',('chi=sum (-1)^q h^q; target -3*Gamma',),accept=True)
SINGLE=rule('single_index_range','NECESSARY','1307.4787 Section 5 step 1',('GUT_FULL; no anti-families; nontrivial common zero-slope summands',))
PAIR=rule('pair_index_range','NECESSARY','1307.4787 (4.10), Section 5 steps 3-6',('restricted historical domain: all pair indices nonpositive; wedge index fixed',))
PARTIAL=rule('partial_index_budget','NECESSARY','1307.4787 Section 5 steps 3-4',('nonpositive individual/pair indices; total fixed',))
COMPLETION=rule('component_completion_bound','NECESSARY','1307.4787 Section 5 step 4(i); triangle inequality',('every remaining component lies in [-K,K]',))
SLOPE=rule('signed_slope_matrices','NECESSARY','1307.4787 Section 5',('search restricted to positive ambient Kahler chamber; zero matrices allowed',))
EXACT_SLOPE=rule('rational_slope_witness','SUFFICIENT','1307.4787 (4.5)',('exact rational t>0 in ambient Kahler chamber',),False,True)
NUMERIC_SLOPE=rule('numerical_slope_witness','NUMERIC_WITNESS','1307.4787 (4.5)',('floating point root; no existence certificate',),False,False)
SPECTRUM=rule('full_spectrum','EXACT','1307.4787 (4.8)-(4.9); 2306.03147 C4',('all cohomologies computed by certified backend',),True,True)
RULES=(C1,STRUCTURE,ANOMALY,INDEX,SINGLE,PAIR,PARTIAL,COMPLETION,SLOPE,EXACT_SLOPE,NUMERIC_SLOPE,SPECTRUM)
SPECTRUM_GENERIC=rule('generic_full_spectrum','EXACT','1307.4787 (4.8)-(4.9); Koszul rank certificates',('Zariski-generic smooth family; not a specified invariant subfamily',),False,False)
