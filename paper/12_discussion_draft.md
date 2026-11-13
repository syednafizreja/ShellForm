# 4. Discussion (draft 1, 11 Nov 2026)

Written by Claude in Syed's voice under his standing rule of 10 Nov (Claude writes the prose; Syed reads, changes and owns it). Built from `00_core.md` section 4, the Results draft (`11_results_draft.md`), `notes/buckling_threshold_sources.md` and the freeze files (tag `freeze-2026-11-09`, ShellBench v0.3.0). Every number already appears in the Results draft and has, or is listed for, a row in `numbers.md`. No new literature claim is made without a source that has been opened; `[check]` marks the rest. Interpretive sentences are Claude's judgement [J] until Syed accepts them; they are listed at the end.

## 4.1 Why the seismic level does not reach the carbon

The result is a null, and it has a cause. In every one of the 168 designs, the thickness is set by linear buckling or by the 50 mm minimum, and the steel by the minimum ratio (Section 3.2). None of the three responds to the seismic level between 0 and 0.6 g. So carbon cannot follow Sa, and it cannot follow the form either, because the two forms differ by at most 0.7 % of the span (Section 3.1).

This holds for reinforced concrete shells of 10 and 20 m, square in plan, on corner or edge supports, sized to code checks under an equivalent static load. It does not hold, as far as we know, for shells whose material has no tensile capacity. There the form itself must keep the thrust inside the section, and a lateral load can make a gravity form infeasible; that is the setting in which Michiels and Adriaenssens developed seismic form-finding [check: confirm in the journal versions]. Reinforcement takes that job away from the form. The minimum steel ratio, which every shell carries anyway, covers the tension that the small lateral load adds.

A second reason is the four directions of shaking. A form found for one direction leans, as the S4 arch does (0.75 m at the crown at 0.3 g, Section 3.1). A form that must serve four opposite directions keeps the midrange of four leans, which keeps almost none of the lean. The seismic-aware strategy therefore converges back towards the gravity form. We see this as a property of the strategy, not of our code: any form that must carry reversing lateral load with one surface meets the same cancellation [J].

## 4.2 The strongest objection, and our answer

The strongest objection is that the comparison was set up so that it could not find a difference. If the seismic-aware form can only rise and never lean, and if linear buckling governs, then perhaps the study tested a weak strategy against a check that cannot see it.

We take this in two parts. First, the strategy. We used the method Michiels and Adriaenssens proposed for lateral load, extended to four directions and to a 3D network, and we checked our lateral-load code against the closed-form leaned parabola to 1e-9 (test S4). A one-direction form would lean more, but it would fail when the shaking reverses, so it is not a design option for a building. Second, the check. Linear buckling does respond to the form: at equal thickness, the seismic-aware form buckles at a 2-5 % lower load in the cells near λ ≥ 3 (Section 3.4). The check sees the form; the form is simply too close to the gravity form for the difference to cross one 5 mm thickness step in most cells. Where it does cross, the sign is not consistent. At λ ≥ 5, five cells favour the seismic-aware form, and at λ ≥ 3 two cells favour the gravity form. Both are the same step effect pointing in opposite directions.

So the null is not built into the design of the study [J]. A shell that the code checks pushed close to the boundary between two thickness steps would show a difference, and in a few cells it does. What the study shows is that such differences are smaller than the resolution of practical sizing, and that their sign depends on where the step falls, not on the strategy.

## 4.3 What does move carbon

For these shells the carbon is set by the support condition and by the buckling factor a designer chooses. Corner-supported shells carry 75-105 mm at 10 m and 185-265 mm at 20 m, edge-supported shells 50 mm everywhere (Table 4). Moving the buckling threshold from 5 to 3 or 8 moves corner-shell carbon by 19 to 29 %, against at most 0.4 % for the seismic level on the gravity form (Section 3.4).

This matters more than the null itself [J]. No code fixes the buckling factor for shells: ACI 318.2-14 requires only that instability be "precluded" (cl. 3.1.8), and the reduction-factor approach (Dulácska and Kollár, 1995) leaves the reductions for imperfection, creep and cracking to the designer. Read through that approach, our three thresholds correspond to combined reductions of 1.0, 0.6 and 0.375 under a safety factor of 3.0 (Section 2.5). The carbon of a corner-supported concrete shell therefore depends on an engineering judgement that is rarely reported. A study that compares shell forms, or shells against other roofs, should report its buckling factor and its sensitivity, as we do in Table 5.

