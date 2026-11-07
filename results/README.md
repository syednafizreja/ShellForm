# results

Every file here is written by a script in the repo and names the ShellBench tag it used. `results/tmp/` is git-ignored.

- `day04_sizing_10m.csv`, `day04_sizing_10m_tried.json`: Day 4 thickness sizing (provisional).
- `day05_steel_carbon_10m.csv`, `day05_comparison_10m.csv`, `day05_meta.json`: Day 5 steel, support zones and carbon (provisional until the author confirms ShellBench's carbon factors).
- `day04_sizing_20m.csv`, `day04_sizing_20m_tried.json`, `day05_steel_carbon_20m.csv`, `day05_comparison_20m.csv`, `day05_meta_20m.json`: Day 6, the same for the 20 m designs (provisional).
- `day07_s4_arch.csv`, `day07_s4_shells.csv`, `day07_s4_meta.json`: Day 7, test S4 (fallback, closed-form lean of a parabolic arch) and S4b on the design shells. Passes.
- `batch_smoke8.csv`, `batch_smoke8_meta.json`: Day 8, 8 designs run by `python -m shellform.batch --compare-record` (done-when check); 0 mismatches against the record.
- `batch_all.csv`, `batch_all_meta.json`: Day 8, all 168 designs through the batch runner, checked against the Day 4-6 record.
- `sens_lam3.*`, `sens_lam8.*`, `sens_mesh61.*`: Day 9, all 168 designs at λ_LBA ≥ 3, at λ_LBA ≥ 8 and on a 61 x 61 network (`python -m shellform.sensitivity --run ...`; pre-registration section 7).
- `sensitivity_summary.csv`, `sensitivity_cells.csv`, `sensitivity_reference.csv`, `sensitivity_meta.json`: Day 9 tables against the baseline `batch_all.csv` (`python -m shellform.sensitivity --summarise`).
- `batch_pinmove_v020.*`: Day 10, all 168 designs rerun at ShellBench v0.2.0 with the Day 4-9 settings (one buckling factor requested): 0 mismatches against the Day 4-6 record. Evidence for the pin move.
- `batch_all.*`, `sens_*`, `sensitivity_*`, `day04_*`, `day05_*`: rewritten on 7 Nov (Day 10) with four buckling factors requested (pre-registration D10-1). These are the record from 7 Nov.
- `s5_plateau.csv`, `s5_summary.csv`, `s5_meta.json`: Day 10, test S5 (`python -m shellform.s5`). 0 failures.
- `fe_crosscheck.csv`, `fe_crosscheck_meta.json`: Day 10, `fe.py` against ShellBench's `shellfe` on four gravity shells (`python -m shellform.crosscheck`).
- `buckling_modes_check.csv`: Day 10, near-threshold designs rechecked with four buckling factors (the measurement behind D10-1; `python -m shellform.crosscheck --modes`).
