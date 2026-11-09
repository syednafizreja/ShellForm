# ShellForm v0.1.0 (prepared 9 Nov 2026, Day 13)

Release notes for the GitHub release. Paste the section "Release text" into the release form.

## Release text

ShellForm v0.1.0: code, results, figures and design explorer for "The carbon cost of seismic resilience: gravity-only versus seismic-aware form-finding of concrete shells".

- Code frozen at `freeze-2026-11-09` (pre-registration section 9 and its entry of 9 Nov 2026); results from one run, `python scripts/day12_freeze.py` (`results/freeze_meta.json`).
- Pinned to ShellBench v0.3.0 (`src/shellform/pin.py`); every result file names that tag.
- 168 sized designs; tests S1-S5 (S1b waits for ShellBench `floor-r1`; S4 is the pre-registered fallback); 94 tests (`python -m pytest`, CalculiX 2.21).
- Figures 1-5: `python scripts/day11_figures.py`. Explorer: open `explorer/index.html`.
- Extends Michiels & Adriaenssens (C&S 2018; J. IASS 2017) by sizing each form to code checks and counting A1-A3 carbon.

## Steps for the author (cannot be done from the cloud)

1. Make sure the tag `freeze-2026-11-09` is on GitHub (handoff of 9 Nov).
2. Zenodo: sign in at zenodo.org with GitHub, open Account > GitHub, and switch ShellForm on. Zenodo's GitHub link archives a repository when a release is published; as far as I know it needs the repository to be public. Check on the Zenodo page before you change the visibility.
3. Repository visibility: the project goal is a public repo. Making it public is your decision.
4. On the laptop: `git pull origin main`, then `git tag -a v0.1.0 -m "ShellForm v0.1.0"` and `git push origin v0.1.0`.
5. On GitHub: Releases > Draft a new release > tag v0.1.0 > title "ShellForm v0.1.0" > paste the release text > Publish. Zenodo then mints the DOI.
6. Put the DOI in `CITATION.cff` (`doi:` line), the README and `paper/references.md`; commit.
