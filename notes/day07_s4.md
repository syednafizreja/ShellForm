# Day 7 (4 Nov 2026): test S4, closed-form lean of a parabolic arch

Written by Claude in the app, under the author's standing delegation. ShellBench tag: v0.1.0 (no ShellBench value is used; S4 is geometry and statics only).

## Why the fallback

Pre-registration section 8: S4 was to reproduce one Michiels & Adriaenssens arch (C&S 195 (2018) 85-98, rise-to-span 1/4, 0.3 g). If the full text was not available by 4 Nov, S4 becomes the closed-form lean of a parabolic arch under uniform horizontal acceleration. The full text is not in the repo or the project files, and the ResearchGate request is still open, so the fallback applies. The amendment of 4 Nov records the case, the closed form and the tolerance. They were set in the script before the run; the amendment text was written just after it.

## The closed form

A cable or arch under parallel loads, equal per unit of its plan parameter s, is a parabola whose axis is parallel to the loads. Gravity alone gives z(s) = 4 f s (L − s) / L². A horizontal acceleration Sa on the same weight tilts every load by atan(Sa), so the compression line leans into the load:

- x(s) = s − Sa z(s), z unchanged; the crown moves by Sa f.
- Support thrusts: H_g − Sa W / 2 on the windward support, H_g + Sa W / 2 on the far one, with H_g = w L² / (8 f h) (the discrete q L² / 8 f).
- Vertical reactions stay W / 2 each: each tilted load's line of action meets the support level at its own plan point s.

Code: `shellform.checks.leaned_parabola`, `leaned_arch_reactions`, `support_reactions`. Script: `scripts/day07_s4.py`. Tests: `tests/test_s4.py`.

## Results

Files: `results/day07_s4_arch.csv` (18 arches), `results/day07_s4_shells.csv` (72 shells), `results/day07_s4_meta.json`.

| Check | Worst relative error | Pass (< 1e-9) |
|---|---|---|
| Arch node positions (÷ span) | 3.5e-15 | yes |
| Arch reactions (÷ W) | 8.4e-15 | yes |
| Arch S2 equilibrium | 5.6e-13 | yes |
| S4b shells against sheared gravity form (÷ span) | 6.2e-16 | yes |
| S4b shells S2 equilibrium | 2.1e-11 | yes |

Pre-registered case, rise-to-span 1/4 at 0.3 g: crown lean 0.75 m at 10 m and 1.50 m at 20 m (Sa f, as the closed form gives). With w = 1 N per node and 39 free nodes, the thrusts are 14.15 N and 25.85 N (H_g = 20 N), and both vertical reactions are 19.5 N. The largest lean in the design shells is 2.40 m (20 m, rise 0.20, 0.6 g).

**S4 passes at the pre-registered tolerance on both spans.**

## What S4 does and does not show [J]

- It shows that the lateral-load code (loads, solver, rise scaling, reactions) agrees with statics to round-off, for arches and for every design shell family.
- It does not show that ShellForm reproduces Michiels & Adriaenssens. Their C&S method is thrust-line plus limit analysis, and their shells use dynamic relaxation (`notes/michiels2017.md`). The paper must say that S4 is the fallback of section 8.
- The closed form is exact for nodal loads at equal plan spacing, so S4 cannot detect a discretisation error. S1b (the 0.0737 membrane value) covers that.
- Observation, not a result: the windward thrust H_g − Sa W / 2 reaches zero at Sa ≈ L / (4 f). At rise-to-span 1/2 that is about 0.5 g (1.225 N left at 0.45 g). For the design rises (0.10-0.20) the limit is 1.25-2.5 g, well above the largest Sa of 0.6 g, so no design form loses its windward thrust.

## Still open

- Full texts of the Michiels papers (ResearchGate request, author). If they arrive before 10 Nov, the published arch is run as an extra check.
- ShellBench has no `floor-r2` or `floor-r3` tag (checked 4 Nov), so the pin stays at v0.1.0.
