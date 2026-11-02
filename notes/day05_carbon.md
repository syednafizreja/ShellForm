# Day 5: steel, support zones and carbon of the 10 m designs (2 Nov 2026)

ShellBench tag: v0.1.0. Script: `scripts/day05_carbon_10m.py`. Code: `src/shellform/quantities.py`. Rules: `docs/preregistration.md`, amendment of 2 Nov 2026 (D5-1 to D5-6), committed before any run. Results: `results/day05_carbon_10m.csv` (84 rows), `results/day05_strategies_10m.csv`, `results/day05_mesh_check.csv`. 41 x 41 grid, S8R, CalculiX 2.23.

**Status: provisional.** 10 m only. This note gives no headline verdict: the pre-registration needs the 20 m designs and the robustness checks first.

## Inputs (all from ShellBench v0.1.0, read in place)

| Input | Value | Source in ShellBench |
|---|---|---|
| Concrete factor | 340 kgCO2e/m³ (C40) | `load_carbon_factors`, GB/T 51366 set; C40 is an interpolation [J] |
| Steel factor | 2.34 kgCO2e/kg (HRB400) | as above |
| Steel density | 7850 kg/m³ | as above [J][?] |
| ρ_min | 45 f_t / f_y = 0.214 % (f_t 1.71 MPa, f_y 360 MPa) | rule read from `docs/floor_concept.md` by `rho_min_slab` |

ρ_min t is taken as the total per direction (D5-3). The each-face sensitivity doubles it. ShellBench's sources differ on the 0.15 % or 0.20 % floor; it does not matter here, because 45 f_t / f_y is larger than both.

## Checks

- All 84 designs reproduce Day 4 λ and compression to 1e-4. The script stops if any does not.
- The test `test_minus_x_run_matches_the_mirrored_plus_x_field` compares a real -x run with the mirrored +x field on a 21 x 21 corner shell: within 2 %. So the seismic images of D5-2 hold.
- Hand-checkable tests: uniform tension gives N / f_y; pure bending gives the stress triangle; resultants do not change with the axes; thickening scales with the stress ratio. pytest: 50 passed.

## Carbon, kgCO2e per m² of covered plan (GB/T 51366 factors)

Covered plan is 73.395 m² for corner shells and 100 m² for edge shells.

| Supports, rise | Strategy | Sa = 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 |
|---|---|---|---|---|---|---|---|---|
| Corners, 0.10 | gravity | 45.21 | 45.21 | 45.21 | 45.21 | 45.21 | 45.21 | 45.21 |
| Corners, 0.10 | seismic | 45.21 | 45.21 | 45.22 | 45.22 | 45.21 | 45.20 | 45.19 |
| Corners, 0.15 | gravity | 39.68 | 39.68 | 39.68 | 39.68 | 39.68 | 39.68 | 39.68 |
| Corners, 0.15 | seismic | 39.68 | 37.50 | 37.50 | 37.49 | 37.47 | 37.43 | 37.39 |
| Corners, 0.20 | gravity | 34.20 | 34.20 | 34.20 | 34.20 | 34.20 | 34.20 | 34.20 |
| Corners, 0.20 | seismic | 34.20 | 34.21 | 34.19 | 34.15 | 34.09 | 34.00 | 33.89 |
| Edges, 0.10 | gravity | 21.59 | 21.59 | 21.59 | 21.59 | 21.59 | 21.59 | 21.59 |
| Edges, 0.10 | seismic | 21.59 | 21.59 | 21.59 | 21.59 | 21.60 | 21.60 | 21.61 |
| Edges, 0.15 | gravity | 22.38 | 22.38 | 22.38 | 22.38 | 22.38 | 22.38 | 22.38 |
| Edges, 0.15 | seismic | 22.38 | 22.38 | 22.38 | 22.40 | 22.42 | 22.45 | 22.48 |
| Edges, 0.20 | gravity | 23.42 | 23.42 | 23.42 | 23.42 | 23.42 | 23.42 | 23.42 |
| Edges, 0.20 | seismic | 23.42 | 23.42 | 23.45 | 23.49 | 23.55 | 23.64 | 23.76 |

## Findings