For edge-supported shells the answer is simpler. They sit at the 50 mm minimum with a buckling factor far above any threshold (Section 3.2). Their carbon is set by the constructible minimum, so a lower minimum, for example from a thinner mesh layout or a different cover rule, would lower their carbon directly, and a different form would not.

## 4.4 What this means for design

For a designer of a reinforced concrete shell roof in the range studied, the message is practical. Form-find for gravity. Then check the seismic combinations. Sized to the same checks, the gravity form was feasible in all 84 of its designs, at a cost of resilience of 1.000-1.004 up to 0.6 g. Spend the design effort on the support condition, the buckling factor and the minimum thickness, because these set the carbon.

The method is the part that transfers beyond shells [J]. The study pre-registered its rules before any run, sized every design to the same code checks, compared strategies with a fixed decision rule, and asked which check governs before asking which form wins. That sequence separates a real carbon saving from a sizing artefact, and it applies to any structure in which a design strategy is meant to save material: the saving is real only if it changes the governing check.

## 4.5 Limitations

We state each limit with what would remove it.

1. **Linear buckling without imperfections.** Buckling governs every corner shell, and we used the linear factor with a safety threshold in place of a geometrically nonlinear analysis with imperfections. An imperfection-sensitive analysis could separate the two forms more than the linear factor does, because the seismic-aware form changes the curvature near the edges. A nonlinear buckling analysis of the governing cells, with an imperfection of 1/4 to 3/4 of the thickness as Dulácska and Kollár suggest (p. 317), would test this. The linear factor itself is sound: on a sphere it lies within 2 % of the classical value, and it is mesh-converged to 0.6 % (Section 3.6).
2. **Equivalent static load.** We applied the plateau spectral value as a uniform lateral acceleration. Every first period lies at or below T_g, so the load is on the plateau or conservative (Section 3.5), but higher modes and vertical excitation were not modelled. A response-spectrum or time-history analysis of the governing cells would remove this limit.
3. **One material, one plan, two spans.** Reinforced concrete C40, square plans, 10 and 20 m. Longer spans, heavier finishes and unreinforced shells are where we expect the null to break (Section 4.1). The code is open, so each of these is one change to the design space.
4. **Uniform thickness and net steel.** Each shell has one thickness, and steel is a net take-off without laps or waste. Both apply to both strategies alike, so they do not affect the comparison, but they affect the absolute carbon.
5. **A1-A3 only, one factor source.** Carbon covers product stages A1-A3 with GB/T 51366 factors and a ±25 % band. Every verdict holds at all four corners of the band, so the comparison does not depend on the factors; the absolute values do. Formwork is outside the boundary. It cannot change the comparison, because the soffit areas of the two strategies differ by at most 1.44 % (Section 3.6), but it would raise the absolute carbon by an amount that depends on its factor and its number of uses.
6. **The buckling threshold is a judgement.** We could not read the IASS (1979) recommendations, and neither source we read states the factor of 5. We therefore report it as an assumption and give the full study at 3 and 8 (Section 2.5, Table 5).

## Side notes for Syed (delete before submission)

- [J] sentences to accept, change or cut: "We see this as a property of the strategy, not of our code" (4.1); "So the null is not built into the design of the study" (4.2); "This matters more than the null itself" (4.3); "The method is the part that transfers beyond shells" (4.4).
- 4.1: the claim about Michiels and Adriaenssens' masonry setting is from their abstracts and thesis (`notes/michiels2017.md`). Confirm it in the J. IASS published version you saved (Zotero 2EPDR7PB) before keeping it.
- 4.1: "covers the tension that the small lateral load adds" rests on Section 3.2 (the seismic case adds at most 0.82 kg, 0.95 kg and 57.9 kg of steel). Keep the sentence only if you accept that reading.
- 4.5 item 5 (14 Nov): the unsourced clause "formwork is often the largest cost of a shell" was cut and replaced by the V5 result.
- No comparison with other published carbon figures for shells yet. That needs the documented literature search (`01_professor_test.md`), which is still open. Add one paragraph to 4.3 when it is done.
- C&S allows a combined Results and Discussion. If the editor or word count prefers it, 4.1 and 4.3 merge into Section 3 and 4.2, 4.4 and 4.5 stay as Discussion.
- AI-use declaration: this section was drafted by Claude from your results and rules; the Elsevier declaration must say so.
