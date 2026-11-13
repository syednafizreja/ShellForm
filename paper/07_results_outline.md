# Results: outline and figure list (Day 11, 8 Nov 2026)

Outline only, not paper text. Syed writes the sentences (academic-manuscript-writing ground rule 1; syed-academic-voice-dna section 0). Each bullet is one paragraph's job, in ISCT order (Identify, Summarise, Compare, Transition), with the figure it rests on and the file each number comes from. All numbers were checked against the **freeze run** (9 Nov 2026, tag `freeze-2026-11-09`, ShellBench v0.3.0): the rerun gave the same values as the 7 Nov files to the last digit. Each has a row in `numbers.md`. [J] marks the assistant's judgement.

Order follows the narrative in `00_core.md` and `04_supervisor_advice.md`: the mechanism leads, the pre-registered null is the evidence, robustness and validation follow. The sensitivity paragraphs are in `03_sensitivity_outline.md` and slot in as section 3.4.

## Figure list (all built by `python scripts/day11_figures.py`)

| No. | File (figures/) | Question it answers | Record it reads |
|---|---|---|---|
| 1 | `gallery_10m.png`, `gallery_20m.png` | What do the two strategies' forms look like, and how far apart are they? | `day04_sizing_*`, `day05_steel_carbon_*`, form finder |
| 2 | `fig02_mechanism.{png,pdf}` | Which check sets the thickness, and does Sa change that? | `batch_all.csv` |
| 3 | `fig03_strategy_difference.{png,pdf}` | Pre-registered rule: is one strategy cheaper by 5 % or more? | `sensitivity_cells.csv` (baseline) |
| 4 | `fig04_carbon_drivers.{png,pdf}` | What moves carbon, and by how much compared with Sa? | `batch_all.csv`, `sensitivity_cells.csv`, `sens_*.csv` |
| 5 | `fig05_s5_periods.{png,pdf}` | Test S5: are the equivalent static loads on the plateau or conservative? | `s5_plateau.csv` |

[J] Fig. 2 is the main figure (graphical abstract candidate). Fig. 5 could move to the validation section or the supplement if the journal limits figures. Carbon tables go to the supplement (`04_supervisor_advice.md` section 3).

## 3.1 The forms (Fig. 1)

- I: the seismic-aware form is the midrange of four sheared thrust surfaces; in plan it does not move.
- S: at rise/span 0.15 it rises near mid-edge by at most 72 mm at 10 m and 144 mm at 20 m (0.72 % of span, 0.6 g); no horizontal shift (`figures/gallery_*.json`, dz_max_mm, max_horizontal_shift_mm).
- C: compare with the leaned arch of Michiels & Adriaenssens (crown lean 0.75 m at 10 m, 0.3 g, S4 fallback, `results/day07_s4_meta.json`) [J]: the four-direction envelope cancels most of the lean, which is why the two forms are so close (F2, `notes/michiels2017.md`).
- T: small form differences raise the question of whether the checks see any difference at all.

## 3.2 What sets the thickness (Fig. 2, the mechanism)

- I: demand/limit ratio of each pre-registered check at the sized thickness, for all 168 designs.
- S: corner-supported shells sit on the buckling limit in 84 of 84 designs (λ_min/λ 0.888-0.997 at 10 m, 0.956-0.999 at 20 m; below 1 only because of the 5 mm grid). Edge-supported shells sit on the 50 mm minimum in 84 of 84; their next-closest check is buckling at 0.020-0.074 (10 m) and 0.095-0.357 (20 m). Compression reaches at most 0.51 of f_c (20 m corners), deflection at most 0.28 of L/300 (`figures/fig02_mechanism.json`, ratio_range).
- C: no ratio changes with Sa in a way that moves a check onto its limit; the governing check is the same at Sa 0 and 0.6 g in every design (`batch_all.csv`, governing_check). Test `tests/test_figures.py` confirms that the named governing check is the one closest to its limit in all 168 rows.
- C (steel): minimum reinforcement governs; the seismic case adds at most 0.82 kg (10 m corners), 0.95 kg (20 m edges) and 57.9 kg (20 m corners, against 2028-2953 kg of steel in those shells) (`batch_all.csv`, steel_from_seismic_kg, steel_kg). Concrete is at least 79.9 % of carbon in every design (carbon_concrete_share, lowest in 20 m corners).
- [J] Mechanism sentence for Syed to put in his own words: thickness is set by linear buckling (corners) or the code minimum (edges), steel by the minimum ratio, and none of these depends on Sa in this range; so carbon cannot depend on Sa or on the strategy.
- T: the pre-registered comparison then tests this directly.

