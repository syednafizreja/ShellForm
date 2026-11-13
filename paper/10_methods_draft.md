# 2. Methods (draft 1, 10 Nov 2026)

Written by Claude in Syed's voice at his request of 10 Nov ("it's supposed to be done by itself; follow the same style"), from `02_methods_outline.md`, `09_drafting_kit.md`, the pre-registration and the freeze files. Syed reads, changes and owns it. Every number has a row in `numbers.md` or a table in `paper/tables/`. `[check]` = source not yet opened by Syed; `[?]` = value still missing; `[J]` in the side notes = Claude's judgement. Side notes in *italics* are for Syed and are deleted before submission.

## 2.1 Overview and pre-registration

We compare two ways of finding the form of a reinforced concrete shell: a gravity-only form and a seismic-aware form. Each form is sized to the same code checks, and we measure its embodied carbon. The question is whether the seismic-aware form changes the carbon of a shell that meets those checks, and by how much.

The study was pre-registered on 30 October 2026, before any design was run. The pre-registration fixed the design space, the loads, the checks, the carbon basis, the decision rules and the validation tests with their tolerances. Every later change is a dated amendment that says why it was made and whether it was written before or after the results it affects. The amendments are listed in Appendix A [?].

All results come from one run of the frozen code (git tag `freeze-2026-11-09`). The code is pinned to ShellBench v0.3.0, the author's earlier validated model, from which every material value, load, code factor and carbon factor is read in place (Hasib, 2026 [ShellBench, DOI 10.5281/zenodo.23851676]). ShellForm copies no ShellBench value. The code, results and figures are archived as ShellForm v0.1.0 (DOI 10.5281/zenodo.24084111).

*Side note: Appendix A = the amendments table from `docs/preregistration.md`. Decide whether it goes in the paper or the supplement.*

## 2.2 Design space

The design space has 168 sized designs (Table 1). Each one is a square-plan shell with a span of 10 m or 20 m, supported either at its four corners or along its four edges. The rise-to-span ratio is 0.10, 0.15 or 0.20. Each shell is found by one of the two strategies and sized for one of seven plateau spectral accelerations, Sa = 0 to 0.6 g in steps of 0.1 g.

The corner-supported shells need one more choice. With equal force densities everywhere, their free edges pulled in by 0.24 × span and the shell kept only 38 % of its plan area, which is not a usable roof. We therefore set the force density of the boundary edges so that each free edge is drawn in by 0.10 × span at mid-edge. This value is a judgement; it was fixed on one shell before the design space was run, and it is the same for every span and rise.

## 2.3 Form-finding

We find the forms with our own three-dimensional force density solver on a 41 × 41 network. The load is uniform per unit plan area. A seismic action is added, as in Michiels and Adriaenssens (2018) [check], as a horizontal acceleration Sa applied to the same nodal weights.

This load has a simple consequence. Under a uniform horizontal acceleration Sa in x, the force density solution is a shear of the gravity form: x = x_g − Sa z_g, with y and z unchanged. Our solver reproduces this to 1 × 10⁻¹² m. A shell form-found for one direction of shaking therefore leans in that direction, as the arches of Michiels and Adriaenssens (2018) do.

An earthquake can come from any direction, so a form found for +x alone is not a design. The seismic-aware strategy finds four thrust surfaces, for Sa in +x, −x, +y and −y, scales each to the target rise, and takes their midrange at every node. We chose the midrange, not the mean, because it is the centre of the band that has to contain all four thrust surfaces. The gravity-only strategy uses the form under gravity alone. Both forms have the same rise and the same supports, and at Sa = 0 they are identical (test S1).

For each form we also compute t_env, the thickness of the band that contains every thrust surface. This is Michiels' criterion for unreinforced masonry. Our shells are reinforced, so tension and bending are carried by the checks of Section 2.5, and t_env is reported but not used to size them.

## 2.4 Structural analysis and loads

Each form is analysed with CalculiX 2.21 as a shell of eight-node S8R elements on the same 41 × 41 network: a static analysis for stresses and deflection, a frequency analysis for the first period T1, and a linear buckling analysis for the load factor λ. We request four buckling factors in every run and take the lowest, because with one factor requested the eigenvalue solver could return a factor up to 3.6 % too high.

