# Contributing to ShellForm

ShellForm is a frozen research artefact. Its results back a pre-registered study, so changes follow the rules below. Code and data changes that would alter a result need a dated amendment in `docs/preregistration.md`.

## Rules

1. **No invented values.** Never invent references, numbers, code clauses, results or DOIs. If a value cannot be traced, mark it `[?]` and say how to check it.
2. **ShellBench is the only source of shared values.** ShellForm never copies or hard-codes a ShellBench value. Import `shellbench` at the tag pinned in `src/shellform/pin.py`, or read ShellBench's data files in place. Carbon factors and code values are read from their source, never supplied. The data contract is [`docs/data_contract.md`](docs/data_contract.md).
3. **Every number has a source.** A number from a design code gives the clause; a number from a paper gives the page, table or figure.
4. **Plain British English.** Short sentences, no hype words. ShellForm extends Michiels & Adriaenssens; it is not described as the first seismic form-finding method. Judgement calls are marked `[J]`.
5. **The pre-registration is fixed.** Nothing in [`docs/preregistration.md`](docs/preregistration.md) changes after approval without a dated amendment that says why.

## Code standards

- SI units everywhere.
- Every function has a docstring.
- No hidden constants: every number in a result traces to ShellBench (tag named), a code clause, a paper or this repository's code.
- Every file in `results/` names the ShellBench tag it used.

## Checks before a pull request

```bash
pip install -r requirements.txt
pip install -e . --no-deps
python -m pytest
python -m shellform.batch --compare-record
```

All tests must pass, and `git status` must show no change under `results/` unless the change is intended and recorded in `docs/CHANGELOG.md`.

## Markers used in notes

| Marker | Meaning |
| --- | --- |
| `[J]` | A judgement call rather than a sourced fact, stated so a reader can disagree with it |
| `[check]` | A source read in abstract or secondary form, not yet confirmed in full text |
| `[?]` | A missing value, with the rule that closes it |

Notes that say "the assistant" record work drafted with an AI assistant under the author's direction, as declared in the manuscript. The author checked and owns every result.
