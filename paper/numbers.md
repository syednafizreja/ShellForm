# Numbers in the manuscript

Skill section 8. One row per number in the paper. A number without a row does not go in the paper. Values come from files at the freeze tag `freeze-2026-11-09` (run 9 Nov 2026, `results/freeze_meta.json`), never from memory. The author fills the last column.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Methods, reproducibility | freeze run: 168 designs, 0 record mismatches, 168 of 168 feasible; code at tag `freeze-2026-11-09`; 9 steps, wall time 6740 s (4 workers, CalculiX 2.21) | `results/freeze_meta.json`, `results/batch_all_meta.json` | freeze-2026-11-09, ShellBench v0.3.0 | |

Rows from the sensitivity runs. **Freeze run, 9 Nov 2026 (Day 12): every value below was compared with the freeze files and agrees** (ShellBench v0.3.0, four buckling factors, D10-1; CalculiX 2.21 in the cloud). The rerun at v0.3.0 reproduced the 7 Nov files in every thickness, buckling factor, period and carbon value (largest relative difference 0); only the tag column changed. Syed checks each row. Outline: `03_sensitivity_outline.md`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Results 3.x, para A | corner carbon at λ ≥ 3: 0.736-0.812 of baseline (gravity form, Sa 0; rounded from 0.7358-0.8124, corrected 14 Nov from 0.735) | `results/sensitivity_reference.csv`, carbon_ratio_to_baseline, variant lam3, corners | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para A | corner carbon at λ ≥ 8: 1.220-1.295 of baseline (gravity form, Sa 0; rounded from 1.2197-1.2946, corrected 14 Nov from 1.219-1.294) | same, variant lam8 | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para A | lowest edge λ at 50 mm: 14.00 (20 m, rise 0.10) | `results/sensitivity_reference.csv`, buckling_factor, edges | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para A | gravity-form cost of resilience: 1.000-1.004 (λ 5), 1.000-1.003 (λ 3), 1.000-1.036 (λ 8) | `results/sensitivity_cells.csv`, cost_of_resilience_gravity | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para A | λ 8, 20 m, corners, rise 0.10: 325 → 330 → 335 mm at 0-0.3, 0.4-0.5, 0.6 g | `results/sensitivity_cells.csv`, thickness_gravity_m | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para B | verdict counts per span and variant | `results/sensitivity_summary.csv`, verdict_counts_central | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para C | λ at 55 mm, 10 m corners rise 0.20: gravity 3.0003; seismic 2.936 (0.5 g), 2.846 (0.6 g) | `results/sens_lam3_meta.json`, tried | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para D | 61 × 61: 17 of 168 thicknesses move one step; carbon ratio 1.000-1.026; T1 max 0.318 s | `results/sens_mesh61.csv`, `sensitivity_reference.csv` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.x, para E | headline: 0 of 10 scope cells per span under every variant | `results/sensitivity_summary.csv`, headline_cells_holding | freeze-2026-11-09, ShellBench v0.3.0 | |
| S5 row of the validation table | T1 < Tg = 0.35 s for all 168 designs; baseline T1 0.029-0.308 s; longest 0.308 s (20 m corners); 0 failures in baseline and in all three variants (longest 0.341 s, λ 3, 20 m corners) | `results/s5_summary.csv`, `s5_plateau.csv` | freeze-2026-11-09, ShellBench v0.3.0 | |
| S5 row, caveat | 70 of 84 edge designs have T1 < 0.1 s (rising branch, alpha 0.61-0.95 alpha_max; corrected 14 Nov from 0.45-1.0, the file gives 0.607-0.946); the plateau load is conservative for them | `results/s5_plateau.csv`, branch, alpha_shape | freeze-2026-11-09, ShellBench v0.3.0 | |
| Methods, solver | `fe.py` against `shellbench.shellfe`, four gravity shells: displacement identical, first buckling factor within 0.26 % (2 factors each) | `results/fe_crosscheck.csv` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Methods, solver | one requested buckling factor reads high: up to 0.26 % (λ 5) and 3.6 % (λ 8) in the Day 4-9 sizing; 4 requested since 7 Nov (D10-1) | `results/buckling_modes_check_pre_d10.csv` (before the fix); `results/fe_crosscheck_meta.json`, modes_check (after: 173 rechecked, 0 would fail) | freeze-2026-11-09, ShellBench v0.3.0 | |

