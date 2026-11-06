# Day 9 (6 Nov 2026): sensitivity runs of pre-registration section 7

Written by Claude in the app, under the author's standing delegation. ShellBench tag: v0.1.0. CalculiX 2.21 (cloud). Results are provisional until the 10 Nov freeze run.

Plan line (setup guide, Fri 6 Nov): "Stop-loss check: more than 2 days behind → drop 20 m span. Run all 168 designs." Both were already met on Day 8 (all 168 through the batch runner, 0 mismatches), so Day 9 took the next item of Phase 2, the section 7 sensitivity runs (plan line of Sun 8 Nov: "Sensitivity: buckling threshold ×2, factor set, mesh density"; done when "Sensitivity table; note any flipped conclusion").

**Stop-loss check:** not behind. 168 of 168 designs are on main; the 20 m span stays.

## What changed in the code

- `src/shellform/designs.py`: `grid_n(case)` gives the network size of a case, 41 unless the case carries `grid_n`. `form()` uses it.
- `src/shellform/sizing.py`: `check_thickness` and `size_design` take `lambda_min` (default `LAMBDA_MIN` = 5).
- `src/shellform/pipeline.py`: `size_one` and `takeoff_one` pass the case's `grid_n` and `lambda_min` through. With neither key, the calculation is the same line for line as Day 8: the 60 earlier tests pass, the baseline tables below reproduce the record, and `python -m shellform.batch --compare-record` (smoke8) after the change gives 0 mismatches (largest difference 4.4e-5, deflection, the CalculiX version).
- `src/shellform/carbon.py`: `FACTOR_SET = "GBT51366"`, the default of `load_factors`. See "ShellBench v0.2.0" below.
- `src/shellform/sensitivity.py`: `python -m shellform.sensitivity --run lam3 lam8 mesh61` and `--summarise`. Writes `results/sens_<variant>.csv` and `_meta.json`, `results/sensitivity_summary.csv` (variant × span), `sensitivity_cells.csv` (variant × cell, with "flipped"), `sensitivity_reference.csv` (gravity form at Sa = 0 under each setting) and `sensitivity_meta.json`.
- `tests/test_sensitivity.py`: 7 tests (verdict rule, variants change one setting, grid size, infeasible cells kept, headline rule, baseline reproduces the record, reference table).

## Decisions (Claude, under the standing delegation) [J]

- **D9-1:** every variant runs all 168 designs, not only the headline scope named in section 7 (rise 0.15, both supports, Sa ≥ 0.2 g). It cost 17 min (λ 3), about 17 min (λ 8) and 43 min (61 × 61) on four cores, and it shows every verdict, not only the headline.
- **D9-2:** "a conclusion that flips" (section 7) is read as: any cell whose verdict changes at any band corner, or a change of headline status. Infeasible designs would get the verdict "infeasible" (none occurred).
- **D9-3:** the factor band is not rerun: its four corners are columns of every baseline row (P3). Its sensitivity is "verdict the same at all four corners", reported per variant.
- **D9-4:** ShellBench v0.2.0 was tagged today. The pin stays at v0.1.0 for Day 9 so that the variants and the baseline use the same inputs. The pin moves to v0.2.0 before the 10 Nov freeze run (see below).

## Results

| variant | 10 m verdicts (42 cells) | 20 m verdicts (42 cells) | flipped vs baseline | headline (scope cells holding, per span) |
|---|---|---|---|---|
| baseline (λ 5, 41 × 41) | 36 no meaningful difference, 6 seismic cheaper | 42 no meaningful difference | — | 5 of 10; 0 of 10 → not made |
| λ ≥ 3 | 40 no meaningful difference, 2 gravity cheaper | 42 no meaningful difference | 8; 0 | 0; 0 → not made |
| λ ≥ 8 | 42 no meaningful difference | 42 no meaningful difference | 6; 0 | 0; 0 → not made |
| 61 × 61 | 42 no meaningful difference | 42 no meaningful difference | 6; 0 | 0; 0 → not made |

Every cell of every variant has the same verdict at all four band corners (42 of 42 per span and variant). 168 of 168 designs are feasible in every variant.

**1. The six baseline "seismic cheaper" cells are an artefact, now on three grounds.** They are 10 m, corners, rise 0.15, Sa 0.1-0.6 g (85 against 90 mm). They vanish at λ 3 (both 70 mm), at λ 8 (both 110 mm) and on 61 × 61 (both 90 mm). The earlier grounds were the load basis (D4-5) and the 2 Nov 61 × 61 cross-check.

