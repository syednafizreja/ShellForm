# Methods and Results: drafting kit (10 Nov 2026)

**Update, 10 Nov:** at Syed's request Claude has now written draft 1 of both sections in his voice: `10_methods_draft.md` and `11_results_draft.md`. Use this kit to check them: the numbers, caption facts and professor-mode risks below still apply.

For Syed's drafting days, 11-13 Nov. This file is not paper text. Your skills say you write the first rough sentences and Claude turns them into academic prose (academic-manuscript-writing, ground rule 1; syed-academic-voice-dna, section 0). So Claude has not written the Methods or Results prose. Claude has done everything around it: the tables are built from the freeze record, the outlines are checked against the freeze files, and every paragraph below has a slot for your rough sentence with its numbers next to it. [J] marks Claude's judgement.

## How to use it (about 3 hours per section)

1. For each slot below, type one or two rough sentences in your own words under "Your rough sentence". Typos and plain words are fine. Keep your order of ideas.
2. Paste the filled slots into a ShellForm thread and ask for the voice-dna pass. Claude returns prose plus a two-column list, "kept (yours)" and "changed (and why)".
3. Check every number against `numbers.md` and the table it names. Accept or reject each change.
4. Then the humanizer pass (academic-humanizer, layers 1-5) and the SKIP test: read only the first sentence of each paragraph; it must carry the argument.

Tables (all built by `python scripts/day14_paper_tables.py` from the freeze record, ShellBench v0.3.0; never edit them by hand):

| Paper | File | Section |
|---|---|---|
| Table 1 | `tables/table1_design_space.md` | Methods 2.2 |
| Table 2 | `tables/table2_inputs.md` | Methods 2.4, 2.6 |
| Table 3 | `tables/table3_validation.md` | Methods 2.8 |
| Table 4 | `tables/table4_sized_designs.md` | Results 3.2 |
| Table 5 | `tables/table5_verdicts.md` | Results 3.3, 3.4 |
| Table S1 | `tables/tableS1_all_designs.{md,csv}` | Supplement |

## Methods (section 2)

Order from `02_methods_outline.md`: a reader who wants to rebuild the study. Methods is the most factual section, so it is the easiest place to start [J].

