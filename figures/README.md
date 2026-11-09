# figures

Every figure is regenerated from `results/` by a script; none is edited by hand. One command builds them all:

```powershell
python scripts/day11_figures.py               # Figs. 1-5
python scripts/day11_figures.py --no-gallery  # Figs. 2-5 only
```

Each figure names, in its PNG and PDF metadata and in its `.json` file, the ShellBench tag that its record files carry (not the pin, so a pin move before a rerun cannot mislabel a figure). The `.json` file holds the plotted numbers. Every figure is written as PNG (600 dpi) and vector PDF at full page width (190 mm), in the ShellForm visual system ([docs/visual_style.md](../docs/visual_style.md)): Inter type, one colour per meaning, no footer on the artwork. The restyle of 9 Nov 2026 left every `.json` byte-identical.

| Paper figure | File | Built by | Record read |
|---|---|---|---|
| 1 | `gallery_10m.{png,pdf,json}`, `gallery_20m.{png,pdf,json}` | `shellform.gallery` | `results/day04_sizing_*`, `day05_steel_carbon_*`, form finder |
| 2 (mechanism) | `fig02_mechanism.{png,pdf,json}` | `shellform.figures.fig02_mechanism` | `results/batch_all.csv` |
| 3 | `fig03_strategy_difference.{png,pdf,json}` | `shellform.figures.fig03_strategy_difference` | `results/sensitivity_cells.csv` (baseline) |
| 4 | `fig04_carbon_drivers.{png,pdf,json}` | `shellform.figures.fig04_carbon_drivers` | `results/batch_all.csv`, `sensitivity_cells.csv`, `sens_*.csv` |
| 5 | `fig05_s5_periods.{png,pdf,json}` | `shellform.figures.fig05_s5_periods` | `results/s5_plateau.csv`, ShellBench spectrum |

The figures of 8 Nov 2026 (Day 11) are pre-freeze (record at ShellBench v0.2.0). They are rebuilt from the freeze run on 10 Nov with the same command. Questions each figure answers and the Results outline: `paper/07_results_outline.md`.
