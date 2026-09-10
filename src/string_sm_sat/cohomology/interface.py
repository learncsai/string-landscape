from dataclasses import dataclass
from enum import StrEnum
from ..physics.index import index
class CohomologyStatus(StrEnum):
    EXACT_ANALYTIC='EXACT_ANALYTIC'; EXACT_EXTERNAL='EXACT_EXTERNAL'; CERTIFIED_FINITE_BOX='CERTIFIED_FINITE_BOX'; UNKNOWN='UNKNOWN'
@dataclass(frozen=True)
class Cohomology:
    dimensions: tuple[int,int,int,int] | None
    status: CohomologyStatus
    method: str
    reference: str
    def validate(self,geometry,line):
        if self.dimensions is None:
            if self.status!=CohomologyStatus.UNKNOWN: raise ArithmeticError('missing certified dimensions')
            return self
        if self.status==CohomologyStatus.UNKNOWN: raise ArithmeticError('unknown result must not contain trusted dimensions')
        if len(self.dimensions)!=4 or any(type(x) is not int or x<0 for x in self.dimensions): raise ArithmeticError('invalid dimensions')
        if sum((-1)**q*x for q,x in enumerate(self.dimensions))!=index(geometry,line): raise ArithmeticError('cohomology/HRR mismatch')
        return self
    def as_tuple(self): return (*(self.dimensions or (None,)*4),self.status)