1. **ρ_min governs the steel.** On the 41 x 41 grid, tension exceeds ρ_min t in one design of 84 (corners, rise 0.20, seismic, Sa 0.6), over 2.2 % of its area, with a peak of 1.13 times the minimum. So steel follows thickness and hardly responds to Sa. Steel is 1.7 to 3.6 kg/m², and 18.8 % of the carbon in every design. The Day 4 note expected steel to separate the strategies. It does not.
2. **Thickening is small.** The rule adds 0.009 to 0.050 m³ on corner shells, at most 0.63 % of the concrete, and nothing on edge shells.
3. **Cost of resilience.** The gravity form stays at 1.000 at every Sa to the precision reported. The seismic form runs from 0.942 to 1.014. The largest real rise is +1.44 % (edges, rise 0.20, Sa 0.6). The large values below 1 are the artefact in finding 5.
4. **Strategy verdicts.** At the four band corners, 144 of 168 verdicts are "no meaningful difference". The other 24 favour the seismic form: all four corners of the six rows with Sa > 0 at corners, rise 0.15 (-5.5 to -5.8 %). The verdicts are the same per m² of covered plan, per total kg, and with each-face ρ_min. All other rows lie between -0.9 % and +1.4 %.
5. **Those 24 verdicts are a grid-step artefact, not a strategy effect [J].** They come only from the 85 against 90 mm step of Day 4. Two separate checks remove it:
   - Load basis: under surface-area loading the seismic form fails at 85 mm too (D4-5).
   - Mesh: at 61 x 61 all six 85 mm shells fall below the limit of 5.0 (table below), so they would take 90 mm.

   The rules generated these numbers, so they stay in the results unchanged. The 61 x 61 robustness check of the pre-registration applies to the headline, and these rows would not pass it.

## Mesh check, corners, rise 0.15 (41 to 61 nodes per side)

| Design | t [mm] | λ 41 | λ 61 | Added concrete 41 [m³] | Added 61 | Steel 41 [kg] | Steel 61 | Peak T / ρ_min 41 | Peak 61 |
|---|---|---|---|---|---|---|---|---|---|
| Gravity, Sa 0.3 | 90 | 5.614 | 5.565 | 0.0200 | 0.0272 | 233.53 | 233.34 | 0.28 | 0.59 |
| Seismic, Sa 0.1 | 85 | 5.023 | **4.971** | 0.0231 | 0.0283 | 220.71 | 220.48 | 0.18 | 0.30 |
| Seismic, Sa 0.2 | 85 | 5.052 | **4.986** | 0.0238 | 0.0285 | 220.71 | 220.44 | 0.25 | 0.44 |
| Seismic, Sa 0.3 | 85 | 5.061 | **4.986** | 0.0245 | 0.0287 | 220.62 | 220.34 | 0.34 | 0.63 |
| Seismic, Sa 0.4 | 85 | 5.054 | **4.973** | 0.0251 | 0.0288 | 220.49 | 220.18 | 0.47 | 0.88 |
| Seismic, Sa 0.5 | 85 | 5.037 | **4.953** | 0.0255 | 0.0288 | 220.29 | 220.16 | 0.63 | 1.18 |
| Seismic, Sa 0.6 | 85 | 5.008 | **4.935** | 0.0259 | 0.0288 | 220.04 | 220.97 | 0.82 | 1.57 |

Steel moves by under 0.5 %. Added concrete moves by up to 36 %, but it stays under 0.7 % of the concrete, so the carbon does not notice. Peak tension nearly doubles, because it sits at the singular corner supports. It passes ρ_min at 61 x 61 at Sa 0.5 and 0.6, and the steel total moves by at most 0.4 %. The peak is therefore a local result, not a converged one.

## What this means [J]

- At 10 m, in this model, resilience costs almost nothing in carbon, and the seismic form saves nothing. Rise and supports decide the carbon: corners cost 34 to 45 kgCO2e/m², edges 22 to 23. This is one span in a model with no bending-based detailing rules, so it is a provisional reading.
- Steel at ρ_min on a thin shell is a lower bound. Ring beams, edge members and support details are not in the model, and they would add steel in both strategies.
- The 20 m designs are the next test of whether seismic governs anywhere.

## Open

- `scripts/day04_size_10m.py` scales T1 with SDL mass on `span**2`, not on covered plan, for corner shells. This overstates the mass, so T1 is on the long (safe) side for S5. No result changes. Fix it before the 20 m run.
- The 41 x 41 grid decides thickness for shells that sit within 1.5 % of the λ limit. The 20 m run should report how many designs are that close.
- Steel density is [J][?] and the C40 factor is an interpolation [J]; both are ShellBench's to settle.
