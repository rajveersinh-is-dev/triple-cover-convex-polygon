"""Tests for the polygon enumerator and the local structural identities."""

from __future__ import annotations

import pytest

from triplecover.polygon import (
    all_triples,
    boundary_edges,
    crosses,
    dual_degrees,
    dual_tree,
    ear_faces,
    ears,
    face_type,
    face_type_name,
    is_boundary_edge,
    is_triangulation,
    triangulations,
)
from triplecover.triples import gaps, maxgap, triple_type

SMALL = range(3, 11)


def catalan(m: int) -> int:
    from math import comb

    return comb(2 * m, m) // (m + 1)


@pytest.mark.parametrize("n", SMALL)
def test_count_is_catalan(n: int) -> None:
    assert len(triangulations(n)) == catalan(n - 2)


@pytest.mark.parametrize("n", SMALL)
def test_representation_is_self_consistent(n: int) -> None:
    for diags, faces in triangulations(n):
        assert is_triangulation(diags, faces, n)


@pytest.mark.parametrize("n", SMALL)
def test_diagonals_are_non_crossing_and_counted(n: int) -> None:
    bnd = boundary_edges(n)
    for diags, _ in triangulations(n):
        assert len(diags) == n - 3
        assert not (set(diags) & bnd)
        assert len(set(diags)) == len(diags)


def test_crossing_predicate() -> None:
    assert crosses((0, 3), (1, 4))
    assert crosses((1, 4), (0, 3))
    assert crosses((0, 2), (1, 3))  # interleaving
    assert not crosses((0, 4), (1, 3))  # nested
    assert not crosses((0, 1), (1, 5))  # share a vertex


@pytest.mark.parametrize("n", range(4, 11))
def test_face_budget_identity(n: int) -> None:
    """(#A, #B, #C) = (e, n - 2e, e - 2) with e the number of ears (Prop. 3.1)."""
    for diags, faces in triangulations(n):
        e = len(ears(diags, n))
        assert dual_degrees(faces, n) == (e, n - 2 * e, e - 2)
        assert len(ear_faces(faces, n)) == e


@pytest.mark.parametrize("n", range(5, 11))
def test_ear_count_is_bounded(n: int) -> None:
    es = [len(ears(d, n)) for d, _ in triangulations(n)]
    assert min(es) == 2
    assert max(es) == n // 2


@pytest.mark.parametrize("n", range(4, 10))
def test_dual_tree_is_a_tree(n: int) -> None:
    for _, faces in triangulations(n):
        adj = dual_tree(faces, n)
        assert len(adj) == n - 2
        seen = set()
        stack = [faces[0]]
        while stack:
            f = stack.pop()
            if f in seen:
                continue
            seen.add(f)
            stack.extend(adj[f])
        assert len(seen) == n - 2
        for f, nb in adj.items():
            for g in nb:
                assert f in adj[g]


def test_gaps_sum_to_n_minus_three() -> None:
    for n in range(5, 13):
        for s in all_triples(n):
            assert sum(gaps(s, n)) == n - 3
            assert min(gaps(s, n)) >= 0


def test_gap_zero_iff_adjacent_pair() -> None:
    for n in (7, 8, 9):
        for s in all_triples(n):
            a, b, c = s
            zeros = sum(
                1 for u, v in ((a, b), (b, c), (a, c)) if is_boundary_edge((u, v) if u < v else (v, u), n)
            )
            assert gaps(s, n).count(0) == zeros
            assert triple_type(s, n) == face_type_name(s, n)


def test_face_type_counts() -> None:
    """(|A|, |B|, |C|) = (n, n(n-4), n(n-4)(n-5)/6) for n >= 5."""
    for n in range(5, 12):
        cnt = [0, 0, 0]
        for s in all_triples(n):
            cnt[face_type(s, n)] += 1
        assert (cnt[2], cnt[1], cnt[0]) == (n, n * (n - 4), n * (n - 4) * (n - 5) // 6)


@pytest.mark.parametrize("n", range(5, 12))
def test_maxgap_threshold_partitions_types(n: int) -> None:
    k = (n - 3) // 2
    for s in all_triples(n):
        if face_type(s, n) == 0:
            assert maxgap(s, n) >= 1
        if maxgap(s, n) <= k:
            continue
        assert maxgap(s, n) >= k + 1