# Numbers in the manuscript

Skill section 8. One row per number in the paper. A number without a row does not go in the paper. Values come from files at the freeze commit (10 Nov), never from memory or from this table's draft rows. The author fills the last column.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| (none yet) | | | | |

Draft rows from the sensitivity runs, refreshed on 7 Nov 2026 (Day 10: ShellBench v0.2.0, four buckling factors requested, D10-1; CalculiX 2.21 in the cloud; pre-freeze). The Day 9 values (v0.1.0, one factor) are superseded. They show where each number will come from; the values are replaced from the freeze run and only then checked by Syed. Outline: `03_sensitivity_outline.md`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Results 3.x, para A | corner carbon at λ ≥ 3: 0.735-0.812 of baseline | `results/sensitivity_reference.csv`, carbon_ratio_to_baseline, variant lam3, corners | pre-freeze, v0.2.0 | |
| Results 3.x, para A | corner carbon at λ ≥ 8: 1.219-1.294 of baseline | same, variant lam8 | pre-freeze, v0.2.0 | |
| Results 3.x, para A | lowest edge λ at 50 mm: 14.00 (20 m, rise 0.10) | `results/sensitivity_reference.csv`, buckling_factor, edges | pre-freeze, v0.2.0 | |
| Results 3.x, para A | gravity-form cost of resilience: 1.000-1.004 (λ 5), 1.000-1.003 (λ 3), 1.000-1.036 (λ 8) | `results/sensitivity_cells.csv`, cost_of_resilience_gravity | pre-freeze, v0.2.0 | |
| Results 3.x, para A | λ 8, 20 m, corners, rise 0.10: 325 → 330 → 335 mm at 0-0.3, 0.4-0.5, 0.6 g | `results/sensitivity_cells.csv`, thickness_gravity_m | pre-freeze, v0.2.0 | |
| Results 3.x, para B | verdict counts per span and variant | `results/sensitivity_summary.csv`, verdict_counts_central | pre-freeze, v0.2.0 | |
| Results 3.x, para C | λ at 55 mm, 10 m corners rise 0.20: gravity 3.0003; seismic 2.936 (0.5 g), 2.846 (0.6 g) | `results/sens_lam3_meta.json`, tried | pre-freeze, v0.2.0 | |
| Results 3.x, para D | 61 × 61: 17 of 168 thicknesses move one step; carbon ratio 1.000-1.026; T1 max 0.318 s | `results/sens_mesh61.csv`, `sensitivity_reference.csv` | pre-freeze, v0.2.0 | |
| Results 3.x, para E | headline: 0 of 10 scope cells per span under every variant | `results/sensitivity_summary.csv`, headline_cells_holding | pre-freeze, v0.2.0 | |
| S5 row of the validation table | T1 < Tg = 0.35 s for all 168 designs; baseline T1 0.029-0.308 s; longest 0.308 s (20 m corners); 0 failures in baseline and in all three variants (longest 0.341 s, λ 3, 20 m corners) | `results/s5_summary.csv`, `s5_plateau.csv` | pre-freeze, v0.2.0 | |
| S5 row, caveat | 70 of 84 edge designs have T1 < 0.1 s (rising branch, alpha 0.45-1.0 alpha_max); the plateau load is conservative for them | `results/s5_plateau.csv`, branch, alpha_shape | pre-freeze, v0.2.0 | |
| Methods, solver | `fe.py` against `shellbench.shellfe`, four gravity shells: displacement identical, first buckling factor within 0.26 % (2 factors each) | `results/fe_crosscheck.csv` | pre-freeze, v0.2.0 | |
| Methods, solver | one requested buckling factor reads high: up to 0.26 % (λ 5) and 3.6 % (λ 8) in the Day 4-9 sizing; 4 requested since 7 Nov (D10-1) | `results/buckling_modes_check.csv` | pre-freeze, v0.2.0 | |

Rules: units always; state the comparison base; ShellBench values name the tag (`src/shellform/pin.py`); code values name the clause and say "confirm in your copy".

Draft rows from the Day 11 figures (8 Nov 2026; record at ShellBench v0.2.0, pre-freeze). Outline: `07_results_outline.md`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Results 3.2, Fig. 2 | governing check: buckling 84 of 84 corner designs, t_min 84 of 84 edge designs | `figures/fig02_mechanism.json`, panels.*.governing; `results/batch_all.csv`, governing_check | pre-freeze, v0.2.0 | |
| Results 3.2, Fig. 2 | corner λ_min/λ 0.888-0.997 (10 m), 0.956-0.999 (20 m) | `figures/fig02_mechanism.json`, ratio_range.buckling | pre-freeze, v0.2.0 | |
| Results 3.2, Fig. 2 | edge buckling ratio 0.020-0.074 (10 m), 0.095-0.357 (20 m); compression at most 0.51 f_c; deflection at most 0.28 of L/300 | `figures/fig02_mechanism.json`, ratio_range | pre-freeze, v0.2.0 | |
| Results 3.2 | steel from the seismic case at most 0.82 kg (10 m corners), 0.95 kg (20 m edges), 57.9 kg (20 m corners; total 2028-2953 kg) | `results/batch_all.csv`, steel_from_seismic_kg, steel_kg | pre-freeze, v0.2.0 | |
| Results 3.3, Fig. 3 | 79 of 84 cells no meaningful difference; 5 seismic cheaper (10 m corners, rise 0.15, Sa 0.1-0.5 g) | `results/sensitivity_cells.csv` (baseline), `figures/fig03_strategy_difference.json` | pre-freeze, v0.2.0 | |
| Results 3.4, Fig. 4 | carbon ratio by driver (Sa, strategy, λ 3, λ 8, 61 x 61, band) | `figures/fig04_carbon_drivers.json`, ranges | pre-freeze, v0.2.0 | |
| Results 3.5, Fig. 5 | T1 ranges per group; all at or below Tg 0.35 s | `figures/fig05_s5_periods.json`, groups | pre-freeze, v0.2.0 | |
