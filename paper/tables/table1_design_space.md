# Table 1. Design space

Methods 2.2. Pre-registration section 3; coded in `src/shellform/design_space.py`.

| Variable | Levels |
|---|---|
| Plan | square |
| Span L [m] | 10, 20 |
| Supports | four corners; four continuous edges |
| Rise-to-span ratio [-] | 0.10, 0.15, 0.20 |
| Form-finding strategy | gravity-only; seismic-aware |
| Plateau spectral acceleration Sa [g] | 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 |
| Designs | 168 |

- Each design is sized separately; uniform thickness per shell (pre-registration section 5).
- Corner-supported free edges are drawn in by 0.10 × span (decision D3-1) [J].

Built by `python scripts/day14_paper_tables.py` from the freeze record (freeze-2026-11-09); ShellBench v0.3.0. Do not edit by hand; rerun the script.
