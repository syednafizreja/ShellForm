# Table 3. Validation tests and their results

Methods 2.8. Tolerances were fixed in pre-registration section 8 before any design run.

| Test | What it shows | Pass if | Result | Status |
|---|---|---|---|---|
| S1 zero lateral load | seismic-aware form at Sa = 0 equals the gravity form | machine precision | largest Δx = 0.0e+00 m (four 41 × 41 networks) | pass |
| S2 nodal equilibrium | every free node in equilibrium under gravity + 0.6 g | < 1e-9 of the load | 1.4e-11 | pass |
| S3 rotation | rotating loads and supports rotates the form | < 1e-9 | 5.4e-16 | pass |
| S4 published case (fallback) | closed-form lean of a parabolic arch under uniform horizontal acceleration | < 1e-09 | 2.1e-11 (18 arch, 72 shell cases) | pass |
| S5 plateau | first-mode period T1 of every sized design ≤ T_g | 0 failures | baseline T1 0.029-0.308 s; longest in any variant 0.341 s; 0 failures | pass |
| Solver cross-check | fe.py against shellbench.shellfe, four gravity shells | displacement and first buckling factor within 2 % | displacement 0.0e+00; buckling factor within 0.26 % | pass |

- S1-S3 recomputed by this script on the 41 × 41 baseline networks (rise 0.15, both spans and supports).
- S4: fallback case of the 4 Nov amendment; it checks the solver against a closed form, not against Michiels & Adriaenssens' published arch (`results/day07_s4_meta.json`).
- S5: `results/s5_summary.csv`; baseline and the λ 3, λ 8 and 61 × 61 runs.
- Cross-check: `results/fe_crosscheck.csv`; tolerance `crosscheck.TOLERANCE`, the 2 % ShellBench validated its wrapper to (pre-registration section 8).

Built by `python scripts/day14_paper_tables.py` from the freeze record (freeze-2026-11-09); ShellBench v0.3.0. Do not edit by hand; rerun the script.
