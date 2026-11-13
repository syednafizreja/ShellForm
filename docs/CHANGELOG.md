# Changelog

Dated record of what changed, newest first. The day-by-day working log is [LOG.md](../LOG.md); the handover between sessions is [handoff.md](handoff.md).

## 15 Nov 2026

Release v0.2.0 (published 13 Nov 2026 by the calendar; the project's day labels run ahead of it). Long-term reproduction: exact environment in `environment-lock.yml`, SHA-256 checksums of every result and figure in `SHA256SUMS`, and `docs/REPRODUCE.md` (archives, versions, verification without rerunning, fallbacks when a dependency has gone). Package version set to 0.2.0.

Repository tidy-up: README rewritten as a landing page; this changelog split out of it; the design explorer served on GitHub Pages; CITATION.cff and repository metadata completed; project rules moved to `CONTRIBUTING.md`; assistant tool names replaced by "the assistant" in notes and drafts (the manuscript's AI-use declaration still names the tool; dated wording amendment in the pre-registration). No code under `src/` and no result changed.

## 14 Nov 2026 (check window, day 2)

Manuscript assembled for Computers & Structures (`paper/manuscript/`), with supplement, highlights and a self-review (`paper/16_self_review.md`). Drafts 10-15 superseded.

## 14 Nov 2026 (check window, day 1)

five verification add-ons beside the frozen record, with no frozen setting or result changed ([notes/day17_verification.md](../notes/day17_verification.md)). A complete sphere under pressure buckles within 2.0 % (R/t 50) and 1.3 % (R/t 100) of the classical value in the same CalculiX path that sizes every shell; λ1 changes by at most 0.6 % between 61 and 81 nodes per side; the force density residual is below 2.5e-11 N; 76-100 % of the strain energy is membrane energy; no formwork factor or reuse count can move a verdict across the 5 % rule. New Fig. 6 (carbon against λ1, with the Pareto front) and Fig. S1. Cloud pytest 125 passed.

## 13 Nov 2026

manuscript draft 1 complete. Documented literature search ([paper/13_literature_search.md](../paper/13_literature_search.md)); Introduction ([paper/14_introduction_draft.md](../paper/14_introduction_draft.md)); title options, Abstract (246 words), highlights and Conclusions ([paper/15_abstract_conclusion_draft.md](../paper/15_abstract_conclusion_draft.md)). The author checks every section 14-17 Nov. No code under `src/` and no result changed.

## 11 Nov 2026

sources for the buckling threshold read ([notes/buckling_threshold_sources.md](../notes/buckling_threshold_sources.md): Dulácska & Kollár 1995, ACI 318.2-14 cl. 3.1.8); Methods 2.5 rewritten; Discussion draft 1 ([paper/12_discussion_draft.md](../paper/12_discussion_draft.md)). The pin stays at ShellBench v0.3.0, because v0.4.0 changes only plotting code in the modules ShellForm imports. Cloud pytest 101 passed.

## 10 Nov 2026

manuscript tables built by script from the freeze record (`python scripts/day14_paper_tables.py`, Tables 1-5 and S1 in [paper/tables/](../paper/tables/)); drafting kit ([paper/09_drafting_kit.md](../paper/09_drafting_kit.md)); draft 1 of Methods and Results ([paper/10_methods_draft.md](../paper/10_methods_draft.md), [paper/11_results_draft.md](../paper/11_results_draft.md)), which the author checks 11-13 Nov. Laptop re-run: pytest 101 passed, `results/` unchanged. No code under `src/` and no result changed.

## 9 Nov 2026 (release)

v0.1.0 tagged and published on GitHub; Zenodo DOI [10.5281/zenodo.24084111](https://doi.org/10.5281/zenodo.24084111) (all versions [10.5281/zenodo.24084110](https://doi.org/10.5281/zenodo.24084110)), added to `CITATION.cff` and the paper files. Inter bold-italic font fallback fixed in `style.py` (no plotted number moved). 94 tests.

## 9 Nov 2026 (evening)

premium-quality pass. One visual system for figures and explorer ([docs/visual_style.md](visual_style.md)); explorer rebuilt (offline, dark theme, 84-cell matrix, table view); Figs. 1-5 restyled with every plotted number unchanged; `tests/test_visual_style.py`. 93 tests.

## Day 13 (9 Nov 2026)

design explorer with the frozen results ([explorer/index.html](../explorer/index.html), open it in a browser); v0.1.0 release prepared ([docs/release_v0.1.0.md](release_v0.1.0.md)). 82 tests.

## Day 12 (9 Nov 2026)

freeze run. Code frozen at tag `freeze-2026-11-09`; all 168 designs, the three robustness checks, S5, the solver cross-check and every figure rerun from it at ShellBench `v0.3.0` (`python scripts/day12_freeze.py`, record in `results/freeze_meta.json`); the rerun reproduced the 7 Nov values exactly. 81 tests.

## Day 11 (8 Nov 2026)

all 168 designs sized with steel and carbon; tests S4 (fallback) and S5 pass; sensitivity runs done; every paper figure built by one script, including the mechanism figure; 81 tests. Pinned to ShellBench `v0.3.0` (record files at `v0.2.0` until the 9 Nov freeze run; the pin move changed no number).

## Component status (14 Nov 2026)

| Item | Where | Status |
|---|---|---|
| Pre-registration | [docs/preregistration.md](preregistration.md) | Approved 30 Oct 2026, dated amendments since |
| Seismic-aware form-finding | `src/shellform/formfind.py`, `strategies.py` | 3D solver and both strategies done, tested |
| Tests S1-S5 | `tests/`, `src/shellform/checks.py` | S1-S4 pass, except the S1b comparison with ShellBench `floor-r1`, which waits for that tag; S4 is the section 8 fallback; S5 holds on every design (T1 at most 0.308 s) |
| 168 sized designs | `src/shellform/pipeline.py`, `batch.py`, `results/` | All feasible; carbon factor check closed in ShellBench v0.3.0; frozen 9 Nov (`freeze-2026-11-09`, ShellBench v0.3.0) |
| Figures | `src/shellform/figures.py`, `gallery.py`, `scripts/day11_figures.py`, [figures/](../figures/README.md) | Figs. 1-5 from the record, incl. the mechanism figure (rebuilt from the freeze run) |
| Design explorer | [explorer/index.html](../explorer/index.html), `scripts/day13_explorer_data.py` | All 168 designs from the freeze run; both strategies in 3D, carbon against Sa, the 5 % rule in all 84 cells; offline, light and dark |
| Paper tables and drafts | [paper/](../paper/README.md), `scripts/day14_paper_tables.py` | Tables 1-5 and S1 from the freeze record (`tests/test_paper_tables.py`); draft 1 of every section (Introduction, Methods, Results, Discussion, Conclusions, Abstract, highlights) with the author for checking, 14-17 Nov |
| Release | [v0.1.0](https://github.com/syednafizreja/ShellForm/releases/tag/v0.1.0), [CITATION.cff](../CITATION.cff) | Published 9 Nov 2026, DOI 10.5281/zenodo.24084111 |
| Verification add-ons | `src/shellform/verification.py`, `scripts/day17_verification.py`, Fig. S1 | Sphere buckling benchmark within 2.0 % of the classical value; λ1 mesh-converged to 0.6 %; FDM residual below 1e-10 N; membrane energy share; formwork bound (14 Nov 2026) |
| Visual system | [docs/visual_style.md](visual_style.md), `src/shellform/style.py` | One colour per meaning in figures and explorer; checked by `tests/test_visual_style.py` |
