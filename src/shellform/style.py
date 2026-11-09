"""The ShellForm visual system for paper figures (docs/visual_style.md).

One place for every visual constant of the figures: colours, type, sizes,
line weights and the export settings. Nothing here changes a number in a
figure; it only changes how the numbers look. The explorer
(explorer/index.html) uses the same colour roles as CSS custom properties,
and tests/test_visual_style.py checks that the two stay in step.

Colour roles (fixed across every figure and the explorer):

- Strategy (reserved, never used for anything else): gravity-only form =
  blue, seismic-aware form = orange.
- Sizing checks (Fig. 2, explorer "governing check"): buckling = violet,
  minimum thickness = aqua, compression = magenta, deflection = yellow.
  Every check also has its own marker, so colour is never the only cue.
- Ordered variables (span, rise ratio): neutral ink steps, light to dark,
  with their own markers.
- Height change of the seismic-aware form (gallery, explorer): diverging
  teal (lower) to brick (higher) through a warm grey zero.
- The 5 % "no meaningful difference" band: one warm grey wash.

The categorical hexes are the dataviz skill's validated reference palette
(light mode): strategy = slots 1-2 (adjacent CVD dE 24.7, normal dE 33.6),
checks = slots 7, 3, 5, 4 (all-pairs normal dE >= 19.6; CVD 6.1 is in the
floor band, legal because each check has its own marker). Validator runs are
recorded in docs/visual_style.md.

Sizes follow Elsevier's artwork widths (single column 90 mm, 1.5 column
140 mm, full width 190 mm; docs/visual_style.md gives the source to check).
Text is 7 pt at final size, panel titles 7.5 pt, panel letters 8 pt bold.

Usage:
    from shellform import style
    style.apply()                       # once, before drawing
    fig, ax = plt.subplots(figsize=style.size("full", 0.45))
"""

from pathlib import Path

import matplotlib
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "assets" / "fonts"

# --- Colour roles -----------------------------------------------------------
GRAVITY = "#2a78d6"       # strategy 1, gravity-only form
SEISMIC = "#eb6834"       # strategy 2, seismic-aware form
STRATEGY = {"gravity": GRAVITY, "seismic": SEISMIC}
STRATEGY_LABEL = {"gravity": "gravity-only form", "seismic": "seismic-aware form"}

CHECK_COLOUR = {"buckling": "#6250d6", "t_min": "#1baf7a",
                "compression": "#e87ba4", "deflection": "#eda100"}
CHECK_MARKER = {"buckling": "o", "t_min": "s", "compression": "^", "deflection": "D"}

INK = "#0b0b0b"           # primary text
INK_2 = "#52514e"         # secondary text, axes
MUTED = "#898781"         # tertiary text, subtitles
GRID = "#e1e0d9"          # hairline grid
AXIS = "#c3c2b7"          # baseline / spines
BAND = "#efeee9"          # 5 % rule band wash
BAND_EDGE = "#d6d4cb"     # 5 % rule band edge
SURFACE = "#ffffff"       # figure background (print)

#: Ordered neutral steps for ordered variables (light -> dark), 2 or 3 levels.
ORDINAL = {2: ("#9c9a92", "#2b2b29"), 3: ("#b4b2aa", "#6f6e68", "#1f1f1d")}
ORDINAL_MARKER = ("o", "s", "^")

#: Ordered orange steps for the two seismic levels of the gallery sections.
SEISMIC_STEPS = ("#f4a582", "#c4441a")

#: Diverging anchors for a height change: lower, zero, higher.
DIVERGING = ("#0f6e78", "#f2f1ec", "#b5452a")

# --- Type and sizes ----------------------------------------------------------
FONT_FILES = ("Inter-Regular.otf", "Inter-Italic.otf", "Inter-Medium.otf", "Inter-SemiBold.otf")
FONT_FAMILY = ["Inter", "Arial", "Helvetica", "DejaVu Sans"]
TEXT_PT = 7.0
TITLE_PT = 7.5
LETTER_PT = 8.0
FOOTER_PT = 5.5
LINE_PT = 1.0             # data line weight [pt]
HAIR_PT = 0.5             # grid and spine weight [pt]
MARKER_PT = 3.4           # marker size [pt]
MM = 1 / 25.4             # inch per mm
WIDTH_MM = {"single": 90.0, "onehalf": 140.0, "full": 190.0}
DPI = 600                 # raster for print; PDF is vector


def size(width="full", aspect=0.5):
    """Return a figure size (inch) for an Elsevier column width.

    Args:
        width: "single", "onehalf" or "full" (WIDTH_MM).
        aspect: height / width [-].
    """
    w = WIDTH_MM[width] * MM
    return (w, w * aspect)


def register_fonts():
    """Register the bundled Inter files (assets/fonts) with matplotlib.

    Bundling the font makes the figures look the same on every machine. If
    the files are missing, matplotlib falls back along FONT_FAMILY.

    Returns:
        Number of font files registered.
    """
    n = 0
    for name in FONT_FILES:
        p = FONT_DIR / name
        if p.exists():
            font_manager.fontManager.addfont(str(p))
            n += 1
    return n


def apply():
    """Set matplotlib's rcParams to the ShellForm figure style."""
    register_fonts()
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FONT_FAMILY,
        "font.size": TEXT_PT,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Inter",
        "mathtext.it": "Inter:italic",
        "mathtext.bf": "Inter:semibold",
        "mathtext.sf": "Inter",
        "mathtext.cal": "Inter",
        "mathtext.tt": "DejaVu Sans Mono",
        "axes.titlesize": TITLE_PT,
        "axes.titleweight": "medium",
        "axes.titlecolor": INK,
        "axes.titlelocation": "left",
        "axes.titlepad": 6.0,
        "figure.constrained_layout.use": False,
        "axes.labelsize": TEXT_PT,
        "axes.labelcolor": INK_2,
        "axes.edgecolor": AXIS,
        "axes.linewidth": HAIR_PT,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.facecolor": SURFACE,
        "grid.color": GRID,
        "grid.linewidth": HAIR_PT,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.labelsize": TEXT_PT - 0.5,
        "ytick.labelsize": TEXT_PT - 0.5,
        "xtick.major.width": HAIR_PT,
        "ytick.major.width": HAIR_PT,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "xtick.minor.width": HAIR_PT * 0.8,
        "ytick.minor.width": HAIR_PT * 0.8,
        "lines.linewidth": LINE_PT,
        "lines.markersize": MARKER_PT,
        "legend.fontsize": TEXT_PT,
        "legend.frameon": False,
        "legend.handletextpad": 0.5,
        "legend.columnspacing": 1.4,
        "figure.facecolor": SURFACE,
        "figure.dpi": 150,
        "savefig.dpi": DPI,
        "savefig.facecolor": SURFACE,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })


def diverging_cmap():
    """Return the height-change colour map (teal - warm grey - brick)."""
    return LinearSegmentedColormap.from_list("shellform_dz", list(DIVERGING), N=256)


def panel_letter(ax, letter, x=-0.02, y=1.0):
    """Write a bold panel letter, e.g. "a", at the top left of an axes.

    Args:
        ax: matplotlib axes (2D or 3D).
        letter: the letter, without brackets.
        x, y: position in axes fraction.
    """
    ax.text2D(x, y, letter, transform=ax.transAxes, fontsize=LETTER_PT, fontweight="semibold",
              color=INK, ha="right", va="bottom") if hasattr(ax, "text2D") else \
        ax.text(x, y, letter, transform=ax.transAxes, fontsize=LETTER_PT, fontweight="semibold",
                color=INK, ha="right", va="bottom")

