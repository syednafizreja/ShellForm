# Day 17 (14 Nov 2026): verification add-ons V1-V5, Fig. 6 and Fig. S1

Check window, day 1. Written by Claude in the app under the author's standing delegation. The add-ons come from the "strength add-ons" the author kept from the top-1 % finishing blueprint (13 Nov), in order of reviewer value.

**What did not change.** No sizing setting (λ ≥ 5, L/300, t_min 50 mm, 5 mm steps), no ShellBench value (pin `v0.3.0`), no frozen result file and no freeze tag. Every add-on is a new output beside the record. They were added after the freeze, so they are not pre-registered (pre-registration amendment of 14 Nov 2026).

**How to rerun.** `python scripts/day17_verification.py` (about 6 min on 4 workers), then `python scripts/day17_figures.py`. Code: `src/shellform/verification.py`, `src/shellform/verify_figures.py`. Tests: `tests/test_verification.py` (24 tests). Cloud pytest: 125 passed (CalculiX 2.21).

## Results

| Add-on | Record file | Limit | Result | Verdict |
|---|---|---|---|---|
| V1 Zoelly sphere | `results/verify_v1_zoelly.csv` | < 3 % | finest mesh (3456 S8R): +1.96 % at R/t 50, +1.33 % at R/t 100 | pass |
| V2 h-convergence, λ1 | `results/verify_v2_hconv.csv` | < 1.5 % (61 → 81) | at most 0.62 % (edges), 0.21 % (corners) | pass |
| V2 h-convergence, δ_SLS | same | < 1.5 % (61 → 81) | edges at most 1.48 %; corners 3.8-5.8 % | corners fail; see below |
| V3 FDM residual | `results/verify_v3_fdm_residual.csv` | < 1e-10 N | worst 2.2e-11 N over 84 solves (laptop rerun 14 Nov: 2.3e-11 N) | pass |
| V4 membrane share | `results/verify_v4_energy.csv` | (descriptive) | corners 76.3-89.2 %, edges 91.0-99.9 % | — |
| V5 formwork bound | `results/verify_v5_formwork.csv` | (5 % rule) | formwork area differs by at most 1.44 %; 79 of 84 verdicts safe for any formwork term | — |

Summary of every run, with pass flags and wall times: `results/verify_meta.json`.

## V1. Complete sphere under external pressure

The classical buckling pressure of a complete sphere is p_cr = 2E / √(3(1 − ν²)) · (t/R)² (Hutchinson 2016, Proc. R. Soc. A 472: 20160577, Section 3, opened by Claude 14 Nov; Timoshenko & Gere 1961 not reachable without a library copy, so it is no longer cited. The name "Zoelly" is kept in file names only; the paper says "the classical value" because no opened source tied the formula to Zoelly). The blueprint called it a "spherical cap" test. We used the complete sphere, because the formula is exact for it and a cap needs a boundary condition that the formula does not have [J].

- Mesh: a cube projected to the sphere (equiangular), m × m S8R elements per face, m = 8, 12, 16, 20, 24 (384 to 3456 elements). Six translations fixed in a statically determinate way, so the pressure meets no reaction.
- Material: ShellBench's E = 32.5 GPa and ν = 0.2 (`shellform.inputs`). R = 5 m, t = 0.10 and 0.05 m.
- The deck uses the same element (S8R) and step (`*BUCKLE`) that size every ShellForm shell.
- **Sign check.** CalculiX's shell pressure `P` acts along the element normal. With outward normals, a positive `P` moved the wall outward. So external pressure is a negative `P`. The static step then moves every node inward.
- **Membrane check.** The inward displacement is within 1.49 % (R/t 50) and 0.75 % (R/t 100) of p R² (1 − ν) / (2 E t), stiff by about 0.75 t/R. This is the thickness effect of CalculiX's expansion of S8R into 20-node bricks [J]. It explains most of the +2.0 % and +1.3 % buckling offsets, which also scale with t/R.
- The error still falls slowly at m = 24 (R/t 50: 3.55, 2.74, 2.48, 2.21, 1.96 %). Every mesh at R/t 100 and the three finest at R/t 50 are inside 3 %.
- **Scope.** The sized shells have R/t of about 78 to 520 (circular-arc estimate). We did not run the sphere above R/t 100. In a trial run at R/t 25 (t = 0.2 m, m = 16), outside the range of the sized shells and of the thin-shell formula, FE was 10 % below the closed form. It is not part of the record [J].

## V2. h-convergence at the sized thickness

Eight designs: both spans and both supports, rise 0.15, gravity-only form at Sa = 0 and seismic-aware form at Sa = 0.6 g. Each is form-found again on 21, 41, 61 and 81 nodes per side (100 to 1600 S8R elements) and run through every load case at its frozen thickness. The 41 × 41 run reproduces the record λ1 to 1e-6 (asserted in the script).

