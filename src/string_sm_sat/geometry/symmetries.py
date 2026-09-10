"""Ambient-factor relabelings for published count comparison, not equivariance."""
from itertools import permutations

def ambient_relabelings(geometry):
    # Initial registry only compares identical ambient/configuration rows.
    return tuple(p for p in permutations(range(geometry.h11)) if all(geometry.ambient[i]==geometry.ambient[p[i]] and geometry.configuration[i]==geometry.configuration[p[i]] for i in range(geometry.h11)))

def canonical_row_orbit(geometry,columns):
    return min(tuple(sorted(tuple(k[i] for i in p) for k in columns)) for p in ambient_relabelings(geometry))