### 2.1 Overview and pre-registration
- Point: the study was pre-registered on 30 Oct 2026, before any design run; amendments are dated and listed with reasons.
- Facts: `docs/preregistration.md` sections 1 and 9 and the amendments list; code at tag `freeze-2026-11-09`; ShellForm v0.1.0, DOI 10.5281/zenodo.24084111; ShellBench v0.3.0 (DOI for v0.3.0 [?], due with ShellBench's 11 Nov release).
- Your rough sentence:

### 2.2 Design space (Table 1)
- Point: 168 designs: 2 spans × 2 support types × 3 rises × 2 strategies × 7 Sa levels, each sized separately.
- Facts: Table 1; corner free-edge inset 0.10 × span (D3-1) and why (equal force densities let the free edges collapse inward, LOG Day 3).
- Your rough sentence:

### 2.3 Form-finding
- Point: own 3D force density solver; the seismic-aware form is the midrange of four sheared thrust surfaces, at the same rise.
- Facts: F1 (a uniform lateral load only shears the gravity form, x = x_g − Sa·z_g, confirmed to 1e-12, LOG Day 1); P1; t_env reported, not used to size. Fig. 1.
- Credit: Michiels & Adriaenssens (C&S 2018) for horizontal acceleration as a first-order seismic load. You extend their work; never "first".
- Your rough sentence:

### 2.4 Structural analysis (Table 2)
- Point: CalculiX S8R shells, static, modal and linear buckling; loads and materials read from ShellBench, never typed in.
- Facts: Table 2 (each value with its ShellBench source and code clause; confirm each clause in your copy); D4-1 (+x stands for four directions), D4-5 (plan-area load basis, GB 50009 cl. 5.3.1); four buckling factors requested (D10-1).
- Your rough sentence:

### 2.5 Checks and sizing
- Point: smallest thickness in 5 mm steps from 50 mm that passes every check in every combination.
- Facts: pre-registration section 5 table (compression ≤ f_c, steel A_s = T/f_y with ρ_min, λ ≥ 5, deflection ≤ L/300, t ≥ 50 mm); D4-2 to D4-4; steel D5-1 to D5-5.
- 11 Nov: Dulácska & Kollár 1995 and ACI 318.2-14 opened; IASS 1979 not (cited via ACI). See P1 and `notes/buckling_threshold_sources.md`.
- Your rough sentence:

### 2.6 Carbon (Table 2)
- Point: A1-A3 of concrete and steel, one factor set (GB/T 51366-2019) with a ±25 % band, four corners, per m² of plan.
- Facts: Table 2 rows for C40 and HRB400; why ICE is not used (licence, P3). Never write "both factor sets".
- Your rough sentence:

### 2.7 Decision rules
- Point: the rules were fixed before any result. Quote pre-registration section 7 as written.
- Your rough sentence:

### 2.8 Validation (Table 3)
- Point: five tests with tolerances fixed in advance, all passed, plus a cross-check against ShellBench's own CalculiX wrapper.
- Facts: Table 3. Say plainly that S4 is the closed-form fallback, not the published Michiels arch (4 Nov amendment).
- Your rough sentence:

### 2.9 Sensitivity
- Point: three runs fixed in advance (λ ≥ 3, λ ≥ 8, 61 × 61), all 168 designs each.
- Facts: `03_sensitivity_outline.md`, Methods bullets 1-3.
- Your rough sentence:

### 2.10 Reproducibility
- Point: every figure and table is rebuilt by one script from `results/`; each names its ShellBench tag.
- Facts: `scripts/day11_figures.py`, `scripts/day14_paper_tables.py`, `scripts/day12_freeze.py`.
- Your rough sentence:

## Results (section 3)

Order from `07_results_outline.md`: the mechanism leads, the pre-registered null is the evidence. Each paragraph follows ISCT (Identify, Summarise, Compare, Transition).

### 3.1 The forms (Fig. 1)
- I/S: the seismic-aware form rises near mid-edge by at most 72 mm (10 m) and 144 mm (20 m) at 0.6 g, rise 0.15; no horizontal shift.
- C: the four-direction envelope cancels most of the lean of the one-direction arch (S4 fallback, 0.75 m crown lean at 10 m, 0.3 g).
- Your rough sentence:

### 3.2 What sets the thickness (Fig. 2, Table 4)
- I/S: buckling governs all 84 corner designs, the 50 mm minimum all 84 edge designs; the governing check never changes with Sa.
- S (Table 4): corner thickness 75-105 mm (10 m) and 185-265 mm (20 m); edges 50 mm everywhere; concrete is 79.9-81.2 % of carbon; seismic steel at most 57.9 kg against 2028-2953 kg (20 m corners).
- C: so carbon has no route to depend on Sa or on the strategy. This is the mechanism sentence; write it in your words.
- Your rough sentence:

### 3.3 The pre-registered comparison (Fig. 3, Table 5)
- I/S: 79 of 84 cells no meaningful difference; 5 cells seismic cheaper by 5.5-5.7 % (10 m corners, rise 0.15, Sa 0.1-0.5 g); every verdict the same at all four band corners; headline 4 of 10 scope cells at 10 m, 0 of 10 at 20 m, so not made.
- C: the 5 cells are one 5 mm step (85 against 90 mm) next to the buckling limit; three independent reasons (load basis D4-5, 61 × 61, λ 3 and λ 8).
- Your rough sentence:

### 3.4 Robustness (Fig. 4, Table 5)
- Paragraphs A-E of `03_sensitivity_outline.md` (checked against the freeze files today).
- Key contrast: the buckling threshold moves corner-shell carbon to 0.735-0.812 (λ 3) and 1.219-1.294 (λ 8) of the baseline; Sa moves gravity-form carbon by at most 0.4 % in the baseline.
- Your rough sentence:

### 3.5 Validation of the equivalent static load (Fig. 5)
- I/S: T1 0.029-0.308 s in the baseline, all ≤ T_g = 0.35 s; 0 failures in all four runs (longest 0.341 s, λ 3).
- C: 70 of 84 edge designs sit on the rising branch, where the plateau load is conservative.
- Your rough sentence:

## Figure captions: what each must say

Captions are yours to word. Each must carry these facts so the figure stands alone [J]:

- Fig. 1: one figure per span, rise 0.15; rows = corner and edge supports; Δz = height of the seismic-aware form minus the gravity-only form [mm] at Sa 0.3 and 0.6 g; panel subtitles give t, λ and carbon; section panels drawn at vertical scale ×3; plan positions unchanged.
- Fig. 2: demand/limit ratio of each check at the sized thickness; each ratio defined once (λ_min/λ, t_min/t, σ_c/f_c outside the corner zones, δ/(L/300)); filled = gravity-only, open = seismic-aware; log scale.
- Fig. 3: relative carbon difference, seismic-aware minus gravity-only; shaded band = ±5 % rule; whiskers = range over the four factor-band corners, mostly hidden by the markers because the band moves both strategies almost equally.
- Fig. 4: carbon per m² of plan as a ratio to each driver's reference (defined in `shellform.figures.driver_ranges`; state it in words); shaded band = ±5 %; panels by support type.
- Fig. 5: GB 50011 design spectrum shape read from ShellBench; T_g = 0.35 s; every baseline design.

## Professor-mode check of the plan (research-method-playbook; Reviewer 2 at Computers & Structures)

Ranked by risk to acceptance [J]. None of these changes a result; each changes what you must read or write.

- P1 (high; **downgraded to medium 11 Nov**: Dulácska & Kollár 1995 and ACI 318.2-14 opened, IASS 1979 not; Methods 2.5 now states 5 as an assumption inside the λ 3-8 bracket, see `notes/buckling_threshold_sources.md`). The λ ≥ 5 threshold sizes every corner shell, and Fig. 4 shows it moves carbon by 20-30 %. Its sources (IASS 1979; Dulácska & Kollár 1995) are still [check] and unopened. Before submission, open them and give page or clause, or call the threshold a stated assumption and lean on the λ 3 / λ 8 runs.
- P2 (high). S4 is a closed-form fallback, not the published Michiels arch. A C&S reviewer will ask for the published case. The email in `05_email_michiels.md` and the journal papers in `06_michiels_sources.md` remain the route; until then, say so in Methods 2.8 and Limitations.
- P3 (medium). Half the design space (edge supports) sits at the 50 mm minimum, so it cannot discriminate between strategies. Present that as part of the mechanism (the support condition decides), not as filler. The 50 mm itself is [J] (cover on both faces); give the reasoning in one sentence.
- P4 (medium). The 5 % rule is smaller than one 5 mm step on 55-90 mm shells (6-9 %). Table S1 gives λ at the sized thickness for every design, which answers "are the 79 cells near a step?" (R2-3 in `01_professor_test.md`).
- P5 (medium). Linear buckling, no imperfections, equivalent static load. These are the limits where the null could break; they belong in Discussion with the data that would remove each one (paper 3, "where the null breaks").
- P6 (low). Deflection limit L/300 (GB 50010 Table 3.4.3) and G_E without roof live load (GB 50011 Table 5.1.3) are still [check] in the pre-registration. Confirm both clauses in your copies.

## Before you send any section on

- Every number has a row in `numbers.md`, checked by you.
- No "first", no "novel"; "extends Michiels & Adriaenssens".
- Never "resilience at no carbon cost"; never "both factor sets".
- Elsevier generative-AI declaration: say how Claude was used (code, checks, tables, editing). Keep it accurate.
