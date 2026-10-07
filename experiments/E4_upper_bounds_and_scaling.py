"""E4 -- constructive upper bounds and computational scaling.

Two questions:
  (i)  can we *build* a cover of size Phi(n) without an exact solver?  We run
       randomized greedy set cover with several tie-breaking rules and record the
       best cover found; this is an independent, solver-free upper bound.
  (ii) how does the pipeline scale?  We time enumeration, the incidence build,
       the MILP solve and the LP-dual solve as a function of n.

Usage:  python experiments/E4_upper_bounds_and_scaling.py [--max-n 13] [--greedy-max-n 12]
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

from triplecover.exact import incidence_matrix, solve_exact, solve_lp  # noqa: E402
from triplecover.polygon import all_triples, triangulations  # noqa: E402
from triplecover.triples import phi  # noqa: E402
import numpy as np
import random



sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def greedy(n: int, rng: random.Random, mode: str):
    """Greedy.
    
    Args:
        n:
        rng:
        mode:
    
    Returns:
        The computed result
    
    """
    tris, triples, A = incidence_matrix(n)
    need = np.ones(A.shape[0], dtype=bool)
    chosen = np.zeros(A.shape[1], dtype=bool)
    fam = []
    while need.any():
        rem = np.asarray(need.astype(float) @ A).ravel()
        scores = np.where(chosen, -np.inf, rem)
        best = float(scores.max())
        cands = np.flatnonzero(scores == best)
        j = int(cands[0] if mode == "first" else cands[-1] if mode == "last" else rng.choice(cands))
        chosen[j] = True
        fam.append(tris[j])
        need &= ~np.asarray(A[:, j].todense()).ravel().astype(bool)
    return fam


def main() -> None:
    """Entry point — parse arguments and run the main computation.
    
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=13)
    ap.add_argument("--greedy-max-n", type=int, default=12)
    ap.add_argument("--restarts", type=int, default=9)
    ap.add_argument("--seed", type=int, default=20261004)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    os.makedirs(RESULTS, exist_ok=True)

    rows = []
    print("n | #triangulations | C(n,3) | greedy best | Phi | greedy==Phi | T(n) | timings (enum/inc/milp/lp)")
    for n in range(5, args.max_n + 1):
        t0 = time.time()
        ntri = len(triangulations(n))
        t_enum = time.time() - t0

        t0 = time.time()
        tris, triples, A = incidence_matrix(n)
        t_inc = time.time() - t0

        gbest = None
        if n <= args.greedy_max_n:
            best = min(len(greedy(n, rng, m)) for m in ("first", "last", "random") for _ in range(3))
            gbest = best

        t0 = time.time()
        res = solve_exact(n)
        t_milp = time.time() - t0
        t0 = time.time()
        lp = solve_lp(n)
        t_lp = time.time() - t0

        rows.append(dict(
            n=n, triangulations=ntri, triples=len(triples), greedy_best=gbest, Phi=phi(n),
            greedy_equals_phi=(gbest == phi(n)) if gbest is not None else "",
            T_exact=res.value, lp=lp, certified=res.certified,
            t_enum=round(t_enum, 3), t_incidence=round(t_inc, 3),
            t_milp=round(t_milp, 3), t_lp=round(t_lp, 3),
        ))
        print(f"{n:>2} | {ntri:>15} | {len(triples):>7} | {str(gbest):>11} | {phi(n):>4} | "
              f"{str(gbest == phi(n)) if gbest is not None else '-':>11} | {res.value:>4} | "
              f"{t_enum:.2f}/{t_inc:.2f}/{t_milp:.2f}/{t_lp:.2f}", flush=True)

    path = os.path.join(RESULTS, "E4_upper_bounds_scaling.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")
    g = [r for r in rows if r["greedy_best"] is not None]
    print(f"greedy matched Phi(n) in {sum(1 for r in g if r['greedy_equals_phi'])}/{len(g)} cases")


if __name__ == "__main__":
    main()