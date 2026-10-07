"""Structural facts about triangulations and the lower-bound certificate.

Everything here is a machine-checkable version of a lemma proved in the paper.

Main objects
------------
``T(n)``  -- the *triple-covering number* of ``P_n``: the minimum size of a family
             of triangulations such that every 3-subset of vertices is a face of
             at least one member of the family.

The certificate: a family ``F_1, ..., F_t`` of triangulations covering all triples
must satisfy ``t >= sum_s y(s) = Phi(n)``, because the faces of any single
triangulation have total certificate weight at most 1.
"""

from __future__ import annotations

from math import comb
from typing import Iterable, Sequence

from .polygon import Face, Triangulation, all_triples, dual_degrees, ears, triangulations
from .triples import is_half, is_light, maxgap, phi, triple_type, weight



__all__ = [
    "catalan",
    "ear_bounds",
    "max_ear_triangulation_count",
    "face_budget",
    "weights_of",
    "verify_weight_bound",
    "verify_light_claims",
    "fans_cover_types",
    "cover_family",
]


def catalan(m: int) -> int:
    """The ``m``-th Catalan number, ``C_m = C(2m, m) / (m + 1)``."""
    return comb(2 * m, m) // (m + 1)


def ear_bounds(n: int) -> tuple[int, int]:
    """``(min, max)`` number of ears of a triangulation of ``P_n`` (max for n>=5)."""
    return (2, n // 2)


def max_ear_triangulation_count(n: int) -> int:
    """Number of triangulations of ``P_n`` with exactly ``floor(n/2)`` ears.

    Such a triangulation is obtained by choosing a maximum independent set of the
    cycle ``C_n`` as the ear set and triangulating the residual
    ``ceil(n/2)``-gon; there are ``I(n, floor(n/2)) * C_{ceil(n/2) - 2}`` of them,
    where ``I(n, m) = (n / (n - m)) * C(n - m, m)`` counts independent ``m``-sets
    of the cycle (Proposition 3.2).
    """
    m = n // 2
    indep = n * comb(n - m, m) // (n - m)
    return indep * catalan(n - m - 2)


def face_budget(tri: Triangulation, n: int) -> tuple[int, int, int]:
    """``(#A, #B, #C)`` faces of ``tri`` -- equal to ``(e, n-2e, e-2)`` (Prop. 3.1)."""
    return dual_degrees(tri[1], n)


def weights_of(tri: Triangulation, n: int) -> float:
    """Total certificate weight of the faces of one triangulation (Proposition 3.4)."""
    return sum(weight(f, n) for f in tri[1])


def verify_weight_bound(n: int) -> tuple[bool, dict]:
    """Check ``sum_faces y <= 1`` for every triangulation of ``P_n``.

    Returns ``(ok, stats)``.  Exhaustive; only for small ``n``.
    """
    worst = 0.0
    worst_tri = None
    for tri in triangulations(n):
        w = weights_of(tri, n)
        if w > worst:
            worst, worst_tri = w, tri
    return (worst <= 1.0 + 1e-12), {
        "n": n,
        "max_face_weight": worst,
        "argmax_faces": list(worst_tri[1]) if worst_tri else None,
    }


def verify_light_claims(n: int) -> tuple[bool, dict]:
    """Check the three face-level claims that underpin Proposition 3.4.

    (i)  at most one face of any triangulation is *light*;
    (ii) if ``n`` is even and a light face exists, no face has largest gap ``k+1``;
    (iii) if ``n`` is even, at most two faces have largest gap ``k+1``.

    Returns ``(ok, stats)``.  Exhaustive; only for small ``n``.
    """
    nlight = 0
    nhalf_max = 0
    viol_light = viol_pair = viol_half = 0
    for tri in triangulations(n):
        fs = tri[1]
        nl = sum(1 for f in fs if is_light(f, n))
        nh = sum(1 for f in fs if is_half(f, n))
        nlight = max(nlight, nl)
        nhalf_max = max(nhalf_max, nh)
        if nl > 1:
            viol_light += 1
        if n % 2 == 0 and nl >= 1 and nh >= 1:
            viol_pair += 1
        if n % 2 == 0 and nh > 2:
            viol_half += 1
    ok = viol_light == 0 and viol_pair == 0 and viol_half == 0
    return ok, {
        "n": n,
        "max_light_faces": nlight,
        "max_half_faces": nhalf_max,
        "violations_light": viol_light,
        "violations_light_plus_half": viol_pair,
        "violations_half": viol_half,
    }


def fans_cover_types(n: int) -> bool:
    """True iff the ``n`` fans cover every ``A``- and ``B``-triple (Theorem 3.6)."""
    covered = set()
    for v in range(n):
        covered.update(fan(v, n)[1])
    return all(triple_type(s, n) == "C" or s in covered for s in all_triples(n))


def fan(v: int, n: int) -> Triangulation:
    """The fan triangulation: all diagonals through ``v``.

    Its faces are ``(v, v+i, v+i+1)`` for ``i = 1, ..., n-2`` (indices mod n).
    """
    others = [w for w in range(n) if w != v and (w - v) % n not in (1, n - 1)]
    diags = frozenset((min(v, w), max(v, w)) for w in others)
    faces = tuple(
        sorted(tuple(sorted((v, (v + i) % n, (v + i + 1) % n))) for i in range(1, n - 1))
    )
    return diags, faces


def cover_family(tris: Sequence[Triangulation], n: int) -> tuple[bool, dict]:
    """Check that ``tris`` covers every triple of ``P_n``; report multiplicities."""
    mult: dict[Face, int] = {}
    for d, fs in tris:
        for f in fs:
            mult[f] = mult.get(f, 0) + 1
    missing = [s for s in all_triples(n) if mult.get(s, 0) == 0]
    by_type = {"A": [], "B": [], "C": []}
    for s, m in mult.items():
        by_type[triple_type(s, n)].append(m)
    stats = {
        "family_size": len(tris),
        "missing": len(missing),
        "min_multiplicity": min(mult.values()) if mult else 0,
        "max_multiplicity": max(mult.values()) if mult else 0,
        "A_multiplicity": sorted(by_type["A"]),
        "B_multiplicity": sorted(by_type["B"]),
        "C_multiplicity": sorted(by_type["C"]),
        "total_weight": sum(weight(s, n) for s in all_triples(n)),
        "face_weight_sum": sum(weights_of(t, n) for t in tris),
    }
    return (not missing), stats


def lower_bound_certificate(n: int) -> dict:
    """The full lower-bound package for ``n``: value, weight sum, exhaustive check."""
    tot = sum(weight(s, n) for s in all_triples(n))
    out = {
        "n": n,
        "Phi": phi(n),
        "certificate_total": tot,
        "matches": abs(tot - phi(n)) < 1e-9,
        "triangulations": len(triangulations(n)),
    }
    if n <= 11:
        ok1, s1 = verify_weight_bound(n)
        out.update({"weight_bound_ok": ok1, **s1})
    return out


def verify_gap_sum_lemma(n: int) -> tuple[bool, dict]:
    """Check Lemma 3.6: two distinct faces F, G of a triangulation satisfy
    ``maxgap(F) + maxgap(G) >= n - 2``.

    Returns ``(ok, stats)`` with the observed minimum of the left-hand side.
    Exhaustive; only for small ``n``.
    """
    best = None
    argmin = None
    for _, faces in triangulations(n):
        for i, f in enumerate(faces):
            for g in faces[i + 1:
                ]:
                s = maxgap(f, n) + maxgap(g, n)
                if best is None or s < best:
                    best, argmin = s, (f, g)
    return (best is not None and best >= n - 2), {
        "n": n,
        "min_pair_sum": best,
        "required": n - 2,
        "argmin": list(argmin) if argmin else None,
    }


def verify_antipodal_claims(n: int) -> tuple[bool, dict]:
    """Check Lemma 3.7 for even ``n = 2M``.

    (i) every face with ``maxgap = M-1`` contains the antipodal chord ``{v, v+M}``;
    (ii) two such faces are the two faces adjacent to one and the same antipodal
    chord, so there are at most two of them;
    (iii) no face with ``maxgap <= M-2`` can be a face of a triangulation that also
    contains a face with ``maxgap = M-1``.
    """
    if n % 2 != 0:
        return True, {"n": n, "skipped": "odd n"}
    m = n // 2
    antipodal = {}
    viol_i = viol_ii = viol_iii = 0
    max_half = 0
    for _, faces in triangulations(n):
        half = [f for f in faces if maxgap(f, n) == m - 1]
        light = [f for f in faces if maxgap(f, n) <= m - 2]
        max_half = max(max_half, len(half))
        if half and light:
            viol_iii += 1
        chords = set()
        for f in half:
            pairs = {
                tuple(sorted((a, b)))
                for a, b in ((f[0], f[1]), (f[1], f[2]), (f[0], f[2]))
                if (b - a) % n == m or (a - b) % n == m
            }
            if len(pairs) != 1:
                viol_i += 1
            chords |= pairs
        if len(chords) > 1:
            viol_ii += 1
        antipodal[len(chords)] = antipodal.get(len(chords), 0) + 1
    ok = viol_i == 0 and viol_ii == 0 and viol_iii == 0 and max_half <= 2
    return ok, {
        "n": n,
        "max_half_faces": max_half,
        "violations_unique_antipode": viol_i,
        "violations_shared_antipode": viol_ii,
        "violations_light_with_half": viol_iii,
        "antipode_cardinalities": dict(sorted(antipodal.items())),
    }


def fan_families(n: int) -> Iterable[Triangulation]:
    """The ``n`` fans, as a covering family of ``P_n``."""
    return [fan(v, n) for v in range(n)]