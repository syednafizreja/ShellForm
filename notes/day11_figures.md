# Day 11: paper figures and pin move to ShellBench v0.3.0 (8 Nov 2026)

Done by Claude in the app under the author's standing delegation, on the spare day (the author asked to pull Day 11 forward: "finish all"). Day 11 was locked on main first (7372bc3). [J] marks Claude's judgement.

## Done-when

"Every paper figure built by a script in `scripts/`": met. `python scripts/day11_figures.py` builds Figs. 1-5 from `results/`; `--no-gallery` builds Figs. 2-5 without form finding. List and questions: `figures/README.md`, `paper/07_results_outline.md`.

## The mechanism figure (Fig. 2)

For each of the 168 baseline designs, the ratio of each pre-registered check's demand to its limit at the sized thickness: λ_min/λ (buckling), t_min/t (minimum thickness), σ_c/f_c outside the D4-2 support zones (compression), δ/(L/300) (deflection). Rows: support case; columns: span; x: Sa; filled markers gravity form, open markers seismic-aware form; the three rises are offset in Sa. Limits come from `shellform.sizing`; f_c (19.1 MPa) from ShellBench through `inputs.load_inputs`. Numbers: `figures/fig02_mechanism.json`.

What it shows (record at v0.2.0):

- Corners: buckling sits on its limit in 84 of 84 designs (λ_min/λ 0.888-0.997 at 10 m, 0.956-0.999 at 20 m; below 1 only by the 5 mm grid). Compression at most 0.51 f_c, deflection at most 0.28 of L/300.
- Edges: the 50 mm minimum sets the thickness in 84 of 84; the next check is buckling at 0.020-0.074 (10 m) and 0.095-0.357 (20 m).
- No ratio moves onto a limit as Sa rises to 0.6 g. A new test (`tests/test_figures.py`) checks that in every one of the 168 rows the check the sizing names as governing is the one with the largest ratio, and that no ratio exceeds 1.

## The other figures

- Fig. 3: the section 7 rule per cell, with the 5 % band and the range over the four factor-band corners (the bars are mostly hidden by the markers, because the band moves both strategies almost equally).
- Fig. 4: what moves carbon, on one axis. Sa: 0-0.4 % (gravity form); strategy: -5.7 to +1.4 %; λ 3: 0.73-0.83 of baseline (corners); λ 8: 1.22-1.30; 61 x 61: up to +6.0 % (10 m corners); band ±25 % by construction. Edge shells move only with the band. [J] This is the clearest single picture of the mechanism: the buckling threshold, a judgement, outweighs the seismic level by about an order of magnitude.
- Fig. 5: test S5, T1 of every design on ShellBench's spectrum shape; 0 failures.

## Decisions (Claude, under the standing delegation) [J]

- **D11-1, pin moved to ShellBench v0.3.0 before the freeze.** v0.3.0 was tagged on 8 Nov (03:50 UTC). Between v0.2.0 and v0.3.0 the only changes in what ShellForm reads are the source notes of `data/carbon_factors.csv` (official-copy check closed, 6 Nov; no value changed) and two docstrings in `shellbench/carbon.py`. v0.3.0 still reports `__version__` 0.2.0, so `pin.py` keeps that string and checks the tag. Evidence: all 168 designs rerun at v0.3.0, compared with the record: see "Record check" below. The record files (`batch_all.*`, `sens_*`, day04-day06 files) were not overwritten: they stay at v0.2.0 until the freeze run on 10 Nov, which reruns everything at the pinned tag.
- **D11-2, figures name the record's tag, not the pin.** Each figure reads `shellbench_tag` from the record rows and refuses mixed tags (`figures.record_tag`, `gallery.record_tag`). So today's figures say v0.2.0 (their record), and after the freeze they will say v0.3.0.
- **D11-3, carbon status read from ShellBench.** `carbon.factor_status()` reads the source notes of the C40 and HRB400 rows in place; `batch.py` writes that into each meta file instead of the fixed text "provisional: ... author to confirm". At v0.3.0 it returns "confirmed" (check closed 6 Nov). The status text is the only thing that changes; no number does.
- **D11-4, figure format.** PNG at 600 dpi and vector PDF (manuscript workflow skill, section 6), deterministic (no creation date in the PDF). Colours: fixed categorical order with a second encoding (marker shape or fill) on every series, so the figures survive greyscale and colour-blind reading.

## Day 10 loose end closed

The Day 8 gallery (Fig. 1) was never rebuilt after Day 10: its JSON still named v0.1.0 and showed 37.5 kgCO₂e/m² for 10 m corners, rise 0.15, seismic-aware, 0.6 g, the design D10-1 moved from 85 to 90 mm (now 39.7). Rebuilt from the Day 10 record; forms unchanged.

## Record check (pin move)

`python -m shellform.batch --preset all --compare-record --workers 4 --name pinmove_v030` at v0.3.0 (CalculiX 2.21, 1061 s): 168 of 168 feasible, 168 rows compared, **0 mismatches**, and the largest relative difference in every compared column is 0.0 (thickness, governing check, buckling factor, period, compression, deflection, concrete, steel, carbon). Files: `results/batch_pinmove_v030.csv` and `_meta.json`. The run started before D11-3 was written, so its meta `status` still carries the old fixed text ("provisional: ... author to confirm"); runs from now on write the status read from ShellBench.

## Open

- 10 Nov freeze: rerun `batch --preset all`, `sensitivity --run lam3 lam8 mesh61 --summarise`, `s5`, then `python scripts/day11_figures.py`; all files then name v0.3.0.
- Syed: write Results from `paper/07_results_outline.md` (outline only; numbers from the freeze files).
