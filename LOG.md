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
