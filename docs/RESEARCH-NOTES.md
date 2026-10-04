# Research notes: candidate selection, novelty audit, and method

This file records the reasoning behind the project, including the direction that
was **abandoned** and why. It is deliberately explicit about what is proved,
what is conjectured, and what the searches did and did not establish.

## 1. Rejected first direction (and why it matters)

**Question.** How many pairwise edge-disjoint triangulations of a convex $n$-gon
can be packed, and how many are needed to cover all diagonals?

**Claimed result.** `τ(n) = ⌊n/2⌋` and `κ(n) = ⌈n/2⌉`: the diagonals of the
$n$-gon can be partitioned into `⌈n/2⌉` triangulations (a "double fan"
construction), and the lower bound is the one-line count
`n(n−3)/2 ÷ (n−3) = n/2`.

**Why it was abandoned.**

* The lower bound is immediate arithmetic; there is no mathematics in it.
* The upper bound is classical. Covering all edges of `K_n` by `⌈n/2⌉` outerplanar
  pieces is the book-thickness theorem `bt(K_n) = ⌈n/2⌉` of Bernhart and
  Kainen (1979); the standard construction puts the vertices on a circle so that
  each page is a triangulation of the polygon, so the "partition of diagonals"
  statement is a re-derivation of a known result.
* Verified with web/arXiv/OEIS searches (queries: "edge-disjoint triangulations of
  a convex polygon", "book thickness complete graph ceil(n/2)", "triangulation
  packing", "decompose into maximal outerplanar").

This is recorded because it shaped the final project: the new question is the
same object with the covering requirement moved from *edges* to *triples*, where
counting genuinely fails.

## 2. Candidates screened before settling

Roughly two dozen directions were screened across enumerative combinatorics,
convex geometry, graph thickness, design theory and combinatorial optimisation,
rejecting any that (a) rediscovered a known result, (b) had no natural central
question, or (c) could not be validated at all.

| candidate | verdict |
|---|---|
| Ducci-type dynamics over `Z_m^n` | period structure already classified; natural questions covered |
| book thickness / geometric thickness of `K_n` | fully classical |
| outerthickness of `K_n` with a fixed Hamiltonian cycle | classical, counting-settled |
| max pairwise-crossing families of triangles in convex position | active literature (Füredi–Mubayi–O'Neill–Verstraëte) |
| covering designs with arbitrary blocks | classical, and the counting bound is tight |
| triangulations with bounded degree | essentially settled by the `(e, n−2e, e−2)` budget |
| **cover all vertex triples by triangulations** | **chosen** |

## 3. Chosen problem and why it looked right

For a convex $n$-gon, the minimum number of triangulations whose face sets cover
every 3-subset of the vertices. Early evidence that this is non-trivial:

* the counting bound is `≈ n²/6` while exact computation gives `1, 2, 5, 8, 14,
  20, 30, 40, 55, …`, i.e. `≈ n³/24` — a factor `Θ(n)` beyond counting;
* the exact values fit a closed form immediately after $n = 4$:

  ```
  T(n) − T(n−1) = 1, 3, 3, 6, 6, 10, 10, 15, 15, 21, 21, …
                = tri(⌊(n−1)/2⌋)
  ⇒  T(2M)   = Σ_{k≤M} k(k−1) = 2·C(M+1,3)
     T(2M+1) = Σ_{k≤M} k²
  ```

  which suggested that the sequence is exactly `Φ(n)`.

## 4. How the certificate was found (and why it is not a solver artefact)

The covering instance is a set cover, so its LP dual is
`max Σ_S y_S` subject to `Σ_{S ∈ faces(T)} y_S ≤ 1` for every triangulation `T`.
Solving the dual for small `n` and *symmetrising by gap profile* revealed an
exact pattern:

```
weight 1     : largest gap ≤ ⌊(n−3)/2⌋          ("light")
weight 1/2   : largest gap = ⌊(n−3)/2⌋+1, n even ("half")
weight 0     : everything else
```

Because the certificate is a *proved* statement about every triangulation
(Lemmas 3.6 and 3.7 of the paper) and its total weight equals `Φ(n)` by an
inclusion–exclusion calculation, the solver is only used for verification and
for the exact values — never as part of a proof. The tests check the lemmas
exhaustively for `5 ≤ n ≤ 12`.

## 5. Falsification attempts (all recorded in `E3`)

| attack | outcome |
|---|---|
| exhaustive search for a face-weight sum `> 1` | none, `5 ≤ n ≤ 12` |
| exhaustive search for two light faces in one block | none |
| exhaustive search for a light face together with a half face (even `n`) | none |
| exhaustive check of `Σ y = Φ` | holds, `5 ≤ n ≤ 60` |
| exact MILP vs `Φ` | equal, `3 ≤ n ≤ 14` |
| randomized greedy set cover (3 tie-break rules × restarts) | never below `Φ` |

Additional negative results worth recording:

* building **one block per light triple** does *not* work: half triples provably
  cannot share a block with a light one, and there are as many half triples as
  light triples up to a constant factor;
* a naive per-cap greedy ("maximise the number of internal faces inside each
  cap of the chosen triple") covers only the chosen triples and fails for
  `n ≥ 10`;
* the two canonical constructions tried (fan-filled caps; cap-optimised caps)
  both produce blocks with too few `C`-faces.

## 6. What remains open

A general construction achieving `Φ(n)`. Concretely: (i) find a rule assigning
every non-half `C`-triple to a light block, and (ii) pair up the half triples.
Step (ii) has a candidate — the map `(a, b, a+M) ↦ (a+M, b+M)` on `Z/2M` is a
fixed-point-free involution whose pairs are co-realisable as two faces of a
triangulation — but the matching argument needed for (i) is not done, so the
conjecture remains open.

## 7. Honesty checklist

* No number in the paper, README or CSV files was estimated or invented; every
  value comes from the committed code.
* Proved: the gap-sum lemma, the antipodal lemma, the weight bound, the counting
  identity, the main lower bound, the fans theorem, the max-ear count.
* Computed with certification: `T(n)` for `3 ≤ n ≤ 14`.
* Conjectured: `T(n) = Φ(n)` for all `n ≥ 5`, and hence `T(n) ~ n³/24`.
* Literature: no source establishing `T(n)` was found; we state explicitly that
  this is a search outcome, not a proof of novelty.