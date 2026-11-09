"""tests/test_visual_style.py — the ShellForm visual system holds (docs/visual_style.md).

Checks that the explorer and the figures use the same colour roles, that the
explorer opens offline (no network reference), and that every figure image
names the ShellBench tag in its metadata, at an Elsevier column width.
"""

import json
import re
from pathlib import Path

import pytest

from shellform import style

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "explorer" / "index.html").read_text(encoding="utf-8")


def css_light(name):
    """Return the value of a CSS custom property in the explorer's light :root block."""
    block = HTML.split(":root {", 1)[1].split("}", 1)[0]
    m = re.search(rf"--{name}:\s*([^;]+);", block)
    assert m, f"--{name} missing from the explorer's :root"
    return m.group(1).strip().lower()


def test_explorer_colour_roles_match_the_figures():
    """Strategy, check and diverging colours are the same in the explorer and in style.py."""
    assert css_light("gravity") == style.GRAVITY
    assert css_light("seismic") == style.SEISMIC
    for key, hexval in style.CHECK_COLOUR.items():
        assert css_light(f"check-{key}") == hexval
    assert (css_light("div-lo"), css_light("div-hi")) == (style.DIVERGING[0], style.DIVERGING[2])


def test_strategy_colours_are_reserved():
    """No other role reuses a strategy colour (colour follows the entity)."""
    others = set(style.CHECK_COLOUR.values()) | set(style.DIVERGING) | set(style.ORDINAL[2]) | set(style.ORDINAL[3])
    assert style.GRAVITY not in others and style.SEISMIC not in others


def test_explorer_is_offline():
    """The explorer loads nothing from the network: scripts and fonts are in explorer/vendor/."""
    for m in re.finditer(r'(?:src|href)="([^"#]+)"', HTML):
        assert not m.group(1).startswith(("http:", "https:", "//")), m.group(1)
    assert "url(\"http" not in HTML
    for name in ("three.min.js", "OrbitControls.js", "three.LICENSE", "Inter-Regular.woff2",
                 "Inter-Medium.woff2", "Inter-SemiBold.woff2", "Inter.OFL.txt"):
        assert (ROOT / "explorer" / "vendor" / name).is_file(), name


def test_explorer_rule_is_the_pipeline_rule():
    """The 5 % verdict on the page is the pipeline's MEANINGFUL_DIFFERENCE."""
    from shellform.pipeline import MEANINGFUL_DIFFERENCE

    m = re.search(r"const RULE = ([0-9.]+);", HTML)
    assert m and float(m.group(1)) == MEANINGFUL_DIFFERENCE


def test_bundled_fonts_register():
    assert style.register_fonts() == len(style.FONT_FILES)


@pytest.mark.parametrize("stem", ["fig02_mechanism", "fig03_strategy_difference", "fig04_carbon_drivers",
                                  "fig05_s5_periods", "gallery_10m", "gallery_20m"])
def test_figure_metadata_names_the_tag_and_width(stem):
    """Each PNG names the record's ShellBench tag in its metadata and is full width (190 mm) at 600 dpi."""
    from PIL import Image

    tag = json.loads((ROOT / "figures" / f"{stem}.json").read_text(encoding="utf-8"))["shellbench_tag"]
    im = Image.open(ROOT / "figures" / f"{stem}.png")
    assert f"ShellBench {tag}" in im.info.get("Description", "")
    width_mm = im.size[0] / style.DPI * 25.4
    assert abs(width_mm - style.WIDTH_MM["full"]) < 1.0
    assert (ROOT / "figures" / f"{stem}.pdf").is_file()