## 3.3 The pre-registered comparison (Fig. 3)

- I: relative carbon difference, seismic-aware minus gravity form, per (span, supports, rise, Sa) cell, against the 5 % rule (pre-registration section 7).
- S: 79 of 84 cells "no meaningful difference"; 5 cells "seismic cheaper" by 5.5-5.7 %, all 10 m corners, rise 0.15, Sa 0.1-0.5 g. Every verdict is the same at all four corners of the ±25 % factor band (`sensitivity_cells.csv`, verdict_same_at_all_corners). Headline claim not made (4 of 10 scope cells at 10 m, 0 of 10 at 20 m; `sensitivity_summary.csv`).
- C: the 5 cells are one 5 mm thickness step (90 against 85 mm) on a shell whose buckling factor sits next to the threshold; they vanish at λ 3, λ 8 and 61 × 61 (section 3.4) and under surface-area loading (D4-5). [J] Report them, label them as a grid-step artefact, and give the three independent reasons.
- T: so the size of each effect needs to be put on one scale.

## 3.4 Robustness (Fig. 4; paragraphs A-E in `03_sensitivity_outline.md`)

- I: carbon ratio range caused by each driver, on one axis.
- S: Sa moves carbon by 0.0-0.4 % for the gravity form and by -5.7 to +1.5 % for the seismic-aware form; the strategy by -5.7 to +1.4 %. The buckling threshold moves corner-shell carbon to 0.73-0.83 (λ 3) and 1.22-1.30 (λ 8) of the baseline; the 61 × 61 network by +0.2 to +6.0 % (10 m corners); the factor band by ±25 % by construction (`figures/fig04_carbon_drivers.json`).
- C: [J] the buckling threshold, a judgement that codes do not fix for shells, moves carbon five to ten times more than the seismic level does. Edge-supported shells do not respond to any driver except the factor band, because they sit on the code minimum.
- T: the validity of the equivalent static load rests on the periods, which S5 checks.

## 3.5 Validation (Fig. 5 and the S1-S5 table)

- I: S5, first-mode periods on the GB 50011 design spectrum shape read from ShellBench (Tg 0.35 s).
- S: all 168 baseline designs have T1 at or below Tg (0.029-0.308 s); 10 m and 20 m corners on the plateau; 70 of 84 edge designs on the rising branch (`figures/fig05_s5_periods.json`, `results/s5_summary.csv`).
- C: on the rising branch the spectral value is 0.61 to just under 1.0 of the plateau (alpha_shape_min 0.607 at 10 m, 0.831 at 20 m), so the plateau load used is conservative there [J]; the null is not an artefact of an under-estimated load.
- T: to the Discussion (limitations: linear buckling only, no imperfections, equivalent static load; "where the null breaks" is the next paper, `04_supervisor_advice.md`).

## Checks before Syed writes

- Numbers above agree with the freeze files (9 Nov); Syed checks the `numbers.md` rows.
- Fig. 3's factor-band bars are mostly hidden by the markers because the band moves both strategies almost equally; say so in the caption.
- Never "resilience at no carbon cost"; never "first"; "extends Michiels & Adriaenssens".
