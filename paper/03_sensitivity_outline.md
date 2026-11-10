# Sensitivity: Methods and Results outline (Day 9, 6 Nov 2026)

Outline only, not paper text. The skills that govern the paper (academic-manuscript-writing ground rule 1; syed-academic-voice-dna section 0) say Syed writes the sentences; Claude gives the order, the evidence and the checks. Each bullet below is one paragraph's job, with the numbers it needs and where they come from. **Updated 7 Nov 2026 (Day 10):** numbers below are refreshed to the corrected runs (ShellBench v0.2.0, four buckling factors requested, pre-registration D10-1; `notes/day10_s5_pin.md`). All numbers are pre-freeze (ShellBench v0.2.0, main before the 10 Nov freeze) and are refreshed from the freeze run; none goes into the paper without a row in `numbers.md`. [J] marks Claude's judgement.

Factor set, said once and used everywhere: the paper uses one carbon factor set, GB/T 51366-2019 Table D.0.1 (read from ShellBench `data/carbon_factors.csv`), with a ±25 % band on the concrete and steel factors, moved independently (four corners; pre-registration decision P3). It does not use two factor sets. ICE was dropped because its licence does not allow its values in a public repository. Never write "both factor sets".

**Checked 10 Nov 2026 against the freeze files and `paper/tables/table5_verdicts.md`:** four counts left over from before the D10-1 correction were fixed (baseline 37 + 5 cells, headline 4 of 10 at 10 m, five artefact cells, 79 robust cells).

## Methods, section 2.9 "Sensitivity" (bullets for Syed's prose)

1. Point: three sensitivity runs were fixed in the pre-registration before any result (section 7), and each changes one setting while everything else stays as in the baseline.
   - Buckling threshold λ_LBA ≥ 3 and ≥ 8 (baseline 5). Why these two: the IASS (1979) and Dulácska & Kollár (1995) reduction-factor approach behind the 5 [check both sources, still not opened].
   - Network 61 × 61 (baseline 41 × 41), for both form-finding and the CalculiX analysis.
   - Factor band: the four corners are part of every baseline row; no rerun is needed.
2. Point: every run covers all 168 designs, not only the headline scope. [J] Reason: the pre-registration names the headline scope (rise 0.15, both supports, Sa ≥ 0.2 g) for the re-check, but running all 168 costs about 20 min (λ runs) and about 50 min (61 × 61) on four cores, and it shows whether any other verdict moves.
3. Point: what counts as "sensitive". A conclusion is sensitive if any cell's verdict (section 7 rule, 5 % band) changes at any band corner, or if the headline status changes. Code: `python -m shellform.sensitivity`; tables `results/sensitivity_summary.csv`, `sensitivity_cells.csv`, `sensitivity_reference.csv`.

## Results, section 3.x "How robust is the null result?" (ISCT per paragraph)

### Paragraph A: the buckling threshold moves carbon, the seismic level does not (Table: `sensitivity_reference.csv`)
- I: corner-supported shells are sized by linear buckling at every threshold; edge-supported shells stay at the 50 mm minimum at every threshold (lowest edge λ at 50 mm is 14.00, 20 m, rise 0.10), so edges do not move.
- S: corner carbon at Sa = 0 (gravity form) is 0.735 to 0.812 of the baseline at λ ≥ 3, and 1.219 to 1.294 at λ ≥ 8 (all six span and rise cases). Example: 10 m, rise 0.15: 90 mm and 39.8 kgCO₂e/m² at λ 5, 70 mm and 31.1 at λ 3, 110 mm and 48.6 at λ 8.
- C: compare with the seismic effect in the same shells. For the gravity form (the cleanest measure, because its shape does not change with Sa) the cost of resilience (carbon at Sa / carbon at Sa = 0) is 1.000 to 1.004 in the baseline, 1.000 to 1.003 at λ 3 and 1.000 to 1.036 at λ 8 (`sensitivity_cells.csv`). [J] So the choice of buckling safety factor moves corner-shell carbon by about 20 to 30 %, an order of magnitude more than seismic level up to 0.6 g.
- C (second point): the one place where seismic level first moves a thickness is λ 8, 20 m, corners, rise 0.10: the gravity form goes from 325 mm to 330 mm at 0.5 g and 335 mm at 0.6 g (cost of resilience 1.018 and 1.036), because the buckling factor of the seismic combination falls below 8 there. [J] This is the edge of the null result inside the pre-registered ranges: a stricter threshold on the heaviest, flattest shell. It is still below the 5 % band.
- T: so the comparison between strategies must be read against a threshold that is a judgement, which is the next paragraph.

