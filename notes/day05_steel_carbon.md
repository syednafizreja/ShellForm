# Day 5: steel, support zones and carbon of the 10 m designs (2 Nov 2026)

ShellBench tag: v0.1.0. Script: `scripts/day05_steel_carbon_10m.py`. Results: `results/day05_steel_carbon_10m.csv` (84 rows), `results/day05_comparison_10m.csv` (42 rows, the decision rules of pre-registration section 7) and `results/day05_meta.json` (inputs, factors and their status). Code: `src/shellform/steel.py`, `src/shellform/carbon.py`. Run in the cloud on CalculiX 2.21; the thicknesses are Day 4's, read from `results/day04_sizing_10m.csv`.

**Status: provisional.** Every carbon factor row in ShellBench's `data/carbon_factors.csv` is marked "author to confirm" (see "For the author" below). The paper's results come from one run after the 10 Nov freeze.

## Method (decisions D5-1 to D5-5, pre-registration amendment of 2 Nov)

Each design is rerun at its sized thickness under every ULS load case (ULS gravity; ULS seismic +x when Sa > 0). For every S8R element:

1. **Bar directions** (D5-1) [J]: two orthogonal directions along the grid lines (in plan, x and y).
2. **Tension demand** (D5-2): at each depth, σ_nn + |τ_12| (tension positive), the orthogonal reinforcement rule for in-plane stress (EN 1992-1-1:2004 Annex F, expressions (F.2) and (F.3) [check]), applied layer by layer between the two faces. T = the integral of its positive part over the thickness; A_s = T / f_y. The Annex F relief for biaxial compression is not taken (conservative) [J].
3. **Minimum steel** (D5-3): A_s ≥ ρ_min t in both directions everywhere. ρ_min = max(0.15 %, 45 f_t / f_y) = 0.214 %, the slab rule read in place from ShellBench `docs/floor_concept.md` (GB 50010 Table 8.5.1 note 2, p. 101-102 as cited there; applied to a shell [J]). Confirm the table in your copy of GB 50010.
4. **Four seismic directions** (D5-4) [J]: the +x steel field is mapped by the eight symmetries of the square (bar directions swapped where x and y swap), and the largest value is taken. This follows D4-1.
5. **Support zones** (D5-5) [J]: inside the 0.2 L corner zones of D4-2, an element whose face compression exceeds f_c is thickened to t σ_c / f_c, and the extra concrete is counted.

Steel is net: no laps, anchorage or waste [J], the same for both strategies. Carbon = concrete × C40 factor + steel × HRB400 factor, per m² of plan (100 m²), with the ±25 % band of decision P3.

Inputs read from ShellBench v0.1.0: f_y, f_t, f_c (`shellbench.checks`); C40, HRB400 and steel density 7850 kg/m³ (`shellbench.carbon`; the density is marked [J] / [?] there); factors from `data/carbon_factors.csv` with ShellBench's own reader. As read on 2 Nov: C40 340 kgCO₂e/m³ (ShellBench's interpolation between C30 and C50 [J]), HRB400 2340 kgCO₂e/t, both GB/T 51366-2019 Table D.0.1, printed page not read [?].

## Results

| Supports, rise | Strategy | t [mm] | Steel [kg/m²] | Carbon [kgCO₂e/m²], Sa 0 → 0.6 |
|---|---|---|---|---|
| Corners, 0.10 | gravity | 105 | 2.75 | 33.39 → 33.39 |
| Corners, 0.10 | seismic | 105 | 2.75 | 33.39 → 33.37 |
| Corners, 0.15 | gravity | 90 | 2.38 | 29.23 → 29.23 |
| Corners, 0.15 | seismic | 90, then 85 | 2.38 → 2.24 | 29.23 → 27.54 |
| Corners, 0.20 | gravity | 75 | 2.04 | 25.16 → 25.16 |
| Corners, 0.20 | seismic | 75 | 2.04 → 2.03 | 25.16 → 24.94 |
| Edges, 0.10 | gravity / seismic | 50 | 1.73 | 21.59 → 21.59 / 21.61 |
| Edges, 0.15 | gravity / seismic | 50 | 1.79 → 1.80 | 22.38 → 22.38 / 22.48 |
| Edges, 0.20 | gravity / seismic | 50 | 1.88 → 1.90 | 23.42 → 23.42 / 23.76 |

- **Minimum steel governs almost everywhere.** The T / f_y demand is at most 22 % of the minimum steel mass. Steel above the minimum is at most 3.8 % of a design's steel, all in the few elements at the corner supports, and all from ULS gravity.
- **The seismic case adds almost no steel.** The most it adds over ULS gravity is 0.82 kg (corners, rise 0.20, seismic form, Sa 0.6 g), against 203 kg in that shell. Without the minimum, the seismic demand would add at most 13.4 kg to a demand of 44 kg, still far below the 199 kg minimum.
- **Support zones are small.** At most 4 elements per shell are thickened (to at most 162 mm). The extra concrete is at most 0.050 m³, 0.6 % of the shell's concrete.
- **Concrete is 81 % of the carbon** in every design (80.7-81.2 %).
- **Cost of resilience** (carbon at Sa / carbon at Sa = 0): gravity strategy 1.000 everywhere (largest 1.00004); seismic strategy 0.942-1.014.
- **Which strategy is cheaper (5 % rule):** "no meaningful difference" in 36 of 42 (supports, rise, Sa) cells. In the other 6, corners at rise 0.15 with Sa 0.1-0.6, the seismic form is 5.5-5.8 % cheaper, at the central factors and at all four band corners. That difference is the 85 against 90 mm step of Day 4, which depends on the plan-area load basis (D4-5): under surface-area loading both forms take 90 mm and the gap closes. So it is not evidence of a strategy effect [J].
- **Headline claim:** not made. Section 7 needs it at rise 0.15 for both supports at every Sa ≥ 0.2 g; the edge-supported shells show no meaningful difference.
- The edge-supported seismic forms carry slightly more carbon at high Sa (at most 1.4 %, rise 0.20, Sa 0.6) because their surface area is larger, and minimum steel and concrete follow area.

## What this means [J]

For the 10 m shells, seismic resilience costs no carbon in this model. Thickness is set by buckling under ULS gravity or by the 50 mm minimum (Day 4), and steel is set by the minimum ratio. Neither responds to Sa up to 0.6 g. The seismic-aware form changes carbon only through its surface area and through grid-step effects. If the 20 m designs behave the same way, the paper's answer is "no meaningful difference", which the pre-registration allows and requires to be reported as such. The 20 m span carries more load per unit width, so T / f_y may rise above the minimum there; that run is the real test (6 Nov).

## For the author

- **Carbon factors:** confirm the four rows of ShellBench `data/carbon_factors.csv` in your official copy of GB/T 51366-2019, Table D.0.1, and fill in the printed page. Claude did not write or change any factor. When you confirm them in ShellBench, rerun `python scripts/day05_steel_carbon_10m.py` in env `shellform` after the pin moves; nothing in ShellForm needs editing.
- **Annex F rule:** confirm EN 1992-1-1:2004 Annex F, expressions (F.2) and (F.3), in a copy of the Eurocode. If you prefer a GB-only basis, the rule is also the plain membrane yield rule; the steel would not change here, because the minimum governs.
- **ρ_min:** confirm GB 50010 Table 8.5.1 note 2 (ShellBench cites p. 101-102). ShellBench's `notes/gb50010_design_values.md` gives 0.20 % as the fixed term for flexural members, and `docs/floor_concept.md` gives 0.15 % for slabs; both give 0.214 % here, because 45 f_t / f_y governs.
