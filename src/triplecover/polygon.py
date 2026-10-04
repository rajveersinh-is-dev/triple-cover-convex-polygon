"""Triangulations of a convex n-gon and their faces.

Conventions
-----------
The vertices of the convex ``n``-gon ``P_n`` are labelled ``0, 1, ..., n-1``
in cyclic order.  Indices are taken modulo ``n`` throughout, so edge
``{i, i+1}`` is a boundary edge and ``{i-1, i+1}`` are the neighbours of ``i``.

A *triangulation* ``T`` is stored as a ``frozenset`` of diagonals, each
diagonal being a sorted pair ``(a, b)`` with ``a < b``.  Its *faces* are the
``n - 2`` triangles of the dissection; each face is stored as a sorted triple
``(a, b, c)``, ``a < b < c``.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterator

Diagonal = tuple[int, int]
Face = tuple[int, int, int]

#: A triangulation together with its faces.
Triangulation = tuple[frozenset[Diagonal], tuple[Face, ...]]


def boundary_edges(n: int) -> frozenset[Diagonal]:
    """The ``n`` boundary edges of ``P_n`` (cyclically closed), sorted pairs."""
    return frozenset(
        (min(i, j), max(i, j)) for i, j in ((i, (i + 1) % n) for i in range(n))
    )


def is_boundary_edge(e: Diagonal, n: int) -> bool:
    a, b = e
    return (b - a) % n == 1 or (a - b) % n == 1


def crosses(d1: Diagonal, d2: Diagonal) -> bool:
    """True iff two chords interleave strictly (they cross in the interior).

    For chords ``(a, b)`` and ``(c, d)`` written with ``a < b``, ``c < d`` this
    holds iff ``a < c < b < d`` or ``c < a < d < b``.
    """
    a, b = d1
    c, d = d2
    return (a < c < b < d) or (c < a < d < b)


def all_triples(n: int) -> tuple[Face, ...]:
    """All ``C(n, 3)`` vertex triples, sorted, in lexicographic order."""
    return tuple(combinations(range(n), 3))


def face_type(face: Face, n: int) -> int:
    """Classify a triple by the number of boundary edges it uses.

    Returns ``k`` = number of boundary edges of ``P_n`` among the three sides of
    the triple.  For ``n >= 5`` we write ``A`` for ``k = 2``, ``B`` for ``k = 1``
    and ``C`` for ``k = 0``.
    """
    a, b, c = face
    k = 0
    for u, v in ((a, b), (b, c), (a, c)):
        if is_boundary_edge((u, v) if u < v else (v, u), n):
            k += 1
    return k


def face_type_name(face: Face, n: int) -> str:
    """``'A'``, ``'B'`` or ``'C'`` as in :func:`face_type` (only valid for n>=5)."""
    return {2: "A", 1: "B", 0: "C"}[face_type(face, n)]


def _subpoly(lo: int, hi: int) -> Iterator[tuple[frozenset[Diagonal], tuple[Face, ...]]]:
    """All triangulations of the polygon ``lo, lo+1, ..., hi`` (inclusive).

    The recursion is driven by the triangle ``(lo, k, hi)`` that contains the
    closing edge ``(lo, hi)``.  Sub-polygons with fewer than three vertices
    contribute no faces.
    """
    m = hi - lo + 1
    if m == 2:
        yield frozenset(), ()
        return
    if m == 3:
        yield frozenset(), ((lo, lo + 1, hi),)
        return
    for k in range(lo + 1, hi):
        dl: frozenset[Diagonal] = frozenset() if k == lo + 1 else frozenset({(lo, k)})
        dr: frozenset[Diagonal] = frozenset() if k == hi - 1 else frozenset({(k, hi)})
        for left_d, left_f in _subpoly(lo, k):
            for right_d, right_f in _subpoly(k, hi):
                yield (
                    left_d | right_d | dl | dr,
                    left_f + right_f + ((lo, k, hi),),
                )


def triangulations(n: int) -> list[Triangulation]:
    """All triangulations of ``P_n`` as ``(diagonals, faces)`` pairs.

    There are ``C_{n-2}`` of them.  The output is sorted by the diagonal set so
    that runs are reproducible across platforms.
    """
    if n < 3:
        raise ValueError("need n >= 3")
    out = list(_subpoly(0, n - 1))
    out.sort(key=lambda t: (sorted(t[0]), t[1]))
    return out


def ears(diagonals: frozenset[Diagonal], n: int) -> frozenset[int]:
    """The ear vertices: those ``i`` with the diagonal ``(i-1, i+1)`` present."""
    out = set()
    for i in range(n):
        a, b = (i - 1) % n, (i + 1) % n
        d = (a, b) if a < b else (b, a)
        if d in diagonals:
            out.add(i)
    return frozenset(out)


def ear_faces(faces: tuple[Face, ...], n: int) -> frozenset[Face]:
    """The faces that use two boundary edges (``A``-faces); one per ear."""
    return frozenset(f for f in faces if face_type(f, n) == 2)


def dual_degrees(faces: tuple[Face, ...], n: int) -> tuple[int, int, int]:
    """Numbers of ``A``-, ``B``- and ``C``-faces of a triangulation of ``P_n``.

    Returns ``(#A, #B, #C)``.  These coincide with the degrees of the
    corresponding nodes in the dual tree: an ``A``-face is a leaf, a ``B``-face
    has dual degree 2 and a ``C``-face has dual degree 3.
    """
    a = b = c = 0
    for f in faces:
        k = face_type(f, n)
        if k == 2:
            a += 1
        elif k == 1:
            b += 1
        elif k == 0:
            c += 1
        else:
            raise ValueError("a face cannot use three boundary edges for n >= 4")
    return a, b, c


def dual_tree(faces: tuple[Face, ...], n: int) -> dict[Face, list[Face]]:
    """Explicit adjacency structure of the dual tree (used for figure output)."""
    by_edge: dict[Diagonal, list[Face]] = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (a, c)):
            e = (u, v) if u < v else (v, u)
            by_edge.setdefault(e, []).append((a, b, c))
    adj: dict[Face, list[Face]] = {f: [] for f in faces}
    for e, incident in by_edge.items():
        if is_boundary_edge(e, n):
            continue
        if len(incident) != 2:
            raise ValueError(f"diagonal {e} is not shared by two faces")
        f1, f2 = incident
        adj[f1].append(f2)
        adj[f2].append(f1)
    return adj


def is_triangulation(diagonals, faces, n: int) -> bool:
    """Structural self-check of the ``(diagonals, faces)`` representation."""
    if len(diagonals) != n - 3 or len(faces) != n - 2:
        return False
    if len(set(faces)) != n - 2:
        return False
    for d1, d2 in combinations(sorted(diagonals), 2):
        if crosses(d1, d2):
            return False
    usage: dict[Diagonal, int] = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (a, c)):
            e = (u, v) if u < v else (v, u)
            usage[e] = usage.get(e, 0) + 1
    if set(diagonals) - set(usage):
        return False
    if any(usage[d] != 2 for d in diagonals):
        return False
    bnd = boundary_edges(n)
    if set(usage) != bnd | set(diagonals):
        return False
    return all(usage[e] == 1 for e in bnd)