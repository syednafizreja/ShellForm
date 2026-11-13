# Day 10 (7 Nov 2026): S5 plateau table, pin to ShellBench v0.2.0, solver cross-check

Written by the cloud session, under the author's standing delegation. ShellBench tag: v0.2.0. CalculiX 2.21 (cloud). Results are provisional until the 10 Nov freeze run. Pre-registration: dated entry of 7 Nov (D10-1).

Plan line (`docs/plan.md`): S5 plateau table; move the pin to v0.2.0 and run `python -m shellform.batch --preset all --compare-record`; write the `sensitivity_meta.json` baseline path with `as_posix()`. Done when: S5 table in `results/`, 0 record mismatches, tests pass.

## 1. Pin move

`src/shellform/pin.py` now names v0.2.0 (`shellbench.__version__` reports "0.2.0"). Every result row names the tag. ShellBench changes between v0.1.0 and v0.2.0 that touch ShellForm: the factor file gained a second set (named in code since Day 9, `carbon.FACTOR_SET`), the CalculiX shell wrapper `shellbench.shellfe`, new frame-beam options. None changes a value ShellForm reads.

**Record check at the pin move:** all 168 designs rerun at v0.2.0 with the Day 4-9 settings: 0 mismatches against the Day 4-6 record (largest relative difference: deflection 2.3e-4, which is CalculiX 2.21 against 2.23; everything else 1.3e-9 or less). Files: `results/batch_pinmove_v020.csv` and its meta file. This is the evidence that moving the pin changed nothing.

## 2. Cross-check of `fe.py` against ShellBench's wrapper (31 Oct amendment)

The 31 Oct amendment promised this when ShellBench's shell wrapper was tagged. `python -m shellform.crosscheck` builds the same S8R shell in both programs (same nodes, elements, pinned nodes, E, nu, density, self-weight) for four gravity forms: 10 m and 20 m, corners and edges, rise 0.15, sized thickness. `results/fe_crosscheck.csv`:

- Largest displacement: identical to all printed digits in all four.
- First buckling factor, both programs asking for 2 factors: within 0.26 % (edges, 10 m: 348.88 against 347.98); corners identical.

Inside the 2 % limit, so `fe.py` stays the analysis code. [J] The comparison is for self-weight only, because that is the one load both programs apply the same way; it does not test the plan-area nodal loads.

## 3. A solver set-up error found by the cross-check (D10-1)

When the two programs were first compared, ShellBench's wrapper was asked for one buckling factor and ShellForm's `fe.analyse` for two, and the first factor differed by up to 2.8 % for edges and 0.2 % for corners. The models are the same; the number of factors requested is not. With few factors requested, CalculiX's eigensolver returns a lowest value that is too high. Asking for 2, 4 or 8 gives the same converged value (10 m corners: 12.82882 at 2, 4 and 8; 10 m edges: 346.71 at 4, 346.71 at 8, 356.49 at 1). The sizing of Days 4-9 asked for one factor.

Measured on the sizing: every design within 3 % of its threshold (149 designs, baseline and the three Day 9 variants) was rechecked at its sized thickness with 4 factors requested (`results/buckling_modes_check.csv`). Reading too high by up to 0.26 % at λ 5, 0.08 % at λ 3, 0.17 % on 61 x 61 and 3.6 % at λ 8. Seven sized designs would fail with the converged value: one baseline design and six at λ 8.

Correction: `sizing.N_BUCKLE_SIZING = 4`. Baseline and the three variants rerun. The corrected record is `results/batch_all.csv` and `results/sens_*.csv`. [J] The error made the factor too high, so the Day 4-9 designs sat slightly below the threshold they were sized to: at most 0.013 % at λ 5 (L10-corners-r0.15-seismic-sa0.6: 4.9994 at 85 mm) and at most 1.4 % at λ 8 (L20-corners-r0.10-seismic-sa0.5: 7.886 at 325 mm).

### What changed in the baseline

