# The Triple-Covering Number of a Convex Polygon

A research project on a new extremal problem for triangulations of a convex
$n$-gon: **how many triangulations does it take so that every triangle inscribed
in the polygon appears as a face of at least one of them?**

For a convex *n*-gon let **T(n)** be the minimum number of triangulations in a
family such that every 3-subset of the $n$ vertices is a face of one of them.

| | |
|---|---|
| `T(3..14)` | 1, 2, 5, 8, 14, 20, 30, 40, 55, 70, 91, 112 |
| lower bound | `T(n) ≥ Φ(n)` for all `n ≥ 5`, proved |
| `Φ(2M)` | `2·C(M+1, 3)` |
| `Φ(2M+1)` | `1² + 2² + … + M²` |

`Φ(n) = n³/24 − O(n)`, so `T(n) = Ω(n³)`, whereas the classical counting bound
gives only `≈ n²/6`. The factor `Θ(n)` gap is the content of the paper.

## TL;DR

Give a triple `S = {a,b,c}` (`a<b<c`) its three cyclic *gaps*
`(b−a−1, c−b−1, n−1−c+a)`; they always sum to `n−3`. Put
`k = ⌊(n−3)/2⌋` and define a weight

```
y(S) = 1     if max gap ≤ k                     ("light")
y(S) = 1/2   if n even and max gap = k+1        ("half")
y(S) = 0     otherwise
```

Two facts about a *single* triangulation `T` make this a certificate:

1. **Gap-sum lemma.** Any two distinct faces `F, G` of `T` satisfy
   `maxgap(F) + maxgap(G) ≥ n−2` (tight).
2. **Antipodal lemma** (`n` even). Every face of weight `½` contains the same
   antipodal chord `{v, v+n/2}`, so there are at most two of them, and no face of
   weight `1` can coexist with one.

Hence the faces of any triangulation have total weight at most **1**, while
`Σ_S y(S) = Φ(n)` exactly. Double counting gives `T(n) ≥ Φ(n)`.

## Research question

> Given the $\binom{n}{3}$ vertex triples of a convex $n$-gon, what is the
> smallest number of triangulations whose face sets together contain all of them?

This is *not* settled by counting. A triangulation has `n−2` faces, so counting
allows `≈ n²/6` blocks; the truth is `≈ n³/24`. Nor is it settled by the
classical decompositions of $K_n$ into outerplanar pieces (book thickness), which
partition *edges*, not *triples*.

## Main result

**Theorem (gap-weight certificate).** For every `n ≥ 5`,
`T(n) ≥ Φ(n)` with `Φ(2M) = 2·C(M+1,3)` and `Φ(2M+1) = Σ_{j≤M} j²`.

**Theorem (exact values).** `T(n) = Φ(n)` for `3 ≤ n ≤ 14`. In every case the
LP-dual optimum equals the integer optimum of the set-cover formulation, so
optimality is *certified*, not merely reported by a solver.

**Theorem (a solved sub-problem).** `n` triangulations suffice to cover every
triple that uses a boundary edge, each such triple exactly once (the `n` fans),
and `n` is optimal. *(Proved in full.)*

