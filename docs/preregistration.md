# ShellForm pre-registration

**Status: APPROVED 30 Oct 2026, before any form-finding run of the design space.** It was approved by Claude under the author's standing delegation of 30 Oct 2026 ("do not ask me ever. you do it based on the best that you think"). The author may reverse any choice by a dated amendment. After approval, changes are made only by a dated amendment at the end that says why.

Markers: [J] = Claude's judgement. [check] = read by Claude, still to be confirmed by the author in the source. [?] = still open, with the rule that closes it. Values from ShellBench are imported from the pinned tag (`src/shellform/pin.py`), never copied.

## 1. Research question

How much embodied carbon does seismic resilience cost in a form-found concrete shell, and does seismic-aware form-finding deliver it more cheaply than thickening a gravity-only shape?

## 2. Strategies

Both strategies use ShellForm's own 3D force density solver (`src/shellform/formfind.py`; section 8, S1b). ShellBench `floor-r1` form-finds a 2D vault curve, not a doubly curved shell, so it is the 2D cross-check, not the solver (decision P2 below).

**Thrust surfaces.** For a force density pattern q, the gravity form G has heights z_G. Under gravity plus a horizontal acceleration Sa in direction d (one of +x, -x, +y, -y), the admissible thrust surfaces of the same pattern scaled by 1/λ are T(d, λ): heights λ z_G, moved horizontally by -Sa λ z_G d (finding F1, `notes/michiels2017.md`). λ > 0 is free, because the horizontal thrust of a funicular is statically free.

