"""Check the composition-counting formula used in the paper's counting lemma."""
import sys
from math import comb
from fractions import Fraction
sys.path.insert(0, "src")
from triplecover.polygon import all_triples
from triplecover.triples import gaps, maxgap, phi, weight


def G_brute(s, m):
    """#{g >= 0 : sum = s, max <= m} by brute force."""
    return sum(1 for a in range(s + 1) for b in range(s + 1)
               if (c := s - a - b) >= 0 and max(a, b, c) <= m)


def C2(x):
    return comb(x, 2) if x >= 2 else 0


def G_formula(s, m):
    """Inclusion-exclusion: #{g >= 0 : sum = s, each <= m} (three parts)."""
    if s < 0 or m < 0:
        return 0
    return (
        C2(s + 2)
        - 3 * C2(s - m + 1)
        + 3 * C2(s - 2 * m)
        - C2(s - 3 * m - 1)
    )


bad = 0
for s in range(0, 26):
    for m in range(0, 14):
        b, f = G_brute(s, m), G_formula(s, m)
        if b != f:
            bad += 1
            if bad < 6:
                print(f"MISMATCH s={s} m={m} brute={b} formula={f}")
print(f"composition formula mismatches over the grid: {bad}")

# now verify sum_S w(S) = Phi(n) using the formula only
print()
print("n | Phi(n) | formula value | ok")
for n in range(5, 41):
    s = n - 3
    k = (n - 3) // 2
    light = Fraction(n * G_formula(s, k), 3)
    if n % 2 == 0:
        half = Fraction(n, 6) * (G_formula(s, k + 1) - G_formula(s, k))
    else:
        half = Fraction(0)
    val = light + half
    print(f"{n:>2} | {phi(n):>6} | {str(val):>11} | {val == phi(n)}")