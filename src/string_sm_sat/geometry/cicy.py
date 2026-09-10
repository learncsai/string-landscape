from dataclasses import dataclass
from functools import cached_property
from .intersections import triple_intersections
from .chern import tangent_c2_pairings

@dataclass(frozen=True)
class CICY:
    identifier: str
    ambient: tuple[int,...]
    configuration: tuple[tuple[int,...],...]
    h11: int
    h21: int
    symmetry_orders: tuple[int,...] = ()
    cone: str = 'AMBIENT_SUBCONE'
    basis: str = 'ordered restrictions of ambient integral hyperplane classes'
    def __post_init__(self):
        if not isinstance(self.ambient,tuple) or not isinstance(self.configuration,tuple): raise TypeError('immutable tuples required')
        if not self.ambient or len(self.ambient)!=len(self.configuration): raise ValueError('ambient/configuration mismatch')
        if any(type(n) is not int or n<1 for n in self.ambient): raise ValueError('positive integral projective dimensions required')
        c=len(self.configuration[0])
        if c<1 or any(not isinstance(row,tuple) or len(row)!=c or any(type(q) is not int or q<0 for q in row) for row in self.configuration): raise ValueError('invalid configuration')
        if sum(self.ambient)-c!=3: raise ValueError('not a threefold')
        if any(sum(row)!=n+1 for row,n in zip(self.configuration,self.ambient)): raise ValueError('Calabi-Yau row condition failed')
        if self.h11!=len(self.ambient): raise ValueError('only declared favourable embeddings supported')
        if self.cone not in ('POSITIVE_ORTHANT','AMBIENT_SUBCONE'): raise ValueError('unsupported cone')
    @cached_property
    def d(self): return triple_intersections(self.ambient,self.configuration)
    @cached_property
    def c2(self): return tangent_c2_pairings(self.ambient,self.configuration)
    @cached_property
    def nonzero_intersections(self):
        return tuple((i,j,k,self.d[i][j][k]) for i in range(self.h11) for j in range(self.h11) for k in range(self.h11) if self.d[i][j][k])

def benchmark(identifier):
    identifier=str(identifier).lower().removeprefix('x')
    if identifier=='7862': return CICY('7862',(1,)*4,((2,),)*4,4,68,(2,4,8,16),'POSITIVE_ORTHANT')
    if identifier=='7447': return CICY('7447',(1,)*5,((1,1),)*5,5,45,(2,4,10),'POSITIVE_ORTHANT')
    if identifier=='quintic': return CICY('quintic',(4,),((5,),),1,101,(), 'POSITIVE_ORTHANT')
    if identifier=='bicubic': return CICY('bicubic',(2,2),((3,),(3,)),2,83,(), 'POSITIVE_ORTHANT')
    raise ValueError('unsupported geometry: '+identifier)
