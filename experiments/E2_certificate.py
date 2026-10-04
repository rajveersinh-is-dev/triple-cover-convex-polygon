"""E2 -- the certificate: weight bound, face claims and the counting identity.

Three independent checks of the lower bound of Theorem 3.4 / Corollary 3.5:

1. exhaustive: for every triangulation of P_n the faces have total weight <= 1;
2. exhaustive: the three face-level claims (at most one light face; for even n no
   half face together with a light one; at most two half faces);
3. the counting identity sum_s y(s) = Phi(n), checked by brute force up to n = 60
   and against the closed form.

Usage:  python experiments/E2_certificate.py [--exhaustive-max-n 12] [--count-max-n 60]
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triplecover.bounds import verify_light_claims, verify_weight_bound  # noqa: E402
from triplecover.polygon import all_triples  # noqa: E402
from triplecover.triples import certificate_total, phi, weight  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exhaustive-max-n", type=int, default=12)
    ap.add_argument("--count-max-n", type=int, default=60)
    args = ap.parse_args()

    os.makedirs(RESULTS, exist_ok=True)
    rows = []
    print("n |  max face weight | light<=1 | half<=2 | light+half | sum y | Phi | ok")
    for n in range(5, args.count_max_n + 1):
        wsum = certificate_total(n)
        rec = dict(n=n, sum_weight=wsum, Phi=phi(n), count_ok=abs(wsum - phi(n)) < 1e-9)
        if n <= args.exhaustive_max_n:
            ok_w, st_w = verify_weight_bound(n)
            ok_l, st_l = verify_light_claims(n)
            rec.update(
                max_face_weight=round(st_w["max_face_weight"], 12),
                weight_bound_ok=ok_w,
                max_light_faces=st_l["max_light_faces"],
                max_half_faces=st_l["max_half_faces"],
                light_claims_ok=ok_l,
                violations=st_l["violations_light"] + st_l["violations_light_plus_half"]
                + st_l["violations_half"],
            )
            print(f"{n:>2} | {st_w['max_face_weight']:>15.3f} | {st_l['max_light_faces']:>8} | "
                  f"{st_l['max_half_faces']:>7} | {st_l['violations_light_plus_half']:>10} | "
                  f"{wsum:>5.0f} | {phi(n):>3} | {ok_w and ok_l and rec['count_ok']}", flush=True)
        else:
            print(f"{n:>2} | {'-':>15} | {'-':>8} | {'-':>7} | {'-':>10} | "
                  f"{wsum:>5.0f} | {phi(n):>3} | {rec['count_ok']}", flush=True)
        rows.append(rec)

    path = os.path.join(RESULTS, "E2_certificate.csv")
    keys = sorted({k for r in rows for k in r})
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")

    bad_count = [r for r in rows if not r["count_ok"]]
    print(f"counting-identity failures: {len(bad_count)}")
    exh = [r for r in rows if "weight_bound_ok" in r]
    print(f"exhaustive rows: {len(exh)}, failures: {sum(1 for r in exh if not (r['weight_bound_ok'] and r['light_claims_ok']))}")


if __name__ == "__main__":
    main()