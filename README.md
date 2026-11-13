<h1 align="center">ShellForm</h1>

<p align="center"><b>The carbon cost of seismic resilience</b><br>
Gravity-only versus seismic-aware form-finding of concrete shells: 168 sized designs, their A1-A3 carbon, and an interactive explorer.</p>

<p align="center">
<a href="explorer/index.html">Design explorer</a> ·
<a href="figures/README.md">Figures</a> ·
<a href="docs/preregistration.md">Pre-registration</a> ·
<a href="paper/README.md">Paper</a> ·
<a href="paper/numbers.md">Numbers and sources</a> ·
<a href="CITATION.cff">Cite</a>
</p>

<p align="center">
<a href="https://github.com/syednafizreja/ShellForm/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/syednafizreja/ShellForm/actions/workflows/tests.yml/badge.svg"></a>
<a href="https://doi.org/10.5281/zenodo.24084111"><img alt="DOI 10.5281/zenodo.24084111" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24084111-2b2b29"></a>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/explorer_dark.webp">
  <img alt="The ShellForm design explorer: controls, a 3D view of the seismic-aware form coloured by its height change, the comparison panel, carbon against Sa and the matrix of all 84 comparisons." src="docs/img/explorer_light.webp">
</picture>

### The method in one equation

Each shell is form-found as a pin-jointed network in equilibrium (force density method, Schek 1974):

$$
\mathbf{C}_f^{\mathsf T}\mathbf{Q}\,\mathbf{C}_f\,\mathbf{x}_f \;=\; \mathbf{p}_f \;-\; \mathbf{C}_f^{\mathsf T}\mathbf{Q}\,\mathbf{C}_x\,\mathbf{x}_x ,
\qquad
\mathbf{p} = W\,(S_a,\;0,\;-1)
$$

$\mathbf{C}$ is the branch-node matrix (free nodes $f$, supports $x$), $\mathbf{Q}$ the diagonal of force densities, $\mathbf{x}$ the coordinates (solved for $x$, $y$ and $z$ alike) and $\mathbf{p}$ the nodal loads: the weight $W$ of each node, plus a lateral load $S_a W$ (Michiels & Adriaenssens). The seismic-aware form is the midrange of the four thrust surfaces for $S_a$ in $\pm x$ and $\pm y$; the gravity-only form has $S_a = 0$. Every form is then sized in CalculiX (linear buckling $\lambda_1 \ge 5$, compression, $L/300$) and its A1-A3 carbon counted. The residual of this system is below $10^{-10}$ N on all 84 form-finding solves (`results/verify_v3_fdm_residual.csv`).

How much embodied carbon does seismic resilience cost in a form-found concrete shell, and does form-finding that includes seismic loads deliver it more cheaply than thickening a gravity-only shape?