We checked this solver against ShellBench's own CalculiX wrapper on four gravity shells (both spans and both supports, rise 0.15). The largest displacements were identical, and the first buckling factors agreed within 0.26 %, against a tolerance of 2 % (Table 3).

The loads and materials are listed in Table 2 with their sources. The shells are C40 concrete with HRB400 reinforcement. Superimposed dead load and roof live load act per unit plan area, because the code gives roof live load on the horizontal projection (GB 50009-2012, cl. 5.3.1 [check]) and the form-finding load is per plan area too. The representative gravity load G_E for the seismic case takes no roof live load (GB 50011-2010, Table 5.1.3 [check]).

The seismic action is an equivalent static horizontal load Sa × G_E. This is valid only if every sized shell sits on the plateau of the design spectrum or below it, which we test (S5). The seismic combination is 1.3 G_E + 1.4 E_h (GB 55002-2021, cl. 4.3.2 [check]). Both strategies give forms that are symmetric under the mirrors and quarter turns of the square plan, so we run the seismic case in +x only and map the result to −x, +y and −y. A test confirms the symmetry to 0.1 %.

## 2.5 Checks and sizing

A shell passes if it meets five checks in every load combination: principal compressive stress at most f_c; linear buckling factor λ at least 5; deflection at most L/300 (GB 50010-2010, Table 3.4.3 [check]); thickness at least 50 mm; and reinforcement A_s = T / f_y, with at least the minimum ratio ρ_min = max(0.15 %, 45 f_t / f_y) in each direction (GB 50010-2010, Table 8.5.1, note 2 [check]).

Two of these limits are our judgement, and we say so. Codes require shell instability to be precluded but give no factor (ACI 318.2-14, cl. 3.1.8). The factor of 5 follows the reduction-factor approach for reinforced concrete shells (IASS Working Group No. 5, 1979, cited after ACI 318.2R-14, R3.1.8). In this approach the linear buckling load is multiplied by reduction factors for imperfections, creep and cracking, and the result must exceed the design load times a safety factor of 1.5 to 3.0, which rises with slenderness (Dulácska and Kollár, 1995, p. 318 and Table 3). A linear factor λ on the factored load must therefore cover the safety factor divided by the product of the reductions. With the buckling-governed safety factor of 3.0, λ ≥ 3 assumes no reduction at all, λ ≥ 5 a combined reduction of 0.6, and λ ≥ 8 one of 0.375. We do not compute these reductions for each shell, so the baseline of 5 is a stated assumption, and we repeat the whole study at λ ≥ 3 and λ ≥ 8 (Section 2.9). The 50 mm minimum leaves cover to a reinforcement mesh on both faces.

Stresses at point supports are singular in a linear elastic model. We therefore leave zones of radius 0.2 × span around the four corners out of the compression check. Inside those zones, any element whose face compression exceeds f_c is thickened locally to t σ_c / f_c, and the extra concrete is counted in the carbon. The deflection check uses the characteristic combination, which is an upper bound on the quasi-permanent one, because the quasi-permanent live factor for this roof is zero (GB 50009-2012, Table 5.3.1 [check]).

Each shell has one uniform thickness. We find the smallest thickness, in 5 mm steps from 50 mm, that passes every check, by bisection; the step below each answer is always run and always fails. Steel is designed in two orthogonal directions along the network lines, layer by layer through the thickness, with the in-plane rule of EN 1992-1-1:2004, Annex F, expressions (F.2) and (F.3), without the relief for biaxial compression. Steel is a net take-off, without laps or waste, and the same rule applies to both strategies.

## 2.6 Embodied carbon

We count the A1-A3 carbon of concrete and reinforcement with one factor set, GB/T 51366-2019, Table D.0.1, read from ShellBench (Table 2). We do not use the ICE database, because its licence does not allow its values in a public repository. To show how much the factors matter, every result is recomputed with the concrete and steel factors each moved by ±25 %, independently, which gives four band corners. Carbon is reported per m² of plan area.

## 2.7 Decision rules

