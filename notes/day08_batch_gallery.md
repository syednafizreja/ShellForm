# Day 8 (5 Nov 2026): batch runner and first gallery

Written by Claude in the app, under the author's standing delegation. ShellBench tag: v0.1.0. CalculiX 2.21 (cloud); the record on main was written with 2.23 on the laptop.

Plan line (setup guide, Thu 5 Nov): "Batch runner (every row names the ShellBench tag); first gallery." Done when: "8 designs run from one command."

## What changed

- `src/shellform/pipeline.py`: the per-design steps of Day 4 (`size_one`) and Day 5 (`takeoff_one`), the section 7 rules (`comparison`) and `write_csv`. They were moved out of `scripts/day04_size_10m.py` and `scripts/day05_steel_carbon_10m.py` without changing the calculation. The scripts now import them, so the scripts, the batch runner and the freeze run share one copy of the code.
- `src/shellform/batch.py`: `python -m shellform.batch` runs any set of designs start to finish (form, sizing, modal, steel, support zones, carbon), one design per worker. Selection by preset (`smoke8`, `all`) or by filters (`--span`, `--supports`, `--rise`, `--strategy`, `--sa`, `--ids`). Writes `results/batch_<name>.csv` (every row has `shellbench_tag`) and `results/batch_<name>_meta.json` (tag, CalculiX version, command, wall time, every thickness tried). `--compare-record` checks each row against the committed Day 4-6 results and exits with status 1 on a mismatch.
- `src/shellform/gallery.py`: `python -m shellform.gallery` draws `figures/gallery_10m.png` and `figures/gallery_20m.png`, with the plotted numbers in `figures/gallery_<span>m.json`.
- `tests/test_batch.py`: 4 tests (selection, record check passes on the record and catches a change, one design end to end against the record).

## Decisions (Claude, under the standing delegation) [J]

- D8-1: preset `smoke8` = rise/span 0.15, Sa 0.3 g, every span, support case and strategy (8 designs). It touches every branch of the code at the middle rise and the S4 Sa.
- D8-2: record check tolerance. Text columns (`feasible`, `governing_check`, `steel_governing_case`) and the thickness must match exactly; other numbers to 1e-3 relative. Day 4's CalculiX 2.21 against 2.23 difference was at most 2.3e-4 (deflection), so 1e-3 allows the version difference and still catches a model change.
- No design, load, check or threshold changed, so there is no pre-registration amendment today.

## Results

**Done-when met.** `python -m shellform.batch --compare-record` ran the 8 `smoke8` designs from one command in 68 s (4 workers): 8 of 8 feasible, 0 mismatches. Largest relative difference from the record: deflection 4.4e-5 (CalculiX version); all other columns at or below 1.6e-14.

| design | t [mm] | governs |
|---|---|---|
| L10 corners gravity | 90 | buckling |
| L10 corners seismic | 85 | buckling |
| L10 edges gravity / seismic | 50 / 50 | t_min |
| L20 corners gravity / seismic | 215 / 215 | buckling |
| L20 edges gravity / seismic | 50 / 50 | t_min |

The L10 corners 85 against 90 mm pair is the D4-5 load-basis artefact (Day 4 and Day 5 notes). It must not be read as a strategy effect.

**All 168 through the batch runner** (`python -m shellform.batch --preset all --compare-record`, 20 min on 4 workers): 168 of 168 feasible, 168 rows compared, 0 mismatches. Largest relative differences: deflection 2.3e-4 (the same CalculiX 2.21 against 2.23 difference as Day 4), compression 1.2e-9, steel 1.4e-10, carbon 2.7e-11, buckling factor 0. So the moved code reproduces the whole Day 4-6 record, and the 10 Nov freeze run can be this one command.

## Gallery, what it shows

Rise/span 0.15. Row per support case: gravity form; plan map of z_seismic − z_gravity at Sa 0.3 and 0.6 g; section at y = 0 (vertical scale × 3). Titles give t, λ and carbon per m² from the record.

| span, supports | Δz at 0.3 g [mm] | Δz at 0.6 g [mm] | carbon gravity → seismic at 0.6 g [kgCO₂e/m²] |
|---|---|---|---|
| 10 m corners | −2.1 to 16.9 | −1.4 to 72.0 | 39.8 → 37.5 |
| 10 m edges | 0 to 14.6 | 0 to 62.6 | 22.4 → 22.5 |
| 20 m corners | −4.2 to 33.7 | −2.8 to 143.9 | 96.2 → 95.9 |
| 20 m edges | 0 to 29.2 | 0 to 125.2 | 22.4 → 22.5 |

- The seismic-aware mid-surface does not move in plan (largest horizontal shift 0.0 mm). It rises near the middle of each edge and stays near the gravity form at the crown and the corners. This follows from strategy 2: the midpoint of the four leaned forms cancels the shear and keeps a height change that grows with Sa (pre-registration P1).
- Largest Δz is 0.72 % of span at 0.6 g, on both spans. That is small next to the rise (15 % of span), which agrees with F2 (Day 2) and with the "no meaningful difference" verdicts of Days 5 and 6 [J].

## Still open

- Carbon factor rows, Annex F and the Michiels full texts: author, as in the handoff.
- ShellBench `v0.3` (due 5 Nov), `floor-r2` and `floor-r3` were not tagged at 03:15 UTC on 5 Nov; pin stays at v0.1.0.
- Laptop: pull, `python -m pytest` (expect 60 passed with CalculiX), then `python -m shellform.batch --compare-record` to repeat the done-when check on CalculiX 2.23.