ShellForm extends the seismic form-finding of Michiels & Adriaenssens (2017, 2018) by sizing each form to pass code checks and counting its A1-A3 embodied carbon. It is built on the validated, tagged modules of [ShellBench](https://github.com/syednafizreja/ShellBench) and never copies a ShellBench value (see [docs/data_contract.md](docs/data_contract.md)).

## At a glance

| | |
|---|---|
| **Question** | Does seismic-aware form-finding save carbon against a gravity-only form sized for the same seismic level? |
| **Design space** | 2 spans × 2 support cases × 3 rises × 2 strategies × 7 Sa levels = 168 sized designs |
| **Decision rule** | Pre-registered: a strategy is cheaper only if it saves 5 % or more ([section 7](docs/preregistration.md)) |
| **Result (freeze run)** | 79 of 84 cells: no meaningful difference. Details under [Main result](#main-result-freeze-run-9-nov-2026). |
| **Record** | Code tag `freeze-2026-11-09`, ShellBench `v0.3.0`; every number traces to `results/` |
| **Release** | [v0.1.0](https://github.com/syednafizreja/ShellForm/releases/tag/v0.1.0), DOI [10.5281/zenodo.24084111](https://doi.org/10.5281/zenodo.24084111) |

## Explore

Open [`explorer/index.html`](explorer/index.html) in any browser, straight from disk; it needs no server and no internet (three.js and the Inter typeface are bundled in `explorer/vendor/`). Pick a span, support case, rise and Sa level to see both strategies side by side: the form in 3D coloured by how far the seismic-aware form moves from the gravity-only one, carbon and thickness for each, carbon against Sa, and a clickable matrix of all 84 comparisons. Light and dark themes, keyboard control, a shareable link for every view, and a CSV of all 168 designs.

## Figures

All figures are drawn from `results/` by `python scripts/day11_figures.py`, at full page width, as 600 dpi PNG and vector PDF ([figures/README.md](figures/README.md)). The visual system is [docs/visual_style.md](docs/visual_style.md).

| Fig. 2: what sets the thickness | Fig. 4: what moves carbon |
|---|---|
| <img src="figures/fig02_mechanism.png" alt="Fig. 2, demand over limit of each sizing check against Sa"> | <img src="figures/fig04_carbon_drivers.png" alt="Fig. 4, range of the carbon ratio caused by each driver"> |

<img src="figures/gallery_10m.png" alt="Fig. 1, 10 m gallery: gravity-only form, height change of the seismic-aware form at Sa 0.3 g and 0.6 g, and the mid-plan section">

## Status

14 Nov 2026 (check window, day 1): five verification add-ons beside the frozen record, with no frozen setting or result changed ([notes/day17_verification.md](notes/day17_verification.md)). A complete sphere under pressure buckles within 2.0 % (R/t 50) and 1.3 % (R/t 100) of the classical value in the same CalculiX path that sizes every shell; λ1 changes by at most 0.6 % between 61 and 81 nodes per side; the force density residual is below 2.5e-11 N; 76-100 % of the strain energy is membrane energy; no formwork factor or reuse count can move a verdict across the 5 % rule. New Fig. 6 (carbon against λ1, with the Pareto front) and Fig. S1. Cloud pytest 125 passed.

13 Nov 2026: manuscript draft 1 complete. Documented literature search ([paper/13_literature_search.md](paper/13_literature_search.md)); Introduction ([paper/14_introduction_draft.md](paper/14_introduction_draft.md)); title options, Abstract (246 words), highlights and Conclusions ([paper/15_abstract_conclusion_draft.md](paper/15_abstract_conclusion_draft.md)). The author checks every section 14-17 Nov. No code under `src/` and no result changed.

11 Nov 2026: sources for the buckling threshold read ([notes/buckling_threshold_sources.md](notes/buckling_threshold_sources.md): Dulácska & Kollár 1995, ACI 318.2-14 cl. 3.1.8); Methods 2.5 rewritten; Discussion draft 1 ([paper/12_discussion_draft.md](paper/12_discussion_draft.md)). The pin stays at ShellBench v0.3.0, because v0.4.0 changes only plotting code in the modules ShellForm imports. Cloud pytest 101 passed.

10 Nov 2026: manuscript tables built by script from the freeze record (`python scripts/day14_paper_tables.py`, Tables 1-5 and S1 in [paper/tables/](paper/tables/)); drafting kit ([paper/09_drafting_kit.md](paper/09_drafting_kit.md)); draft 1 of Methods and Results ([paper/10_methods_draft.md](paper/10_methods_draft.md), [paper/11_results_draft.md](paper/11_results_draft.md)), which the author checks 11-13 Nov. Laptop re-run: pytest 101 passed, `results/` unchanged. No code under `src/` and no result changed.

9 Nov 2026 (release): v0.1.0 tagged and published on GitHub; Zenodo DOI [10.5281/zenodo.24084111](https://doi.org/10.5281/zenodo.24084111) (all versions [10.5281/zenodo.24084110](https://doi.org/10.5281/zenodo.24084110)), added to `CITATION.cff` and the paper files. Inter bold-italic font fallback fixed in `style.py` (no plotted number moved). 94 tests.

9 Nov 2026 (evening): premium-quality pass. One visual system for figures and explorer ([docs/visual_style.md](docs/visual_style.md)); explorer rebuilt (offline, dark theme, 84-cell matrix, table view); Figs. 1-5 restyled with every plotted number unchanged; `tests/test_visual_style.py`. 93 tests.

Day 13 (9 Nov 2026): design explorer with the frozen results ([explorer/index.html](explorer/index.html), open it in a browser); v0.1.0 release prepared ([docs/release_v0.1.0.md](docs/release_v0.1.0.md)). 82 tests.

Day 12 (9 Nov 2026): freeze run. Code frozen at tag `freeze-2026-11-09`; all 168 designs, the three robustness checks, S5, the solver cross-check and every figure rerun from it at ShellBench `v0.3.0` (`python scripts/day12_freeze.py`, record in `results/freeze_meta.json`); the rerun reproduced the 7 Nov values exactly. 81 tests.

Day 11 (8 Nov 2026): all 168 designs sized with steel and carbon; tests S4 (fallback) and S5 pass; sensitivity runs done; every paper figure built by one script, including the mechanism figure; 81 tests. Pinned to ShellBench `v0.3.0` (record files at `v0.2.0` until the 9 Nov freeze run; the pin move changed no number).

| Item | Where | Status |
|---|---|---|
| Pre-registration | [docs/preregistration.md](docs/preregistration.md) | Approved 30 Oct 2026, dated amendments since |
| Seismic-aware form-finding | `src/shellform/formfind.py`, `strategies.py` | 3D solver and both strategies done, tested |
| Tests S1-S5 | `tests/`, `src/shellform/checks.py` | S1-S4 pass, except the S1b comparison with ShellBench `floor-r1`, which waits for that tag; S4 is the section 8 fallback; S5 holds on every design (T1 at most 0.308 s) |
| 168 sized designs | `src/shellform/pipeline.py`, `batch.py`, `results/` | All feasible; carbon factor check closed in ShellBench v0.3.0; frozen 9 Nov (`freeze-2026-11-09`, ShellBench v0.3.0) |
| Figures | `src/shellform/figures.py`, `gallery.py`, `scripts/day11_figures.py`, [figures/](figures/README.md) | Figs. 1-5 from the record, incl. the mechanism figure (rebuilt from the freeze run) |
| Design explorer | [explorer/index.html](explorer/index.html), `scripts/day13_explorer_data.py` | All 168 designs from the freeze run; both strategies in 3D, carbon against Sa, the 5 % rule in all 84 cells; offline, light and dark |
| Paper tables and drafts | [paper/](paper/README.md), `scripts/day14_paper_tables.py` | Tables 1-5 and S1 from the freeze record (`tests/test_paper_tables.py`); draft 1 of every section (Introduction, Methods, Results, Discussion, Conclusions, Abstract, highlights) with the author for checking, 14-17 Nov |
| Release | [v0.1.0](https://github.com/syednafizreja/ShellForm/releases/tag/v0.1.0), [CITATION.cff](CITATION.cff) | Published 9 Nov 2026, DOI 10.5281/zenodo.24084111 |
| Verification add-ons | `src/shellform/verification.py`, `scripts/day17_verification.py`, Fig. S1 | Sphere buckling benchmark within 2.0 % of the classical value; λ1 mesh-converged to 0.6 %; FDM residual below 1e-10 N; membrane energy share; formwork bound (14 Nov 2026) |
| Visual system | [docs/visual_style.md](docs/visual_style.md), `src/shellform/style.py` | One colour per meaning in figures and explorer; checked by `tests/test_visual_style.py` |

## Run

From the repo root, in env `shellform`:

```powershell
python -m shellform.batch                     # 8 designs (preset smoke8), results/batch_smoke8.csv
python -m shellform.batch --preset all        # all 168 designs
python -m shellform.batch --span 10 --supports corners --sa 0.0 0.6   # any subset
python -m shellform.batch --compare-record    # also check against the committed results
python -m shellform.gallery                   # figures/gallery_10m.png, gallery_20m.png
python scripts/day11_figures.py               # every paper figure (Figs. 1-5)
python scripts/day12_freeze.py                # the whole freeze run (about 2 h on 4 workers)
python scripts/day13_explorer_data.py         # explorer/explorer_data.js from results/batch_all.csv
python scripts/day14_paper_tables.py          # manuscript tables in paper/tables/ from the freeze record
python scripts/day17_verification.py          # verification add-ons V1-V5 (about 6 min on 4 workers)
python scripts/day17_figures.py               # Fig. 6 (carbon against buckling factor) and Fig. S1
python -m pytest
```

Every results row names the ShellBench tag it used.

## Design space

2 spans (10, 20 m) x 2 supports (4 corners, continuous edges) x 3 rise-to-span ratios (0.10, 0.15, 0.20) x 2 strategies (gravity-only, seismic-aware) x 7 plateau spectral accelerations (0-0.6 g) = 168 sized designs.

## Setup

ShellForm uses its own conda environment, `shellform` (a clone of ShellBench's `research`), and a second, read-only clone of ShellBench checked out at the pinned tag. Daily ShellBench work in `research` never changes ShellForm's inputs, and ShellForm never changes ShellBench's environment.

```powershell
$conda = "C:\Users\ASUS\miniconda3\Scripts\conda.exe"
cd C:\Users\ASUS
git clone https://github.com/syednafizreja/ShellBench.git ShellBench-pin
cd ShellBench-pin; git checkout v0.3.0          # the tag in src/shellform/pin.py
& $conda create -n shellform --clone research -y
& $conda run -n shellform pip install -e C:\Users\ASUS\ShellBench-pin --no-deps
& $conda run -n shellform pip install meshio
cd C:\Users\ASUS\ShellForm
& $conda run -n shellform pip install -e . --no-deps
& $conda run -n shellform python -m pytest
```

To move the pin: `cd C:\Users\ASUS\ShellBench-pin; git fetch --tags; git checkout <new tag>`, update `src/shellform/pin.py`, run `pytest`, note it in LOG.md.

## Main result (freeze run, 9 Nov 2026)

In 79 of 84 cells the two strategies differ in carbon by less than 5 % ("no meaningful difference", pre-registration section 7). The other 5 cells (10 m, corner supports, rise 0.15, Sa 0.1-0.5 g) are one 5 mm thickness step next to the buckling limit, and they disappear under every robustness check. Thickness is set by linear buckling (corner supports) or the 50 mm minimum (edge supports), and steel by the minimum ratio; none of these responds to Sa up to 0.6 g. Numbers and sources: `paper/numbers.md`.

## Licence

Code: MIT. Cite with [CITATION.cff](CITATION.cff) or DOI [10.5281/zenodo.24084111](https://doi.org/10.5281/zenodo.24084111) (v0.1.0; all versions [10.5281/zenodo.24084110](https://doi.org/10.5281/zenodo.24084110)). Bundled third-party files keep their own licences: three.js r128 (MIT, `explorer/vendor/three.LICENSE`) and the Inter typeface (SIL Open Font License 1.1, `assets/fonts/OFL.txt`).
