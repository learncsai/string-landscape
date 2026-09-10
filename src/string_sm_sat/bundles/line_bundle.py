from dataclasses import dataclass
@dataclass(frozen=True, order=True)
class LineBundle:
    k: tuple[int,...]
    def __post_init__(self):
        if not isinstance(self.k,tuple) or not self.k or any(type(x) is not int for x in self.k): raise TypeError('nonempty immutable Python integer tuple required')
    @property
    def c1(self): return self.k
    def tensor(self, other):
        if len(self.k)!=len(other.k): raise ValueError('dimension mismatch')
        return LineBundle(tuple(a+b for a,b in zip(self.k,other.k)))
    def dual(self): return LineBundle(tuple(-x for x in self.k))