- **λ1 converges.** The change from 61 to 81 is at most 0.62 %. The record (41 × 41) λ1 is above the 81 × 81 value for corner shells by 0.8-1.0 % (gravity-only form) and 1.6 % (seismic-aware form). So a corner shell sized at λ1 = 5.00-5.05 on the record network would read about 4.92-5.00 on the finest one. Both strategies are meshed alike, and the 61 × 61 sensitivity run already showed that no verdict moves (17 of 168 thicknesses move one step, carbon ratio 1.000-1.026).
- **δ_SLS does not converge at corner point supports.** It grows by 3.8 to 5.8 % from 61 to 81 nodes. The largest displacement of a corner-supported shell sits next to a point support, where the linear-elastic field is singular, so it grows with each refinement. Edge shells converge (at most 1.48 %). The deflection check never governs: at 81 × 81 the largest SLS deflection is 0.18 of L/300. So the singularity does not reach any thickness [J].

## V3. Residual of the assembled force density system

max |D x_f − (p_f − D_f x_x)| over x, y and z, with D = C_fᵀ Q C_f assembled again from the edges (independently of `formfind.solve`). Unit nodal weights (1 N), so the residual is in N and relative at once. 84 solves: 4 families × 3 rises × 7 Sa levels (the lateral load at each Sa on the scaled gravity network). Worst 2.2e-11 N. A 1 mm move of one free node gives a residual above 1e-7 N (test).

## V4. Membrane and bending shares of the strain energy

With stress linear through the thickness, the energy per unit area is t u(σ_m) + (t/3) u(σ_b), where σ_m is the mean of the two face stresses, σ_b half their difference, and u the complementary energy density. Transverse shear is left out. Every sized design, under each ULS case.

- Corner shells: 76.3-89.2 % membrane. Edge shells: 91.0-99.9 %.
- The lateral case lowers the share, more for the seismic-aware form. 10 m, rise 0.15, Sa 0.6 g: corner shells 87.3 % (gravity form) and 84.3 % (seismic-aware form); edge shells 97.6 % and 94.3 %.
- Reading [J]: both forms remain membrane-dominated under the design lateral load. The seismic-aware form, found for a band of four lateral directions, is a little less funicular for any one of them than the gravity form is for gravity, which fits the small carbon differences in Fig. 3.

## V5. Formwork (A5)

ShellBench holds no formwork factor, and ShellForm supplies none (CLAUDE.md rule 2). So the add-on asks a question that needs no factor. Add a formwork term φ · A_fw to the carbon of both strategies, with A_fw the soffit (surface) area per m² of plan and φ = F/N for any factor F and any number of reuses N (1, 5, 20 or other). Then the relative difference (C_s + φ A_s)/(C_g + φ A_g) − 1 lies between the carbon difference and the formwork-area difference, for every φ ≥ 0 (mediant inequality; tested for φ from 1e-3 to 1e4).

- The surface areas of the two strategies differ by at most 1.44 % in every cell.
- So in the 79 "no meaningful difference" cells, no formwork term can create a difference of 5 % or more.
- In the 5 grid-step cells (−5.5 to −5.7 %), a large formwork share would pull the difference towards the area difference (at most 0.22 % in those cells), that is, into the band.
- N = 1, 5 and 20 therefore change the absolute carbon, not any verdict. The absolute values need F, which the author reads from a source and adds to ShellBench first [?].

## Fig. 6: carbon against the first buckling factor

From the frozen record only (`batch_all.csv`, `sens_lam3.csv`, `sens_lam8.csv`). Corner shells at λ ≥ 3, 5, 8, joined design by design. Non-dominated front per span.

- The front is made of edge-supported shells in both spans: λ1 of 68-252 (10 m) and 14-53 (20 m) at 21.6-23.8 kgCO₂e/m², because they sit on the 50 mm minimum.
- Corner shells sit on the threshold they were sized to; each step from λ 3 to 5 to 8 costs carbon (10 m: 25.2-37.0, 34.0-45.5, 42.9-56.2 kgCO₂e/m²).
- Gravity-only and seismic-aware forms lie on top of each other. Support condition and the buckling threshold move the trade-off; the strategy does not [J].

## Open

- Resolved 14 Nov (Claude): cite Hutchinson 2016, Section 3, instead of Timoshenko & Gere. Author to confirm.
- Author: a formwork factor F with its source, if the paper should give absolute A5 values [?].
- A sphere run at R/t 200-500 needs finer meshes (more than 3456 elements); it would close the scope gap of V1.