- One thickness: L10-corners-r0.15-seismic-sa0.6 goes from 85 to 90 mm (λ 4.9994 at 85 mm). Nothing else changes.
- That cell was one of the six "seismic cheaper" artefact cells, so the baseline now reads **5 artefact cells and 37 + 42 = 79 of 84 "no meaningful difference"**, not 6 and 78. The artefact explanation is unchanged: the seismic form is 85 mm and the gravity form 90 mm because of a 0.1-0.9 % margin on the λ 5 threshold.
- Headline cells holding: 4 of 10 at 10 m (was 5), still 0 of 10 at 20 m; headline not made.
- Edge-supported shells stay at the 50 mm minimum; the lowest edge λ at 50 mm is now 14.00 (20 m, rise 0.10), was 14.98, because the old value was the too-high one.
- Every buckling factor in the tables is now lower by 0.1-0.3 % (corners) or 3-9 % (edges, where the value is far above the threshold and does not matter).

### What changed in the sensitivity runs

| Variant | Thicknesses moved vs baseline (10 m / 20 m) | Cells flipped at 10 m | Verdicts | Notes |
|---|---|---|---|---|
| λ 3 | 42 / 42 | 7 (was 8) | gravity cheaper 2, no meaningful difference 40 at 10 m | the two "gravity cheaper" cells are unchanged (55 mm: λ 3.0003 for gravity, 2.936 and 2.846 for the seismic forms) |
| λ 8 | 42 / 42 | 5 (was 6) | all no meaningful difference | 20 m corners, rise 0.10: 325 mm at 0-0.3 g, 330 mm at 0.4-0.5 g, 335 mm at 0.6 g, cost of resilience up to 1.0357 |
| 61 x 61 | 5 / 12 (17, was 20) | 5 (was 6) | all no meaningful difference | T1 at most 0.318 s |

Headline: 0 of 10 cells per span in every variant, as before. The narrative does not move.

## 4. S5 plateau table (`python -m shellform.s5`)

`results/s5_plateau.csv` (168 baseline designs), `results/s5_summary.csv` (baseline and the three variants), `results/s5_meta.json`. Tg = 0.35 s from `shellbench.seismic.TG_ANCHOR_S` (spec S4, B5; GB 50011-2010 Table 5.1.4-2 — confirm in your copy). Rule: T1 < Tg.

- **0 failures** in the baseline and in every variant (672 design-runs).
- Baseline: 10 m corners T1 0.159-0.184 s (at most 0.53 Tg); 10 m edges 0.029-0.045 s; 20 m corners 0.253-0.308 s (at most 0.88 Tg); 20 m edges 0.069-0.111 s.
- Closest to the limit: λ 3, 20 m corners, T1 0.341 s (0.97 Tg). 61 x 61: at most 0.318 s.
- **Rising branch [J]:** all 42 10 m edge designs and 28 of 42 20 m edge designs have T1 < 0.1 s, on the rising branch of the spectrum (0.45 alpha_max at T = 0, reaching alpha_max at 0.1 s; GB 50011-2010 Fig. 5.1.5). The pre-registered load uses the plateau value for every design, so for these shells the applied lateral load is larger than the spectrum gives, by up to 1 / 0.45 = 2.2 times at T → 0. The check "on the plateau" therefore holds as "at or below Tg" and is conservative for the seismic case on edge shells. It is reported, not changed: section 3 fixes the load. The paper should say this in the S5 row.

## 5. Other changes

- `results/sensitivity_meta.json` writes the baseline path with `as_posix()` and now lists the ShellBench tag of each input file, so a summary across a pin move says where each file came from (Day 9 open item).
- The sensitivity tables take the tag from the rows they summarise, not from the current pin.
- The committed Day 4-6 record files (`day04_*`, `day05_*`) are regenerated, so that `--compare-record` checks against the corrected record. `day04_sizing_*` and `_tried.json` were written from `results/batch_all.csv`, which runs the same `pipeline.size_one` (a first attempt through `scripts/day04_size_10m.py` failed after the sizing with a missing `import csv`, a leftover of the Day 8 refactor; fixed). `day05_*` were rerun by `scripts/day05_steel_carbon_10m.py` from those thicknesses: steel, concrete and carbon equal the batch values exactly (largest relative difference 0).

## 6. Tests

New `tests/test_day10.py` (9): pin, spectrum constants from ShellBench, S5 branches and pass rule, deck requests the number of buckling factors, ShellBench model matches the mesh, cross-check cases, `fe.py` against the wrapper on a small shell, sizing default of 4 factors. `tests/test_sensitivity.py` baseline verdict counts updated to 37 + 5.

## 7. Lessons

- A cross-check between two programs finds set-up errors in both: compare with the same settings, then with the settings the results used.
- A linear buckling factor from a single requested mode is not converged in CalculiX; request at least 2, and 4 for margin.