Rules: units always; state the comparison base; ShellBench values name the tag (`src/shellform/pin.py`); code values name the clause and say "confirm in your copy".

Rows from the Day 11 figures, rebuilt from the freeze files on 9 Nov 2026 (figures now name v0.3.0). Outline: `07_results_outline.md`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Results 3.2, Fig. 2 | governing check: buckling 84 of 84 corner designs, t_min 84 of 84 edge designs | `figures/fig02_mechanism.json`, panels.*.governing; `results/batch_all.csv`, governing_check | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.2, Fig. 2 | corner λ_min/λ 0.888-0.997 (10 m), 0.956-0.999 (20 m) | `figures/fig02_mechanism.json`, ratio_range.buckling | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.2, Fig. 2 | edge buckling ratio 0.020-0.074 (10 m), 0.095-0.357 (20 m); compression at most 0.51 f_c; deflection at most 0.28 of L/300 | `figures/fig02_mechanism.json`, ratio_range | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.2 | steel from the seismic case at most 0.82 kg (10 m corners), 0.95 kg (20 m edges), 57.9 kg (20 m corners; total 2028-2953 kg) | `results/batch_all.csv`, steel_from_seismic_kg, steel_kg | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.3, Fig. 3 | 79 of 84 cells no meaningful difference; 5 seismic cheaper (10 m corners, rise 0.15, Sa 0.1-0.5 g) | `results/sensitivity_cells.csv` (baseline), `figures/fig03_strategy_difference.json` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.4, Fig. 4 | carbon ratio by driver (Sa, strategy, λ 3, λ 8, 61 x 61, band) | `figures/fig04_carbon_drivers.json`, ranges | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.5, Fig. 5 | T1 ranges per group; all at or below Tg 0.35 s | `figures/fig05_s5_periods.json`, groups | freeze-2026-11-09, ShellBench v0.3.0 | |

