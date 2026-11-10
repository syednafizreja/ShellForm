# Methods: bullet skeleton (not prose)

The author writes the prose (skill ground rule 1). This skeleton gives the order and points each item to where its facts live. Every number in the final text needs a row in `numbers.md`. Order follows a reader who wants to rebuild the study.

## 2.1 Overview and pre-registration
- Research question: `docs/preregistration.md` section 1.
- Pre-registered 30 Oct 2026, before any design-space run; amendments dated (list them in a table or appendix, with why).
- Code: ShellForm repository, freeze commit (section 9), pinned to ShellBench tag (`src/shellform/pin.py`; v0.3.0 from 8 Nov 2026). Zenodo DOI 10.5281/zenodo.24084111 (ShellForm v0.1.0; concept DOI 10.5281/zenodo.24084110, `CITATION.cff`). One command per output: `python -m shellform.batch --preset all`, `python -m shellform.sensitivity`, `python -m shellform.s5`, `python scripts/day11_figures.py`.

## 2.2 Design space
- 168 designs: table of prereg section 3 (`src/shellform/design_space.py`).
- Square plan, two spans, two support types, three rises, two strategies, seven Sa levels.
- Corner-supported free-edge inset 0.10 × span (D3-1) and why.

## 2.3 Form-finding
- Own 3D force density solver (`src/shellform/formfind.py`); 41 × 41 network.
- Thrust surfaces under gravity + Sa: the shear result F1 (`notes/michiels2017.md`).
- Strategy 1: gravity form. Strategy 2: midrange of four thrust surfaces at target rise (P1, midrange amendment). Fig. 1 = `figures/gallery_*` (list and questions: `07_results_outline.md`).
- t_env reported, not used to size (prereg section 5).

## 2.4 Structural analysis
- CalculiX S8R deck (`src/shellform/fe.py`); name the CalculiX version the freeze run records in `results/batch_all_meta.json` ("calculix"); cloud runs use 2.21, the laptop 2.23, and the record check shows the two agree (largest difference: deflection 2.3e-4 relative, Day 8).
- Cross-check against ShellBench's own CalculiX wrapper (`shellbench.shellfe`): displacement identical, first buckling factor within 0.26 % (`results/fe_crosscheck.csv`); four buckling factors requested in sizing (D10-1) and why.
- Loads and combinations: prereg section 4, D4-5 (plan-area basis, GB 50009 cl. 5.3.1), D4-1 (+x stands for four directions).
- Material values imported from ShellBench, with code clauses.

## 2.5 Checks and sizing
- Table of prereg section 5, with D4-2 (support zones), D4-3 (characteristic combination as upper bound), D4-4 (bisection).
- Steel: D5-1 to D5-5 (`src/shellform/steel.py`).

## 2.6 Carbon
- A1-A3, GB/T 51366-2019 factors read from ShellBench; ±25 % band, four corners (P3); per m² of plan area (3 Nov amendment). Factor status read from ShellBench's file (`carbon.factor_status`): at v0.3.0 the official-copy check is recorded as closed (6 Nov 2026), so the carbon numbers are no longer provisional on that account.
- One factor set only (GB/T 51366) with the band. Say why ICE is not used (licence, P3). Never "both factor sets", even though the 28 Oct project goal says so.

## 2.7 Decision rules
- Prereg section 7, quoted as written before results.

## 2.8 Validation
- S1-S5 table with tolerances set in advance; S4 fallback (4 Nov amendment) and what it does not show.
- Mesh sensitivity at 61 × 61 and buckling factor 3 and 8 (Day 9 runs).

## 2.9 Sensitivity
- See `03_sensitivity_outline.md` (Methods bullets and the Results paragraphs, Day 9).

## 2.10 Figures and reproducibility (Day 11)
- Every figure is built by `scripts/day11_figures.py` from `results/`; each names the ShellBench tag of its record (`figures/README.md`).
- Mechanism figure (Fig. 2): demand/limit ratio of each section 5 check at the sized thickness; define each ratio once (λ_min/λ, t_min/t, σ_c/f_c outside the D4-2 zones, δ/(L/300)).
