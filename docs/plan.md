# ShellForm plan: remaining days (from 7 Nov 2026)

Source: `docs/data_contract.md` section 5 (dates agreed 29 Oct) and the author's decision of 29 Oct in `docs/handoff.md`: "build ends 13 Nov; check window 14-17 Nov". This file only restates that plan from today on. If a date moves, add a dated line under "Changes" and say why.

**13 Nov is the end of the build, not the finished paper.** By 13 Nov: code, results, figures, explorer, README, ShellForm v0.1 with a Zenodo DOI, and Syed's draft of Methods and Results. The full paper is written after the 17 Nov check window.

ShellBench comes first until 11 Nov: its GATE days are never displaced by ShellForm work. One Claude per day; lock the day on main first.

| Date | Day | Work | Done when |
|---|---|---|---|
| Sat 7 Nov | 10 | S5 plateau table; move the pin to ShellBench v0.2.0 and run `python -m shellform.batch --preset all --compare-record`; write the `sensitivity_meta.json` baseline path with `as_posix()` | S5 table in `results/`, 0 record mismatches, tests pass |
| Sun 8 Nov | 11 (pulled forward) | Spare day used for Day 11 (author's request); pin moved to ShellBench v0.3.0 (tagged 8 Nov) with the record check | Every paper figure built by `scripts/day11_figures.py`; 0 record mismatches |
| Mon 9 Nov | — | Now spare (Day 11 done on 8 Nov). Was: figures from the pre-freeze record, including the mechanism figure (governing check per design against Sa, by support case; `paper/04_supervisor_advice.md` section 3) | Every paper figure built by a script in `scripts/` |
| Mon 9 Nov (pulled forward) / Tue 10 Nov | 12 | **Freeze** (done 9 Nov, tag `freeze-2026-11-09`): final run, freeze commit; fill `paper/numbers.md` rows from the freeze files | Freeze commit tagged; every row names its file and ShellBench tag |
| 11–13 Nov | 13–15 | Final figures; explorer with real results; README; ShellForm v0.1 release and Zenodo DOI; Syed drafts Methods and Results from `paper/02_methods_outline.md` and `paper/03_sensitivity_outline.md` | v0.1 on GitHub and Zenodo; Methods and Results drafts in `paper/` |
| 14–17 Nov | — | Check window, shared with ShellBench: Syed checks every number; Claude fixes | Every `numbers.md` row checked by Syed |
| After 17 Nov | — | Syed writes Discussion, Introduction, Abstract; preprint; submit to *Computers & Structures* | Submitted before the European deadlines in January |

## Open items carried into the plan

- ShellBench PR #130 (carbon official-copy note): waits for Syed to merge.
- S4 published case: fallback in use (no full text by 4 Nov). If the Michiels full text arrives before 10 Nov, run the published arch as an extra check beside S4. Sources: `docs/handoff.md`, 6 Nov.
- EN 1992-1-1 Annex F (F.2)/(F.3): checked by Claude 8 Nov in the full BS EN 1992-1-1:2004 text: F.1(4), printed p. 211 (PDF p. 213); expressions and relief condition match `steel.py`. Author to confirm.
- Michiels journal papers: links and access status in `paper/06_michiels_sources.md` (7 Nov). Thesis chapters are the working source.
- `paper/00_core.md`: Syed fills it before the Methods prose.

## Guidance actions (adopted 6 Nov, `paper/04_supervisor_advice.md`)

- Before 10 Nov: Syed sends `paper/05_email_michiels.md` (full text and S4 inputs). If inputs arrive before the freeze, the published arch runs beside S4.
- 9 Nov: mechanism figure (above). Paper leads with the mechanism; the null is the evidence.
- 11-13 Nov: explorer is a repo and Zenodo asset only; Methods framed around the solver, envelope and S1-S5.
- 14-17 Nov: Syed checks the journal shortlist (C&S, Engineering Structures, Structures, J. IASS) for scope, quartile, APC and word limit.
- After 17 Nov: preprint; one-page research summary; emails to 3-5 groups (Adriaenssens first); IASS Symposium abstract (check dates).
- Later: paper 3, "where the null breaks", as the PhD or postdoc proposal.

## Changes

- 9 Nov 2026: Day 12 (freeze) done on the spare day, at the author's request ("its a new day. lets go"). Tag `freeze-2026-11-09`; 10 Nov is now spare for the app. Pre-registration entry of 9 Nov.

- 8 Nov 2026: Day 11 done on the spare day, at the author's request ("finish all"); 9 Nov becomes spare. ShellBench v0.3.0 was tagged on 8 Nov, so the pin moved before the freeze (LOG Day 11).

- 6 Nov 2026: guidance actions added; mechanism figure added to 9 Nov. Why: supervisor-style review adopted by Syed.
