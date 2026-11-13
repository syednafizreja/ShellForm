# 1. Introduction (draft 1, 13 Nov 2026)

> **Superseded on 14 Nov 2026** by the assembled manuscript `manuscript/shellform_cas.tex`. Corrections made there during the self-review (`16_self_review.md`) are not back-ported here; edit the manuscript, not this draft.

Written by Claude in Syed's voice under his standing rule of 10 Nov (Claude writes the prose; Syed reads, changes and owns it). Sources: `13_literature_search.md` (abstract-level reading, 13 Nov), `notes/michiels2017.md`, `00_core.md` section 4, the Results and Discussion drafts. Every cited number carries `[check]` until Syed has opened the full text and added a page. No global statistics are quoted, because none has been read from a source. Interpretive sentences [J] are listed at the end.

## Paragraph 1: shells as a low-carbon structure

Thin concrete shells carry load mainly by membrane action, so they need far less material than members that carry it in bending. Recent work has turned this into measured carbon savings. A thin-shell floor was designed, built and tested as a low-carbon alternative to a flat slab (Hawkins et al., 2018). Compared with reinforced concrete flat slabs, shell floors may cut cradle-to-gate embodied carbon by up to 65 % (Jayasinghe et al., 2022 [check]), and a segmented shell floor prototype by about 50 % (Oval et al., 2023 [check]). Form-finding with the force density method, combined with finite element checks and reinforcement design, is now used to search directly for low-carbon reinforced concrete shells (Leonardi et al., 2026 [check]).

## Paragraph 2: the seismic question

These savings were found for gravity loads. In a seismic region, a designer must also carry lateral load, and the form that is efficient under gravity is not the form that is efficient under lateral load. Michiels and Adriaenssens addressed this for masonry: they added lateral load to form-finding, so that a compression-only load path exists under combined gravity and seismic load (Michiels et al., 2017; Michiels and Adriaenssens, 2018). Later work extended the idea to corrugated shells with pushover validation (Michiels et al., 2019), to iso-resistant compression-only shells (Olivieri et al., 2025) and to arches, where a seismically form-found shape saved 10-50 % of material against a constant-thickness arch (Málaga-Chuquitaype et al., 2022 [check]). In all of these the material has little or no tensile capacity, so the form must keep the thrust inside the section.

## Paragraph 3: reinforced concrete shells behave differently

Reinforced concrete shells do not need a compression-only form, because reinforcement can carry tension. Their seismic behaviour has been studied mainly on gravity forms. Small and midsized concrete roof shells (spans below 30 m) were found to stay elastic under earthquake excitation, because their high stiffness and low mass place their natural frequencies far above the dominant frequencies of ground motion (Hammood and Jawad, 2023 [check]). Nonlinear analyses of force-density reinforced concrete shells under synthetic accelerograms show controlled damage, and show that geometric imperfections reduce their ultimate capacity by 22-45 % (Pérez Vega et al., 2026 [check]); fragility analysis of a free-form shell places its damage near the supports (Caycedo Garcia et al., 2024 [check]). These studies analyse a given form. They do not ask whether a form found for seismic load would lower the material, and so the carbon, of a reinforced concrete shell that meets the same code checks.

## Paragraph 4: the gap

So two lines of work have not met. Seismic-aware form-finding has been developed where the form must do all the work, in masonry and unreinforced materials. The carbon of reinforced concrete shells has been studied for gravity forms. We found no study that reports what seismic-aware form-finding costs or saves in embodied carbon when reinforced concrete shells are sized to code checks (search protocol in the supplementary material). A designer in a seismic region therefore cannot tell whether a seismic-aware form is worth the extra design effort, or whether a gravity form, checked and sized for the seismic case, already gives the lower-carbon roof.

## Paragraph 5: this study

This paper answers that question for square reinforced concrete roof shells of 10 and 20 m on corner or edge supports, at three rise-to-span ratios and seven plateau spectral accelerations from 0 to 0.6 g. We compare two strategies on equal terms: gravity-only form-finding, and seismic-aware form-finding that extends the method of Michiels and Adriaenssens to a three-dimensional force density network and four directions of shaking. Every one of the 168 designs is sized to the same code checks and its A1-A3 carbon is computed with GB/T 51366-2019 factors and a ±25 % band. The comparison rule, thresholds and sensitivity runs were pre-registered before any design was run.

## Paragraph 6: contributions and structure

The study makes three contributions. First, an open and verified pipeline: a three-dimensional force density solver with a four-direction lateral-load envelope, verified by five tests (S1-S5) and cross-checked against an independent finite element wrapper, released with every result. Second, a pre-registered comparison of the two strategies over 168 sized designs, with the result and its mechanism: which code check sets the thickness and steel, and why the seismic level does not reach the carbon. Third, a measure of what does move carbon in these shells, the support condition and the buckling factor, which no code fixes. Section 2 describes the method, Section 3 the results, and Section 4 discusses them, their limits, and where we expect the result to change.

## Side notes for Syed (delete before submission)

- [J] sentences to accept, change or cut: "the form that is efficient under gravity is not the form that is efficient under lateral load" (P2); "So two lines of work have not met" (P4); the whole of P4's last sentence (the designer's question).
- Every `[check]` number is from an abstract only (`13_literature_search.md`). Open Jayasinghe 2022, Oval 2023, Leonardi 2026, Málaga-Chuquitaype 2022, Hammood 2023, Pérez Vega 2026 and Caycedo Garcia 2024, and add pages to `references.md` before submission.
- Michiels and Adriaenssens (2018) is the C&S arch paper: its journal version is still unread (thesis Ch. 3 used). Cite it only after you have it.
- Leonardi et al. (2026) is the paper a reviewer will hold closest to ours. From the abstract it is gravity-only with FRP reinforcement; confirm in the full text that it has no seismic case before keeping P4's "no study".
- Never "first": P4 says "we found no study", tied to the documented search. Keep it that way.
- C&S fit (`01_professor_test.md` R2-6): P6 puts the computational pipeline first on purpose.
- AI-use declaration: this section was drafted by Claude from your search, results and rules; the Elsevier declaration must say so.
