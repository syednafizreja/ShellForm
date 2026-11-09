# ShellForm visual system

Every figure, interface, graphic and document that ShellForm produces follows this guide. It exists because of the author's rule of 9 Nov 2026: *every output must look and work like careful, months-long work, never like a quick draft.* Work that does not meet the checklist at the end of this file is not finished.

The code that carries the rules: `src/shellform/style.py` (figures) and the `:root` tokens in `explorer/index.html` (explorer). `tests/test_visual_style.py` checks that the two agree.

## 1. Principles

1. **The data is the loudest thing.** Grids, axes and frames are hairline and warm grey. No chart junk, no heavy borders, no 3D effects on 2D data.
2. **One colour, one meaning, everywhere.** A colour means the same thing in every figure, in the explorer and in slides (section 2). Colour is never the only cue: every coloured series also has a marker, a line style or a text label.
3. **Same numbers, better form.** Restyling never changes a plotted number. Each figure writes the plotted numbers to a `.json` beside it; a restyle must leave that JSON byte-identical (checked on 9 Nov 2026 for Figs. 1-5).
4. **Provenance in the file, not on the artwork.** The ShellBench tag, record files and script go into the PNG and PDF metadata and the JSON, not into a footer on the image, so a figure drops into the manuscript as it is.
5. **Text is plain.** Sentence case, short labels, units in square brackets in figures (`[mm]`, `[-]`), SI units, British spelling, no hype words.

## 2. Colour roles

All categorical colours are steps of the dataviz skill's validated reference palette. Hexes are given as light / dark (explorer dark theme).

| Role | Meaning | Light | Dark | Secondary cue |
|---|---|---|---|---|
| Strategy 1 | gravity-only form | `#2a78d6` blue | `#3987e5` | legend, label, filled marker |
| Strategy 2 | seismic-aware form | `#eb6834` orange | `#d95926` | legend, label, open marker |
| Check | buckling | `#6250d6` violet | `#9085e9` | circle marker, text |
| Check | minimum thickness | `#1baf7a` aqua | `#199e70` | square marker, text |
| Check | compression | `#e87ba4` magenta | `#e87ba4` (see note) | triangle marker, text |
| Check | deflection | `#eda100` yellow | `#c98500` | diamond marker, text |
| Ordered | span, rise (2 or 3 levels) | `#9c9a92` → `#2b2b29`; `#b4b2aa` → `#6f6e68` → `#1f1f1d` | — | circle / square / triangle |
| Diverging | height change Δz, carbon difference | `#0f6e78` teal → `#f2f1ec` → `#b5452a` brick | `#2a9aa6` → `#2a2a28` → `#d8603f` | numbers in cells, colour bar |
| Band | ±5 % "no meaningful difference" | `#efeee9` wash, `#d6d4cb` edge | `#252523`, `#3a3a37` | legend entry or in-plot label |
| Ink | text, secondary, muted | `#0b0b0b`, `#52514e`, `#898781` | `#f0efec`, `#c3c2b7`, `#8f8d86` | — |
| Lines | grid, axis | `#e1e0d9`, `#c3c2b7` | `#2c2c2a`, `#383835` | — |

Rules:

- **The two strategy colours are reserved.** Nothing else is ever blue or orange (tested). The diverging map uses teal and brick so it cannot be read as a strategy.
- Diverging maps are symmetric about zero and interpolated in OKLab through a warm grey zero. In the 3D explorer view the zero is concrete grey `#d8d4ca` (dark `#a9a59b`) so the shell reads as concrete.
- Status colours (good/warning) are not used for data.

Validator runs (dataviz skill, `scripts/validate_palette.js`, 9 Nov 2026):

- Strategy pair, light: all checks pass (CVD ΔE 24.7, normal ΔE 33.6). Dark: all pass (CVD 26.8, normal 31.8).
- Checks, light, all pairs: pass; CVD ΔE 6.1 (magenta-aqua, deutan) is in the 6-8 band, legal because every check has its own marker and label; three steps are below 3:1 contrast, so they always carry a marker and text.
- Checks, dark, all pairs: the reference dark magenta `#d55181` **fails** CVD against aqua (ΔE 1.6, deutan), so the dark theme keeps the light magenta `#e87ba4` (CVD 8.3, normal ≥ 17.2; its lightness 0.716 is just above the dark band, accepted [J]).

