# 3. Results (draft 1, 10 Nov 2026)

> **Superseded on 14 Nov 2026** by the assembled manuscript `manuscript/shellform_cas.tex`. Corrections made there during the self-review (`16_self_review.md`) are not back-ported here; edit the manuscript, not this draft.

Written by Claude in Syed's voice at his request of 10 Nov, from `07_results_outline.md`, `03_sensitivity_outline.md`, the freeze files (tag `freeze-2026-11-09`, ShellBench v0.3.0) and `paper/tables/`. Syed reads, changes and owns it. Every number has a row in `numbers.md`. Interpretive sentences are Claude's judgement [J] until Syed accepts them; they are listed in the side notes at the end. Each paragraph follows Identify, Summarise, Compare, Transition.

## 3.1 The two forms are close

Fig. 1 shows the gravity-only form and the seismic-aware form for both spans at rise 0.15. In plan the two forms are the same: no node moves horizontally. The seismic-aware form only rises, mostly near the middle of each edge. At 0.6 g the largest rise is 72 mm at 10 m and 144 mm at 20 m for the corner-supported shells, and 63 mm and 125 mm for the edge-supported ones, about 0.7 % of the span at most. At 0.3 g it is a quarter of that or less.

These differences are small because the four directions of shaking cancel. A form found for one direction leans: the 10 m parabolic arch of test S4, at rise-to-span 1/4, leans its crown by 0.75 m at 0.3 g. The midrange of four opposite leans keeps almost none of that lean and only lifts the surface where the four thrust surfaces spread apart. So the first question is whether the code checks see such a small change at all.

## 3.2 What sets the thickness

Fig. 2 shows, for all 168 designs, how close each check is to its limit at the sized thickness. One check sets the thickness in every design, and it depends only on the support condition. Linear buckling governs all 84 corner-supported designs: λ_min/λ is 0.888-0.997 at 10 m and 0.956-0.999 at 20 m, below 1 only because of the 5 mm thickness step. The 50 mm minimum governs all 84 edge-supported designs; their next-closest check is buckling, at 0.020-0.074 of its limit at 10 m and 0.095-0.357 at 20 m. Compression reaches at most 0.51 of f_c and deflection at most 0.28 of L/300.

Sa does not change this picture. The governing check is the same at 0 g and at 0.6 g in every design, and no other check moves onto its limit. Table 4 gives the result in thickness. Corner-supported shells need 75-105 mm at 10 m and 185-265 mm at 20 m, set by the rise; edge-supported shells stay at 50 mm everywhere.

Steel follows the same pattern. The minimum ratio governs the reinforcement almost everywhere, and the seismic case adds at most 0.82 kg of steel to a 10 m corner shell, 0.95 kg to a 20 m edge shell and 57.9 kg to a 20 m corner shell, which carries 2028-2953 kg in total. Concrete is 79.9-81.2 % of the carbon of every design.

This is the mechanism of the study. Thickness is set by buckling or by the code minimum, steel by the minimum ratio, and none of the three responds to Sa between 0 and 0.6 g. Carbon therefore has no route to depend on Sa, or on which form is used. The pre-registered comparison tests this directly.

## 3.3 The pre-registered comparison

Fig. 3 shows the carbon difference between the two strategies in each of the 84 cells (span, supports, rise and Sa), against the 5 % rule. In 79 of the 84 cells there is no meaningful difference. In the other 5 cells the seismic-aware form is cheaper by 5.5-5.7 %; all 5 are 10 m corner-supported shells at rise 0.15, Sa 0.1-0.5 g. Every verdict is the same at all four corners of the ±25 % factor band, because the band moves both strategies almost equally. The headline claim holds in 4 of its 10 scope cells at 10 m and in 0 of 10 at 20 m, so it is not made (Table 5).

The 5 cells are one thickness step, not a saving. At 85 mm the gravity form has λ = 4.978 and fails by 0.4 %, while the seismic-aware forms at 0.1-0.5 g have λ = 5.016-5.052 and pass by at most 1.0 %. So the seismic-aware shells size to 85 mm and the gravity shells to 90 mm. Three independent checks remove them: loading the shells per surface area instead of per plan area, the 61 × 61 network, and either buckling threshold (Section 3.4). In each case both strategies size to the same thickness. We report the 5 cells as a grid-step artefact.

