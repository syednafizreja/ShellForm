# Abstract, highlights, title and Conclusion (draft 1, 13 Nov 2026)

> **Superseded on 14 Nov 2026** by the assembled manuscript `manuscript/shellform_cas.tex`. Corrections made there during the self-review (`16_self_review.md`) are not back-ported here; edit the manuscript, not this draft.

Written by the assistant in Syed's voice under his standing rule of 10 Nov (the assistant writes the prose; Syed reads, changes and owns it). Built only from numbers that already have a row in `numbers.md` (freeze tag `freeze-2026-11-09`, ShellBench v0.3.0) and from the Methods, Results, Discussion and Introduction drafts. Journal limits (Computers & Structures guide for authors, read 13 Nov 2026): abstract at most 250 words, standing alone, no references unless essential (then author and year); highlights 3 to 5 bullets, each at most 85 characters including spaces, as a separate file. Interpretive sentences [J] are listed at the end.

## Title (pick one)

**Chosen 14 Nov 2026: option 1** (the assistant, under the standing delegation; author to confirm).

1. Does seismic-aware form-finding lower the embodied carbon of reinforced concrete shells? A pre-registered comparison of 168 sized designs
2. Seismic-aware form-finding and the embodied carbon of code-sized reinforced concrete shells
3. What sets the carbon of reinforced concrete shells in seismic regions: form, seismic level or buckling factor?

[J] Recommend 1: it states the question, the method and the scale, and it does not promise a saving.

## Abstract

Seismic-aware form-finding has been developed for shells and arches whose material carries little or no tension. For reinforced concrete shells it is not known whether such a form lowers embodied carbon once the shell is sized to code checks. We compare gravity-only form-finding with a seismic-aware extension of Michiels and Adriaenssens' method: a three-dimensional force density network with four directions of shaking. All 168 designs, square shells of 10 and 20 m on corner or edge supports at three rise-to-span ratios and plateau spectral accelerations from 0 to 0.6 g, are sized to the same checks: a linear buckling factor of at least 5, deflection within span/300, a 50 mm minimum thickness and the minimum steel ratio. A1-A3 carbon uses GB/T 51366-2019 factors with a ±25 % band. The decision rule and sensitivity runs were pre-registered. In 79 of 84 comparisons the two strategies differ by less than 5 % (no meaningful difference). The other 5 are one 5 mm thickness step and disappear in every sensitivity run. The cause is the governing checks. Linear buckling sets the thickness of all 84 corner-supported shells, the 50 mm minimum sets all 84 edge-supported shells, and the minimum ratio sets the steel. None responds to the seismic level, so the gravity form carries 1.000-1.004 times its zero-seismic carbon up to 0.6 g. The buckling factor matters far more: at 3 and 8, corner-shell carbon is 0.735-0.812 and 1.219-1.294 of the baseline. The code and every result are open.

## Highlights

- 168 reinforced concrete shells sized to the same code checks, two form strategies
- Seismic-aware and gravity forms differ by under 5 % carbon in 79 of 84 cases
- Buckling or the 50 mm minimum sets thickness; minimum steel sets reinforcement
- Seismic level up to 0.6 g leaves gravity-form carbon within 0.4 %
- Buckling factor of 3 or 8 moves corner-shell carbon by 19 to 29 %

## Keywords

Form-finding; force density method; reinforced concrete shells; embodied carbon; seismic design; linear buckling; pre-registration. (Seven keywords; the C&S guide for authors asks for 1 to 7, read by the assistant 14 Nov 2026; author to confirm.)

## 5. Conclusions

This study asked whether seismic-aware form-finding lowers the embodied carbon of reinforced concrete shells sized to code checks. For square shells of 10 and 20 m, on corner or edge supports, up to a plateau spectral acceleration of 0.6 g, it does not. Four conclusions follow.

1. **The two strategies give the same carbon.** In 79 of 84 pre-registered comparisons they differ by less than 5 %. The other 5 are one 5 mm thickness step, and they disappear under each of the three sensitivity runs. The headline claim, that the seismic-aware form is cheaper, is not made.
2. **The governing checks explain why.** Linear buckling sets the thickness of every corner-supported shell, the 50 mm minimum sets every edge-supported shell, and the minimum steel ratio sets the reinforcement. None of the three responds to the seismic level. The seismic case adds at most 57.9 kg of steel to a 20 m corner shell that carries 2028-2953 kg.
3. **The buckling factor moves carbon; the seismic level does not.** Changing the buckling threshold from 5 to 3 or 8 gives corner-shell carbon of 0.735-0.812 or 1.219-1.294 of the baseline. Raising the seismic level from 0 to 0.6 g changes gravity-form carbon by a factor of 1.000-1.004. Since no code fixes the buckling factor for shells, studies of shell carbon should report it and its sensitivity.
4. **The equivalent static load is on the safe side.** Every first period is at or below T_g = 0.35 s, so the shells sit on the plateau or on the rising branch of the spectrum.

For design in this range, form-find for gravity, check the seismic combinations, and spend the effort on the support condition, the buckling factor and the minimum thickness [J]. The result should change where the form must keep the thrust inside the section, as in unreinforced shells, and may change for longer spans, heavier roofs, imperfection-sensitive buckling or a dynamic analysis. Each is one change to the open pipeline. The pipeline itself, pre-registered rules, the same code checks for every design, and the question of which check governs asked before the question of which form wins, applies to any design strategy that claims to save material [J].

## Side notes for Syed (delete before submission)

- Word count: abstract 246 words (counted by script, 13 Nov). Highlights: longest 81 characters. Recount after any edit.
- Every number traces to `numbers.md`: 168 designs (Table 1 row); 79 of 84 and the 5 cells (Results 3.3 row); governing checks 84/84 (Fig. 2 row); 57.9 kg and 2028-2953 kg (Results 3.2 steel row); 1.000-1.004 (Results 3.x para A row); 0.735-0.812 and 1.219-1.294 (para A rows); T_g 0.35 s (S5 row); thresholds and minimum from Methods 2.5 and Table 2.
- Highlight 4 "within 0.4 %" is 1.000-1.004 rounded up; highlight 5 "19 to 29 %" is 1 − 0.812 = 0.188 to 1.294 − 1 = 0.294, rounded to whole percent. Resolved 14 Nov: "19 to 29 %" (the exact rounding) now stands in Results 3.4, Discussion and Highlight 5 alike.
- The abstract names Michiels and Adriaenssens without a year, as the guide allows; add the year if the editor asks.
- [J] sentences to accept, change or cut: "The cause is the governing checks" (abstract); the design advice sentence and the last sentence of the Conclusions.
- No word "first", "novel" or "robust". The abstract says "it is not known", tied to the documented search in `13_literature_search.md`.
- AI-use declaration: the abstract, highlights and conclusions were drafted by the assistant from your results and rules; the Elsevier declaration must say so.
