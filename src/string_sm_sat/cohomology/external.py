"""External backends must provide their own exactness evidence. None configured."""
from .interface import Cohomology,CohomologyStatus
def cohomology(geometry,line):
    return Cohomology(None,CohomologyStatus.UNKNOWN,'external backend not configured','none')
