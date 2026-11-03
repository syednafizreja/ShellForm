# results

Every file here is written by a script in the repo and names the ShellBench tag it used. `results/tmp/` is git-ignored.

- `day04_sizing_10m.csv`, `day04_sizing_10m_tried.json`: Day 4 thickness sizing (provisional).
- `day05_steel_carbon_10m.csv`, `day05_comparison_10m.csv`, `day05_meta.json`: Day 5 steel, support zones and carbon (provisional until the author confirms ShellBench's carbon factors).
- `day06_designs.csv`, `day06_comparison.csv`, `day06_tried.json`, `day06_meta.json`: Day 6 run of all 168 designs (both spans) from `scripts/day06_all_designs.py`: sizing, steel, support zones and carbon per m² of covered plan area (D6-1), with T1 on the covered plan mass (D6-2). Provisional until the author confirms ShellBench's carbon factors. These supersede the Day 4 and Day 5 files for any later use; the older files stay as the record of those days.
