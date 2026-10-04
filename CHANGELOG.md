# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-04

### Research
- **Main theorem.** `T(n) ≥ Φ(n)` for all `n ≥ 5`, where `Φ(2M) = 2·C(M+1,3)`
  and `Φ(2M+1) = Σ_{j≤M} j²`; in particular `T(n) = Ω(n³)` with
  `Φ(n) = n³/24 − O(n)`.
- **Certificate.** The weight `y(S) = 1 / ½ / 0` determined by the largest cyclic
  gap of `S`; the faces of any triangulation have total weight ≤ 1, and the total
  weight of all triples is exactly `Φ(n)` (inclusion–exclusion).
- **Structural lemmas.** (i) Any two distinct faces of a triangulation satisfy
  `maxgap(F) + maxgap(G) ≥ n−2`; the bound is attained. (ii) For even `n`, all
  faces of weight `½` contain one common antipodal chord, so there are at most two
  of them, and no weight-1 face coexists with one.
- **Solved sub-problem.** The `n` fans cover every triple that uses a boundary
  edge exactly once, and `n` is optimal for that sub-problem.
- **Exact values.** `T(n) = Φ(n)` for `3 ≤ n ≤ 14`, each with a machine-checked
  LP-dual optimality certificate.
- **Conjecture.** `T(n) = Φ(n)` for all `n ≥ 5`; the general construction is open.

### Rejected
- The first direction (packings/coverings of the diagonals of a convex `n`-gon by
  triangulations, `τ(n)=⌊n/2⌋`, `κ(n)=⌈n/2⌉`) was **abandoned**: the lower bound
  is a one-line count and the upper bound is the classical book-thickness result
  `bt(K_n)=⌈n/2⌉` (Bernhart–Kainen 1979). Rationale recorded in
  `docs/RESEARCH-NOTES.md`.

### Software
- `src/triplecover`: verified enumerator of triangulations with faces, gaps and
  A/B/C types, structural identities with machine-checkable verifiers, and a
  set-cover MILP with an LP-dual certificate.
- `tests/`: 160 tests covering Catalan counts, representation consistency,
  crossing predicate, dual tree, the face budget, the certificate bound and its
  three face-level claims, the counting identity (5 ≤ n ≤ 40), the fans, and
  certified exact values (5 ≤ n ≤ 9).
- `experiments/`: `E1` exact values, `E2` certificate checks, `E3`
  falsification (six attacks, zero anomalies), `E4` solver-free upper bounds and
  scaling, `E5` verification of the inclusion–exclusion formula, plus figure
  generation. Committed CSV outputs under `experiments/results/`.
- `paper/`: LaTeX manuscript with abstract, introduction, related work and
  novelty statement, preliminaries, structural results, the certificate and its
  proof, exact values, an explicit section on the open gap, experiments,
  limitations, conclusion, and two appendices (counting algebra, and why the
  naive bounds fail). Compiles with `tectonic` or `pdflatex`.