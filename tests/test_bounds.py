"""Tests for the certificate: the lower bound, its counting identity, and the fans."""

from __future__ import annotations

from math import comb

import pytest

from triplecover.bounds import (
    catalan,
    cover_family,
    face_budget,
    fan,
    fan_families,
    fans_cover_types,
    max_ear_triangulation_count,
    verify_light_claims,
    verify_weight_bound,
    weights_of,
)
from triplecover.polygon import all_triples, ear_faces, ears, triangulations
from triplecover.triples import (
    certificate_total,
    is_half,
    is_light,
    maxgap,
    phi,
    triple_type,
    weight,
)

SMALL = range(4, 10)


def test_phi_closed_forms() -> None:
    for m in range(2, 20):
        assert phi(2 * m) == 2 * comb(m + 1, 3)
        assert phi(2 * m + 1) == sum(j * j for j in range(1, m + 1))


def test_phi_small_values() -> None:
    assert [phi(n) for n in range(3, 15)] == [1, 2, 5, 8, 14, 20, 30, 40, 55, 70, 91, 112]


@pytest.mark.parametrize("n", range(5, 41))
def test_certificate_total_equals_phi(n: int) -> None:
    """Theorem 3.5: sum of the certificate weights over all triples is Phi(n)."""
    assert abs(certificate_total(n) - phi(n)) < 1e-9


@pytest.mark.parametrize("n", SMALL)
def test_face_weight_never_exceeds_one(n: int) -> None:
    """Proposition 3.4: the faces of any triangulation have total weight <= 1."""
    ok, stats = verify_weight_bound(n)
    assert ok, stats
    assert stats["max_face_weight"] <= 1.0 + 1e-12


@pytest.mark.parametrize("n", SMALL)
def test_light_face_claims(n: int) -> None:
    """The three face-level claims behind Proposition 3.4."""
    ok, stats = verify_light_claims(n)
    assert ok, stats
    assert stats["max_light_faces"] <= 1
    if n % 2 == 0:
        assert stats["max_half_faces"] <= 2


@pytest.mark.parametrize("n", SMALL)
def test_weight_of_a_single_face_is_at_most_one(n: int) -> None:
    for s in all_triples(n):
        assert weight(s, n) in (0.0, 0.5, 1.0)
        if weight(s, n) == 1.0:
            assert is_light(s, n)
        if weight(s, n) == 0.5:
            assert n % 2 == 0 and is_half(s, n)


@pytest.mark.parametrize("n", SMALL)
def test_fans_are_triangulations_and_cover_a_and_b(n: int) -> None:
    assert fans_cover_types(n)
    for v in range(n):
        d, f = fan(v, n)
        assert len(d) == n - 3
        assert len(f) == n - 2


@pytest.mark.parametrize("n", (5, 6, 7, 8, 9, 10))
def test_fans_cover_each_b_triple_exactly_once(n: int) -> None:
    """Theorem 3.6: the n fans cover every B-triple exactly once, and every A-triple."""
    mult: dict[tuple, int] = {}
    for tri in fan_families(n):
        for f in tri[1]:
            mult[f] = mult.get(f, 0) + 1
    for s in all_triples(n):
        t = triple_type(s, n)
        if t == "B":
            assert mult.get(s, 0) == 1
        elif t == "A":
            assert mult.get(s, 0) >= 1
        else:
            assert mult.get(s, 0) == 0


@pytest.mark.parametrize("n", range(6, 13))
def test_max_ear_count_formula(n: int) -> None:
    """Proposition 3.2: number of triangulations with floor(n/2) ears."""
    m = n // 2
    indep = n * comb(n - m, m) // (n - m)
    expected = indep * catalan(n - m - 2)
    observed = sum(1 for d, _ in triangulations(n) if len(ears(d, n)) == m)
    assert observed == expected == max_ear_triangulation_count(n)


@pytest.mark.parametrize("n", SMALL)
def test_face_budget_matches_ear_count(n: int) -> None:
    for tri in triangulations(n):
        e = len(ears(tri[0], n))
        assert face_budget(tri, n) == (e, n - 2 * e, e - 2)
        assert weights_of(tri, n) <= 1.0 + 1e-12


@pytest.mark.parametrize("n", (6, 7, 8))
def test_cover_family_reports(n: int) -> None:
    ok, stats = cover_family(fan_families(n), n)
    assert stats["family_size"] == n
    # the fans miss exactly the C-triples
    missing = [s for s in all_triples(n) if triple_type(s, n) == "C"]
    assert stats["missing"] == len(missing)
    assert stats["face_weight_sum"] <= n * 1.0 + 1e-12