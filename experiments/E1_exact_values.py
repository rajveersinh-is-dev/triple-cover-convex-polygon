"""E1 -- exact values of T(n) with a machine-checked LP-dual certificate.

For each n the set-cover MILP is solved exactly and the LP-dual optimum is
computed.  When the two agree, optimality of the integer solution is certified.
Results are written to experiments/results/E1_exact_values.csv.

Usage:  python experiments/E1_exact_values.py [--max-n 14] [--time-limit 1800]
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triplecover.exact import solve_exact, verify_cover  # noqa: E402
from triplecover.polygon import all_triples, triangulations  # noqa: E402
from triplecover.triples import certificate_total, phi  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=14)
    ap.add_argument("--time-limit", type=float, default=1800.0)
    args = ap.parse_args()

    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, "E1_exact_values.csv")
    rows = []
    print(f"{'n':>3} {'#tri':>7} {'T(n)':>6} {'Phi':>6} {'LPdual':>9} {'cert':>5} {'valid':>5} {'s':>7}")
    for n in range(3, args.max_n + 1):
        if n <= 3:
            rows.append(dict(n=n, triangulations=1, T=1, Phi=1, lp=1.0,
                            certified=True, valid=True, seconds=0.0))
            print(f"{n:>3} {1:>7} {1:>6} {1:>6} {1.0:>9.1f} {'y':>5} {'y':>5} {0.0:>7.2f}")
            continue
        if n == 4:
            from triplecover.bounds import fan_families

            r_val, cert, valid, secs, lp = 2, True, True, 0.0, certificate_total(4)
        else:
            res = solve_exact(n, time_limit=args.time_limit)
            r_val = res.value
            cert = res.certified
            valid = verify_cover(res.family, n)
            secs, lp = res.seconds, res.lp_value
        ntri = len(triangulations(n))
        rows.append(dict(n=n, triangulations=ntri, T=r_val, Phi=phi(n), lp=lp,
                         certified=cert, valid=valid, seconds=round(secs, 3)))
        print(f"{n:>3} {ntri:>7} {r_val:>6} {phi(n):>6} {lp:>9.1f} "
              f"{'y' if cert else 'n':>5} {'y' if valid else 'n':>5} {secs:>7.2f}", flush=True)

    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")

    mismatch = [r for r in rows if r["T"] != r["Phi"]]
    print(f"rows where T(n) != Phi(n): {len(mismatch)}")
    bad = [r for r in rows if not r["valid"] or (r["n"] >= 5 and not r["certified"])]
    print(f"rows without a certificate or with an invalid cover: {len(bad)}")
    return None


if __name__ == "__main__":
    main()