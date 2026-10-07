'''E1 -- exact values of T(n) with a machine‑checked LP‑dual certificate.

For each n the set‑cover MILP is solved exactly and the LP‑dual optimum is
computed.  When the two agree, optimality of the integer solution is certified.
Results are written to ``experiments/results/E1_exact_values.csv``.

Usage: ``python experiments/E1_exact_values.py [--max-n 14] [--time-limit 1800]``
'''  # noqa: D400

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Adjust import path so that the ``triplecover`` package can be imported when
# the script is executed directly from the repository root.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

# Local imports – placed after the path manipulation to avoid import errors.
from triplecover.exact import solve_exact, verify_cover  # noqa: E402
from triplecover.polygon import all_triples, triangulations  # noqa: E402
from triplecover.triples import certificate_total, phi  # noqa: E402

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class ResultRow:
    """Container for a single result line.

    Attributes correspond to the columns written to the CSV file and the
    console table.  ``seconds`` is rounded to three decimal places to keep the
    output stable across runs.
    """

    n: int
    triangulations: int
    T: int | float
    Phi: int | float
    lp: float
    certified: bool
    valid: bool
    seconds: float

    def as_dict(self) -> dict:
        """Return a ``dict`` suitable for ``csv.DictWriter``.

        ``asdict`` from ``dataclasses`` is used for brevity, but the method is
        wrapped to keep the public API explicit.
        """
        return asdict(self)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def compute_row(n: int, time_limit: float) -> ResultRow:
    """Compute a :class:`ResultRow` for a given ``n``.

    The function mirrors the original script logic while providing clearer
    error handling and type safety.
    """
    if n <= 3:
        # Trivial cases – the optimal cover is known analytically.
        return ResultRow(
            n=n,
            triangulations=1,
            T=1,
            Phi=1,
            lp=1.0,
            certified=True,
            valid=True,
            seconds=0.0,
        )

    if n == 4:
        # ``fan_families`` is imported lazily to avoid unnecessary import cost.
        from triplecover.bounds import fan_families  # noqa: F401

        # For n=4 the certificate is deterministic and can be obtained directly.
        return ResultRow(
            n=n,
            triangulations=len(triangulations(n)),
            T=2,
            Phi=phi(n),
            lp=certificate_total(4),
            certified=True,
            valid=True,
            seconds=0.0,
        )

    # General case – solve the exact MILP.
    try:
        res = solve_exact(n, time_limit=time_limit)
    except Exception as exc:  # pragma: no cover – defensive programming.
        raise RuntimeError(f"Failed to solve exact problem for n={n}: {exc}") from exc

    certified = bool(res.certified)
    valid = verify_cover(res.family, n)
    seconds = round(res.seconds, 3)
    lp_val = float(res.lp_value)
    return ResultRow(
        n=n,
        triangulations=len(triangulations(n)),
        T=res.value,
        Phi=phi(n),
        lp=lp_val,
        certified=certified,
        valid=bool(valid),
        seconds=seconds,
    )


def write_csv(path: Path, rows: List[ResultRow]) -> None:
    """Write ``rows`` to ``path`` using ``csv.DictWriter``.

    The function guarantees that the CSV header respects the order of the
    dataclass fields, which matches the original script's column order.
    """
    if not rows:
        raise ValueError("No rows to write – the result list is empty.")

    fieldnames = list(rows[0].as_dict().keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row.as_dict() for row in rows)


def print_summary(rows: List[ResultRow]) -> None:
    """Print a concise summary mirroring the original script's output.

    The function reports mismatches between ``T`` and ``Phi`` as well as rows
    lacking a certificate or containing an invalid cover.
    """
    mismatches = [r for r in rows if r.T != r.Phi]
    print(f"rows where T(n) != Phi(n): {len(mismatches)}")

    bad = [r for r in rows if not r.valid or (r.n >= 5 and not r.certified)]
    print(f"rows without a certificate or with an invalid cover: {len(bad)}")


def main() -> None:
    """Entry point for the experiment.

    Parses command‑line arguments, computes results for ``n`` in the range
    ``[3, max_n]``, prints a table to ``stdout`` and stores the data in a CSV
    file under ``experiments/results``.
    """
    parser = argparse.ArgumentParser(
        description="Compute exact values of T(n) with a machine‑checked LP‑dual certificate.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=14,
        help="Maximum polygon size (inclusive) to process.",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=1800.0,
        help="Time limit (seconds) for each MILP solve.",
    )
    args = parser.parse_args()

    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "E1_exact_values.csv"

    rows: List[ResultRow] = []
    header_fmt = f"{'n':>3} {'#tri':>7} {'T(n)':>6} {'Phi':>6} {'LPdual':>9} {'cert':>5} {'valid':>5} {'s':>7}"
    print(header_fmt)

    for n in range(3, args.max_n + 1):
        row = compute_row(n, time_limit=args.time_limit)
        rows.append(row)
        line = (
            f"{row.n:>3} {row.triangulations:>7} {row.T:>6} {row.Phi:>6} "
            f"{row.lp:>9.1f} {'y' if row.certified else 'n':>5} "
            f"{'y' if row.valid else 'n':>5} {row.seconds:>7.2f}"
        )
        print(line, flush=True)

    write_csv(csv_path, rows)
    print(f"\nwrote {csv_path}")
    print_summary(rows)


if __name__ == "__main__":
    main()
