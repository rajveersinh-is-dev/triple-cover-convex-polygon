"""E3 -- falsification: try hard to break the conjectured formula T(n) = Phi(n).

Attacks, in order of increasing strength:

A. search for triangulations whose faces violate the certificate bound
   (max face weight > 1) -- would refute Proposition 3.4;
B. search for triangulations violating the three face-level claims;
C. exhaustive check of the counting identity sum_s y(s) = Phi(n);
D. exact solve of the covering instance and comparison with Phi(n), including the
   LP-dual value, which would reveal a gap;
E. adversarial heuristics for the covering problem (greedy set cover with many
   random restarts and several tie-breaking rules) -- if any run returns fewer
   than Phi(n) blocks, the lower bound is refuted;
F. a scaling check: how large can n get in the exact pipeline.

Usage:  python experiments/E3_falsification.py [--max-n 11] [--restarts 40]
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triplecover.exact import incidence_matrix, solve_exact  # noqa: E402
from triplecover.polygon import all_triples, face_type, triangulations  # noqa: E402
from triplecover.triples import certificate_total, is_half, is_light, phi, weight  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def greedy_cover(n: int, rng: random.Random, mode: str) -> int:
    """Greedy set cover on the incidence structure; ``mode`` picks the tie-break.

    Gains are recomputed as *remaining* coverage and already-chosen blocks are
    excluded, so the iteration always makes progress.
    """
    tris, triples, A = incidence_matrix(n)
    need = np.ones(A.shape[0], dtype=bool)
    chosen = np.zeros(A.shape[1], dtype=bool)
    count = 0
    while need.any():
        rem = np.asarray(need.astype(float) @ A).ravel()
        scores = np.where(chosen, -np.inf, rem)
        best = float(scores.max())
        if best <= 0.0:
            raise RuntimeError(f"greedy stalled for n={n}")
        cands = np.flatnonzero(scores == best)
        if mode == "first":
            j = int(cands[0])
        elif mode == "last":
            j = int(cands[-1])
        else:  # random tie-break
            j = int(rng.choice(cands))
        chosen[j] = True
        count += 1
        col = np.asarray(A[:, j].todense()).ravel().astype(bool)
        need &= ~col
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--restarts", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20261004)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    os.makedirs(RESULTS, exist_ok=True)
    rows = []
    print(f"{'n':>3} {'A:maxw':>7} {'B:viol':>6} {'C:count':>8} {'D:T':>6} {'D:Phi':>6} "
          f"{'E:best':>7} {'E<Phi?':>7} {'Phi':>5}")
    for n in range(5, args.max_n + 1):
        # A + B: exhaustive structural attacks
        maxw = 0.0
        viol = 0
        for diags, faces in triangulations(n):
            maxw = max(maxw, sum(weight(f, n) for f in faces))
            nl = sum(1 for f in faces if is_light(f, n))
            nh = sum(1 for f in faces if is_half(f, n))
            if nl > 1 or (n % 2 == 0 and ((nl >= 1 and nh >= 1) or nh > 2)):
                viol += 1
        # C: counting identity
        count_ok = abs(certificate_total(n) - phi(n)) < 1e-9
        # D: exact value with LP certificate
        res = solve_exact(n)
        t_exact = res.value
        # E: adversarial greedy restarts
        best = min(
            min(greedy_cover(n, rng, m) for m in ("first", "last", "random"))
            for _ in range(max(1, args.restarts // 3))
        )
        breach = best < phi(n)
        rows.append(dict(n=n, max_face_weight=round(maxw, 12), structural_violations=viol,
                         count_ok=count_ok, T_exact=t_exact, Phi=phi(n),
                         lp=res.lp_value, greedy_best=best, greedy_breaches_bound=breach))
        print(f"{n:>3} {maxw:>7.3f} {viol:>6} {str(count_ok):>8} {t_exact:>6} {phi(n):>6} "
              f"{best:>7} {str(breach):>7} {phi(n):>5}", flush=True)

    path = os.path.join(RESULTS, "E3_falsification.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")

    total_bad = (
        sum(1 for r in rows if r["structural_violations"])
        + sum(1 for r in rows if not r["count_ok"])
        + sum(1 for r in rows if r["T_exact"] != r["Phi"])
        + sum(1 for r in rows if r["greedy_breaches_bound"])
        + sum(1 for r in rows if r["max_face_weight"] > 1 + 1e-12)
    )
    print(f"total anomalies: {total_bad}  (0 means no attack succeeded)")


if __name__ == "__main__":
    main()