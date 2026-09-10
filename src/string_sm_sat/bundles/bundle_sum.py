from dataclasses import dataclass
from itertools import combinations
from .line_bundle import LineBundle
@dataclass(frozen=True)
class BundleSum:
    lines: tuple[LineBundle,...]
    def __post_init__(self):
        if not isinstance(self.lines,tuple) or not self.lines or any(not isinstance(l,LineBundle) for l in self.lines): raise TypeError('line bundle tuple required')
        if len({len(l.k) for l in self.lines})!=1: raise ValueError('dimension mismatch')
    @property
    def c1(self): return tuple(map(sum,zip(*(l.k for l in self.lines))))
    @property
    def canonical(self): return tuple(sorted(l.k for l in self.lines))
    def wedge2(self): return BundleSum(tuple(a.tensor(b) for a,b in combinations(self.lines,2)))
    @classmethod
    def from_columns(cls, columns): return cls(tuple(LineBundle(tuple(k)) for k in columns))
    @classmethod
    def from_rows(cls, rows):
        if not rows or len({len(row) for row in rows})!=1: raise ValueError('ragged matrix')
        return cls.from_columns(zip(*rows))