So the comparison confirms the mechanism. The next question is how large the effect of Sa is next to the other choices a designer makes.

## 3.4 What moves carbon

Fig. 4 puts every driver of carbon on one scale. For the gravity-only form, raising Sa from 0 to 0.6 g changes carbon by at most 0.4 %. For the seismic-aware form the change is −5.7 to +1.5 %, and the strategy itself moves carbon by −5.7 to +1.4 %; the extreme values are the 5 artefact cells. The buckling threshold moves much more. At λ ≥ 3, corner-shell carbon falls to 0.735-0.812 of the baseline, and at λ ≥ 8 it rises to 1.219-1.294. For the 10 m corner shell at rise 0.15, for example, the thickness is 70, 90 and 110 mm at λ ≥ 3, 5 and 8, and its carbon is 31.1, 39.8 and 48.6 kgCO₂e/m². The buckling threshold, a choice that no code fixes for shells, therefore moves corner-shell carbon by 19 to 29 %, an order of magnitude more than the seismic level up to 0.6 g. Edge-supported shells respond to nothing except the factor band, because they sit on the code minimum.

The verdicts barely move under the three sensitivity runs (Table 5). At 20 m every cell is no meaningful difference in all three runs. At 10 m, λ ≥ 8 and the 61 × 61 network give no meaningful difference in all 42 cells. λ ≥ 3 gives 40 cells of no meaningful difference and 2 of "gravity cheaper", and these 2 need their own explanation. In every run, every verdict is the same at all four band corners, and the headline holds in 0 of 10 scope cells at both spans.

The 2 new cells are the same grid step pointing the other way. They are 10 m corner shells at rise 0.20 and Sa 0.5 and 0.6 g. At 55 mm the gravity form has λ = 3.0003 and passes by 0.01 %. The seismic-aware forms have λ = 2.936 and 2.846 and fail, so they size to 60 mm and carry 8.4 % and 8.2 % more carbon. At equal thickness the seismic-aware form buckles at a 2-5 % lower load here, and one 5 mm step (9 % of 55 mm) turns that into an 8 % carbon difference. Near a threshold, which strategy "wins" depends only on which side of a thickness step each form falls. The 5 % rule cannot separate differences smaller than one step on shells this thin.

The 61 × 61 network changes little. All 168 designs remain feasible, and 17 of 168 thicknesses move by one 5 mm step (5 at 10 m, 12 at 20 m). At equal thickness the corner buckling factor moves by at most 2.0 %. Gravity-form carbon at Sa = 0 is 1.000-1.026 of the 41 × 41 value. The 5 baseline "seismic cheaper" cells vanish here as well. So the result does not depend on the buckling threshold, the network or the factor band. It does rest on the equivalent static load, which the next section checks.

## 3.5 The equivalent static load is on the safe side

Fig. 5 places the first period of every baseline design on the GB 50011 design spectrum shape read from ShellBench. All 168 designs have T1 between 0.029 and 0.308 s, at or below T_g = 0.35 s, so test S5 has no failure; the same holds in all three sensitivity runs (longest T1 0.341 s, at λ ≥ 3). The corner-supported shells sit on the plateau. 70 of the 84 edge-supported designs are stiffer still and sit on the rising branch, where the spectral value is 0.61 to just under 1.0 of the plateau value. For them the plateau load we used is conservative. The no-difference result is therefore not caused by an underestimated seismic load. Its limits lie elsewhere: linear buckling without imperfections, and an equivalent static load in place of a dynamic analysis. Section 4 discusses both.

## 3.6 Verification of the analysis chain

The checks in this section were added after the freeze. They test the tools, not the hypothesis, and none of them changes a thickness or a verdict (Fig. S1).

The buckling path is accurate where it matters. A complete sphere under external pressure, meshed with the same S8R elements and solved with the same eigenvalue step, buckles at 1.96 % above the classical value at R/t = 50 and 1.33 % above it at R/t = 100, on the finest of five meshes (3456 elements). The offset falls with t/R and matches the membrane stiffness of the same model, which is 1.49 % and 0.75 % too stiff. We read it as the thickness effect of the solid-element expansion of S8R, not as a mesh error [J]. The sized shells are thinner than either sphere (R/t of about 78 to 520), so we did not test their whole range.

