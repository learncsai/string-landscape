"""Summand permutations only; repeated summands retain their multiplicities."""
def canonical(columns): return tuple(sorted(tuple(k) for k in columns))
