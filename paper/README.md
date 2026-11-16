# paper

Material that the paper's numbers come from. The manuscript itself is not part of this repository.

| Path | What it is | Built by |
| --- | --- | --- |
| `tables/*.md`, `tables/tables.json` | Tables 1-5 and S1, read from the frozen record | `python scripts/day14_paper_tables.py` |
| `tables/tableS1_all_designs.csv` | All 168 sized designs (Table S1) | `python scripts/day14_paper_tables.py` |
| `tables/latex/*.tex` | The same tables as LaTeX (booktabs) | `python scripts/day18_manuscript_tables.py` |
| `numbers.md` | Every number reported in the paper, with the file, row and ShellBench tag it comes from | by hand, checked against `results/` |

Never edit the tables by hand: rerun the scripts. `tests/test_paper_tables.py` checks them against `results/`.
