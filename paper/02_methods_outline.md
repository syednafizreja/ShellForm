# Methods: bullet skeleton (not prose)

The author writes the prose (skill ground rule 1). This skeleton gives the order and points each item to where its facts live. Every number in the final text needs a row in `numbers.md`. Order follows a reader who wants to rebuild the study.

## 2.1 Overview and pre-registration
- Research question: `docs/preregistration.md` section 1.
- Pre-registered 30 Oct 2026, before any design-space run; amendments dated (list them in a table or appendix, with why).
- Code: ShellForm repository, freeze commit (section 9), pinned to ShellBench tag (`src/shellform/pin.py`). Zenodo DOI [?].

## 2.2 Design space
- 168 designs: table of prereg section 3 (`src/shellform/design_space.py`).
- Square plan, two spans, two support types, three rises, two strategies, seven Sa levels.
- Corner-supported free-edge inset 0.10 × span (D3-1) and why.

## 2.3 Form-finding
- Own 3D force density solver (`src/shellform/formfind.py`); 41 × 41 network.
- Thrust surfaces under gravity + Sa: the shear result F1 (`notes/michiels2017.md`).
- Strategy 1: gravity form. Strategy 2: midrange of four thrust surfaces at target rise (P1, midrange amendment). One figure from `figures/gallery_*`.
- t_env reported, not used to size (prereg section 5).

## 2.4 Structural analysis
- CalculiX S8R deck (`src/shellform/fe.py`), version 2.23 [check which version the freeze run uses].
- Loads and combinations: prereg section 4, D4-5 (plan-area basis, GB 50009 cl. 5.3.1), D4-1 (+x stands for four directions).
- Material values imported from ShellBench, with code clauses.

## 2.5 Checks and sizing
- Table of prereg section 5, with D4-2 (support zones), D4-3 (characteristic combination as upper bound), D4-4 (bisection).
- Steel: D5-1 to D5-5 (`src/shellform/steel.py`).

## 2.6 Carbon
- A1-A3, GB/T 51366-2019 factors read from ShellBench; ±25 % band, four corners (P3); per m² of plan area (3 Nov amendment).
- One factor set only (GB/T 51366) with the band. Say why ICE is not used (licence, P3). Never "both factor sets", even though the 28 Oct project goal says so.

## 2.7 Decision rules
- Prereg section 7, quoted as written before results.

## 2.8 Validation
- S1-S5 table with tolerances set in advance; S4 fallback (4 Nov amendment) and what it does not show.
- Mesh sensitivity at 61 × 61 and buckling factor 3 and 8 (Day 9 runs).

## 2.9 Sensitivity
- See `03_sensitivity_outline.md` (Methods bullets and the Results paragraphs, Day 9).
