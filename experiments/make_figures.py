"""Generate the figures of the paper.

F1  T(n) vs Phi(n) and the decomposition of the certificate into A/B/C parts.
F2  Face-weight profiles: how many (light, half) pairs occur, and why the
    certificate sum never exceeds 1.
F3  Cubic growth: T(n) against n^3/24, showing T(n) ~ n^3/24.
F4  A picture of an optimal cover of P_9: one optimal block per drawn
    triangulation, with light / half / dark faces marked.

Usage:  python experiments/make_figures.py
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triplecover.bounds import fan, fan_families, weights_of  # noqa: E402
from triplecover.exact import solve_exact  # noqa: E402
from triplecover.polygon import all_triples, triangulations  # noqa: E402
from triplecover.triples import (  # noqa: E402
    is_half,
    is_light,
    maxgap,
    phi,
    triple_type,
    weight,
)

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
RES = os.path.join(HERE, "results")
os.makedirs(FIGS, exist_ok=True)


def fig1(ns, values):
    """Fig1.
    
    Args:
        ns:
        values:
    
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(ns, values, "o-", color="#1f4e79", label=r"$T(n)$ (certified exact)")
    ax.plot(ns, [phi(n) for n in ns], "s--", color="#c00000",
            label=r"$\Phi(n)$ (proved lower bound)")
    ax.set_xlabel("$n$")
    ax.set_ylabel("value")
    ax.set_title(r"$T(n)=\Phi(n)$ for $3\leq n\leq 14$; $\Phi$ is proved for all $n$")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "F1_T_vs_Phi.png"), dpi=200)
    plt.close(fig)


def fig1b(ns):
    """Certificate weight split by triple type."""
    even = [n for n in ns if n % 2 == 0]
    odd = [n for n in ns if n % 2 == 1]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for xs, marker, lab in ((even, "o", "$n$ even"), (odd, "s", "$n$ odd")):
        a, b, c = [], [], []
        for n in xs:
            tot = {"A": 0.0, "B": 0.0, "C": 0.0}
            for s in all_triples(n):
                tot[triple_type(s, n)] += weight(s, n)
            a.append(tot["A"])
            b.append(tot["B"])
            c.append(tot["C"])
        ax.plot(xs, a, marker, color="#7f7f7f", label=f"weight from A-triples ({lab})")
        ax.plot(xs, b, marker, color="#2e8b57", label=f"weight from B-triples ({lab})")
        ax.plot(xs, c, marker, color="#1f4e79", label=f"weight from C-triples ({lab})")
    ax.set_xlabel("$n$")
    ax.set_ylabel(r"$\sum_S y(S)$")
    ax.set_title(r"Decomposition of the certificate $\Phi(n)=\sum_S y(S)$")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "F2_certificate_decomposition.png"), dpi=200)
    plt.close(fig)


def fig2(max_n=12):
    """Fig2.
    
    Args:
        max_n (int):
    
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    xs = range(5, max_n + 1)
    maxlight, maxhalf, maxw = [], [], []
    for n in xs:
        ml = mh = mw = 0
        for tri in triangulations(n):
            fs = tri[1]
            ml = max(ml, sum(1 for f in fs if is_light(f, n)))
            mh = max(mh, sum(1 for f in fs if is_half(f, n)))
            mw = max(mw, weights_of(tri, n))
        maxlight.append(ml)
        maxhalf.append(mh)
        maxw.append(mw)
    ax.plot(xs, maxlight, "o-", color="#1f4e79", label="max # light faces in a block")
    ax.plot(xs, maxhalf, "s-", color="#c00000", label=r"max # half faces in a block")
    ax.plot(xs, maxw, "^--", color="#7030a0", label=r"max face weight $\sum_{F} y(F)$")
    ax.axhline(1.0, color="k", lw=0.8, ls=":")
    ax.set_xlabel("$n$")
    ax.set_title("Why the certificate works: at most one light face, at most two half faces")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "F3_face_profiles.png"), dpi=200)
    plt.close(fig)


def fig3(ns, values):
    """Fig3.
    
    Args:
        ns:
        values:
    
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(ns, values, "o-", color="#1f4e79", label=r"$T(n)$")
    ax.plot(ns, [(n ** 3) / 24 for n in ns], "k--", lw=0.9, label=r"$n^3/24$")
    ax.set_xlabel("$n$")
    ax.set_ylabel("value")
    ax.set_title(r"Cubic growth: $T(n)\sim n^3/24$")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "F4_cubic_growth.png"), dpi=200)
    plt.close(fig)


def fig4(n=9, nblocks=6):
    """Draw one optimal cover: pick the certified optimal family and show a few blocks."""
    res = solve_exact(n)
    fam = res.family[:nblocks]
    fig, axes = plt.subplots(2, 3, figsize=(9.0, 6.0))
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.column_stack([np.cos(th), np.sin(th)])
    for ax, tri in zip(axes.ravel(), fam):
        for f in tri[1]:
            w = weight(f, n)
            col = {1.0: "#ffd966", 0.5: "#a9d18e", 0.0: "#deebf7"}[w]
            ax.add_patch(Polygon(pts[list(f)], closed=True, facecolor=col,
                                 edgecolor="#404040", lw=0.8, alpha=0.95))
        for i, (x, y) in enumerate(pts):
            ax.plot([x], [y], "o", ms=3.5, color="#1f4e79")
            ax.annotate(str(i), (x, y), textcoords="offset points", xytext=(4, 4),
                        fontsize=7, color="#1f4e79")
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        kinds = [triple_type(f, n) for f in tri[1]]
        ax.set_title(f"block: A={kinds.count('A')} B={kinds.count('B')} C={kinds.count('C')}"
                     f", weight={weights_of(tri, n):.1f}", fontsize=8)
    fig.suptitle(f"Blocks of a certified optimal cover of $P_{n}$ "
                 r"(yellow: light, green: half, blue: zero weight)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIGS, "F5_optimal_cover_P9.png"), dpi=200)
    plt.close(fig)


def fig5(n=10):
    """The fans: the canonical n-block family that covers every A and B triple."""
    fig, axes = plt.subplots(2, 3, figsize=(9.0, 6.0))
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.column_stack([np.cos(th), np.sin(th)])
    for ax, v in zip(axes.ravel(), range(6)):
        d, faces = fan(v, n)
        for f in faces:
            t = triple_type(f, n)
            col = {"A": "#ffd966", "B": "#a9d18e", "C": "#deebf7"}[t]
            ax.add_patch(Polygon(pts[list(f)], closed=True, facecolor=col,
                                 edgecolor="#404040", lw=0.8, alpha=0.95))
        for i, (x, y) in enumerate(pts):
            ax.plot([x], [y], "o", ms=3.5, color="#1f4e79")
            ax.annotate(str(i), (x, y), textcoords="offset points", xytext=(4, 4),
                        fontsize=7, color="#1f4e79")
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"fan at vertex {v}", fontsize=9)
    fig.suptitle(r"The $n$ fans cover every A- and B-triple exactly once ($P_{10}$)",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIGS, "F6_fans.png"), dpi=200)
    plt.close(fig)


def main():
    """Entry point — parse arguments and run the main computation.
    
    """
    import csv

    path = os.path.join(RES, "E1_exact_values.csv")
    ns, values = [], []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ns.append(int(row["n"]))
            values.append(int(row["T"]))
    fig1(ns, values)
    fig1b(range(5, 15))
    fig2(12)
    fig3(ns, values)
    fig4(9)
    fig5(10)
    print("figures written to", FIGS)
    for f in sorted(os.listdir(FIGS)):
        print("  ", f)


if __name__ == "__main__":
    main()