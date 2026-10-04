"""Tests that the exact solver really returns optimal, valid covers."""

from __future__ import annotations

import pytest

from triplecover.exact import incidence_matrix, solve_exact, solve_lp, verify_cover
from triplecover.polygon import all_triples, triangulations
from triplecover.triples import certificate_total, phi


@pytest.mark.parametrize("n", (5, 6, 7, 8, 9))
def test_exact_matches_phi_and_is_certified(n: int) -> None:
    r = solve_exact(n)
    assert r.value == phi(n) == r.formula
    assert r.certified, "LP bound did not match the integer optimum"
    assert verify_cover(r.family, n)


@pytest.mark.parametrize("n", (6, 7, 8))
def test_lp_bound_equals_lower_bound(n: int) -> None:
    """The LP-dual optimum equals the combinatorial certificate total."""
    assert abs(solve_lp(n) - certificate_total(n)) < 1e-6


def test_solver_returns_distinct_triangulations() -> None:
    r = solve_exact(8)
    keys = {frozenset(d) for d, _ in r.family}
    assert len(keys) == len(r.family), "the family repeats a triangulation"


def test_lower_bound_holds_for_every_verified_n() -> None:
    for n in range(6, 11):
        r = solve_exact(n)
        assert r.value >= certificate_total(n) - 1e-9


def test_incidence_matrix_shape() -> None:
    tris, triples, A = incidence_matrix(7)
    assert len(tris) == 42  # C_5
    assert len(triples) == 35  # C(7,3)
    assert A.shape == (35, 42)
    # each triangulation has exactly n-2 = 5 faces
    assert A.sum() == 42 * 5


def test_tiny_cases_by_hand() -> None:
    """T(3) = 1, T(4) = 2, T(5) = 5 checked without the solver."""
    assert phi(3) == 1
    assert phi(4) == 2
    assert phi(5) == 5
    # P_5: the five fans are the five triangulations and each covers 3 triples,
    # and every triple must be covered, so at least ceil(10/3) = 4; the
    # certificate gives the sharp bound 5.
    assert certificate_total(5) == 5
    for tri in triangulations(5):
        assert len(tri[1]) == 3