# v1.0.0

Research question: **how many triangulations of a convex *n*-gon are needed so
that every triangle inscribed in the polygon appears as a face of at least one of
them?** Writing `T(n)` for this minimum, the classical counting bound gives only
`≈ n²/6`, yet the true answer grows like `n³/24`.

## Main theorem (proved)

For every `n ≥ 5`,

```
T(n)  ≥  Φ(n) :=  2·C(M+1, 3)            if n = 2M
                  1² + 2² + … + M²        if n = 2M + 1
```

Since `Φ(n) = n³/24 − O(n)`, this yields `T(n) = Ω(n³)` and
`liminf T(n)/n³ ≥ 1/24` — a factor `Θ(n)` beyond every counting argument.

The bound comes from an explicit **gap-weight certificate**. For a triple
`S = {a,b,c}` (`a<b<c`) let its cyclic gaps be `(b−a−1, c−b−1, n−1−c+a)` (they
always sum to `n−3`) and put `k = ⌊(n−3)/2⌋`. Set

```
y(S) = 1     if max gap ≤ k                   ("light")
y(S) = 1/2   if n even and max gap = k+1      ("half")
y(S) = 0     otherwise
```

Two structural lemmas about a *single* triangulation `T` show that its faces
have total weight at most **1**:

* **Gap-sum lemma** — any two distinct faces `F, G` of `T` satisfy
  `maxgap(F) + maxgap(G) ≥ n−2`. (Tight; three-case analysis: shared edge,
  shared vertex, separated.)
* **Antipodal lemma** (`n` even) — every weight-`½` face contains one common
  antipodal chord `{v, v+n/2}`, so there are at most two of them, and no
  weight-`1` face can coexist with one.

A short inclusion–exclusion computation gives `Σ_S y(S) = Φ(n)` exactly.
Double counting then yields the theorem.

## Also proved

* **Exact values `T(n) = Φ(n)` for `3 ≤ n ≤ 14`** — in every case the LP-dual
  optimum of the set-cover formulation equals the integer optimum, so
  optimality is *certified*, and each returned family was re-verified to cover
  all triples.
* **A solved sub-problem** — the `n` fans cover every triple that uses a
  boundary edge, each exactly once, and `n` is optimal for that task.
* **Face budget** — a triangulation with `e` ears has `(e, n−2e, e−2)` faces of
  types `A`, `B`, `C`; hence at most `⌊n/2⌋−2` `C`-faces per block.
* **Max-ear count** — triangulations with `⌊n/2⌋` ears are
  `I(n, ⌊n/2⌋)·C_{⌈n/2⌉−2}` in number.

## Computational contribution

* A **verified enumerator** for triangulations with faces, ears and dual trees,
  with a structural self-check (Catalan counts through `n = 13`).
* A **set-cover MILP** with an **LP-dual optimality certificate** (HiGHS).
* **Five experiment scripts**, all deterministic and seeded, with committed CSV
  outputs: exact values, exhaustive certificate checks, a dedicated
  **falsification** module (six attacks, zero anomalies), solver-free greedy
  upper bounds, and a check of the inclusion–exclusion formula.
* **170 tests**, including exhaustive verification of both structural lemmas and
  of the face-weight bound for `5 ≤ n ≤ 12`.
* Six figures, each answering a specific mathematical question.

## Reproducing

```bash
pip install -e .
python -m pytest tests -q
python experiments/E1_exact_values.py --max-n 14
python experiments/E2_certificate.py
python experiments/E3_falsification.py --max-n 12 --restarts 9
python experiments/E4_upper_bounds_and_scaling.py
python experiments/E5_counting_formula_check.py
python experiments/make_figures.py
cd paper && tectonic -X compile main.tex
```

Python ≥ 3.10 with `numpy`, `scipy` (HiGHS bundled) and `matplotlib`.
Verified from a clean checkout: all steps reproduce the committed CSVs and PDF.

## Known limitations

* **The general upper bound is open.** We conjecture `T(n) = Φ(n)` for all
  `n ≥ 5`; we prove only the lower bound, the exact values for `n ≤ 14`, and the
  `n`-block solution of the boundary-edge sub-problem. The statement
  `T(n) ~ n³/24` is part of the conjecture, not a theorem.
* Exactness is certified only for `n ≤ 14`; `n = 14` already involves 208 012
  blocks and about 93 seconds of MILP time.
* Only convex position is treated; for points in general position the
  `A`/`B`/`C` face decomposition used throughout does not apply.
* We do not claim the weight function `y` is the unique optimal dual solution.
* No peer review or publication has occurred; this is an independent research
  project.

## Novelty

No published source establishing `T(n)` was found. The nearest relatives are the
book-thickness theorem `bt(K_n) = ⌈n/2⌉` (Bernhart–Kainen, 1979) — which
partitions *edges* and whose bound is a one-line count, and which we explicitly
rejected as a first direction — and the extremal theory of families of inscribed
triangles in convex position (Füredi–Mubayi–O'Neill–Verstraëte,
arXiv:2010.11100). Our structural lemmas and the certificate are new; the
individual ingredients (Catalan counts, the ear/dual-tree budget, the two-ears
bound) are classical and cited as such. Details and the full search log are in
`docs/RESEARCH-NOTES.md`.