"""tests/test_paper_tables.py

Checks on scripts/day14_paper_tables.py: the manuscript tables read the
freeze record correctly and render as valid Markdown tables.
"""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def tables():
    """Import the tables script as a module."""
    spec = importlib.util.spec_from_file_location("day14_paper_tables", ROOT / "scripts" / "day14_paper_tables.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cols(line):
    """Number of cells in one Markdown table row."""
    return line.strip().strip("|").count("|") + 1


def test_md_table_cells_never_contain_a_pipe(tables):
    """Every row has as many cells as the header (a stray '|' would add one)."""
    for build in (tables.table_sized_groups, tables.table_verdicts):
        data, rows, tag = build()
        text = tables.md_table([str(i) for i in range(len(rows[0]))], rows)
        n = _cols(text.splitlines()[0])
        assert all(_cols(line) == n for line in text.splitlines())


def test_design_space_has_168_designs(tables):
    data, rows = tables.table_design_space()
    assert data["designs"] == 168


def test_sized_groups_cover_every_design_and_name_one_tag(tables):
    data, rows, tag = tables.table_sized_groups()
    assert sum(g["designs"] for g in data) == 168
    assert len(data) == 12
    assert tag == tables.one_tag(tables.read_csv("batch_all.csv"), "batch_all.csv")


def test_governing_check_matches_the_mechanism(tables):
    """Corner shells: buckling; edge shells: minimum thickness (Results 3.2)."""
    data, _, _ = tables.table_sized_groups()
    for g in data:
        assert g["governing"] == (["buckling"] if g["supports"] == "corners" else ["t_min"])


def test_headline_is_never_made(tables):
    data, _, _ = tables.table_verdicts()
    assert len(data) == 8
    assert all(d["headline_holds"] == "False" for d in data)


def test_validation_table_without_recompute_passes(tables):
    data, rows, tag = tables.table_validation(None)
    assert [r[-1] for r in rows] == ["pass"] * len(rows)
    assert data["s5_failures"] == 0


def test_rng_collapses_equal_ends(tables):
    assert tables.rng([50.0, 50.0], "{:.0f}") == "50"
    assert tables.rng([50.0, 55.0], "{:.0f}") == "50-55"
