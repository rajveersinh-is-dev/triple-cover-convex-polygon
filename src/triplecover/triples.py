"""Triples of vertices: gaps, types, the certificate weight, and the target value.

For a triple ``S = {a, b, c}`` (``a < b < c``) of the ``n``-gon ``P_n`` define its
three cyclic *gaps*

    g_1 = b - a - 1,   g_2 = c - b - 1,   g_3 = n - 1 - c + a,

the numbers of vertices strictly between consecutive elements of ``S`` around the
cycle.  Always ``g_1 + g_2 + g_3 = n - 3``, and ``g_i >= 0``; ``g_i = 0`` exactly
when two elements of ``S`` are adjacent on the polygon.

Write ``maxgap(S) = max(g_1, g_2, g_3)`` and, for ``n >= 5``,

    k = floor((n - 3) / 2).
"""

from __future__ import annotations

from math import comb

from .polygon import Face, all_triples, face_type

__all__ = [
    "gaps",
    "maxgap",
    "triple_type",
    "weight",
    "is_light",
    "is_half",
    "phi",
    "phi_parts",
    "certificate_total",
    "balanced_c_triples",
    "mid_c_triples",
]


def gaps(s: Face, n: int) -> tuple[int, int, int]:
    """The three cyclic gaps of the triple ``s`` in ``P_n`` (they sum to n-3)."""
    a, b, c = s
    return (b - a - 1, c - b - 1, n - 1 - c + a)


def maxgap(s: Face, n: int) -> int:
    """``max(gaps(s, n))``."""
    return max(gaps(s, n))


def triple_type(s: Face, n: int) -> str:
    """``'A'`` (two boundary edges), ``'B'`` (one) or ``'C'`` (none)."""
    return {2: "A", 1: "B", 0: "C"}[face_type(s, n)]


def is_light(s: Face, n: int) -> bool:
    """True iff every gap of ``s`` is at most ``floor((n-3)/2)`` ('light' triple)."""
    return maxgap(s, n) <= (n - 3) // 2


def is_half(s: Face, n: int) -> bool:
    """True iff the largest gap is exactly ``floor((n-3)/2) + 1`` ('half' triple)."""
    return maxgap(s, n) == (n - 3) // 2 + 1


def weight(s: Face, n: int) -> float:
    """The certificate weight ``y(s)`` used in the lower bound.

    ``y = 1`` for light triples, ``y = 1/2`` for half triples when ``n`` is even,
    and ``y = 0`` otherwise.  Proposition 3.4 of the paper shows that the weight
    of the faces of any triangulation sums to at most 1.
    """
    k = (n - 3) // 2
    m = maxgap(s, n)
    if m <= k:
        return 1.0
    if n % 2 == 0 and m == k + 1:
        return 0.5
    return 0.0


def phi(n: int) -> int:
    """``Phi(n)``, the conjectured value of ``T(n)``.

    ``Phi(2M) = 2*C(M+1, 3)`` and ``Phi(2M+1) = sum_{j<=M} j^2``.
    """
    if n < 3:
        raise ValueError("need n >= 3")
    m = n // 2
    if n % 2 == 0:
        return 2 * comb(m + 1, 3)
    return sum(j * j for j in range(1, m + 1))


def phi_parts(n: int) -> tuple[int, int, int]:
    """``(Phi(n), Phi(n) for even n as 2C(M+1,3), odd part)`` -- for reporting."""
    m = n // 2
    if n % 2 == 0:
        return (phi(n), 2 * comb(m + 1, 3), 0)
    return (phi(n), 0, sum(j * j for j in range(1, m + 1)))


def certificate_total(n: int) -> float:
    """``sum_s y(s)`` over all ``C(n,3)`` triples; equals ``Phi(n)`` (Theorem 3.5)."""
    return sum(weight(s, n) for s in all_triples(n))


def balanced_c_triples(n: int) -> list[Face]:
    """``C``-triples all of whose gaps are at most ``floor((n-3)/2)``."""
    return [s for s in all_triples(n) if face_type(s, n) == 0 and is_light(s, n)]


def mid_c_triples(n: int) -> list[Face]:
    """``C``-triples whose largest gap is exactly ``floor((n-3)/2)+1``."""
    return [s for s in all_triples(n) if face_type(s, n) == 0 and is_half(s, n)]