### Paragraph B: the strategy verdicts under the two thresholds (Table: `sensitivity_summary.csv`)
- I: verdict counts per span at λ 3, 5, 8.
- S: 20 m: 42 of 42 cells "no meaningful difference" at all three thresholds. 10 m: baseline 37 "no meaningful difference" + 5 "seismic cheaper"; λ 8: 42 of 42 "no meaningful difference"; λ 3: 40 "no meaningful difference" + 2 "gravity cheaper". Every verdict is the same at all four band corners (42 of 42 per span and variant).
- C: the five baseline "seismic cheaper" cells (10 m, corners, rise 0.15, Sa 0.1 to 0.5) vanish at both λ 3 and λ 8: both strategies size to the same thickness (70 mm and 110 mm) and differ by at most 0.24 % (λ 3) and 0.35 % (λ 8) in carbon. This is the third independent sign that they are a sizing-grid artefact (after the load basis, D4-5, and the 61 × 61 check of 2 Nov).
- T: the two new λ 3 cells need their own explanation.

### Paragraph C: the two λ 3 "gravity cheaper" cells are a grid step, but they point the other way
- I: 10 m, corners, rise 0.20, Sa 0.5 and 0.6 g.
- S: at 55 mm the gravity form has λ = 3.0003 (passes by 0.01 %); the seismic-aware forms have λ = 2.936 and 2.846 (fail), so they size to 60 mm; carbon +8.4 % and +8.2 % (`sens_lam3_meta.json`, "tried").
- C: the buckling factor of the seismic-aware form at equal thickness is 2.1 % and 5.1 % below the gravity form's here. The 5 mm step (9 % of 55 mm) turns a 2 to 5 % stiffness difference into an 8 % carbon difference. [J] Same mechanism as the baseline's five cells, opposite sign: near a threshold, the strategy that "wins" depends on which side of a grid step each form falls. The 5 % rule cannot resolve differences smaller than one thickness step on thin shells.
- T: the direction of the small λ difference is worth stating as a physical result (the seismic-aware form is slightly less stable in buckling at high Sa for the steepest 10 m corner shells), not as a carbon saving or cost.

### Paragraph D: mesh 61 × 61 (Tables: `sensitivity_summary.csv`, `sensitivity_reference.csv`)
- I: the same 168 designs on a 61 × 61 network, for form-finding and analysis.
- S: 168 of 168 feasible; 17 of 168 thicknesses move by one 5 mm step (5 at 10 m, 12 at 20 m), the rest are unchanged. At equal thickness the corner buckling factor moves by at most 2.0 %. Gravity-form carbon at Sa = 0 is 1.000 to 1.026 of the 41 × 41 value; the largest change for any single design is 6.0 % (one thickness step). Edges do not move. T1 is at most 0.318 s, still below Tg = 0.35 s, so S5 holds on the finer network.
- C: verdicts: 84 of 84 cells "no meaningful difference", the same at all four band corners. The five baseline "seismic cheaper" cells vanish again: on 61 × 61 the seismic-aware 10 m corner shells at rise 0.15 need 90 mm, like the gravity form (the 2 Nov cross-check found the same, λ 4.935 to 4.986 at 85 mm).
- T: so all three checks agree, which leads to the headline paragraph.

### Paragraph E: the headline
- S: the headline claim of section 7 ("seismic-aware form-finding is cheaper") holds in 0 of 10 scope cells at either span under λ 3, λ 8 and 61 × 61, against 4 of 10 (10 m) and 0 of 10 (20 m) in the baseline (Table 5). It is not made, and no conclusion flips to support it.
- C: what is "sensitive" by the section 7 rule: only the 10 m corner cells. Five baseline cells change to "no meaningful difference" under all three variants, and two cells change to "gravity cheaper" at λ 3. Every one of them is a single 5 mm thickness step between two forms whose buckling factors differ by less than about 5 %. The 20 m verdicts do not change at all.
- [J] Wording to use: "no meaningful difference, robust to the buckling threshold, the network density and the factor band". Wording to avoid: "seismic resilience at no carbon cost" (both strategies meet the same checks; the checks, not the form, deliver the resilience; see `00_core.md` section 4).

## Discussion seeds (Syed decides; each needs his sentence)

- [J] Mechanism: corner-supported shell carbon is governed by the buckling threshold and the support condition, not by the seismic level. The design decision that matters for carbon is the buckling safety factor, which codes do not fix for shells (open question for the literature search: what thresholds do recent shell studies use?).
- [J] Limit: the λ sensitivity is linear buckling with a uniform factor. A geometrically nonlinear, imperfection-sensitive analysis could move the corner thickness differently for the two forms, because the seismic-aware form changes the curvature near mid-edge (gallery, Day 8). This is where the null result could break.
- [J] Method lesson for C&S: a "no meaningful difference" band of 5 % is smaller than one thickness step on a 55 to 90 mm shell (6 to 9 %). Reviewers will ask; answer with the λ margins at the sized thickness, or a continuous (unrounded) thickness as a check.

## Reviewer 2 answers this outline supports (update `01_professor_test.md`)

- R2-1 (trivial result): seismic demand governs the thickness in only one corner of the space (λ 8, 20 m, rise 0.10, Sa ≥ 0.5 g, at most +3.6 % carbon); the threshold choice moves corner carbon by 20 to 30 %. That contrast, with numbers, is the answer.
- R2-3 (why trust the 79 cells): all 5 suspect cells vanish at λ 3, λ 8 and 61 × 61; the 79 hold at all thresholds except 2 cells at λ 3, explained by the same grid step.