**2. The two λ 3 "gravity cheaper" cells are the same grid-step effect with the opposite sign.** 10 m, corners, rise 0.20, Sa 0.5 and 0.6 g: at 55 mm the gravity form has λ = 3.0015 and passes; the seismic-aware forms have λ = 2.938 and 2.848 and fail, so they size to 60 mm (+8.4 % and +8.2 % carbon). The underlying difference in buckling factor at equal thickness is 2.1 % and 5.1 %; the 5 mm step is 9 % of 55 mm.

**3. The buckling threshold moves carbon far more than the seismic level does** (`sensitivity_reference.csv`, gravity form at Sa = 0). Corner-supported shells: carbon 0.735-0.812 of the baseline at λ 3, 1.219-1.294 at λ 8. Example, 10 m rise 0.15: 70 / 90 / 110 mm and 31.1 / 39.8 / 48.6 kgCO₂e/m² at λ 3 / 5 / 8. Edge-supported shells stay at 50 mm under every threshold (lowest edge λ at 50 mm is 14.98, 20 m rise 0.10), so their carbon does not move. Against this, the gravity-form cost of resilience is 1.000-1.004 (λ 5), 1.000-1.003 (λ 3) and 1.000-1.036 (λ 8).

**4. Where seismic demand first sets a thickness.** λ 8, 20 m, corners, rise 0.10: the gravity form needs 325 mm up to 0.4 g, 330 mm at 0.5 g and 335 mm at 0.6 g (cost of resilience 1.018 and 1.036), because the buckling factor of the seismic combination falls below 8. This is the only place in the four runs where Sa raises the gravity form's thickness. It stays inside the 5 % band.

**5. Mesh 61 × 61.** 20 of 168 thicknesses move by one 5 mm step (6 at 10 m, 14 at 20 m); at equal thickness the corner λ moves by at most 4.7 %. Gravity-form carbon at Sa = 0 is 1.000-1.026 of the 41 × 41 value; the largest change of any single design is 6.1 % (one step). Edges do not move. T1 is at most 0.321 s (41 × 41: 0.308 s), still below Tg = 0.35 s, so S5 holds on the finer network.

**Professor-mode reading [J].** The null result is robust: no variant produces a single "seismic cheaper" cell, and the headline holds nowhere. What is sensitive is only the 10 m corner cells near a 5 mm thickness step, and every change there is a step effect between forms whose buckling factors differ by under about 5 %. The 5 % rule cannot resolve differences smaller than one thickness step on 55-90 mm shells (6-9 %); the paper must say so (R2-8 in `paper/01_professor_test.md`). The stronger finding for the Discussion is result 3: for corner-supported shells the buckling safety factor is the design choice that sets carbon, by 20-30 %, and seismic level up to 0.6 g moves it by a few per cent at most.

## ShellBench v0.2.0 (tagged 6 Nov 2026)

Checked against v0.1.0 with ShellForm's own readers: every design input (`inputs.load_inputs`), ρ_min and the GB/T 51366 factors (C40 340 kgCO₂e/m³, HRB400 2.34 kgCO₂e/kg) are identical. Two changes matter: (1) the carbon factor rows now read "checked: S. N. R. Hasib, 29 Oct 2026, third-party copy; official-copy check open", so the "author to confirm" status of ShellForm's carbon results can be updated when the pin moves; (2) the file now holds a second set (OVAL2023), so `load_factors()` without a set name would raise. `FACTOR_SET = "GBT51366"` fixes this before the move and changes nothing on v0.1.0.

## Still open

- Day 10 (7 Nov): the S5 table (plan line of 7 Nov; the factor band is already in every row), and move the pin to v0.2.0, then `python -m shellform.batch --preset all --compare-record` (expect 0 mismatches, since the inputs are identical). Figures follow on 9 Nov and the freeze on 10 Nov, as planned.
- Laptop: pull, `pip install -e . --no-deps`, `python -m pytest` (expect 67 passed with CalculiX). Optionally rerun `python -m shellform.sensitivity --summarise` (seconds); it should rewrite the four tables unchanged.
- Author: the Michiels full texts; official-copy check of the carbon factor rows; Annex F, as before.
