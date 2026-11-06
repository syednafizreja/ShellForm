# paper/numbers.md: every number in the manuscript

One row per number. A number without a row does not go in the paper. Values are provisional until the post-freeze run (pre-registration section 9); refill every row from that run.

| Location | Value | Source (file, column, filter) | Commit / tag | Checked by Syed |
|---|---|---|---|---|
| 00_core 2 | 10 m corners carbon 34.3-45.5 kgCO₂e/m² | `results/day05_comparison_10m.csv`, gravity_kgco2e_m2_central, supports=corners | 3e4797b / v0.1.0 | |
| 00_core 2 | 20 m corners carbon 85.2-117.3 kgCO₂e/m² | `results/day05_comparison_20m.csv`, same | 3e4797b / v0.1.0 | |
| 00_core 2 | edges carbon 21.6-23.4 kgCO₂e/m² (both spans) | both comparison files, supports=edges | 3e4797b / v0.1.0 | |
| 00_core 2 | cost of resilience, gravity: 1.000 (10 m), 1.000-1.004 (20 m corners) | cost_of_resilience_gravity | 3e4797b / v0.1.0 | |
| 00_core 2 | cost of resilience, seismic-aware: 0.942-1.000 (10 m corners), 0.983-1.001 (20 m corners), up to 1.0146 (edges) | cost_of_resilience_seismic | 3e4797b / v0.1.0 | |
| 00_core 2 | 78 of 84 cells "no meaningful difference" | verdict_central | 3e4797b / v0.1.0 | |
| 00_core 2 | 6 cells 5.5-5.8 % seismic cheaper (10 m, corners, rise 0.15, Sa 0.1-0.6) | seismic_minus_gravity_rel_central | 3e4797b / v0.1.0 | |
| 00_core 2 | verdict identical at all four band corners, 84 of 84 | verdict_same_at_all_corners | 3e4797b / v0.1.0 | |
| 00_core 3 | zone concrete at most 1.8 % (20 m) | handoff 3 Nov, `notes/day06_20m.md` | main | |
