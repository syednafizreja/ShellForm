# Reproducing ShellForm, now and in the long term

This file is for anyone who wants to check or reuse ShellForm's results years after they were made, when today's software versions may no longer install. It records what was run, how to verify the record without running anything, and what to do when a dependency has gone.

## 1. Where the record lives

| Copy | Address | Notes |
|---|---|---|
| Zenodo (all versions) | [10.5281/zenodo.24084110](https://doi.org/10.5281/zenodo.24084110) | Permanent archive; the concept DOI resolves to the latest version |
| Zenodo v0.1.0 | [10.5281/zenodo.24084111](https://doi.org/10.5281/zenodo.24084111) | The first release, 9 Nov 2026 |
| GitHub | <https://github.com/syednafizreja/ShellForm> | Working repository |

ShellBench, which ShellForm imports, has a Zenodo record (all versions [10.5281/zenodo.23851675](https://doi.org/10.5281/zenodo.23851675)), but the pinned tag `v0.3.0` is a git tag, not a Zenodo release. Identify it by its commit hash (section 2). Independent archives of both repositories can be found by searching the origin URL at [Software Heritage](https://archive.softwareheritage.org/).

## 2. What was run

| Item | Value |
|---|---|
| ShellForm code for the record | git tag `freeze-2026-11-09`, commit `fd5cc85b2ca704f31d3e7640fd388bde0633cd61` |
| ShellBench | git tag `v0.3.0`, commit `f8a77b49bfd8e22552b2fea5a158f902c9da24b0` (reports version string "0.2.0"; see `src/shellform/pin.py`) |
| Python | 3.12 (3.12.15 in the exported environment) |
| Key libraries | numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, meshio 5.3.5, pytest 9.1.1 |
| CalculiX (`ccx`) | 2.21 for the freeze run (`results/README.md`); the earlier Day 4-10 record was written with 2.23, and the freeze run reproduced its values (`docs/CHANGELOG.md`, Day 12) |
| Full environment | [`environment-lock.yml`](../environment-lock.yml) (conda, exact versions of the laptop environment that reproduces the record) |
| Units | SI throughout (m, N, Pa, kg, kgCO2e) |

## 3. Verify the record without running anything

Every file in `results/` and `figures/` has a SHA-256 checksum in [`SHA256SUMS`](../SHA256SUMS), taken from the committed bytes.

```bash
git -c core.autocrlf=false clone https://github.com/syednafizreja/ShellForm.git
cd ShellForm
sha256sum -c SHA256SUMS
```

On Windows, Git's default line-ending conversion changes text files on checkout, so clone with `core.autocrlf=false` as above, or check a Zenodo download instead.

## 4. Rerun

1. Recreate the environment: `conda env create -n shellform -f environment-lock.yml`.
2. Install ShellBench at the pinned tag: clone it, `git checkout v0.3.0`, then `pip install -e <clone> --no-deps`.
3. Install ShellForm: `pip install -e . --no-deps`, then `python -m pytest`.
4. Check against the record: `python -m shellform.batch --compare-record` (8 designs, minutes) or `python scripts/day12_freeze.py` (all of it, about 2 h on 4 workers).

The comparison checks feasibility, thickness, governing check and steel case exactly, and the buckling factor, period, stresses, deflection, volumes and carbon within a stated relative tolerance (`src/shellform/batch.py`). Quantities that are computed live and sit at round-off level (for example the residuals of tests S2 and S3 in `paper/tables/table3_validation.md`, of order 1e-11 and 1e-16) can differ in their last digits between machines and library builds; every such test passes by many orders of magnitude, and no verdict depends on them [J].

## 5. When something no longer installs

- **Exact versions unavailable.** Use the nearest Python 3 and library versions that install, run the tests, then `--compare-record`. Differences in thickness, steel or carbon point to a numerical change worth recording; differences at round-off level do not.
- **ShellBench unavailable on GitHub.** Find commit `f8a77b49bfd8e22552b2fea5a158f902c9da24b0` of `https://github.com/syednafizreja/ShellBench` in Software Heritage, or in any later ShellBench archive that contains tag `v0.3.0`, and install it from the unpacked folder. Check the commit hash before use.
- **CalculiX unavailable.** Any CalculiX 2.x that reads the generated `.inp` files should do; the buckling and static steps use standard keywords. The verification sphere (`scripts/day17_verification.py`, check V1) is a quick test that a new solver build gives the classical buckling pressure.
- **Python itself unavailable.** The record does not need the code to be read. All results are CSV and JSON, figures are PNG and PDF with their plotted data in a JSON beside each, and the method is written out in the manuscript (`paper/manuscript/`) and the pre-registration, so the study can be re-implemented from the text and checked against the CSV files.

## 6. File formats

All data are plain-text open formats (CSV, JSON, Markdown, LaTeX). Figures are PNG and PDF, each with a JSON of the plotted values. The explorer (`explorer/index.html`) is a single static HTML page with its libraries bundled, so it opens from disk with no server or network.
