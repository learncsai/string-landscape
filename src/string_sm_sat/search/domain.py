from dataclasses import dataclass,asdict
from ..geometry.cicy import CICY
from ..physics.constraints import Target
@dataclass(frozen=True)
class Domain:
    geometry: CICY
    K: int
    gamma: int
    target: str = 'GUT_FULL'
    pair_nonpositive: bool = True
    slope_coefficients: int = 1
    allowed_columns: tuple[tuple[int,...],...] | None = None
    def __post_init__(self):
        if type(self.K) is not int or self.K<0: raise ValueError('K must be a nonnegative integer')
        if type(self.gamma) is not int or self.gamma<1: raise ValueError('Gamma order must be a positive integer')
        if self.target not in ('GUT_CHIRAL','GUT_FULL'): raise ValueError('downstairs and non-SUSY targets are not implemented')
        if type(self.slope_coefficients) is not int or not 0<=self.slope_coefficients<=2: raise ValueError('search coefficient bound must be 0..2')
        if self.allowed_columns is not None:
            if not isinstance(self.allowed_columns,tuple) or len(set(self.allowed_columns))!=len(self.allowed_columns): raise ValueError("allowed columns must be a unique tuple")
            if any(not isinstance(k,tuple) or len(k)!=self.geometry.h11 or any(type(x) is not int or abs(x)>self.K for x in k) for k in self.allowed_columns): raise ValueError("invalid allowed columns")
    def as_dict(self):
        return {**asdict(self),'canonicalization':'summand permutations only; repeated columns retained','kahler_domain':'positive ambient chamber','hidden_bundle':'trivial','structure_requirement':'1307.4787 (2.2); exact holonomy not certified','raw_four_column_states':(len(self.allowed_columns)**4 if self.allowed_columns is not None else (2*self.K+1)**(4*self.geometry.h11)),'raw_five_column_states':(len(self.allowed_columns)**5 if self.allowed_columns is not None else (2*self.K+1)**(5*self.geometry.h11)),'gamma_scope':'order sets chiral target; no equivariance asserted'}