The record network is fine enough for buckling but not for deflection at a point support. On eight designs refined from 21 to 81 nodes per side at their frozen thickness, λ1 changes by at most 0.62 % between the two finest networks. On the record network (41 × 41) the corner-shell λ1 is above the finest value by 0.8-1.0 % for the gravity-only form and 1.6 % for the seismic-aware form. This is the bias that the 61 × 61 sensitivity run already measured, and it removed only the 5 grid-step cells (Section 3.4). The SLS deflection of corner-supported shells does not converge: it grows by 3.8-5.8 % per refinement, because its largest value sits next to a point support. It never comes near the limit. On the finest network the largest deflection is 0.18 of L/300.

The form-finding is exact to round-off. The residual of the assembled force density system is below 2.5 × 10⁻¹¹ N for unit nodal weights, over all 84 solves (four families, three rises, seven Sa levels), on both machines that ran the check.

The shells carry the design lateral load mainly as membranes. Membrane action holds 76.3-89.2 % of the strain energy of the corner-supported shells and 91.0-99.9 % of the edge-supported ones, over all 168 designs and both ULS cases. The lateral case lowers the share, and lowers it more for the seismic-aware form. For the 10 m shells at rise 0.15 and Sa = 0.6 g, the share is 87.3 % (gravity-only) and 84.3 % (seismic-aware) with corner supports, and 97.6 % and 94.3 % with edge supports. We read this as the price of one form for four directions of shaking: it is funicular for none of them [J].

Formwork cannot change a verdict. Its carbon scales with the soffit area, and the soffit areas of the two strategies differ by at most 1.44 % in any cell. Adding a formwork term of any size to both strategies gives a difference that lies between the carbon difference and the area difference. So, whatever the formwork factor and whether the formwork is used once, 5 times or 20 times, the 79 "no meaningful difference" cells stay inside the 5 % band. The absolute carbon would change; ShellBench holds no formwork factor yet, so we give none [?].

Fig. 6 puts carbon against λ1 for every sized design. The non-dominated front is made only of edge-supported shells: they sit on the 50 mm minimum with λ1 of 68-252 (10 m) and 14-53 (20 m) at 21.6-23.8 kgCO₂e/m². Corner-supported shells sit on the threshold they were sized to, and each step from λ ≥ 3 to 5 to 8 costs carbon. The two strategies lie on top of each other. The support condition and the buckling threshold move the trade-off between stability and carbon; the strategy does not.

## Side notes for Syed (delete before submission)

- [J] sentences to accept, change or cut: "These differences are small because the four directions of shaking cancel" (3.1); "This is the mechanism of the study" paragraph (3.2); "one thickness step, not a saving" (3.3); "an order of magnitude more" (3.4); "Near a threshold, which strategy wins depends only on..." (3.4); "the plateau load we used is conservative" (3.5).
- Wording kept out on purpose: never "resilience at no carbon cost" (both strategies meet the same checks; the checks deliver the resilience); never "robust"; never "first".
- 3.1: 63 and 125 mm are the edge-supported values from `figures/gallery_*.json` (dz_max_mm at 0.6 g); add these to `numbers.md` when you check them.
- 3.3: λ at 85 mm (gravity 4.978; seismic 5.016-5.052 at 0.1-0.5 g) is `results/batch_all_meta.json`, tried; add a `numbers.md` row.
- 3.4: −5.7 to +1.5 % and −5.7 to +1.4 % are `figures/fig04_carbon_drivers.json`, ranges; 70/90/110 mm and 31.1/39.8/48.6 kgCO₂e/m² are `sensitivity_reference.csv`.
- 3.6 (added 14 Nov): every number is in `notes/day17_verification.md`, `results/verify_meta.json` and the new `numbers.md` rows. [J] sentences: "the thickness effect of the solid-element expansion" (kept: the membrane-stiffness offset of the same model supports it); "less funicular for any one of them" (rewritten 14 Nov as "the price of one form for four directions", a reading rather than a claim). Fig. 6 stays in the main text: it is the only figure that shows the stability-carbon trade-off, and C&S sets no figure limit in its guide [J]. Fig. S1 goes to the supplement. Decided by Claude under the standing delegation, 14 Nov; author to confirm.
- C&S accepts a combined Results and discussion; this draft keeps them separate so that Section 4 can carry the literature comparison.
