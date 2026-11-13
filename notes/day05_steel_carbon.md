# Day 5: steel, support zones and carbon of the 10 m designs (2 Nov 2026)

ShellBench tag: v0.1.0. Script: `scripts/day05_steel_carbon_10m.py`. Results: `results/day05_steel_carbon_10m.csv` (84 rows), `results/day05_comparison_10m.csv` (42 rows, the decision rules of pre-registration section 7) and `results/day05_meta.json` (inputs, factors and their status). Code: `src/shellform/steel.py`, `src/shellform/carbon.py`. Run in the cloud on CalculiX 2.21; on 3 Nov the result files were regenerated on the laptop (CalculiX 2.23) with the plan-area fix, see `notes/day06_20m.md`; the thicknesses are Day 4's, read from `results/day04_sizing_10m.csv`.

**Status: provisional.** Every carbon factor row in ShellBench's `data/carbon_factors.csv` is marked "author to confirm" (see "For the author" below). The paper's results come from one run after the 10 Nov freeze.

## Method (decisions D5-1 to D5-5, pre-registration amendment of 2 Nov)

Each design is rerun at its sized thickness under every ULS load case (ULS gravity; ULS seismic +x when Sa > 0). For every S8R element:

1. **Bar directions** (D5-1) [J]: two orthogonal directions along the grid lines (in plan, x and y).
2. **Tension demand** (D5-2): at each depth, σ_nn + |τ_12| (tension positive), the orthogonal reinforcement rule for in-plane stress (EN 1992-1-1:2004 informative Annex F, F.1, expressions (F.2) and (F.3), valid for σEdx ≤ |τEdxy| with compression positive [check; page TBD from licensed copy]), applied layer by layer between the two faces. T = the integral of its positive part over the thickness; A_s = T / f_y. The Annex F relief where σEdx > |τEdxy| (then f'tdx = 0 and f'tdy = τ²/σEdx − σEdy) is not taken (conservative) [J]. Correction of 7 Nov: this line said "biaxial compression" before; the annex's condition is σEdx > |τEdxy|.
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

- **Carbon factors:** confirm the four rows of ShellBench `data/carbon_factors.csv` in your official copy of GB/T 51366-2019, Table D.0.1, and fill in the printed page. The assistant did not write or change any factor. When you confirm them in ShellBench, rerun `python scripts/day05_steel_carbon_10m.py` in env `shellform` after the pin moves; nothing in ShellForm needs editing.
- **Annex F rule:** confirm EN 1992-1-1:2004 Annex F, expressions (F.2) and (F.3), in a copy of the Eurocode. If you prefer a GB-only basis, the rule is also the plain membrane yield rule; the steel would not change at 10 m, because the minimum governs; at 20 m it would matter (up to 283.5 kg above the minimum, `notes/day06_20m.md`).
- **ρ_min:** GB 50010 Table 8.5.1 note 2 checked 3 Nov 2026 by the assistant in the author's copy (`Downloads\GB50010-2010(2015版)  混凝土结构设计规范.pdf`, printed p. 109, PDF page 124): note 2 says slab-type flexural members (not cantilever slabs) with 400 or 500 MPa bars may use the larger of 0.15 and 45 f_t/f_y (%); notes 4-5 take the ratio on the gross section. ShellBench cites p. 101-102, which is a different printing. ShellBench's `notes/gb50010_design_values.md` gives 0.20 % as the fixed term for flexural members, and `docs/floor_concept.md` gives 0.15 % for slabs; both give 0.214 % here, because 45 f_t / f_y governs.

## Laptop cross-check (2 Nov, laptop session)

A second Day 5 was written on the laptop at the same time, without sight of this one. It is kept unmerged on branch `day05-crosscheck` (commit `4f8f5ba`, script `scripts/day05_carbon_10m.py`), like `day04-crosscheck`. Its pre-registration amendment is on that branch only and is not the record. Both use the Day 4 thicknesses and `fe.py`, so this checks the steel, zone and carbon steps, not the analysis.

- **Rerun on CalculiX 2.23:** `scripts/day05_steel_carbon_10m.py` reproduces every number here to 3e-8 (relative) or better. The committed results stay as they are.
- **Steel rule:** the branch uses tensile resultants from sorted in-plane principals, with no σ_nn + |τ_12| term. Edge shells match exactly. On corner shells its steel is 1.2 to 3.2 % lower and total carbon 0.2 to 0.6 % lower.
- **Verdicts:** the same 6 cells at all four band corners, and the same resilience range, 0.942 to 1.014. The verdicts do not depend on which steel rule is used.
- **Mesh:** at 61 x 61 all six 85 mm seismic shells fall below the limit of 5.0: λ = 4.971, 4.986, 4.986, 4.973, 4.953, 4.935 at Sa 0.1 to 0.6, against 5.008 to 5.061 at 41 x 41 (branch file `results/day05_mesh_check.csv`). They would take 90 mm. So the six cells are an artefact on two separate grounds: the load basis (D4-5) and the mesh. The second does not depend on the first.
- **Plan area of corner shells:** this note divides by 100 m², but the corner shells cover 73.4 m² (D3-1 insets the edges). Per covered m², corner carbon is about 1.36 times the figures above: 34 to 45 kgCO₂e/m², not 25 to 33. Strategy verdicts and resilience ratios do not change, because the denominator is the same within each support type. The comparison of corners with edges does change. Changing the basis needs a dated amendment, so it is the author's decision [J]. **Resolved 3 Nov 2026:** this was a code error against pre-registration section 6; the amendment of 3 Nov corrects it, and the regenerated 10 m results give corners 34.0-45.5 kgCO₂e/m² (`notes/day06_20m.md`, section 1).

