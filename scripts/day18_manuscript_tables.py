"""Convert the frozen manuscript tables (paper/tables/*.md) to LaTeX for the C&S manuscript.

Presentation only: every cell is copied from the Markdown tables that
``scripts/day14_paper_tables.py`` builds from the freeze record
(tag ``freeze-2026-11-09``, ShellBench v0.3.0). No value is computed,
rounded or typed here. Output: ``paper/manuscript/tables/*.tex``
(booktabs, no vertical rules, as the C&S Guide for Authors asks).

Run: ``python scripts/day18_manuscript_tables.py``
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paper" / "tables"
OUT = ROOT / "paper" / "manuscript" / "tables"

# Characters that need a LaTeX form. Unicode symbols are kept for
# readability and mapped to math where pdflatex needs it.
_REPLACE = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("≥", r"$\geq$"),
    ("≤", r"$\leq$"),
    ("×", r"$\times$"),
    ("±", r"$\pm$"),
    ("λ", r"$\lambda$"),
    ("ν", r"$\nu$"),
    ("γ", r"$\gamma$"),
    ("Δ", r"$\Delta$"),
    ("₂", r"$_2$"),
    ("³", r"$^3$"),
    ("²", r"$^2$"),
    ("−", r"$-$"),
    ("<", r"$<$"),
]


_SUB = re.compile(r"(?<![A-Za-z_.])([A-Za-zνγ])_([A-Za-z]{1,3})(?![A-Za-z_])")
_GREEK = {"ν": r"\nu", "γ": r"\gamma"}


def tex(cell: str) -> str:
    """Return ``cell`` as LaTeX text, escaping special characters.

    Symbols with a subscript (``f_c``, ``T_g``, ``t_min``, ``γ_EG``) become
    math; code identifiers such as ``carbon.SLAB_T_M`` stay as text.
    """
    out = cell.strip().replace("`", "")
    maths: list[str] = []

    def _hold(m: re.Match) -> str:
        base = _GREEK.get(m.group(1), m.group(1))
        sub = m.group(2) if len(m.group(2)) == 1 else rf"\mathrm{{{m.group(2)}}}"
        maths.append(rf"${base}_{{{sub}}}$")
        return f"@@{len(maths) - 1}@@"

    out = _SUB.sub(_hold, out)
    for old, new in _REPLACE:
        out = out.replace(old, new)
    out = re.sub(r"(\d)-(\d)", r"\1--\2", out)  # numeric ranges take an en dash
    out = out.replace("$$", "")
    for i, m in enumerate(maths):
        out = out.replace(f"@@{i}@@", m)
    return out


def read_md_table(path: Path) -> tuple[list[str], list[list[str]]]:
    """Read the first pipe table in a Markdown file; return header and rows."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    rows = [[c for c in ln.strip().strip("|").split("|")] for ln in lines]
    header, body = rows[0], [r for r in rows[2:]]
    return header, body


def write_tabular(name: str, colspec: str, size: str = r"\small",
                  drop: tuple[int, ...] = (), header_tex: list[str] | None = None,
                  breakable: tuple[int, ...] = ()) -> None:
    """Write ``paper/manuscript/tables/<name>.tex`` from ``paper/tables/<name>.md``.

    ``header_tex`` replaces the column labels only (short labels for the
    page width); the body cells are always copied from the Markdown table.
    """
    header, body = read_md_table(SRC / f"{name}.md")
    if header_tex is not None:
        assert len(header_tex) == len(header), name
        header = header_tex
    keep = [i for i in range(len(header)) if i not in drop]
    colspec = colspec.replace("p{", r">{\raggedright\arraybackslash}p{")  # no stretched words
    lines = [size, rf"\begin{{tabular}}{{{colspec}}}", r"\toprule",
             " & ".join(header[i] if header_tex else tex(header[i]) for i in keep) + r" \\", r"\midrule"]
    def cell(row: list[str], i: int) -> str:
        out = tex(row[i])
        if i in breakable:  # long code identifiers may break after . and _
            out = out.replace(r"\_", r"\_\allowbreak{}").replace(".", r".\allowbreak{}")
        return out

    lines += [" & ".join(cell(r, i) for i in keep) + r" \\" for r in body]
    lines += [r"\bottomrule", r"\end{tabular}"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_longtable(name: str, colspec: str, out_name: str) -> None:
    """Write a page-breaking longtable version of a long table (supplement)."""
    header, body = read_md_table(SRC / f"{name}.md")
    head = " & ".join(tex(h) for h in header) + r" \\"
    lines = [r"\scriptsize", rf"\begin{{longtable}}{{{colspec}}}", r"\caption{All 168 sized designs.}\\",
             r"\toprule", head, r"\midrule", r"\endfirsthead", r"\toprule", head, r"\midrule", r"\endhead",
             r"\bottomrule", r"\endfoot"]
    lines += [" & ".join(tex(c) for c in r) + r" \\" for r in body]
    lines += [r"\end{longtable}"]
    (OUT / f"{out_name}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Build every manuscript table."""
    write_tabular("table1_design_space", "ll")
    write_tabular("table2_inputs", "p{0.40\\linewidth}p{0.17\\linewidth}p{0.36\\linewidth}", r"\footnotesize",
                  breakable=(2,))
    write_tabular("table3_validation", "p{0.15\\linewidth}p{0.22\\linewidth}p{0.14\\linewidth}p{0.30\\linewidth}l", r"\footnotesize")
    write_tabular("table4_sized_designs", "rlrrlrlllrr", r"\scriptsize", header_tex=[
        r"$L$ (m)", "Supports", r"$f/L$", "Feasible", "Governs", r"$t$ (mm)",
        r"$\lambda$", r"$T_1$ (s)", "Steel (kg)", r"\shortstack{Carbon\\(kgCO$_2$e/m$^2$)}",
        r"\shortstack{Concrete\\share (\%)}"])
    write_tabular("table5_verdicts", "p{0.17\\linewidth}rrrp{0.22\\linewidth}rrrr", r"\scriptsize", header_tex=[
        "Run", r"$L$ (m)", "Feasible", r"\shortstack{$t$\\changed}",
        "Verdicts (central factors)", r"\shortstack{Same at all\\4 corners}",
        r"\shortstack{Largest\\$|\Delta|$ (\%)}", r"\shortstack{Headline\\cells}",
        r"\shortstack{Headline\\made}"])
    write_tabular("tableS1_all_designs", "lrlrrrrrr", r"\scriptsize")
    write_longtable("tableS1_all_designs", "lrlrrrrrr", "tableS1_all_designs_long")
    print(f"wrote {len(list(OUT.glob('*.tex')))} tables to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
