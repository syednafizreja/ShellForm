# ShellForm LOG

## Day 0 — 28 Oct 2026

- Done: repository structure, pin to ShellBench v0.0.1, data contract copied to docs/, draft pre-registration, explorer skeleton with dummy data
- Result: —
- Problem: ShellBench floor-r1/r2/r3 not tagged yet (due 31 Oct, 2 Nov, 3 Nov)
- Lesson: —
- Tomorrow: Day 1, read Michiels & Adriaenssens 2017 (C&S) and approve docs/preregistration.md

## Day 1 — 29 Oct 2026

- Done (Claude, author away): reading notes `notes/michiels2017.md` from the open abstracts of the C&S 2018 and J. IASS 2017 papers (full texts not yet read); `src/shellform/checks.py` (S2 equilibrium error, S3 rotation error) and `src/shellform/design_space.py` (168 cases, results columns); 9 new tests
- Result: pytest 11 passed. Finding F1: a uniform lateral load in force density only shears the gravity form (x = x_g - Sa z_g), confirmed to 1e-12
- Problem: full texts of the Michiels papers not available yet; ShellBench Day 12 still waits on the author's carbon factors and the f_c / minimum confirmation
- Lesson: "add lateral loads" alone gives a one-directional form; the load-reversal rule must be chosen before the pre-registration is approved
- Tomorrow: Day 2, choose the reversal rule (a/b/c), fill the remaining [?] and approve docs/preregistration.md

## Day 2 — 30 Oct 2026

