from functools import lru_cache
from .analytic import analytic_cohomology
@lru_cache(maxsize=50000)
def cohomology(geometry,line):
    result=analytic_cohomology(geometry,line).validate(geometry,line)
    dual=analytic_cohomology(geometry,line.dual()).validate(geometry,line.dual())
    if result.dimensions is not None and dual.dimensions is not None and result.dimensions!=dual.dimensions[::-1]: raise ArithmeticError('Serre duality mismatch')
    return result

@lru_cache(maxsize=50000)
def generic_cohomology(geometry,line):
    if geometry.identifier=="7447":
        from .codimension_two import generic_cohomology as compute
    else:
        from .finite_rank import generic_cohomology as compute
    result=compute(geometry,line).validate(geometry,line)
    dual=compute(geometry,line.dual()).validate(geometry,line.dual())
    if result.dimensions is not None and dual.dimensions is not None and result.dimensions!=dual.dimensions[::-1]: raise ArithmeticError('generic Serre duality mismatch')
    return result
