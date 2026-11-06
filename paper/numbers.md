# Numbers in the manuscript

Skill section 8. One row per number in the paper. A number without a row does not go in the paper. Values come from files at the freeze commit (10 Nov), never from memory or from this table's draft rows. The author fills the last column.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| (none yet) | | | | |

Draft rows from the Day 9 sensitivity runs (6 Nov 2026, pre-freeze, ShellBench v0.1.0, CalculiX 2.21 in the cloud). They show where each number will come from; the values are replaced from the freeze run and only then checked by Syed. Outline: `03_sensitivity_outline.md`.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| Results 3.x, para A | corner carbon at λ ≥ 3: 0.735-0.812 of baseline | `results/sensitivity_reference.csv`, carbon_ratio_to_baseline, variant lam3, corners | pre-freeze, v0.1.0 | |
| Results 3.x, para A | corner carbon at λ ≥ 8: 1.219-1.294 of baseline | same, variant lam8 | pre-freeze, v0.1.0 | |
| Results 3.x, para A | lowest edge λ at 50 mm: 14.98 (20 m, rise 0.10) | `results/sensitivity_reference.csv`, buckling_factor, edges | pre-freeze, v0.1.0 | |
| Results 3.x, para A | gravity-form cost of resilience: 1.000-1.004 (λ 5), 1.000-1.003 (λ 3), 1.000-1.036 (λ 8) | `results/sensitivity_cells.csv`, cost_of_resilience_gravity | pre-freeze, v0.1.0 | |
| Results 3.x, para A | λ 8, 20 m, corners, rise 0.10: 325 → 330 → 335 mm at 0, 0.5, 0.6 g | `results/sensitivity_cells.csv`, thickness_gravity_m | pre-freeze, v0.1.0 | |
| Results 3.x, para B | verdict counts per span and variant | `results/sensitivity_summary.csv`, verdict_counts_central | pre-freeze, v0.1.0 | |
| Results 3.x, para C | λ at 55 mm, 10 m corners rise 0.20: gravity 3.0015; seismic 2.938 (0.5 g), 2.848 (0.6 g) | `results/sens_lam3_meta.json`, tried | pre-freeze, v0.1.0 | |
| Results 3.x, para D | 61 × 61: 20 of 168 thicknesses move one step; carbon ratio 1.000-1.026; T1 max 0.321 s | `results/sens_mesh61.csv`, `sensitivity_reference.csv` | pre-freeze, v0.1.0 | |
| Results 3.x, para E | headline: 0 of 10 scope cells per span under every variant | `results/sensitivity_summary.csv`, headline_cells_holding | pre-freeze, v0.1.0 | |

Rules: units always; state the comparison base; ShellBench values name the tag (`src/shellform/pin.py`); code values name the clause and say "confirm in your copy".