- Done (Claude, under the author's standing delegation): read ShellBench changes (D29 no ICE; floor-r1 is 2D); `src/shellform/formfind.py` (3D force density solver), `src/shellform/strategies.py` (thrust surfaces, envelope thickness, strategy 2 mid-surface); pre-registration approved with decisions P1-P3 and thresholds; data contract amended
- Result: pytest 25 passed. Chain parabola exact; edge-supported net centre 7.366 vs 0.0737 p L²/T = 7.37 (0.06 %). F2: on test nets strategy 2 changes t_env by < 4 %
- Problem: ICE unusable (licence); floor-r1 not a 3D solver; Michiels full texts still missing (S4)
- Lesson: four-direction shaking largely cancels the benefit of re-forming under a uniform-acceleration model; the FE bending checks will decide
- Tomorrow: Day 3, ShellBench v0.1/floor-r1 tags (31 Oct): move the pin, S1b cross-check; CalculiX shell deck for one form (static)

## Day 3 — 31 Oct 2026

- Done (Claude, under the author's standing delegation): checked ShellBench tags (only v0.0.1; v0.1 and floor-r1 not tagged), so the pin stays at v0.0.1 (stop-loss); found the cloud environment had untagged ShellBench code installed and replaced it with a clean v0.0.1 copy; `src/shellform/fe.py` (S8R deck, CalculiX static, frequency and buckling, result parsing); `scripts/day03_one_shell.py`; decision D3-1 (corner free-edge inset 0.10 x span)
- Result: pytest 31 passed. 10 m shell, rise 1.5 m, 80 mm: edge-supported λ = 680, T1 = 0.022 s; corner-supported λ = 11.8, T1 = 0.139 s, max displacement L/5760. Both below Tg = 0.35 s
- Problem: ν and density are not in ShellBench v0.0.1 (placeholders [?]); CalculiX reactions omit load lumped on fixed nodes, so equilibrium is checked on corner shells only
- Lesson: equal force densities let a corner-supported net's free edges collapse inward; the boundary force density is a design input and must be fixed before the runs
- Tomorrow: Day 4, sizing loop (thickness search against λ ≥ 5 and L/300) on the 10 m cases; mesh check

## Day 4 — 1 Nov 2026

- Done (Claude, under the author's standing delegation): ShellBench v0.1.0 tagged, pin moved (pin now checks the clone's git tag, because v0.1.0 still reports version 0.0.1); `src/shellform/inputs.py` reads E, unit weight, roof loads, f_c, f_t, f_y and factors from ShellBench in place; `fe.py` load cases (buckling, static, SLS, modes) with face stresses; `src/shellform/sizing.py`; mesh check 21/41/61; `scripts/day04_size_10m.py` sized all 84 10 m designs; decisions D4-1 to D4-4
- Result: pytest 37 passed. All 84 feasible. Corner shells 105/90/75 mm at rise 0.10/0.15/0.20, governed by buckling; edge shells at 50 mm. Thickness does not change with Sa. T1 at most 0.194 s (S5 holds)
- Problem: Poisson's ratio still not in ShellBench (results provisional); stress at corner supports is singular, so a 0.2 L zone is left out of the check and must be thickened locally
- Lesson: in this model the seismic combination never governs thickness, so the strategies can only differ through steel and support zones
- Tomorrow: Day 5, steel from tension, support-zone concrete, carbon with the ±25 % band
- Later on 1 Nov (Claude Code): ν now read in place from ShellBench's `notes/gb50010_design_values.md` (the Problem line above was wrong; same value, 0.2); D4-5 records the plan-area load basis; the 85 against 90 mm strategy difference disappears under surface-area loading. Results regenerated: no thickness changed. pytest 39 passed
- Later still on 1 Nov (Claude Code): ν_c = 0.2 confirmed in the Chinese GB 50010-2010 (2015) cl. 4.1.5, printed p. 20 (p. 19 in the English translation, so ShellBench's note is right on both). GB 50009-2012 Table 5.3.1, printed p. 18: ψq = 0.0, non-accessible roof; cl. 5.3.1 gives live load on the horizontal projection. ShellBench PR #87 merged

## Day 5 — 2 Nov 2026

- Done (Claude, under the author's standing delegation): `src/shellform/steel.py` (tension demand from face stresses, A_s = T / f_y with ρ_min, symmetry envelope for the four seismic directions, support-zone thickening), `src/shellform/carbon.py` (ShellBench factors read in place, ±25 % band), `src/shellform/designs.py` (form builder shared with the Day 4 script), `scripts/day05_steel_carbon_10m.py`; decisions D5-1 to D5-5; 10 new tests
- Result: pytest 49 passed. Minimum steel (0.214 %) governs almost everywhere; the seismic case adds at most 0.82 kg of steel. Carbon 21.6-33.4 kgCO₂e/m², 81 % from concrete. Cost of resilience 1.000 (gravity), 0.942-1.014 (seismic). 36 of 42 cells "no meaningful difference"; the other 6 (corners, rise 0.15) are the 85 vs 90 mm load-basis artefact of D4-5. Headline claim not made
- Problem: every carbon factor in ShellBench is still "author to confirm" (results provisional); floor-r2 not tagged (ShellBench main has a CalculiX shell wrapper since Day 24, but no tag), so the pin stays at v0.1.0
- Lesson: for 10 m shells neither thickness nor steel responds to Sa; the 20 m run (6 Nov) is where steel may rise above the minimum
- Tomorrow: Day 6, 3 Nov: move the pin if floor-r2/floor-r3 are tagged and cross-check fe.py; otherwise start the 20 m sizing
- Later on 2 Nov (Claude Code): a second Day 5 was written on the laptop in parallel and stays unmerged on `day05-crosscheck` as a cross-check; its amendment is not the record. Same verdicts, same 0.942-1.014, edges identical, corner steel 1-3 % lower. Main's script reruns on CalculiX 2.23 to 3e-8. All six 85 mm seismic shells fall below λ 5.0 at 61 x 61 (4.935 to 4.986), a second reason the six cells are an artefact. Corner carbon here is per 100 m², but the shells cover 73.4 m²: the author's decision. Lesson: pull again just before starting a day's work, not only at session start

## Day 6 — 3 Nov 2026

- Done (Claude Code, under the author's "approve everything just finish all"): morning sync (PR #10); rebuilt the `shellform` pytest launcher, which ran `research`'s Python; `fe.plan_area` and the plan-area fix in both scripts (pre-registration amendment of 3 Nov); `--span` option in both scripts; 10 m rerun; 20 m sizing, steel and carbon; 1 new test
- Result: pytest 50 passed. 10 m after the fix: thicknesses, steel and verdicts unchanged; corner carbon 34.0-45.5 kgCO₂e/m² (was 24.9-33.4); corner T1 5-6 % lower. 20 m: all 84 feasible; edges 50 mm (t_min), corners 185-265 mm (buckling); seismic adds at most 57.9 kg of steel; carbon corners 84.7-117.3, edges 21.6-23.8 kgCO₂e/m²; 42 of 42 cells "no meaningful difference" at all band corners; cost of resilience 0.983-1.015. Headline claim not made
- Problem: carbon factors and two code clauses still need the author's reading of the official copies; floor-r2/r3 still not tagged
- Lesson: the per-m² basis was written in the pre-registration but not checked in code; check every denominator against section 6 before the freeze
- Tomorrow: Day 7, 4 Nov: test S4 (data contract schedule, 4-5 Nov) on both spans; move the pin if floor-r2/r3 are tagged

## Day 7 — 4 Nov 2026

- Done (Claude in the app, under the author's standing delegation): Day 7 locked on main first; test S4 run as the pre-registered fallback (full text of Michiels & Adriaenssens 2018 still not available): `shellform.checks.leaned_parabola`, `leaned_arch_reactions`, `support_reactions`; `scripts/day07_s4.py`; `tests/test_s4.py`; amendment of 4 Nov (case, closed form, tolerance) written before the run; `notes/day07_s4.md`
- Result: pytest 56 (52 passed, 4 CalculiX tests skipped in the cloud). S4 passes on both spans: 18 arches (rise-to-span 1/2, 1/4, 1/8 at 0.15, 0.3, 0.45 g) agree with the closed form to 3.5e-15 in position and 8.4e-15 in reactions; pre-registered case (1/4, 0.3 g) leans 0.75 m at 10 m and 1.50 m at 20 m. S4b: all 72 design shell families equal the sheared gravity form to 6.2e-16. S2 below 2.1e-11 everywhere
- Problem: S4 is now a statics check, not a reproduction of the published case; the paper must say so. floor-r2/r3 still not tagged, so the pin stays at v0.1.0
- Lesson: the windward thrust of a leaned arch vanishes at Sa ≈ L / 4f; the design rises keep it at 1.25 g or more
- Tomorrow: Day 8, 5 Nov (6-9 Nov block starts 6 Nov): sensitivity runs of section 7 (λ_LBA 3 and 8, 61 × 61 network) if the plan says so; move the pin if floor-r2/r3 or v0.3 are tagged

## Day 8 — 5 Nov 2026

- Done (Claude in the app, under the author's standing delegation): Day 8 locked on main first; `src/shellform/pipeline.py` (the Day 4 and Day 5 per-design steps, moved out of the two scripts unchanged; the scripts import them); `src/shellform/batch.py` (`python -m shellform.batch`: presets `smoke8` and `all`, filters, `--compare-record`); `src/shellform/gallery.py` (`figures/gallery_10m.png`, `gallery_20m.png`); `tests/test_batch.py`; decisions D8-1 (smoke8 = rise 0.15, Sa 0.3 g) and D8-2 (record check: text and thickness exact, numbers 1e-3) [J]; README status updated
- Result: pytest 60 passed (cloud, CalculiX 2.21). Done-when met: 8 designs from one command in 68 s, 0 mismatches against the record. All 168 through the batch runner: 0 mismatches, worst deflection 2.3e-4 (CalculiX version), steel 1.4e-10, carbon 2.7e-11. Gallery: the seismic-aware form does not move in plan; it rises near mid-edge by at most 0.72 % of span at 0.6 g (72 mm at 10 m, 144 mm at 20 m)
- Problem: ShellBench v0.3, floor-r2 and floor-r3 still not tagged, so the pin stays at v0.1.0
- Lesson: one code path for scripts, batch and freeze removes a class of "the script and the run differ" errors before the freeze
- Tomorrow: Day 9, 6 Nov: the stop-loss check passes (not behind; all 168 already run); start the section 7 sensitivity runs (λ threshold, factor band, 61 × 61 mesh) with the batch runner; move the pin if a ShellBench tag lands

## Day 9 — 6 Nov 2026

- Done (Claude in the app, under the author's standing delegation): stop-loss check (not behind; 168 of 168 on main since Day 8). Merged the paper workspace PRs #18 and #20. `src/shellform/sensitivity.py` (`python -m shellform.sensitivity`), sensitivity settings passed through `designs.py`, `sizing.py`, `pipeline.py`; `carbon.FACTOR_SET`; 7 new tests. Ran all 168 designs at λ_LBA ≥ 3, ≥ 8 and on a 61 x 61 network. Paper: `paper/03_sensitivity_outline.md` (Methods 2.9 and Results ISCT outline), draft rows in `paper/numbers.md`, notes in `00_core.md` and `01_professor_test.md`
- Result: pytest 67 passed (cloud, CalculiX 2.21). 168 of 168 feasible in every variant. Headline holds in 0 of 10 scope cells per span under every variant (baseline 5 of 10 at 10 m, all artefact cells). The six baseline "seismic cheaper" cells vanish under all three variants; λ 3 adds two "gravity cheaper" cells at 10 m rise 0.20 (one 5 mm step; λ 3.0015 against 2.938 and 2.848 at 55 mm). 20 m verdicts never change. Corner carbon 0.735-0.812 (λ 3) and 1.219-1.294 (λ 8) of baseline; gravity-form cost of resilience at most 1.036 (λ 8, 20 m, rise 0.10). 61 x 61: 20 of 168 thicknesses move one step, T1 max 0.321 s (S5 holds)
- Problem: ShellBench v0.2.0 tagged today; its factor file holds a second set, so the set is now named in code. Pin stays v0.1.0 until the freeze run
- Lesson: on 55-90 mm shells one 5 mm step is 6-9 %, larger than the 5 % band, so every verdict change in the runs is a grid step; the buckling threshold, not Sa, sets corner-shell carbon
- Tomorrow: Day 10 (7 Nov): S5 table; pin to v0.2.0 with the record check; then figures (9 Nov) and freeze (10 Nov)