## 3. Type

- **Inter** (SIL OFL 1.1), bundled: `assets/fonts/*.otf` for figures, subset `.woff2` in `explorer/vendor/` for the explorer. Bundling makes figures identical on Windows and in the cloud. Fallbacks: Arial, Helvetica.
- Maths in figures uses Inter through matplotlib's custom mathtext (`$S_a$`, `$\lambda_{min}$`).
- Figure sizes at final print size: text 7 pt, ticks 6.5 pt, panel titles 7.5 pt medium, panel letters 8 pt semibold (lower case, no brackets: **a**, **b**).
- Explorer: 14 px body, 30 px page title (−0.022 em tracking), tabular figures in every column of numbers.

## 4. Figures

- **Widths:** Elsevier's artwork guide gives single column 90 mm, 1.5 column 140 mm, full width 190 mm [check against the current "Artwork sizing" page of Elsevier's author guide before submission]. All paper figures are full width; heights come from `style.size("full", aspect)`.
- **Export:** PNG at 600 dpi and vector PDF with the fonts embedded and subset (Inter as OpenType CFF, checked with `pdffonts`); 3D surfaces are rasterised inside the PDF.
- **Anatomy:** legend in one row above the panels, left-aligned; panel letter and title on one line above each panel, a muted subtitle under it for counts; y-label only on the left column, x-label only on the bottom row; shared axes inside a figure; reference lines (limit = 1, zero, Tg) in ink or axis grey, never coloured.
- **Bands and limits:** the ±5 % rule and the limit region are a warm grey wash with a hairline edge, labelled once.
- **Markers:** 9-14 pt² scatter markers with a 0.4-0.7 pt edge; filled = gravity-only, open = seismic-aware.
- **Gallery (Fig. 1):** gravity form shaded in strategy blue with a light grid, plan maps of Δz on a shared symmetric scale per row, mid-plan section with strategy colours, support case written down the left edge.
- Build everything with `python scripts/day11_figures.py`; never edit an image by hand.

## 5. Explorer

- Layout: top bar with provenance chips (freeze tag, ShellBench tag, code commit) and theme switch; page title with a four-tile summary computed from the data; three columns (controls, 3D view, comparison panel); two charts (carbon against Sa with the ±5 % band, matrix of all 84 cells); table view with CSV download; footer stating what the page computes.
- Controls are segmented buttons (radio groups with arrow-key support) and stepped sliders with tick labels; the state lives in the URL hash, so a view can be shared.
- 3D: soft shadows, concrete-grey surface coloured by Δz (or plain strategy colour), gravity-only form as blue lines, supports drawn, camera presets (3D, plan, side), PNG export.
- Every chart has a hover tooltip; the matrix is clickable; nothing relies on colour alone.
- Works offline from disk, light and dark themes, phone width (390 px) to wide screens, keyboard only, reduced motion, print.

## 6. Documents and slides

- Markdown in the repo: one H1, sentence-case headings, tables for anything with more than three parallel items, numbers with units and sources.
- Slides and posters use the colour roles of section 2 and Inter; figures are inserted from `figures/` at their native aspect ratio, never stretched.

## 7. The premium checklist (run before calling any artefact done)

1. Same colour, same meaning as section 2; no stray default matplotlib or browser colours.
2. No overlapping text, clipped labels or orphan legend entries at final size (look at the rendered output, not the code).
3. Every number traces to `results/` (JSON unchanged after a restyle) and names the ShellBench tag in its metadata.
4. Colour never the only cue; contrast checked; dark theme checked where it exists.
5. Type: Inter, sizes as section 3, units in brackets, sentence case.
6. Interfaces: keyboard, phone width, offline, light and dark, hover states, empty or error states.
7. A before/after screenshot is kept in the thread or the handoff when the look changes.
