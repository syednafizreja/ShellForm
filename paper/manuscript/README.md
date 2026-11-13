# Manuscript (Computers & Structures)

- `shellform_cas.tex`: the paper (Elsevier `elsarticle`, preprint, line numbers, numbered references as the C&S Guide for Authors asks). Figures are read in place from `../../figures/`.
- `supplement.tex`: S1 search protocol, S2 Fig. S1, S3 pre-registration amendments (summary), S4 Table S1.
- `references.bib`: every DOI checked against Crossref on 14 Nov 2026.
- `tables/`: built by `python scripts/day18_manuscript_tables.py` from `paper/tables/*.md` (presentation only; never edit by hand).
- `highlights.txt`: separate file for submission (each bullet at most 85 characters).

Review marks in the PDF: `[check]` = a source still to open, `[J]` = Claude's judgement to accept or cut, `[?]` = a missing value. Set `\reviewmarksfalse` near the top of `shellform_cas.tex` to hide them for submission.

Build (TeX Live with `elsarticle`):

```powershell
python scripts/day18_manuscript_tables.py
cd paper/manuscript
latexmk -pdf shellform_cas.tex
latexmk -pdf supplement.tex
```

On Windows without LaTeX, upload the folder (with `../../figures` copied in and `\graphicspath` changed) to Overleaf, or use the committed PDFs.
