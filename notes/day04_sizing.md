# Day 4: thickness search on the 10 m cases, and mesh check

1 Nov 2026. ShellBench tag `v0.1.0`. Decisions D4-1 to D4-7 are in the amendment of 1 Nov in `docs/preregistration.md`.

**What these numbers are.** Lower bounds on thickness, from two of the four pass/fail checks: linear buckling (λ ≥ 5) and deflection (L/300). Compression and tension are not checked yet. These are not sized designs and no carbon is computed. The 20 m span was not run. The λ = 3 and λ = 8 sensitivities were not run.

## Inputs

Read at run time by `src/shellform/sb_inputs.py`, not copied here: E, unit weight (X7), roof dead and live loads (L2, L11), load factors, g, Poisson's ratio (`notes/gb50010_design_values.md`). ψq is not in ShellBench, so deflection uses G + Q, an upper bound [?].

## Mesh check (`results/day04_mesh_check.json`)

Trial thickness 80 mm, 10 m span, rise/span 0.15. This thickness is a trial value only.

| Nodes per side | Corners, gravity form, λ_grav | Corners, seismic form (0.3 g), λ_grav | Same, λ_seis | Edges, gravity form, λ_grav | Corners, gravity form, deflection [mm] | Corners, gravity form, T1 [s] |
|---|---|---|---|---|---|---|
| 21 | 4.67 | 4.75 | 5.55 | 269 | 3.29 | 0.1785 |
| 41 | 4.29 | 4.36 | 5.08 | 258 | 4.25 | 0.1735 |
| 61 | 4.25 | 4.29 | 4.98 | 257 | 4.59 | 0.1797 |

- 41 nodes is adequate for λ: within about 1 to 2 % of 61. 21 is too coarse for corner shells.
- Deflection at point supports is not converged (it grows with refinement), but it is far below L/300 = 33 mm.
- T1 moves non-monotonically by about 3 %. It stays far below Tg (0.35 s, ShellBench B5), so the plateau applies either way.

## Sizing (`results/day04_sizing_10m.csv`)

84 cases at 41 x 41. None infeasible. λ below is the lower of the two combinations.

| Supports | Rise/span | Thickness lower bound [mm] | λ at that thickness | Largest T1 [s] | Largest deflection [mm] |
|---|---|---|---|---|---|
| Corners | 0.10 | 105 | 5.01 to 5.06 | 0.184 | 6.6 |
| Corners | 0.15 | 90 | 5.48 to 5.56 | 0.163 | 4.0 |
| Corners | 0.20 | 75 | 5.07 to 5.32 | 0.183 | 4.1 |
| Edges | 0.10 | 50 (minimum) | 67 to 77 | 0.045 | 0.3 |
| Edges | 0.15 | 50 (minimum) | 109 to 157 | 0.037 | 0.2 |
| Edges | 0.20 | 50 (minimum) | 130 to 240 | 0.035 | 0.2 |

- Buckling sets the 42 corner rows. The 42 edge rows sit at the 50 mm minimum, with λ far above 5, so no check sets them.
- One step below the result (5 mm thinner), λ is at most 4.94 on every corner row, so each corner thickness is the true first pass.
- 61 x 61 on the six corner cases at r 0.15: all stay at 90 mm. λ falls from 5.48 to 5.42, from 5.56 to 5.47 and from 5.52 to 5.43 (`results/day04_sizing_10m_grid61.csv`).

## What it shows [J]

1. **Thickness does not respond to Sa or to strategy.** Within each support and rise, every row has the same thickness, for both strategies and for all Sa from 0 to 0.6 g.
2. **Gravity governs buckling.** λ_seismic is below λ_gravity in only 2 of 84 rows (edges, r 0.20, gravity form, Sa 0.5 and 0.6), and those two are at the minimum thickness regardless.
3. **So Day 4 shows no cost of resilience and no strategy difference.** Any such effect can only come from the compression and tension checks. This must not be read as a conclusion of the study. It is a result of two checks out of four.
4. **t_env is much larger than these thicknesses.** At r 0.15, corners: 213 mm at 0.3 g and 422 mm at 0.6 g for the gravity form, 216 mm and 444 mm for the seismic form. t_env is reported, not checked (section 5). It is the thickness an unreinforced shell would need, so the gap is the work that reinforcement and bending must do. It also suggests the tension checks will matter.

## Not verified

- ψq (GB 50009 Table 5.3.1 [check]). L/300 clause (GB 50010 Table 3.4.3 [check]).
- `fe.py` is not cross-checked against ShellBench `floor-r2`, which is not tagged.
- Deflection is elastic, with no creep.
