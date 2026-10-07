"""Exact computation of ``T(n)`` by mixed-integer programming, with LP certificates.

The covering problem is the set-cover instance

    minimise  sum_T x_T
    over      x in {0,1}^(#triangulations of P_n)
    s.t.      sum_{T : s in faces(T)} x_T >= 1   for every triple s,

whose LP relaxation is solved by HiGHS through :func:`scipy.optimize.milp`.
When the LP optimum is an integer the solver's certificate proves optimality of
the corresponding integer solution, so the reported value is *certified*.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix

from .polygon import Triangulation, all_triples, triangulations
from .triples import phi

__all__ = ["ExactResult", "incidence_matrix", "solve_exact", "solve_lp", "verify_cover"]


@dataclass
class ExactResult:
    """Outcome of an exact solve."""

    n: int
    value: int
    certified: bool
    lp_value: float
    family: list[Triangulation] = field(default_factory=list)
    status: int = 0
    seconds: float = 0.0

    @property
    def formula(self) -> int:
        """Formula.
        
        Returns:
            The computed result
        
        """
        return phi(self.n)

    @property
    def matches_formula(self) -> bool:
        """Matches formula.
        
        Returns:
            The computed result
        
        """
        return self.value == self.formula


def incidence_matrix(n: int) -> tuple[list[Triangulation], list, "coo_matrix"]:
    """The triple-by-triangulation incidence matrix of the covering instance."""
    tris = triangulations(n)
    triples = all_triples(n)
    idx = {s: i for i, s in enumerate(triples)}
    rows, cols = [], []
    for j, (_, faces) in enumerate(tris):
        for f in faces:
            rows.append(idx[f])
            cols.append(j)
    A = coo_matrix(
        (np.ones(len(rows)), (rows, cols)), shape=(len(triples), len(tris))
    ).tocsr()
    return tris, triples, A


def solve_lp(n: int, tris=None, triples=None, A=None) -> float:
    """Optimal value of the LP *dual*, i.e. a rigorous lower bound for ``T(n)``.

    The dual is ``max sum_S y_S`` subject to ``sum_{S in faces(T)} y_S <= 1`` for
    every triangulation ``T``; its optimal value equals the primal LP relaxation,
    which lower-bounds the integer optimum ``T(n)``.
    """
    if A is None:
        tris, triples, A = incidence_matrix(n)
    n_triples = A.shape[0]
    res = linprog(
        c=-np.ones(n_triples),
        A_ub=A.T.tocsr(),
        b_ub=np.ones(A.shape[1]),
        bounds=(0, None),
        method="highs",
    )
    return float(-res.fun)


def solve_exact(n: int, time_limit: float = 1800.0) -> ExactResult:
    """Solve the covering instance exactly for ``P_n`` (``time_limit`` seconds)."""
    import time

    t0 = time.time()
    tris, triples, A = incidence_matrix(n)
    cons = LinearConstraint(A, np.ones(len(triples)), np.full(len(triples), np.inf))
    res = milp(
        c=np.ones(len(tris)),
        constraints=cons,
        integrality=np.ones(len(tris)),
        bounds=Bounds(0, 1),
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    if res.fun is None:
        return ExactResult(n, -1, False, float("nan"), [], res.status, time.time() - t0)
    value = int(round(res.fun))
    lp_value = solve_lp(n, tris, triples, A)
    certified = abs(lp_value - value) < 1e-6
    fam = [tris[i] for i, x in enumerate(res.x) if x is not None and x > 0.5]
    return ExactResult(n, value, certified, lp_value, fam, res.status, time.time() - t0)


def verify_cover(fam, n: int) -> bool:
    """True iff every triple of ``P_n`` is a face of some member of ``fam``."""
    seen = set()
    for _, faces in fam:
        seen.update(faces)
    return all(s in seen for s in all_triples(n))