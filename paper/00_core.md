# Core of the paper (write before any section)

Skill: academic-manuscript-writing, section 1. The author writes every sentence below. Claude's notes are marked [J] and are prompts, not text for the paper. If one line cannot be written yet, the paper is not ready for that section.

Status: empty template, 6 Nov 2026. Results are provisional until the 10 Nov freeze (`docs/preregistration.md` section 9).

## 1. Gap (one sentence: context + variable + outcome; name the gap type)

[?] Author.

[J] Prompt: Michiels & Adriaenssens form-found masonry arches (C&S 2018) and shells (J. IASS 2017) for lateral load, judged by material or compression-only paths. What is not known is the embodied carbon of reinforced concrete shells sized to code checks, gravity-only form against seismic-aware form. Gap type to choose: evidence or practical.

## 2. Contribution (one sentence: what is new, who cites it for what)

[?] Author.

[J] Prompt: keep within CLAUDE.md rule 8. ShellForm extends Michiels & Adriaenssens; it is not "the first seismic form-finding".

## 3. Headline result (one sentence with a number)

[?] Author, after the freeze run.

[J] What the pre-freeze record says (both spans, 168 designs, ShellBench v0.1.0): "no meaningful difference" (under 5 %) in 78 of 84 strategy cells; the other 6 (10 m corners, rise 0.15) are an artefact of the load basis and of the mesh (`notes/day05_steel_carbon.md`). Cost of resilience at 20 m: gravity 1.000-1.004, seismic 0.983-1.015 (`notes/day06_20m.md` section 4). The headline claim of pre-registration section 7 is not made. Every one of these numbers needs a row in `numbers.md` from the freeze run.

## 4. Master narrative (pick one the data supports)

[?] Author. Options from the skill: quantify costs and benefits; reveal a hidden phenomenon; explain a mechanism; resolve a dilemma; solve a puzzle; expose an unintended consequence.

[J] The record fits "explain a mechanism" best: thickness is set by linear buckling or the 50 mm minimum, steel by the minimum ratio, and none of these responds to Sa up to 0.6 g, so the form change has nothing to save. A pre-registered null result is reportable; the paper must say what would make it non-null (heavier mass, longer span, unreinforced shells, nonlinear buckling).

## 5. Target journal and article type

Computers & Structures, research article. Three recent C&S papers to model: [?] Author (opened, with DOIs, in `references.md`).

## 6. Strongest Reviewer 2 objection and the answer

[?] Author.

[J] Candidates: (a) equivalent static Sa × G_E and linear buckling are too simple to show a seismic benefit; (b) a null result in one plan shape and two spans does not generalise; (c) the seismic-aware form is ShellForm's own definition (midrange of four thrust surfaces, P1), so the null may come from the definition, not from seismic form-finding as such.