Rows from the manuscript tables, built 10 Nov 2026 by `python scripts/day14_paper_tables.py` from the freeze files (`paper/tables/`). The tables are the source; these rows name what the text quotes from them.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Methods 2.2, Table 1 | 168 designs (2 × 2 × 3 × 2 × 7) | `paper/tables/table1_design_space.md`; `shellform.design_space` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Methods 2.4, Table 2 | E_c 32.5 GPa; ν 0.2; 25.0 kN/m³; SDL 1.224 kPa; live 0.5 kPa; f_c 19.1, f_t 1.71, f_y 360 MPa; γ 1.3/1.5, 1.3/1.4; T_g 0.35 s | `paper/tables/table2_inputs.md`; `shellform.inputs.load_inputs` (each row names its ShellBench source; confirm clauses in your copy) | ShellBench v0.3.0 | |
| Methods 2.6, Table 2 | C40 340 kgCO₂e/m³; HRB400 2.34 kgCO₂e/kg (GB/T 51366-2019 via ShellBench), ±25 % band | `paper/tables/table2_inputs.md`; `shellform.carbon.load_factors` | ShellBench v0.3.0 | |
| Methods 2.8, Table 3 | S1 0 m; S2 1.4e-11; S3 5.4e-16; S4 2.1e-11 (tol. 1e-9); S5 0 failures; cross-check buckling within 0.26 % (tol. 2 %) | `paper/tables/table3_validation.md` (S1-S3 recomputed by the script; S4 `day07_s4_meta.json`; S5 `s5_summary.csv`; `fe_crosscheck.csv`) | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.2, Table 4 | corner t 75-105 mm (10 m), 185-265 mm (20 m); edges 50 mm; concrete share 79.9-81.2 % | `paper/tables/table4_sized_designs.md`; `results/batch_all.csv` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.3-3.4, Table 5 | verdict counts per run and span; headline 4/10 (10 m baseline), 0/10 elsewhere; never made | `paper/tables/table5_verdicts.md`; `results/sensitivity_summary.csv` | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.1 | seismic-aware rise at 0.6 g, rise 0.15: corners 72 mm (10 m), 144 mm (20 m); edges 63 mm, 125 mm; no horizontal shift | `figures/gallery_10m.json`, `gallery_20m.json`, dz_max_mm, max_horizontal_shift_mm | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.3 | λ at 85 mm, 10 m corners rise 0.15: gravity 4.978 (fails); seismic 5.016-5.052 at 0.1-0.5 g (pass) | `results/batch_all_meta.json`, tried | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.1 | S4 arch, rise-to-span 1/4, 10 m, 0.3 g: crown lean 0.75 m | `results/day07_s4_arch.csv`, crown_lean_m | v0.1.0 (S4 run, 4 Nov) | |
| Methods 2.5; Discussion 4.3 | buckling safety factor γ 1.50-3.00 by slenderness; combined reductions implied by λ 3 / 5 / 8 at γ = 3.0: 1.0 / 0.6 / 0.375 (= 3.0 / λ, the assistant's arithmetic [J]) | Dulácska & Kollár (1995), Table 3, p. 319; `notes/buckling_threshold_sources.md` | source read 11 Nov 2026 | |
| Discussion 4.5 | accidental imperfection amplitude 1/4 to 3/4 of the wall thickness | Dulácska & Kollár (1995), p. 317 | source read 11 Nov 2026 | |

Rows for the Abstract, Highlights and Conclusions (13 Nov 2026). No new values: each is a row above, or arithmetic on one.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Highlight 4 | gravity-form carbon within 0.4 % up to 0.6 g | cost of resilience 1.000-1.004 (row "Results 3.x, para A" above), rounded | freeze-2026-11-09, ShellBench v0.3.0 | |
| Highlight 5; Results 3.4; Discussion 4.3 | corner-shell carbon moves 19 to 29 % at λ 3 or 8 (Results and Discussion said 20-30 % until 14 Nov) | 1 − 0.8124 = 0.188; 1.2946 − 1 = 0.295 (rows "Results 3.x, para A" above), the assistant's arithmetic [J] | freeze-2026-11-09, ShellBench v0.3.0 | |

Rows from the verification add-ons, 14 Nov 2026 (check window, after the freeze; not pre-registered). Run: `python scripts/day17_verification.py`, CalculiX 2.21 in the cloud. Sized thicknesses from the freeze record. Summary of every run: `results/verify_meta.json`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Methods 2.8, Results 3.6 para 2 | sphere p_cr FE vs Zoelly, finest mesh (3456 S8R): +1.96 % (R/t 50), +1.33 % (R/t 100); all five meshes at R/t 100 and the four finest at R/t 50 within 3 % (corrected 14 Nov from "three finest"; 864 elements gives 2.74 %) | `results/verify_v1_zoelly.csv`, relative_error | main after 14 Nov merge, ShellBench v0.3.0 | |
| Results 3.6 para 2 | membrane displacement stiff by 1.49 % (R/t 50), 0.75 % (R/t 100) | same, membrane_ur_fe_m / membrane_ur_closed_form_m − 1 | same | |
| Results 3.6 para 2 | sized shells R/t about 78 to 520 (circular-arc estimate R = ((L/2)² + f²)/(2f), t from the record) | `results/batch_all.csv`, the assistant's arithmetic [J] | freeze-2026-11-09 | |
| Results 3.6 para 3 | λ1 change 61 → 81 nodes: at most 0.62 % (edges), 0.21 % (corners) | `results/verify_v2_hconv.csv`; `verify_meta.json` v2 | main after 14 Nov merge, ShellBench v0.3.0 | |
| Results 3.6 para 3 | record λ1 above the 81 × 81 value, corners: 0.8-1.0 % (gravity-only), 1.6 % (seismic-aware) | `results/verify_v2_hconv.csv`, buckling_factor at n 41 and 81 | same | |
| Results 3.6 para 3 | corner SLS deflection change 61 → 81: 3.8-5.8 %; edges at most 1.48 %; largest δ/(L/300) on 81 × 81: 0.18 | same, sls_deflection_m, deflection_ratio | same | |
| Results 3.6 para 4, README | FDM residual below 2.5 × 10⁻¹¹ N over 84 solves (record run 2.18e-11; laptop rerun 14 Nov, CalculiX 2.23, 2.33e-11) | `results/verify_v3_fdm_residual.csv` | same | |
| Results 3.6 para 5 | membrane share: corners 76.3-89.2 %, edges 91.0-99.9 %; 10 m, rise 0.15, 0.6 g: 87.3 / 84.3 % (corners), 97.6 / 94.3 % (edges), gravity-only / seismic-aware | `results/verify_v4_energy.csv`; `figures/figS1_verification.json` panel e | same | |
| Results 3.6 para 6, Discussion 4.5 | soffit area difference at most 1.44 %; 79 of 84 verdicts safe for any formwork term; 5 grid-step cells: area difference at most 0.22 % | `results/verify_v5_formwork.csv` | same | |
| Results 3.6 para 7 (Fig. 6) | front = edge shells only; λ1 68-252 (10 m), 14-53 (20 m); 21.6-23.8 kgCO₂e/m² | `figures/fig06_carbon_stability.json` | freeze-2026-11-09 record | |

Rows added 14 Nov 2026 (check window day 2, manuscript assembly and self-review). Each value was recomputed from the named file by the assistant (script in the handoff entry of 14 Nov); Syed checks.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Methods 2.2 | equal force densities: free edge drawn in by 0.24 × span, 38 % of plan kept | `notes/day03_one_shell.md` (D3-1); pre-registration amendment of 31 Oct | before freeze (Day 3) | |
| Results 3.1 | corner-supported seismic-aware forms dip by at most 4.2 mm (20 m, 0.3 g); edge forms do not dip | `figures/gallery_10m.json`, `gallery_20m.json`, dz_min_mm | freeze-2026-11-09, ShellBench v0.3.0 | |
| Results 3.1 | edge-supported rise at 0.6 g: 63 mm (10 m), 125 mm (20 m) | same, dz_max_mm (62.6, 125.2) | same | |
| Results 3.3 | λ at 85 mm, 10 m corners rise 0.15: gravity 4.978; seismic 5.016-5.052 (0.1-0.5 g) | `results/batch_all_meta.json`, tried | same | |
| Results 3.4 | all 84 corner designs: λ 3 ratio 0.732-0.826, λ 8 ratio 1.219-1.295 (Fig. 4 bars) | `figures/fig04_carbon_drivers.json`, ranges | same | |
| Results 3.4 | seismic-aware cost of resilience −5.7 to +1.5 %; strategy −5.7 to +1.4 % | `fig04_carbon_drivers.json`; `results/sensitivity_cells.csv` (baseline rel_central −0.0567 to +0.0144) | same | |
| Results 3.4 | λ 3 cells: λ at 55 mm 3.0003 (gravity), 2.936 and 2.846 (seismic); +8.4 % and +8.2 % carbon | `results/sens_lam3_meta.json`, tried; `sensitivity_cells.csv` lam3 rel_central 0.0839, 0.0819 | same | |
| Results 3.4 | 61 × 61: corner λ at equal thickness moves at most 2.0 % | `results/sens_mesh61.csv` vs `batch_all.csv`, buckling_factor (max 0.0201) | same | |
| Results 3.6 para 3 | edge shells: record λ1 above the 81 × 81 value by up to 5.8 % | `results/verify_v2_hconv.csv` (L20-edges-r0.15-seismic-sa0.6: 0.0584) | main after 14 Nov merge | |
| Results 3.6 para 5 | seismic-aware form has the smaller membrane share in all 72 cells with Sa > 0, both ULS cases, by up to 13 points; lateral case lowers the share in 129 of 144 designs with Sa > 0, by at most 2.8 points | `results/verify_v4_energy.csv` (form difference −0.1295 to −0.0001; case difference min −0.0284) | same | |
