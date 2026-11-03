# Day 4: thickness sizing of the 10 m designs (1 Nov 2026)

ShellBench tag: v0.1.0 (tagged 1 Nov; the pin moved from v0.0.1). Script: `scripts/day04_size_10m.py`. Results: `results/day04_sizing_10m.csv` (84 rows) and `results/day04_sizing_10m_tried.json` (every thickness tried). 41 x 41 grid, S8R. Results regenerated on CalculiX 2.23 after the ν fix of 1 Nov; the first run, on 2.21, gave the same thicknesses and governing checks. The mesh table below is from the 2.21 run.

**Status: provisional.** Steel and carbon are not computed yet (Day 5).

## Inputs (all from ShellBench v0.1.0, through `src/shellform/inputs.py`)

| Input | Value | Source in ShellBench |
|---|---|---|
| E | 3.25e10 Pa | `anchor_frame.E_KN_M2` (spec X4) |
| Unit weight | 25 kN/m³ | `docs/baseline_spec.md` X7 |
| Roof SDL | 1.224 kPa | L2 (4.224) less the 0.12 m slab in it (X7 x `carbon.SLAB_T_M`) [J] |
| Roof live | 0.5 kPa | L11 |
| f_c | 19.1 MPa | `checks.FC_N_MM2` |
| Factors | 1.3 G + 1.5 Q; 1.3 G_E + 1.4 E_h | `combinations.GAMMA_G`, `GAMMA_Q`, `GAMMA_EG_CODE`, `GAMMA_EH_CODE` |
| ψ_E roof | 0 | `seismic.LIVE_COMBINATION_COEFF_ROOF` |

## Checks of the analysis

- Face stress: a clamped 1 m plate under self-weight gives 3.323 MPa at the first element against 3.320 MPa from beam theory, and the tip deflection is within 0.03 %. This is now a test.
- Buckling step order: running BUCKLE first gives λ = 11.758 on the Day 3 shell, the same as Day 3 (11.758).
- Seismic directions: on a strategy 2 corner shell, +x, -x and +y give the same λ and stress to 0.1 % (test).

## Mesh check (10 m, rise 1.5 m, 80 mm, ULS gravity)

| Supports | n | λ | max disp [mm] | comp. outside 0.2 L [MPa] | T1 [s] |
|---|---|---|---|---|---|
| Corners | 21 | 4.77 | 4.28 | 2.18 | 0.141 |
| Corners | 41 | 4.40 | 5.52 | 2.64 | 0.137 |
| Corners | 61 | 4.36 | 5.96 | 3.01 | 0.142 |
| Edges | 21 | 289 | 0.124 | — | 0.023 |
| Edges | 41 | 284 | 0.124 | — | 0.023 |
| Edges | 61 | 273 | 0.124 | — | 0.023 |

λ, which governs the corner shells, changes by 0.9 % from 41 to 61. Stress near the corner supports does not converge (it is singular), so the check leaves out a 0.2 L zone (D4-2). The 41 x 41 grid stays.

## Results (thickness in mm)

| Supports, rise | Strategy | Sa = 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 |
|---|---|---|---|---|---|---|---|---|
| Corners, 0.10 | gravity | 105 | 105 | 105 | 105 | 105 | 105 | 105 |
| Corners, 0.10 | seismic | 105 | 105 | 105 | 105 | 105 | 105 | 105 |
| Corners, 0.15 | gravity | 90 | 90 | 90 | 90 | 90 | 90 | 90 |
| Corners, 0.15 | seismic | 90 | 85 | 85 | 85 | 85 | 85 | 85 |
| Corners, 0.20 | gravity | 75 | 75 | 75 | 75 | 75 | 75 | 75 |
| Corners, 0.20 | seismic | 75 | 75 | 75 | 75 | 75 | 75 | 75 |
| Edges, all rises | both | 50 | 50 | 50 | 50 | 50 | 50 | 50 |

- All 84 designs are feasible. Corner shells are governed by buckling under ULS gravity; edge shells sit at the 50 mm minimum.
- S5 holds: the longest T1 is 0.194 s, below Tg = 0.35 s. (3 Nov: after the plan-area fix of the T1 mass, 0.184 s; `notes/day06_20m.md`.)
- In the support zones of corner shells, compression reaches about 24-26 MPa, above f_c = 19.1 MPa. These zones need local thickening, and its concrete has to be counted.

## What this means [J]

- Thickness does not respond to Sa at all. The seismic combination (1.3 G_E vertical) is lighter than ULS gravity (1.3 G + 1.5 Q) for buckling, and the horizontal part adds little. So the sized thickness cannot separate the strategies.
- The one difference (85 against 90 mm at rise 0.15) comes from λ sitting just at the limit: 4.99 against 5.02 at 85 mm. That is a grid-step effect. It also depends on the load basis: with SDL and live load per surface area instead of plan area, the seismic form fails at 85 mm too (λ 4.947 at Sa 0.3 g) and takes 90 mm like the gravity form. It is not evidence of a strategy effect (amendment D4-5).
- Any difference in carbon between the strategies will therefore come from reinforcement (tension under the seismic case) and from the support zones. That is Day 5.

λ at rise 0.15, corners, seismic form, 41 x 41 grid (limit 5.0). Sa 0.3 is one of six rows tested; all six fail at 85 mm and pass at 90 mm under surface loading.

| Sa (g) | Plan, 85 mm | Plan, 90 mm | Surface, 85 mm | Surface, 90 mm |
|---|---|---|---|---|
| 0.1 | 5.023 | 5.653 | 4.909 | 5.528 |
| 0.2 | 5.052 | 5.683 | 4.937 | 5.557 |
| 0.3 | 5.061 | 5.693 | 4.947 | 5.569 |
| 0.4 | 5.054 | 5.687 | 4.942 | 5.565 |
| 0.5 | 5.037 | 5.671 | 4.927 | 5.551 |
| 0.6 | 5.008 | 5.645 | 4.902 | 5.529 |
## Independent cross-check

A second sizing code, written separately on 1 Nov (branch `day04-crosscheck`, commit `7d1134b`, not merged), gave the same thickness on 78 of 84 rows. The other 6 are the 85 mm rows above, at 90 mm there. It loads per surface area, smears SDL into density, and checks buckling and deflection only. Largest T1 0.184 s against 0.194 s here; largest deflection 6.6 mm against 6.54 mm.

## Open

- Day 5: steel from tension (A_s = T / f_y, at least ρ_min), support-zone concrete, carbon with the ±25 % band.
- Cross-check `fe.py` against ShellBench's CalculiX wrapper. v0.1.0 has only a cantilever smoke test (`calculix.cantilever_smoke`), so the shell cross-check waits for floor-r2.
- ψq for the quasi-permanent deflection check: GB 50009-2012 Table 5.3.1 gives 0.0 for a non-accessible roof (printed p. 18). It needs a ShellBench row before ShellForm can read it; until then D4-3 stands.
