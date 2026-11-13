# Table 2. Material values, loads and factors

Methods 2.4 and 2.6. Every value is read from ShellBench at the pinned tag (`src/shellform/inputs.py`, `src/shellform/carbon.py`); none is typed into ShellForm (CONTRIBUTING.md rule 2).

| Quantity | Value | ShellBench source |
|---|---|---|
| Concrete elastic modulus E_c | 32.5 GPa | anchor_frame.E_KN_M2 (spec X4) |
| Poisson's ratio ν_c | 0.2 | notes/gb50010_design_values.md row ν_c (cl. 4.1.5) |
| Reinforced concrete unit weight | 25.0 kN/m³ | baseline_spec.md X7 |
| Superimposed dead load (plan) | 1.224 kPa | baseline_spec.md L2 - X7 x carbon.SLAB_T_M (G10) [J] |
| Roof live load, non-accessible (plan) | 0.5 kPa | baseline_spec.md L11 |
| Concrete design compressive strength f_c | 19.1 MPa | checks.FC_N_MM2 (X2) |
| Concrete design tensile strength f_t | 1.71 MPa | checks.FT_N_MM2 (X3) |
| Steel design yield strength f_y | 360 MPa | checks.FY_N_MM2 (X5) |
| Partial factors γ_G, γ_Q | 1.3, 1.5 | combinations.GAMMA_G, GAMMA_Q |
| Seismic combination γ_EG, γ_Eh | 1.3, 1.4 | combinations.GAMMA_EG_CODE (GB 55002-2021 cl. 4.3.2) |
| Live load share in G_E (roof) | 0 | seismic.LIVE_COMBINATION_COEFF_ROOF |
| Characteristic period T_g | 0.35 s | seismic.TG_ANCHOR_S |
| Carbon factor, C40 concrete | 340 kgCO₂e/m³ | GBT51366; data/carbon_factors.csv via carbon.load_factors(), ±25 % band |
| Carbon factor, HRB400 bar steel | 2.34 kgCO₂e/kg | GBT51366; data/carbon_factors.csv via carbon.load_factors(), ±25 % band |

- Code clauses named in the source column are as ShellBench records them; confirm each in your copy of the code (GB 50010-2010 (2015), GB 55002-2021, GB 50011-2010, GB/T 51366-2019).
- Superimposed dead load = roof dead load less the 0.12 m slab it includes [J] (inputs.py).

Built by `python scripts/day14_paper_tables.py` from the freeze record (freeze-2026-11-09); ShellBench v0.3.0. Do not edit by hand; rerun the script.