**Envelope thickness.** For a mid-surface M, t_env(M, Sa) is twice the largest gap, measured normal to M (vertical gap times the cosine of M's slope), between M and the nearest admissible thrust surface. For each direction d, λ is chosen to minimise that gap, and the worst of the four directions governs. This is the lower-bound (safe theorem) requirement used by Michiels & Adriaenssens, applied to the four shaking directions [J].

1. **Gravity-only (strategy 1):** M = G, the gravity form of uniform q (corner supports: boundary edges at 4 q [J]). Size it at each Sa.
2. **Seismic-aware (strategy 2):** M = the midrange height, at each plan point, of the four thrust surfaces T(±x, λ*), T(±y, λ*) at the design Sa, that is halfway between the highest and the lowest of them, with λ* set so that M has the target rise (`src/shellform/strategies.py`). This is a form-found surface that includes the lateral load cases. It plays the role of the middle surface between Michiels' double layers [J; check against the IASS 2017 full text]. Size it at the same Sa.

The strategies differ only in the mid-surface. Checks, materials, the sizing rule and the carbon factors are identical. At Sa = 0, M = G for both (S1).

**Decision P1 (30 Oct, Claude):** a single sheared form (draft option a) suits shaking in one direction only. Averaging +x and -x shears without rescaling gives back G exactly. So strategy 2 is defined by the four-direction thrust-surface mean above (draft option c, refined). It is the simplest definition in which the lateral load changes the form [J].

## 3. Design space (168 sized designs)

| Variable | Levels |
|---|---|
| Plan | Square |
| Span L | 10 m, 20 m |
| Supports | 4 corner supports; continuous edge supports |
| Rise-to-span | 0.10, 0.15 (baseline), 0.20 |
| Strategy | gravity-only; seismic-aware |
| Plateau spectral acceleration Sa | 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 g |

Coded in `src/shellform/design_space.py`. Network for form-finding: 41 x 41 nodes [J]; mesh sensitivity at 61 x 61 (section 7).

Site markers on plots: the Panzhihua frequent earthquake, from ShellBench `seismic.alpha_max_frequent(7, 0.10)` times η2 = 1.0. The design and rare levels and one EN 1998-1 site are added only once they are read in GB 50011 Table 5.1.4-1 and EN 1998-1 [check]. Markers do not change any result.

## 4. Loads and materials

- **Form-finding load:** uniform load per unit plan area, with the lateral load as Sa times the same nodal weights (Michiels & Adriaenssens, C&S 2018 highlights: horizontal acceleration as a first-order approximation of seismic action). The form does not depend on the load magnitude once the rise is fixed.
- **Analysis loads:** shell self-weight at the ShellBench unit weight for reinforced concrete (spec X7); roof superimposed dead load and non-accessible roof live load from ShellBench (spec L2, L11); G_E = dead load only, because GB 50011 Table 5.1.3 takes no roof live load into the representative gravity load, as ShellBench's anchor does [check].
- **Seismic action:** equivalent static horizontal load Sa x G_E in each of +x, -x, +y, -y, separately. Shells are short-period, so they sit on the plateau (checked by S5). Vertical seismic action is not included (as in ShellBench).
- **Combinations:** ShellBench `combinations.CODE_SEISMIC_COMBINATIONS` (1.3 G_E + 1.4 E_h, GB 55002-2021, flag D21) and its gravity combinations.
- **Materials:** C40 and HRB400 design values imported from ShellBench `checks` (f_c, f_t, f_y) and E_c from the ShellBench spec.

## 5. Checks (pass/fail for sizing)

| Check | Rule | Threshold and source |
|---|---|---|
| Concrete compression | principal compressive stress <= f_c | ShellBench f_c |
| Tension | A_s = T / f_y, at least ρ_min | ρ_min = max(0.15 %, 45 f_t/f_y) for slabs, as ShellBench's floor concept [J: slab rule applied to shells] |
| Linear buckling | load factor λ_LBA >= 5 | [J], from the reduction-factor approach of the IASS Recommendations for reinforced concrete shells (1979) and Dulácska & Kollár (1995), which reduce the linear buckling load for imperfections, creep and cracking, then apply a safety factor of 1.5 to 3.0 [check]. Sensitivity at 3 and 8 |
| Deflection | <= L/300 under the quasi-permanent combination | GB 50010-2010 (2015) Table 3.4.3, roof members with l0 > 9 m, printed p. 11 [check] |
| Minimum thickness | t >= 50 mm | Cover to mesh on both faces, as in ShellBench's floor concept section 4 [J] |

**t_env is reported, not checked.** It is the thickness an unreinforced shell would need to keep a compression-only path (Michiels' masonry criterion). The shells here are reinforced, so tension and bending are carried by the checks above; t_env explains the results but does not size them [J].

**Sizing rule:** the smallest thickness, in 5 mm steps from 50 mm, that passes every check in every combination. Uniform thickness per shell [J]. A design that fails at every thickness up to L/50 is reported as infeasible, not dropped.

## 6. Carbon

A1-A3 of concrete and reinforcement, from ShellBench `data/carbon_factors.csv` (GB/T 51366-2019 Table D.0.1; C40 = 340 kgCO₂e/m³ is ShellBench's interpolation [J]).

**Decision P3 (30 Oct, Claude):** ICE is not used. ShellBench's D29 found that its licence forbids distributing its values, and ShellForm's repository is public. Instead, a **factor band**: every result is recomputed with the concrete and steel factors each at ±25 %, independently, which gives four corners [J]. Carbon is reported per m² of plan area.

## 7. Decision rules (written before any result)

- **Cost of resilience:** for each (span, supports, rise, strategy), carbon at Sa divided by carbon at Sa = 0.
- **Which strategy is cheaper:** at each (span, supports, rise, Sa), the strategy with the lower carbon. A difference smaller than 5 % is reported as "no meaningful difference" [J].
- **Headline claim** ("seismic-aware form-finding is cheaper"): made only if it holds at all four corners of the factor band, and at rise-to-span 0.15 for both supports, at every Sa >= 0.2 g. Otherwise the result is reported as conditional, naming the cases where it holds.
- **Robustness:** the headline is re-checked at λ_LBA = 3 and 8, and with a 61 x 61 network. A conclusion that flips is reported as sensitive.
- No result is dropped. Infeasible designs are reported as infeasible.

## 8. Validation (tests S1-S5)

| Test | Proves | Pass |
|---|---|---|
| S1 Zero lateral load | Strategy 2 with Sa = 0 equals the gravity form | Machine precision |
| S1b 2D limit | ShellForm's solver gives the exact nodal parabola for a chain (done), the membrane centre value 0.0737 p L²/T for an edge-supported net (done, within 1 %) [check], and ShellBench `floor-r1`'s vault curve once tagged | Exact; 1 %; 1 % |
| S2 Nodal equilibrium | Every free node in equilibrium under gravity + lateral loads | Residual < 1e-9 of the load |
| S3 Rotation | Rotating all loads and supports rotates the form by the same angle | Error < 1e-9 |
| S4 Published case | One Michiels & Adriaenssens arch (C&S 2018: rise-to-span 1/4, 0.3 g) from its stated inputs | Tolerance fixed here once the full text is read [?]. If the full text is not available by 4 Nov, S4 is replaced by the closed-form lean of a parabolic arch under uniform horizontal acceleration, and the paper says so |
| S5 Plateau | First-mode period of every sized design below Tg = 0.35 s (ShellBench B5), from a CalculiX modal run | Any failure reported with its real spectral value |

The shell analysis uses ShellBench's CalculiX wrapper (`floor-r2`, validated on the Scordelis-Lo roof and the pinched hemisphere within 2 %), which ShellForm cites.

## 9. Freeze

Code and analysis are frozen on 10 Nov 2026 (commit hash recorded here). Results for the paper come from one run after the freeze.

## Amendments

**30 Oct 2026 (Claude, under delegation), made before any design-space run.** Compared with the 28 Oct draft: P1 (strategy 2 defined as a four-direction thrust-surface mean, plus the envelope check), P2 (ShellForm's own 3D solver, with floor-r1 as the 2D cross-check), P3 (ICE replaced by a ±25 % factor band). Thresholds set: λ_LBA 5 (3, 8), L/300, 50 mm, 5 mm steps, L/50 infeasible limit, 5 % band.

**30 Oct 2026, later the same day (Claude, under delegation), still before any design-space run.** While writing the unit tests on 10 m test nets (not design cases), two definitions were corrected: (1) strategy 2 uses the midrange, not the mean, of the four thrust surfaces, because the midrange is the centre of the band that must hold all four; (2) t_env is measured normal to M and is reported, not used as a pass/fail check, because it is a criterion for unreinforced shells. In those tests, the strategy 2 surface changed t_env by less than 4 % (`notes/michiels2017.md`, F2). This was seen before the change. No definition was tuned to make strategy 2 look better, and the 5 % decision rule stands.

**31 Oct 2026 (Claude, under delegation), before any design-space run.** Two additions from the first CalculiX run on one shell (`notes/day03_one_shell.md`): (1) **D3-1** [J]: corner-supported forms use a boundary force density set by bisection so the free edge insets by 0.10 × span at mid-edge (factor 18.5, the same for all spans and rises, because plan equilibrium does not depend on q scaling). With equal force densities the free edges pulled in by 0.24 × span and the shell kept only 38 % of its plan area, which is not a buildable roof. The 0.10 value is a judgement, and it is reported with the results. (2) Section 8 names ShellBench's `floor-r2` CalculiX wrapper. It is not tagged yet, so ShellForm writes its own S8R deck (`src/shellform/fe.py`). When `floor-r2` is tagged, both are run on the same shell and the difference is reported; ShellBench's wrapper is used for the results if they differ by more than 2 %. Neither change was chosen to favour either strategy: both strategies use the same supports and the same rule.

**1 Nov 2026 (Claude, under delegation), written before the first sizing run of the design space.** ShellBench v0.1.0 was tagged on 1 Nov, and the pin moved to it. Choices needed to turn section 5 into code (`src/shellform/sizing.py`, `notes/day04_sizing.md`):
(1) **D4-1** [J]: the seismic case is run in +x only. Both strategies give forms that are symmetric under the mirror and 90° rotations of the square plan, so +x stands for all four directions (checked by `tests/test_sizing.py`, to 0.1 %).
(2) **D4-2** [J]: the compression check leaves out support zones of radius 0.2 × span around the four plan corners, and reports the stress there separately. Linear-elastic stresses at point supports are singular: in the mesh check the peak compression outside a 0.05 L zone rose from 12 to 19 MPa between 41 and 61 nodes per side, while outside 0.2 L it changed by 14 %. These zones are taken as locally thickened, and their extra concrete is to be counted in the carbon step.
(3) **D4-3** [J]: the deflection limit uses the characteristic combination (live factor 1), not the quasi-permanent one, because the quasi-permanent live factor is not in ShellBench v0.1.0. This is an upper bound on the quasi-permanent deflection.
(4) **D4-4** [J]: the thickness grid is searched by bisection, because every check gets easier as the thickness grows. The step below each answer is always run and fails.
(5) Face stresses are extrapolated from CalculiX's two Gauss planes (checked on a clamped plate: 0.1 % from beam theory). T1 is scaled by the square root of (concrete + SDL mass) / concrete mass, because the frequency step carries the concrete mass only.
Poisson's ratio of concrete is still a [?] placeholder (0.2): ShellBench v0.1.0 does not give it. All results until it is replaced are provisional. None of these choices was tuned on results: they were fixed from the mesh check on one gravity form before the 84 designs were run, and they apply to both strategies alike.

**1 Nov 2026, later the same day (Claude, under delegation), written after the 84 designs were run.** Two corrections to the amendment above. Neither changes a thickness.
(1) **Poisson's ratio.** The amendment above says ShellBench v0.1.0 does not give it. That is wrong: it is in the pinned clone, `notes/gb50010_design_values.md`, row ν_c (cl. 4.1.5). `src/shellform/inputs.py` now reads it there in place. The value equals the old placeholder, so the regenerated results keep every thickness and governing check. It no longer makes the results provisional; the missing steel and carbon still do.
(2) **D4-5** [J]: SDL and roof live load act per unit plan area, as the code on main already did. The amendment above did not record this. It is recorded now, and because it is recorded after the results were seen, it is kept unchanged. Reasons: spec L2 and L11 are stated for a flat roof, the form-finding load is per plan area (section 3), and changing the basis after seeing results is the tuning this document exists to prevent. Applying the same loads per surface area is the other reasonable reading, since finishes follow the shell, and it is slightly heavier. Measured on the 10 m corner shell at rise 0.15 with the same code: surface area is 5.1 % above plan area and λ falls by about 2 %. The seismic form at Sa 0.3 g then fails at 85 mm (λ 4.947 against 5.061) and passes at 90 mm, the same as the gravity form. So the 85 against 90 mm difference between the strategies depends on this choice, and it is not evidence of a strategy effect.

**1 Nov 2026, later again (Claude, under delegation).** Two code readings, after the results. No thickness changes. (1) D4-5 now has a code basis for live load: GB 50009-2012 cl. 5.3.1 (printed p. 18) gives the roof live load on the horizontal projection. The plan-area choice for SDL stays [J]; the sensitivity recorded above changed SDL and live load together, so it overstates the live-load part. (2) D4-3 stands. GB 50009-2012 Table 5.3.1 gives ψq = 0.0 for a non-accessible roof, so the characteristic combination stays an upper bound on the pre-registered quasi-permanent one. ψq is not in ShellBench v0.1.0, and ShellForm does not hard-code it. Read from a scan hosted by Zhejiang Gongshang University, not the author's own copy.

**2 Nov 2026 (Claude, under delegation), Day 5: steel, support zones and carbon.** Section 5 says "A_s = T / f_y, at least ρ_min" and section 6 names the carbon basis; these choices turn them into code (`src/shellform/steel.py`, `src/shellform/carbon.py`, `notes/day05_steel_carbon.md`). They were written before the 84-design run. A trial on five designs came first; it found one bug (the 45 f_t / f_y term was read as a fraction instead of a percentage, giving 100 times the minimum steel), which was fixed. No rule was changed after that trial.
(1) **D5-1** [J]: two orthogonal bar directions per element, along the grid lines of the network (plan x and y).
(2) **D5-2**: the bar demand at each depth is σ_nn + |τ_12| (tension positive), the orthogonal reinforcement rule for in-plane stress (EN 1992-1-1:2004 Annex F, expressions (F.2) and (F.3) [check]), applied layer by layer with the linear profile between the two faces; T is the integral of its positive part over the thickness, A_s = T / f_y. The biaxial-compression relief is not taken [J].
(3) **D5-3**: ρ_min = max(0.15 %, 45 f_t / f_y) per direction, everywhere, read in place from ShellBench `docs/floor_concept.md` (GB 50010 Table 8.5.1 note 2). This is the slab rule of section 5, now stated as applying in both directions over the whole shell [J].
(4) **D5-4** [J]: the steel of the -x, +y and -y seismic cases is the +x field mapped by the eight symmetries of the square (follows D4-1); the design steel is the largest over all images and load cases.
(5) **D5-5** [J]: support-zone concrete (D4-2): an element in a corner zone whose face compression exceeds f_c is thickened to t σ_c / f_c, and the extra concrete is counted. Steel is a net take-off (no laps, anchorage or waste), the same for both strategies.
(6) The carbon factors are read in place from ShellBench `data/carbon_factors.csv` with `shellbench.carbon.read_factors`. Every row there is marked "author to confirm", so all carbon results stay provisional until the author confirms them in ShellBench.

**3 Nov 2026 (Claude, under the author's delegation of 3 Nov: "approve everything just finish all"), written after the 10 m and 20 m results were seen. The code fix was made before the first 20 m run; it follows from section 6 alone and was not chosen on any result.** Section 6 says carbon is reported per m² of plan area. The Day 5 code divided by span², which is the plan area only for edge-supported shells. Corner-supported shells have inset free edges (D3-1) and cover 73.34 m² of plan at 10 m, so their per-m² carbon and steel read 1.36 times low. This was a code error against section 6, not a new choice, and it was found after the results were seen (2 Nov). It is corrected: `shellform.fe.plan_area` gives the projected area of the shell from the same triangles as `surface_area`, and both scripts use it. The same error sat in the T1 scaling of `scripts/day04_size_10m.py`, which used span² for the SDL and live-load mass; it now uses the plan area too. Effect at 10 m, measured: no thickness, governing check, buckling factor or steel mass changes; corner T1 falls by 5.3 to 6.2 % (T1 enters only S5, T1 < Tg = 0.35 s; the longest T1 at 10 m is now 0.184 s, so S5 still holds); corner carbon per m² rises from 24.9-33.4 to 34.0-45.5 kgCO₂e/m², edges unchanged. Strategy verdicts, relative differences and costs of resilience are identical, because both strategies of a cell share the same plan area. The comparison of corners with edges changes. The author may reverse this by a later dated amendment.

**4 Nov 2026 (Claude, under the author's standing delegation), Day 7. The case and the 1e-9 tolerance were set in `scripts/day07_s4.py` before the S4 run; this text was written just after it, the same morning, and nothing was changed on seeing the result.** Section 8 gives S4 a fallback if the full text of Michiels & Adriaenssens (C&S 2018) is not available by 4 Nov. It was not: no copy is in the repo or the project files, and the ResearchGate request is still open. So the fallback is now S4, as section 8 already says; nothing in section 8 is changed. This entry only fixes what section 8 left open. (1) **Case:** a 2D chain with 40 equal plan segments (the 41 nodes per line of the design networks), at both design spans (10 m, 20 m); the pre-registered case is rise-to-span 1/4 at 0.3 g, and the eight other pairs of the C&S abstract (rise-to-span 1/2, 1/4, 1/8 at 0.15, 0.3, 0.45 g) are run too. (2) **Closed form:** a funicular under parallel loads is a parabola with its axis parallel to the load, so x(s) = s − Sa z(s), z(s) = 4 f s (L − s) / L² (`shellform.checks.leaned_parabola`), with support thrusts H_g ∓ Sa W / 2, H_g = w L² / (8 f h), and vertical reactions W / 2 (`leaned_arch_reactions`). (3) **Tolerance:** every node position (divided by span) and every reaction (divided by the total weight W) within 1e-9, and S2 below 1e-9. The closed form is exact for nodal loads at equal plan spacing, so any error above round-off is a code fault. (4) **S4b** [J]: the same comparison on every design shell family with a lateral load (72 forms: 2 spans, 2 supports, 3 rises, Sa 0.1-0.6 g, 41 × 41), against the gravity form sheared by −Sa z. (5) S4 now checks ShellForm's lateral-load code against statics. It does not reproduce Michiels & Adriaenssens' algorithm or results, and the paper says so. If the full text arrives before the freeze (10 Nov), their published arch is run as an extra check and reported beside S4; it does not replace it [J].

**6 Nov 2026 (Claude, under the author's standing delegation), Day 9. Written after the λ 3 and λ 8 runs had finished and before the 61 × 61 run ended; nothing in sections 1-8 is changed.** Section 7 names three robustness checks; this entry records how they were run (`src/shellform/sensitivity.py`, `notes/day09_sensitivity.md`). (1) **D9-1** [J]: each check (λ_LBA ≥ 3, λ_LBA ≥ 8, a 61 × 61 network) is run on all 168 designs, not only on the headline scope, with one setting changed and everything else as in the baseline (`results/batch_all.csv`, Day 8). (2) **D9-2** [J]: "a conclusion that flips" means a cell whose verdict changes at any band corner, or a change of headline status; all such cells are reported. (3) **D9-3**: the factor band is not rerun, because its four corners are already in every row (P3). (4) **D9-4** [J]: ShellBench v0.2.0 was tagged on 6 Nov; its design inputs, ρ_min and GB/T 51366 factors are identical to v0.1.0 for ShellForm. The Day 9 runs stay on v0.1.0 so that they share the baseline's inputs; the pin moves to v0.2.0 before the freeze run. `shellform.carbon.FACTOR_SET` now names the GB/T 51366 set explicitly, because v0.2.0's factor file holds a second set; this is not a change of section 6, which already names one factor set. The definition of D9-2 was written into the code before the λ results were read, and none of these choices was changed after seeing them.

**7 Nov 2026 (Claude, under the author's standing delegation), Day 10. Written after the measurement below and before the corrected runs were started; no threshold, load, grid or rule of sections 1-8 changes.** (1) **Pin.** ShellBench v0.2.0 (tagged 6 Nov) is now the pin. The 168 designs rerun at v0.2.0 match the Day 4-6 record with 0 mismatches (`results/batch_pinmove_v020*`). (2) **Cross-check of the 31 Oct amendment.** ShellBench v0.2.0 carries its CalculiX shell wrapper (`shellbench.shellfe`, ShellBench Day 24). It and `src/shellform/fe.py` were run on the same four gravity shells (10 m and 20 m, corners and edges, rise 0.15, sized thickness, self-weight): largest displacement identical; first buckling factor within 0.26 % when both ask CalculiX for the same number of factors (`results/fe_crosscheck.csv`). This is inside the 2 % limit, so `fe.py` stays. (3) **D10-1.** The cross-check showed that CalculiX's buckling eigensolver returns a high lowest factor when only one factor is requested, as the sizing did on Days 4-9. Measured at the sized thickness of every design within 3 % of its threshold (149 designs, `results/buckling_modes_check.csv`): up to 0.26 % high at λ 5 (baseline), 0.08 % at λ 3, 0.17 % on 61 x 61 and 3.6 % at λ 8; with 2 or more factors requested the value is converged (checked at 2, 4 and 8). Seven sized designs would fail their threshold with the converged value: one baseline design (L10-corners-r0.15-seismic-sa0.6, λ 4.9994 at 85 mm) and six at λ 8. This is a numerical error of the solver set-up, not a design choice, so it is corrected: every sizing run now requests 4 buckling factors (`sizing.N_BUCKLE_SIZING`) and the baseline and all three section 7 variants are rerun. The fix applies to both strategies alike and was not chosen on its effect on any verdict. It was adopted before the corrected runs, but its likely effect on the baseline could be foreseen from the measurement: the one failing baseline design is a seismic-aware 85 mm shell in one of the six "seismic cheaper" cells, so that cell is expected to become "no meaningful difference". The Day 4-9 files stay in the repository's history; results quoted before 7 Nov are superseded by the 7 Nov files.

**8 Nov 2026 (Claude, under the author's standing delegation), Day 11. Citation detail only; no rule, threshold, load or result changes.** D5-2 cites EN 1992-1-1:2004 Annex F, expressions (F.2) and (F.3), marked [check]. They have now been read in the full text (BS EN 1992-1-1:2004, `C:\Users\ASUS\Papers\EN_1992-1-1_2004.pdf`): F.1(4), (F.2)-(F.7), printed p. 211 (PDF p. 213). The expressions and the condition σEdx ≤ |τEdxy| (compression positive) match D5-2 and `src/shellform/steel.py`, and the relief (F.5)-(F.7) is the one D5-2 does not take. The [check] in D5-2 is closed by this entry: checked by Claude; author to confirm.