These rules were written before any result. The cost of resilience is the carbon of a design at Sa divided by its carbon at Sa = 0, for the same span, supports, rise and strategy. At each span, support type, rise and Sa, the cheaper strategy is the one with the lower carbon, but a difference smaller than 5 % is reported as no meaningful difference. The headline claim, that seismic-aware form-finding is cheaper, is made only if it holds at all four band corners, at rise 0.15, for both support types and at every Sa ≥ 0.2 g. No design is dropped; an infeasible design is reported as infeasible.

## 2.8 Validation

Five tests check the method, with tolerances fixed in the pre-registration (Table 3). S1 checks that the seismic-aware form at Sa = 0 is the gravity form. S2 checks nodal equilibrium under gravity and a 0.6 g lateral load. S3 checks that rotating every load and support rotates the form by the same angle. S5 checks that the first period of every sized design lies at or below the characteristic period T_g = 0.35 s, so that the plateau load applies.

S4 was meant to reproduce a published arch of Michiels and Adriaenssens (2018) from its stated inputs. We could not read the full paper in time, so, as the pre-registration allowed, S4 compares our solver with the closed-form lean of a parabolic arch under a uniform horizontal acceleration. S4 therefore checks the solver, not agreement with the published forms. All five tests pass (Table 3).

After the freeze we added five checks of the analysis chain. They were not pre-registered, and they change no result (pre-registration amendment of 14 Nov 2026). (V1) A complete sphere under uniform external pressure, solved with the same S8R elements and buckling step as the shells, against the classical value p_cr = 2E/√(3(1 − ν²)) (t/R)² (Zoelly; Timoshenko and Gere 1961 [check]). We used R/t = 50 and 100 and five meshes, with a limit of 3 %. (V2) Eight designs, both spans and supports at rise 0.15, refined from 21 to 81 nodes per side at their frozen thickness, with a limit of 1.5 % on λ1 and on the SLS deflection between the two finest networks. (V3) The residual of the assembled force density system, max |D x_f − (p_f − D_f x_x)|, with unit nodal weights and a limit of 10⁻¹⁰ N. (V4) The membrane share of strain energy, U_m/U, of every sized design under each ULS case, from the face stresses: with stress linear through the thickness, U = t u(σ_m) + (t/3) u(σ_b), and transverse shear is left out. (V5) A formwork (A5) term φ A_fw added to both strategies, with A_fw the soffit area and φ = F/N for any factor F and number of uses N. The relative difference then lies between the carbon difference and the area difference for every φ ≥ 0, so a verdict can move only if the soffit areas differ by 5 % or more. ShellBench holds no formwork factor, so V5 needs none.

## 2.9 Sensitivity

The pre-registration named three checks on the result. Each changes one setting and keeps everything else as in the baseline: a buckling threshold of λ ≥ 3, a threshold of λ ≥ 8, and a finer 61 × 61 network for both form-finding and analysis. We ran each check on all 168 designs, not only on the headline scope, so that any other verdict that moved would also show. A conclusion is sensitive if any cell's verdict changes at any band corner, or if the headline status changes.

## 2.10 Reproducibility

One script reruns every result from the frozen code, and each figure and table is built by a script from the result files. Every result file, figure and table names the ShellBench tag it used. The design explorer in the repository shows all 168 designs; it is a repository asset, not a figure of this paper.

*Side notes for Syed: (1) Section 2.4: name the CalculiX version only once; the laptop runs 2.23 and the record check shows both agree. (2) The [check] marks are the readings still owed. The buckling-factor sources were opened on 11 Nov (`notes/buckling_threshold_sources.md`); confirm pp. 316-319 of Dulácska & Kollár yourself. (3) Reference style follows the C&S Guide for Authors at submission. (4) Table 3, S2 and S3 (decided 13 Nov under your standing delegation [J]): the last digits differ between machines (cloud 1.4e-11 and 5.4e-16; laptop 1.2e-11 and 6.5e-16), so the table keeps the frozen cloud values (add a footnote naming the cloud run when the table is typeset), and the text says only "at round-off level, below 1e-10". (5) [J] Section 2.5: the reading of λ 3 / 5 / 8 as combined reductions of 1 / 0.6 / 0.375 under a safety factor of 3.0 is Claude's derivation from Dulácska & Kollár, not a statement in either source. Accept or cut.*