**Conjecture.** `T(n) = Φ(n)` for all `n ≥ 5`. The upper bound is found by
randomized greedy set cover for `n ≤ 12` but is **not** proved in general —
see [Limitations](#limitations).

## Why this is interesting

* It is a genuinely cubic problem hidden behind a quadratic counting bound, and
  the reason is a *local* obstruction (Lemma 1) rather than a global count.
* The certificate `y` is the exact LP-dual optimum, so the bound is sharp by
  construction and cannot be improved without new insight.
* The parity of `n` matters: for odd `n` every positively-weighted triple is
  light, for even `n` the half triples enter with weight `½` and force the
  antipodal-chord phenomenon.

## Repository structure

```
src/triplecover/
  polygon.py     verified enumerator: triangulations with faces, ears, dual tree
  triples.py     gaps, A/B/C types, the certificate weight y, the value Phi(n)
  bounds.py      structural identities + machine-checkable verifiers
  exact.py       set-cover MILP with an LP-dual optimality certificate
tests/           160 pytest tests (definitions, identities, certificates, solver)
experiments/
  E1_exact_values.py                 certified exact values, n ≤ 14
  E2_certificate.py                  exhaustive certificate checks + counting identity
  E3_falsification.py                six attacks on the conjecture
  E4_upper_bounds_and_scaling.py     solver-free upper bounds, timings
  E5_counting_formula_check.py       inclusion–exclusion formula behind the proof
  make_figures.py                    all figures
  results/                           committed CSV outputs
figures/          generated figures (F1–F6)
paper/            main.tex, main.pdf (compiles with tectonic or pdflatex)
docs/             research notes: novelty audit, rejected directions, method
```

## Reproducing

```bash
pip install -e .

python -m pytest tests -q                              # 160 tests, ~2 s

python experiments/E1_exact_values.py --max-n 14       # ~2 min
python experiments/E2_certificate.py                  # ~1 min
python experiments/E3_falsification.py --max-n 12 --restarts 9
python experiments/E4_upper_bounds_and_scaling.py      # ~1 min
python experiments/E5_counting_formula_check.py       # seconds
python experiments/make_figures.py

cd paper && tectonic -X compile main.tex               # or pdflatex main.tex
```

Python ≥ 3.10 with `numpy`, `scipy` (HiGHS is bundled), `matplotlib`.
All experiments are deterministic and seeded; the CSVs in
`experiments/results/` are the committed outputs of the commands above.

## Verified facts, machine-checked

| check | range |
|---|---|
| `T(n) = Φ(n)` with a certified LP-dual optimum | `3 ≤ n ≤ 14` |
| every returned family really covers all triples | `3 ≤ n ≤ 14` |
| faces of a triangulation have total weight ≤ 1 | exhaustive, `5 ≤ n ≤ 12` |
| gap-sum lemma (and its tightness) | exhaustive, `5 ≤ n ≤ 12` |
| antipodal lemma | exhaustive, `6 ≤ n ≤ 12` |
| `Σ_S y(S) = Φ(n)` | brute force, `5 ≤ n ≤ 60` |
| inclusion–exclusion formula `G(s,m)` | full `26 × 14` grid |
| randomized greedy never returns fewer than `Φ(n)` blocks | `5 ≤ n ≤ 12` |

## Limitations

* **The general upper bound is open.** We conjecture `T(n) = Φ(n)`; we prove only
  the lower bound, the exact values for `n ≤ 14`, and the `n`-block solution of
  the boundary-edge sub-problem. The claim `T(n) ~ n³/24` is part of the
  conjecture, not a theorem.
* Exhaustiveness stops at `n = 14` (208 012 blocks, ≈ 96 s for the MILP) and the
  greedy/E1 pipeline degrades quickly beyond that.
* Convex position only. For point sets in general position the `A`/`B`/`C`
  decomposition used throughout does not apply.
* We do not claim the weight function `y` is the *unique* optimal dual solution,
  only that it is optimal.

## Related work

* F. Bernhart, P. C. Kainen, *The book thickness of a graph*, J. Combin. Theory
  Ser. B 27 (1979) 320–331 — `bt(K_n) = ⌈n/2⌉`; the closest classical relative.
* K. Buchberger, A. Yu. Osipov, *The thickness of the complete graph*,
  Combinatorica 18 (1998) 39–46 — thickness of convex drawings.
* Z. Füredi, D. Mubayi, J. O'Neill, J. Verstraëte, *Extremal problems for pairs
  of triangles*, arXiv:2010.11100 — extremal families of inscribed triangles;
  the nearest modern literature for our "light triple" condition.
* C. J. Colbourn, J. H. Dinitz (eds.), *Handbook of Combinatorial Designs* —
  covering designs; here the admissible blocks are restricted to triangulation
  face sets, which is why the classical bounds fail.

See [`docs/RESEARCH-NOTES.md`](docs/RESEARCH-NOTES.md) for the novelty audit,
including the **rejected first direction** (diagonal packings/coverings, whose
bound is the classical `⌈n/2⌉`) and the searches performed.

## Citation

```bibtex
@techreport{triplecover,
  title  = {The Triple-Covering Number of a Convex Polygon: A Gap-Weight Certificate},
  note  = {Preprint; see paper/main.pdf. Exact values for n <= 14, lower bound for all n},
  year  = {2026}
}
```

## License

MIT — see [LICENSE](LICENSE).