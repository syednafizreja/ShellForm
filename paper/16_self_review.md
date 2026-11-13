# Self-review of the assembled manuscript (14 Nov 2026, check window day 2)

Reviewer-2 pass on `manuscript/shellform_cas.tex` by the assistant, under Syed's standing delegation. Three checks: every number against the result files (recomputed, not read from `numbers.md`), consistency across sections, and claim against evidence. Then the voice and humanizer pass. Frozen results (`results/`, `paper/tables/`, `figures/`) were not touched.

## 1. Fixed in the manuscript

| # | Where | Problem | Fix | Evidence |
|---|---|---|---|---|
| F1 | Abstract, Results 3.4, Conclusions | λ 3 / λ 8 ratios were truncated, not rounded: 0.735 and 1.219-1.294 | 0.736-0.812 and 1.220-1.295 | `sensitivity_reference.csv`: 0.7358, 1.2197, 1.2946 |
| F2 | Results 3.4, Abstract, Conclusions | the ratios hold only for the gravity form at Sa = 0, but Fig. 4 shows all 84 corner designs (0.732-0.826, 1.219-1.295), so a reader sees a different range in the figure | stated the scope ("gravity-only corner shells at Sa = 0") and added the all-design range | `fig04_carbon_drivers.json` |
| F3 | Results 3.4, Discussion 4.3 vs Highlight 5 | "20-30 %" against "19 to 29 %" | "19-29 %" everywhere (the arithmetic: 18.8 % and 29.5 %) [J] | `numbers.md` Highlight 5 row |
| F4 | Results 3.6 para 5 | "The lateral case lowers the share, and lowers it more for the seismic-aware form" is **not what the data shows**. The lateral case lowers the share more for the *gravity* form (mean −0.2 and −0.8 points against +0.03 and −0.1). What holds is a form effect: the seismic-aware form has the smaller share in all 72 cells under both cases | rewritten with the two separate facts and their numbers | `verify_v4_energy.csv` |
| F5 | Results 3.1 | "The seismic-aware form only rises": corner forms also dip, by up to 4.2 mm | "moves almost only upwards ... dip by at most 4.2 mm" | `gallery_*.json`, dz_min_mm |
| F6 | Results 3.3 | "Three independent checks remove them: loading per surface area, the 61 × 61 network and either buckling threshold" lists four items, and the surface-area run is not a pre-registered sensitivity run and has no `numbers.md` row | "Each of the three sensitivity runs removes them" | Table 5; pre-registration section 7 |
| F7 | Results 3.5 | "0.61 to just under 1.0 of the plateau value" | "0.61-0.95" | `s5_plateau.csv`, alpha_shape 0.607-0.946 |
| F8 | Results 3.6, Methods 2.8 | residual "at most 2.2e-11 N" is the cloud value; the laptop gives 2.33e-11 N (handoff 14 Nov) | "below 2.5 × 10⁻¹¹ N on both machines" (wording of the laptop closeout, PR #51) | handoff 14 Nov |
| F9 | Results 3.6 para 3 | edge-shell bias of the record network (up to 5.8 %) was left out; a reviewer reading `verify_v2_hconv.csv` would find it | one sentence added: far above their limit, they read up to 5.8 % high | `verify_v2_hconv.csv` |
| F10 | Results 3.6 para 6 | "Formwork cannot change a verdict" is too strong: for the 5 artefact cells a large formwork term dilutes a 5.5 % difference below 5 % | "cannot turn a 'no meaningful difference' verdict into a difference" | V5 bound |
| F11 | Discussion 4.2 | "checked ... to 1e-9" reads as the result; 1e-9 is the tolerance (result 2.1e-11) | "within the pre-registered tolerance of 1e-9" | Table 3 |
| F12 | Introduction P6 | "an independent finite element wrapper": it is ShellBench's, by the same author, on the same CalculiX | "the finite element wrapper of our earlier benchmark, ShellBench"; V1-V3 added to contribution 1 | Methods 2.4 |
| F13 | Methods 2.3 | force density method had no primary citation; no equation | Schek (1974) cited; Eq. (1) (the README equation) and Eq. (2) (sphere buckling) displayed and numbered, as C&S asks | Crossref |
| F14 | Methods 2.1 | "Appendix A [?]" | amendments summarised in Supplement S3, full text in the repository | `docs/preregistration.md` |
| F15 | Abstract | "A1-A3" undefined (C&S: define abbreviations in the abstract); 246 → 250 words after the fix | "Cradle-to-gate (A1-A3)"; trimmed the last sentence; 248 words | C&S Guide for Authors, read 14 Nov |
| F16 | References | Hawkins et al. is 2019 (Structures 18), not 2018; Caycedo Garcia et al. is 2025 (26(4)), not 2024 | corrected from Crossref | `references.bib` |
| F17 | Reference style | drafts used author-year; the C&S guide asks for numbered references in square brackets, ordered by appearance | `elsarticle-num` | Guide for Authors, read 14 Nov |
| F18 | Conclusions | bold run-in labels inside the list (skill rule: no "**Label:** text" in papers) | plain sentences | manuscript-writing skill §6 |
| F19 | Humanizer pass | "accurate where it matters", "exact to round-off", "itself is sound" claimed more than the checks cover (sphere only at R/t 50 and 100) | matched to the evidence | V1, V3 |
| F20 | `numbers.md` | S5 row said alpha 0.45-1.0 (file: 0.607-0.946); V1 row said "three finest" meshes pass at R/t 50 (four do) | rows corrected; 10 new rows for numbers that had none | result files |

Every other number in the manuscript was recomputed from `results/` and `figures/*.json` and agrees with the text (168 feasible; governing 84/84 each; λ_min/λ 0.888-0.997 and 0.956-0.999; edge buckling 0.020-0.074 and 0.095-0.357; 0.51 f_c; 0.28 L/300; steel 0.82 / 0.95 / 57.9 kg, 2028-2953 kg; concrete share 79.9-81.2 %; 79/84 and 5 cells at 5.5-5.7 %; λ 4.978 and 5.016-5.052; cost of resilience 1.000-1.004, 1.003, 1.036; 70, 90, 110 mm and 31.1, 39.8, 48.6 kgCO₂e/m²; 17 of 168 (5 + 12); 2.0 %; 1.000-1.026; T1 0.029-0.308 s, 0.341 s; 70 of 84; V1 +1.96 / +1.33 %, 1.49 / 0.75 %; V2 0.62 %, 0.8-1.0 / 1.6 %, 3.8-5.8 %, 0.18; V4 76.3-89.2 / 91.0-99.9 %, 87.3 / 84.3 / 97.6 / 94.3 %; V5 1.44 %, 79; Fig. 6 68-252, 14-53, 21.6-23.8).

## 2. Reviewer-2 points that stay open (cannot be fixed by the assistant)

Ranked by desk-reject risk [J].

1. **Michiels & Adriaenssens (C&S 2018) is cited for the method we extend, but the journal paper is still unread** (thesis Ch. 3 used). In a C&S submission, the paper the method extends must be read first-hand, page-cited, and S4 should ideally reproduce one of its arches. Get it through a library or ask the authors (draft email in `05_email_michiels.md`).
2. **Nine sources are abstract-only** (`[check]` in the PDF): Jayasinghe 2022, Oval 2023, Leonardi 2026, Málaga-Chuquitaype 2022, Hammood 2023, Pérez Vega 2026, Caycedo Garcia 2025, Michiels 2017 (Eng. Struct.), Schek 1974. (The sphere benchmark now cites Hutchinson 2016, Section 3, opened by the assistant on 14 Nov; confirm that page too.) Open each, add the page to `references.md`. Leonardi 2026 first: confirm it has no seismic case before keeping "we found no study".
3. **Literature depth.** 27 references, of which 16 are journal papers; the skill target is about 30 (5 foundational, 15 related, 10 recent). Forward snowballing from Michiels 2017/2018 is still to do. Foundational shell-buckling and form-finding texts (beyond Schek) are thin. A C&S reviewer will also expect at least one comparison of our carbon per m² with published shell carbon (Discussion 4.3 has none).
4. **Linear buckling governs every corner shell, and imperfection-sensitive buckling is untested.** Stated as limitation 1, with the remedy (Riks with an eigenmode imperfection of t/4 to 3t/4 on a few governing cells). A reviewer may ask for it as a major revision; it is the natural revision experiment [J].
5. **V1 covers R/t 50 and 100; the sized shells reach about 520.** Said in the text. A sphere at R/t 200-500 would close it (about 30 min of compute).
6. **Code clauses read through ShellBench, not first-hand** (`[check]`): GB 50009 cl. 5.3.1 and Table 5.3.1, GB 50011 Table 5.1.3, GB 55002 cl. 4.3.2, GB 50010 Tables 3.4.3 and 8.5.1. Confirm each in your copy.
7. **Affiliation** `[?]`, and the CRediT, competing-interest, funding and AI statements `[check]`: they are drafts in your name and only you can sign them. The AI statement must stay.
8. **Data availability.** The verification add-ons (V1-V5, Fig. 6, Fig. S1) are after the v0.1.0 archive. A v0.2.0 release with its own Zenodo DOI should exist before submission (needs your Zenodo token; skipped today).
9. **Cover letter and suggested reviewers** are not written (pre-submission checklist).

## 3. [J] items left for you to accept or cut

All are marked `[J]` in the PDF: the title choice; the efficiency sentence and "So two lines of work have not met" and the designer sentence (Introduction); the λ 3/5/8 reading as combined reductions 1/0.6/0.375 (Methods 2.5); the SDL derivation note (Table 2); "the four directions of shaking cancel" (3.1); "This is the mechanism of the study" (3.2); "one thickness step, not a saving" (3.3); "19-29 %, an order of magnitude more" (3.4); "which strategy wins depends only on the step" (3.4); "the plateau load is conservative" (3.5); "the solid-element expansion of S8R" and "funicular for none of them" (3.6, wording from PR #51); the four Discussion sentences (4.1 ×2, 4.2, 4.3, 4.4); the two last sentences of the Conclusions.

## 4. Voice and humanizer pass

No AI-vocabulary clusters, no em dashes, no "novel", "first" or "robust"; hedging is tied to evidence; "we" throughout; British spelling. Sentences kept in Syed's order and framing from drafts 10-15; changes are only those in section 1. Section-opening sentences carry the argument when read alone (SKIP test passed on Results and Discussion [J]).
