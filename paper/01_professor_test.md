# Professor-mode test of the paper (review notes)

Added 6 Nov 2026 alongside `00_core.md`. The assistant's notes [J], not paper text: they test the plan before writing (academic-manuscript-workflow, sections 1 and 2). Numbers quoted are from the pre-freeze record on main (3e4797b, ShellBench v0.1.0) and are provisional; the paper takes numbers only from `numbers.md` rows filled at the freeze run.

Pre-freeze numbers used below (from `results/day05_comparison_10m.csv` and `_20m.csv`): carbon 34.3-45.5 kgCO₂e/m² (10 m corners), 85.2-117.3 (20 m corners), 21.6-23.4 (edges, both spans); cost of resilience 1.000 at 10 m and 1.000-1.004 at 20 m for the gravity strategy; seismic-aware edge forms up to 1.4 % more carbon from extra surface area; verdicts identical at all four band corners in 84 of 84 cells.

## 1. Hostile Reviewer 2: the points to answer before writing

| # | Objection | Answer or action |
|---|---|---|
| R2-1 | "Trivial: stiff, short-period shells under equivalent static load were never going to be seismic-governed." | The paper's value is the number and the mechanism, with the conditions under which it breaks. Show the margin: how far is the seismic demand from governing (steel_from_seismic_kg, λ at design thickness)? Day 9 sensitivity (λ_LBA 3 and 8, 61 x 61) shows whether it flips. [J] Consider a stated "break-even" Sa or span at which seismic first governs, if the code can find one inside pre-registered ranges. |
| R2-2 | "Linear elastic, equivalent static, no vertical action, no ductility or cracking." | List as limitations, each with the data that removes it (section 4). Vertical action is excluded in the pre-registration; adding it now needs a dated amendment and is a judgement for Syed. |
| R2-3 | "The 6 'seismic cheaper' cells are reported as an artefact by the authors themselves. Why trust the other 78?" | Report both grounds (load basis and mesh) in Results, and show that the 78 do not sit near a 5 mm step. [J] a short table of λ margin above 5 for all designs would answer it. |
| R2-4 | "Strategy 2 is your own definition (midrange of four thrust surfaces), not Michiels'." | Say so in Methods, cite P1 and the 30 Oct amendment, and say S4 is the closed-form fallback, not a reproduction (handoff 4 Nov, open item 5). |
| R2-5 | "Carbon under one factor set only." | The project goal says "both factor sets", but pre-registration P3 dropped ICE (licence). Methods must say GB/T 51366-2019 plus a ±25 % band, and why. Do not write "two factor sets". |
| R2-6 | "Why C&S? This is a design-space study, not a computational method." | See section 3. |
| R2-7 | "Support zones (D4-2) and the boundary pull-in (D3-1) are judgements that drive the corner results." | Both are pre-registered amendments written before the runs. Report the zone concrete share (at most 1.8 % at 20 m) and keep D3-1 = 0.10 L visible in Methods. |

## 2. Gap search still owed (Syed, before the Introduction)

Documented search in two or three databases (OpenAlex, Lens, Scopus via library), with field vocabulary: "seismic form finding" shell, "lateral load" funicular shell, "thrust network" seismic, "embodied carbon" concrete shell, "form-found" shell "earthquake". Forward and backward snowballing from Michiels & Adriaenssens (C&S 2018, IASS 2017). Gap matrix (2020-2026 open access, as ShellBench's rule). The gap line in `00_core.md` section 1 stays a draft until this is done. The Michiels full texts are still missing (handoff open item).

## 3. Journal fit [J, check each in the journal's own pages]

C&S publishes computational methods first. Risk: an editor reads ShellForm as an application study. To fit, Methods must carry the computational contribution: the 3D force density solver with the four-direction thrust-surface envelope, its verification (S1-S5), and the reproducible batch pipeline. Keep a backup list of three or four journals with no-APC subscription routes, checked by Syed against Scopus quartile and the Guide for Authors. The assistant has not checked APCs, quartiles or word limits, so none is stated here.

## 4. Limitations list (seed; each needs the data that removes it)

1. Linear elastic shell analysis; no cracking or creep beyond the λ_LBA ≥ 5 reduction. Removed by a geometrically and materially nonlinear analysis of a subset.
2. Equivalent static horizontal load on the plateau; no vertical action, no response history. Removed by modal response spectrum or time-history runs on a subset.
3. Square plan, two spans, uniform thickness. Removed by other plans and variable thickness.
4. A1-A3 only, one factor set with a ±25 % band. Removed by a second licensed factor set and A4-C4 stages.
5. Not validated against a built or tested shell. S4 is a closed-form fallback.
6. Support zones assumed locally thickened (D4-2).

## 5. Frozen names (decide now, never rename after submission)

- Repository and package: `ShellForm` / `shellform` (already public on GitHub; keep).
- ShellBench pin: the tag in `src/shellform/pin.py` at freeze.
- Working title: Syed to write last. Placeholder [J]: "Embodied carbon cost of seismic resilience in form-found concrete shells: gravity-only and seismic-aware form-finding compared". Check C&S title rules before final.
- Key terms, used identically everywhere: "gravity-only form-finding", "seismic-aware form-finding", "cost of resilience", "factor band", "plateau spectral acceleration Sa".

## 6. Figure and table plan (one per question)

| No. | Question it answers | Source | Status |
|---|---|---|---|
| Fig 1 | What are the two strategies? (gravity form, thrust surfaces, midrange) | new script from `strategies.py` | to build |
| Fig 2 | What do the forms look like? | `figures/gallery_10m.png`, `gallery_20m.png` | exists |
| Tab 1 | Design space and checks | pre-registration sections 3 and 5 | text |
| Tab 2 | Verification S1-S5 with errors | `results/day07_s4_*`, tests | to tabulate |
| Fig 3 | Cost of resilience against Sa, per span and support | `results/day05_comparison_*.csv` | to build |
| Fig 4 | Which check governs thickness and steel | `results/batch_all.csv` (governing_check, steel_above_min_kg) | to build |
| Fig 5 | Sensitivity: λ 3/8, mesh 61, factor band | Day 9 runs | Day 9 |
| Tab 3 | Strategy verdicts at all band corners | `day05_comparison_*.csv` | to tabulate |

## 7. Next writing steps (inside-out)

1. Syed writes the gap, contribution and headline lines in `00_core.md`.
2. Methods skeleton (bullets, not prose) from the pre-registration and notes; Syed writes the prose.
3. Results after the freeze run, ISCT per figure, numbers only from `numbers.md`.
4. Discussion, Introduction (after the gap search), Conclusion, Abstract, Highlights, Title.

## 8. Day 9 update (6 Nov 2026)

R2-1 and R2-3 now have numbers from the sensitivity runs; see the last section of `03_sensitivity_outline.md`. New Reviewer 2 point [J]: R2-8 "Your 5 % band is smaller than one 5 mm thickness step on a 55 to 90 mm shell (6 to 9 %), so verdicts near a step are noise." Answer: report λ at the sized thickness and the step below for every corner design (in `results/*_meta.json`, "tried"), and show that every verdict change in the sensitivity runs is a step effect of this kind.
