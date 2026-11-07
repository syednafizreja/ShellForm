# Supervisor-style guidance (adopted 6 Nov 2026)

Claude's judgement [J], written in a demanding professor's voice and adopted by Syed on 6 Nov 2026 as the working guidance. Sources: `paper/00_core.md`, `paper/01_professor_test.md`, Day 9 sensitivity runs. No journal or conference facts were checked here; each one below is marked "check".

## 1. Direction

- Keep: pre-registration, reproducibility, traceable numbers, sensitivity runs.
- The result is a null (no meaningful difference in 79 of 84 cells; the other 5 are artefacts (78 and 6 before the 7 Nov solver correction)). **The paper's lead is the mechanism:** thickness and steel are set by buckling, the support condition and code minimums, not by Sa. Title, abstract and main figure carry the mechanism; the null is the evidence.
- Weakest point: S4 runs on the fallback (no Michiels full text). Fix it by contacting the authors (section 3).

## 2. Papers

1. ShellBench: benchmark and dataset paper (as planned).
2. ShellForm: one paper: mechanism + pre-registered null + verified open pipeline.
3. Later, not now: where the null breaks (masonry or unreinforced shells, longer spans, imperfect or nonlinear buckling, response-spectrum or time-history analysis). This becomes the PhD or postdoc proposal. No salami-slicing.

## 3. Add before the 10 Nov freeze

- Email Michiels or Adriaenssens for the full text and the S4 inputs (draft: `paper/05_email_michiels.md`). Syed sends it.
- One mechanism figure: governing check (buckling, minimum thickness, strength) per design against Sa, by support case. Carbon tables go to the supplement.
- Wording rule kept: "extends Michiels & Adriaenssens"; never "first".

## 4. Keep out

- No new analyses after the freeze: they go into limitations and future work.
- No "resilience at no carbon cost" wording.
- The explorer is a repo and Zenodo asset with one sentence in the paper, not a paper result.

## 5. Journal

C&S needs a computational-methods framing (solver, four-direction envelope, S1–S5 verification). Backup list to rank by fit: Engineering Structures, Structures, Journal of the IASS. Check: scope, quartile, APC, word limit (Syed, in each journal's Guide for Authors).

## 6. Profile

- One story across both projects: reproducible, carbon-aware computational design of structures.
- Public package: preprint, Zenodo DOIs, README with one-command reproduction, one-page research summary with the key figure (after the 17 Nov check).
- Targeted emails to 3–5 groups, Adriaenssens' group first: one specific link to their work, the preprint, one question. No CV-first emails.
- Conference abstract, for example the IASS Symposium. Check: dates and deadlines.

## 7. Where each action sits

See `docs/plan.md` (dates and done-when lines).
