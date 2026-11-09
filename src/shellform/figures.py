"""Paper figures, drawn from the committed record in results/ (Day 11).

Every figure here reads only files in results/ (and ShellBench, for the
compressive strength and the design spectrum), so no number in a figure is
typed by hand. Each figure is written as PNG (600 dpi) and PDF to figures/,
with a JSON file of the plotted numbers beside it. Every JSON and the
metadata of every PNG and PDF name the ShellBench tag that the record files
carry. Look and sizes: shellform.style and docs/visual_style.md (9 Nov 2026
restyle; plotted numbers unchanged).

Figures (numbering is the planned paper order [J]; the form gallery of Day 8,
``shellform.gallery``, is Fig. 1):

- Fig. 2, ``fig02_mechanism``: the mechanism figure of
  ``paper/04_supervisor_advice.md`` section 3. For each of the 168 baseline
  designs, the ratio of each check's demand to its limit at the sized
  thickness, against Sa, by support case and span. The check at ratio 1 is
  the one that sets the thickness.
- Fig. 3, ``fig03_strategy_difference``: the pre-registered decision rule
  (section 7). Relative carbon difference, seismic-aware minus gravity form,
  per cell against Sa, with the 5 % band and the range over the four factor
  band corners.
- Fig. 4, ``fig04_carbon_drivers``: what moves carbon. Range of the carbon
  ratio caused by Sa, by the strategy, by the buckling threshold (3, 8), by
  the 61 x 61 network and by the factor band, by support case.
- Fig. 5, ``fig05_s5_periods``: test S5. First-mode periods of every design
  on ShellBench's design spectrum shape.

Usage: python scripts/day11_figures.py  (or python -m shellform.figures)
"""

import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from shellform.carbon import band_corners  # noqa: E402
from shellform.design_space import RISE_RATIOS, SA_LEVELS_G, SPANS_M, SUPPORTS  # noqa: E402
from shellform.pipeline import MEANINGFUL_DIFFERENCE, ROOT  # noqa: E402
from shellform.sizing import DEFLECTION_SPAN_RATIO, LAMBDA_MIN, THICKNESS_MIN_M  # noqa: E402
from shellform import style  # noqa: E402

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
BASELINE_FILE = "batch_all.csv"
CELLS_FILE = "sensitivity_cells.csv"
VARIANT_FILES = {"lam3": "sens_lam3.csv", "lam8": "sens_lam8.csv", "mesh61": "sens_mesh61.csv"}
S5_FILE = "s5_plateau.csv"

#: The sizing checks in legend order: (key, legend label). Colour and marker
#: come from shellform.style (CHECK_COLOUR, CHECK_MARKER).
CHECKS = (
    ("buckling", r"buckling  $\lambda_{min}/\lambda$"),
    ("t_min", r"minimum thickness  $t_{min}/t$"),
    ("compression", r"compression  $\sigma_c/f_c$"),
    ("deflection", r"deflection  $\delta/(L/300)$"),
)
SUPPORT_LABEL = {"corners": "corner supports", "edges": "edge supports"}
SCRIPT = "scripts/day11_figures.py"


def read_csv(name):
    """Read results/<name> into a list of dicts (text values)."""
    with open(RESULTS / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def record_tag(rows, name):
    """Return the single ShellBench tag named by a record file's rows.

    Raises:
        ValueError: If the rows name no tag or more than one tag.
    """
    tags = {r.get("shellbench_tag", "") for r in rows}
    if len(tags) != 1 or "" in tags:
        raise ValueError(f"results/{name} names ShellBench tags {sorted(tags)}; expected one")
    return tags.pop()


def ratios(row, f_c_pa):
    """Return the demand/limit ratio of each sizing check for one design row.

    Limits are the pre-registered ones in ``shellform.sizing`` (section 5);
    f_c_pa is ShellBench's design compressive strength [Pa]. Compression is
    the value outside the corner support zones (D4-2), as the sizing used it.

    Returns:
        {check key: ratio [-]}; 1.0 means the check is exactly at its limit.
    """
    span = float(row["span_m"])
    t = float(row["thickness_m"])
    return {"buckling": LAMBDA_MIN / float(row["buckling_factor"]),
            "t_min": THICKNESS_MIN_M / t,
            "compression": float(row["max_compression_mpa"]) * 1e6 / f_c_pa,
            "deflection": float(row["max_deflection_m"]) / (span / DEFLECTION_SPAN_RATIO)}


def _style(ax):
    """Finish one axes: recessive hairline grid, no top/right spines."""
    ax.grid(True, which="major")
    ax.grid(False, which="minor")
    ax.tick_params(which="both", direction="out")


def _panel_title(ax, letter, title, sub=None):
    """Write the bold panel letter and a left-aligned title on one line, and an
    optional muted subtitle under it, all above the top left of the axes."""
    y_title = 12.0 if sub else 4.0
    kw = dict(xycoords="axes fraction", textcoords="offset points", va="bottom", annotation_clip=False)
    ax.annotate(letter, (0, 1), xytext=(-12, y_title), fontsize=style.LETTER_PT, fontweight="semibold",
                color=style.INK, ha="left", **kw)
    ax.annotate(title, (0, 1), xytext=(0, y_title), fontsize=style.TITLE_PT, fontweight="medium",
                color=style.INK, ha="left", **kw)
    if sub:
        ax.annotate(sub, (0, 1), xytext=(0, 3.0), fontsize=style.TEXT_PT - 0.5, color=style.MUTED,
                    ha="left", **kw)


def _counts(d):
    """Return 'name n · name n' for a count dict, sorted by name."""
    return " \u00b7 ".join(f"{k.replace('t_min', 'minimum thickness')} {v}" for k, v in sorted(d.items()))


def _save(fig, stem, summary, provenance):
    """Write the figure as PNG (600 dpi) and vector PDF, and its numbers as JSON.

    The provenance (ShellBench tag, record files, script) is written into the
    file metadata of both images and into the JSON, not into the artwork, so
    the figure can go into the manuscript as it is (docs/visual_style.md).
    """
    tag = summary["shellbench_tag"]
    meta_png = {"Title": stem, "Description": f"ShellBench {tag}. {provenance}", "Software": SCRIPT}
    meta_pdf = {"Title": stem, "Subject": f"ShellBench {tag}. {provenance}", "Creator": SCRIPT,
                "CreationDate": None}
    fig.savefig(FIGURES / f"{stem}.png", dpi=style.DPI, metadata=meta_png)
    fig.savefig(FIGURES / f"{stem}.pdf", metadata=meta_pdf)
    plt.close(fig)
    (FIGURES / f"{stem}.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")


def _log_ticks(ax):
    """Label a log axis 0.001, 0.01, 0.1, 1 instead of powers of ten."""
    from matplotlib.ticker import FuncFormatter, LogLocator

    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))


def fig02_mechanism(f_c_pa=None):
    """Draw Fig. 2: demand/limit ratio of each check against Sa.

    Rows: support case; columns: span. Each design is one marker per check
    (filled: gravity-only form; open: seismic-aware form; the three rises are
    shown side by side with a small offset in Sa). The line at 1 is the
    limit; the check that sits on it sets the thickness.

    Returns:
        Dict of the plotted numbers (also written to figures/fig02_mechanism.json).
    """
    if f_c_pa is None:
        from shellform.inputs import load_inputs

        f_c_pa = load_inputs().f_c_pa
    style.apply()
    rows = read_csv(BASELINE_FILE)
    tag = record_tag(rows, BASELINE_FILE)
    fig, axes = plt.subplots(2, 2, figsize=style.size("full", 0.62), sharex=True, sharey=True)
    summary = {"shellbench_tag": tag, "record": f"results/{BASELINE_FILE}",
               "f_c_pa": f_c_pa, "lambda_min": LAMBDA_MIN, "t_min_m": THICKNESS_MIN_M,
               "deflection_span_ratio": DEFLECTION_SPAN_RATIO, "panels": {}}
    offsets = dict(zip(RISE_RATIOS, (-0.022, 0.0, 0.022)))
    letters = iter("abcd")
    for i, sup in enumerate(SUPPORTS):
        for j, span in enumerate(SPANS_M):
            ax = axes[i, j]
            sel = [r for r in rows if r["supports"] == sup and float(r["span_m"]) == span]
            panel = {"designs": len(sel), "governing": {}, "ratio_range": {}}
            for c in sel:
                panel["governing"][c["governing_check"]] = panel["governing"].get(c["governing_check"], 0) + 1
            ax.axhspan(1.0, 2.0, color=style.BAND, lw=0, zorder=0)
            for key, lab in CHECKS:
                vals = []
                col, mk = style.CHECK_COLOUR[key], style.CHECK_MARKER[key]
                for strat, filled in (("gravity", True), ("seismic", False)):
                    pts = [(float(r["sa_g"]) + offsets[float(r["rise_ratio"])], ratios(r, f_c_pa)[key])
                           for r in sel if r["strategy"] == strat]
                    vals += [v for _, v in pts]
                    x, y = zip(*pts)
                    ax.scatter(x, y, s=9, marker=mk, linewidths=0.7, edgecolors=col,
                               facecolors=col if filled else "none", zorder=3 if filled else 4)
                panel["ratio_range"][key] = [min(vals), max(vals)]
            ax.axhline(1.0, color=style.INK, lw=0.7, zorder=2)
            ax.set_yscale("log")
            ax.set_ylim(1.5e-3, 1.7)
            _log_ticks(ax)
            if (i, j) == (0, 1):
                ax.text(0.655, 1.08, "limit", fontsize=style.TEXT_PT - 0.5, color=style.INK_2,
                        ha="right", va="bottom")
            _panel_title(ax, next(letters), f"{span:g} m span, {SUPPORT_LABEL[sup]}",
                         f"sets the thickness: {_counts(panel['governing'])} of {len(sel)}")
            _style(ax)
            if i == 1:
                ax.set_xlabel(r"plateau spectral acceleration $S_a$ [g]")
            if j == 0:
                ax.set_ylabel("demand / limit [-]")
            summary["panels"][f"{span:g}m_{sup}"] = panel
    axes[0, 0].set_xticks(SA_LEVELS_G)
    axes[0, 0].set_xlim(-0.06, 0.66)
    handles = [plt.Line2D([], [], ls="", marker=style.CHECK_MARKER[k], ms=4.2, mew=0.7,
                          color=style.CHECK_COLOUR[k]) for k, _ in CHECKS]
    labels = [lab for _, lab in CHECKS]
    handles += [plt.Line2D([], [], ls="", marker="o", ms=4.2, color=style.INK_2),
                plt.Line2D([], [], ls="", marker="o", ms=4.2, mew=0.7, mfc=style.SURFACE, color=style.INK_2)]
    labels += ["gravity-only form", "seismic-aware form"]
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=6, fontsize=style.TEXT_PT - 0.5,
               handletextpad=0.2, columnspacing=1.1)
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=1.6, w_pad=1.4)
    _save(fig, "fig02_mechanism", summary,
          f"Record: results/{BASELINE_FILE} (168 designs). Rises 0.10/0.15/0.20 offset left to right in Sa.")
    return summary


def fig03_strategy_difference():
    """Draw Fig. 3: (seismic - gravity) / gravity carbon per cell against Sa.

    The marker is the central factor set; the vertical bar spans the four
    corners of the factor band. The grey band is the pre-registered 5 % rule
    ("no meaningful difference" inside it).

    Returns:
        Dict of the plotted numbers (also written to figures/fig03_strategy_difference.json).
    """
    style.apply()
    cells = [c for c in read_csv(CELLS_FILE) if c["variant"] == "baseline"]
    rows = read_csv(BASELINE_FILE)
    tag = record_tag(rows, BASELINE_FILE)
    corners = [f"rel_{b}" for b in band_corners()]
    fig, axes = plt.subplots(2, 2, figsize=style.size("full", 0.56), sharex=True, sharey=True)
    summary = {"shellbench_tag": tag, "record": [f"results/{CELLS_FILE}", f"results/{BASELINE_FILE}"],
               "meaningful_difference": MEANINGFUL_DIFFERENCE, "panels": {}}
    offsets = dict(zip(RISE_RATIOS, (-0.022, 0.0, 0.022)))
    tones = style.ORDINAL[3]
    letters = iter("abcd")
    band = 100 * MEANINGFUL_DIFFERENCE
    for i, sup in enumerate(SUPPORTS):
        for j, span in enumerate(SPANS_M):
            ax = axes[i, j]
            ax.axhspan(-band, band, color=style.BAND, lw=0, zorder=0)
            for yb in (-band, band):
                ax.axhline(yb, color=style.BAND_EDGE, lw=0.5, zorder=1)
            ax.axhline(0, color=style.AXIS, lw=0.6, zorder=1)
            panel = {"verdicts": {}, "rel_central_pct": {}}
            for k, rise in enumerate(RISE_RATIOS):
                sel = [c for c in cells if c["supports"] == sup and float(c["span_m"]) == span
                       and float(c["rise_ratio"]) == rise]
                x = np.array([float(c["sa_g"]) + offsets[rise] for c in sel])
                y = np.array([100 * float(c["rel_central"]) for c in sel])
                lo = np.array([100 * min(float(c[b]) for b in corners) for c in sel])
                hi = np.array([100 * max(float(c[b]) for b in corners) for c in sel])
                ax.vlines(x, lo, hi, color=tones[k], lw=0.7, zorder=2)
                ax.scatter(x, y, s=12, marker=style.ORDINAL_MARKER[k], color=tones[k],
                           edgecolors=style.SURFACE, linewidths=0.4, zorder=3)
                panel["rel_central_pct"][f"{rise:.2f}"] = [round(v, 4) for v in y]
                for c in sel:
                    v = c["verdict_central"]
                    panel["verdicts"][v] = panel["verdicts"].get(v, 0) + 1
            if (i, j) == (0, 1):
                ax.text(0.64, band - 0.35, f"±{band:g} %: no meaningful difference", fontsize=style.TEXT_PT - 0.5,
                        color=style.INK_2, ha="right", va="top")
            _panel_title(ax, next(letters), f"{span:g} m span, {SUPPORT_LABEL[sup]}",
                         _counts(panel["verdicts"]) + " cells")
            _style(ax)
            if i == 1:
                ax.set_xlabel(r"plateau spectral acceleration $S_a$ [g]")
            if j == 0:
                ax.set_ylabel("carbon, seismic-aware vs\ngravity-only form [%]")
            summary["panels"][f"{span:g}m_{sup}"] = panel
    axes[0, 0].set_xticks(SA_LEVELS_G)
    axes[0, 0].set_xlim(-0.06, 0.66)
    axes[0, 0].set_ylim(-7.0, 7.0)
    axes[0, 0].set_yticks([-6, -4, -2, 0, 2, 4, 6])
    handles = [plt.Line2D([], [], ls="", marker=style.ORDINAL_MARKER[k], ms=4.4, color=tones[k])
               for k in range(3)]
    labels = [f"rise/span {r:.2f}" for r in RISE_RATIOS]
    handles.append(plt.Line2D([], [], color=style.INK_2, lw=0.7))
    labels.append("range over the ±25 % carbon-factor band")
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=4,
               fontsize=style.TEXT_PT - 0.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=1.6, w_pad=1.4)
    _save(fig, "fig03_strategy_difference", summary,
          f"Record: results/{CELLS_FILE} (baseline rows). Vertical bars: range over the four corners of "
          "the ±25 % factor band (mostly hidden by the markers).")
    return summary


def driver_ranges():
    """Return the carbon ratio range each driver causes, by span and support.

    Drivers (each a ratio of carbon per m2 of plan area, central factors):
    Sa for the gravity form and for the seismic-aware form (cost of
    resilience, section 7); the strategy (seismic / gravity at equal Sa);
    each sensitivity variant (variant / baseline, same design); the factor
    band (each corner / central).

    Returns:
        (tag, {driver: {(span, supports): (min, max)}}), the tag being the one
        all the record files share.

    Raises:
        ValueError: If the record files name different ShellBench tags.
    """
    base = read_csv(BASELINE_FILE)
    tag = record_tag(base, BASELINE_FILE)
    cells = [c for c in read_csv(CELLS_FILE) if c["variant"] == "baseline"]
    by_id = {r["design_id"]: r for r in base}
    col = "carbon_gbt51366_kgco2e_m2"
    out = {}

    def add(driver, span, sup, v):
        rng = out.setdefault(driver, {}).setdefault((span, sup), [v, v])
        rng[0], rng[1] = min(rng[0], v), max(rng[1], v)

    for c in cells:
        key = (float(c["span_m"]), c["supports"])
        add(r"$S_a$ 0 to 0.6 g, gravity form", *key, float(c["cost_of_resilience_gravity"]))
        add(r"$S_a$ 0 to 0.6 g, seismic-aware form", *key, float(c["cost_of_resilience_seismic"]))
        add("strategy: seismic-aware / gravity", *key, 1 + float(c["rel_central"]))
    labels = {"lam3": r"buckling threshold $\lambda_{min}$ 5 to 3",
              "lam8": r"buckling threshold $\lambda_{min}$ 5 to 8",
              "mesh61": "network 41 x 41 to 61 x 61"}
    for name, fname in VARIANT_FILES.items():
        rows = read_csv(fname)
        if record_tag(rows, fname) != tag:
            raise ValueError(f"results/{fname} and results/{BASELINE_FILE} name different tags")
        for r in rows:
            b = by_id[r["design_id"]]
            add(labels[name], float(r["span_m"]), r["supports"], float(r[col]) / float(b[col]))
    for r in base:
        for b in band_corners():
            add("carbon factors: ±25 % band corners", float(r["span_m"]), r["supports"],
                float(r[f"carbon_kgco2e_m2_{b}"]) / float(r[col]))
    return tag, out


#: Display labels of the drivers in Fig. 4 (the JSON keeps the driver_ranges keys).
DRIVER_LABEL = {
    r"$S_a$ 0 to 0.6 g, gravity form": r"$S_a$ 0 → 0.6 g, gravity-only form",
    r"$S_a$ 0 to 0.6 g, seismic-aware form": r"$S_a$ 0 → 0.6 g, seismic-aware form",
    "strategy: seismic-aware / gravity": "strategy: seismic-aware / gravity-only",
    r"buckling threshold $\lambda_{min}$ 5 to 3": r"buckling threshold $\lambda_{min}$ 5 → 3",
    r"buckling threshold $\lambda_{min}$ 5 to 8": r"buckling threshold $\lambda_{min}$ 5 → 8",
    "network 41 x 41 to 61 x 61": "form-finding network 41×41 → 61×61",
    "carbon factors: ±25 % band corners": "carbon factors: ±25 % band corners",
}


def fig04_carbon_drivers():
    """Draw Fig. 4: the range of carbon ratio caused by each driver.

    One panel per support case; one range bar per driver and span. A bar
    from a to b means the driver moves carbon per m2 by a factor between a
    and b over the pre-registered design space.

    Returns:
        Dict of the plotted numbers (also written to figures/fig04_carbon_drivers.json).
    """
    style.apply()
    tag, ranges = driver_ranges()
    drivers = list(ranges)
    fig, axes = plt.subplots(1, 2, figsize=style.size("full", 0.42), sharey=True, sharex=True)
    summary = {"shellbench_tag": tag,
               "record": [f"results/{BASELINE_FILE}", f"results/{CELLS_FILE}"]
               + [f"results/{f}" for f in VARIANT_FILES.values()],
               "ranges": {d: {f"{s:g}m_{sup}": v for (s, sup), v in r.items()} for d, r in ranges.items()}}
    y = np.arange(len(drivers))[::-1]
    tones = style.ORDINAL[2]
    for i, sup in enumerate(SUPPORTS):
        ax = axes[i]
        ax.axvspan(1 - MEANINGFUL_DIFFERENCE, 1 + MEANINGFUL_DIFFERENCE, color=style.BAND, lw=0, zorder=0)
        for xb in (1 - MEANINGFUL_DIFFERENCE, 1 + MEANINGFUL_DIFFERENCE):
            ax.axvline(xb, color=style.BAND_EDGE, lw=0.5, zorder=1)
        ax.axvline(1.0, color=style.AXIS, lw=0.6, zorder=1)
        for k, span in enumerate(SPANS_M):
            dy = 0.16 if k == 0 else -0.16
            for yi, d in zip(y, drivers):
                lo, hi = ranges[d][(span, sup)]
                ax.plot([lo, hi], [yi + dy] * 2, color=tones[k], lw=2.2, solid_capstyle="round", zorder=3)
                ax.plot([lo, hi], [yi + dy] * 2, ls="", marker="o", ms=3.2, color=tones[k], mew=0, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels([DRIVER_LABEL.get(d, d) for d in drivers])
        ax.tick_params(axis="y", length=0, labelcolor=style.INK)
        ax.grid(False, axis="y")
        ax.set_ylim(-0.6, len(drivers) - 0.4)
        _panel_title(ax, "ab"[i], SUPPORT_LABEL[sup].capitalize())
        ax.set_xlabel("carbon per m² of plan, ratio to the reference [-]")
        _style(ax)
        ax.grid(False, axis="y")
    axes[0].set_xlim(0.68, 1.36)
    handles = [plt.Line2D([], [], color=tones[k], lw=2.2, marker="o", ms=3.2, mew=0) for k in range(2)]
    labels = [f"{s:g} m span" for s in SPANS_M]
    handles.append(plt.Rectangle((0, 0), 1, 1, fc=style.BAND, ec=style.BAND_EDGE, lw=0.5))
    labels.append(f"±{100 * MEANINGFUL_DIFFERENCE:g} %: no meaningful difference")
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=3,
               fontsize=style.TEXT_PT - 0.5)
    fig.tight_layout(rect=(0, 0, 1, 0.93), w_pad=1.6)
    _save(fig, "fig04_carbon_drivers", summary,
          f"Records: results/{BASELINE_FILE}, {CELLS_FILE}, sens_*.csv.")
    return summary


def fig05_s5_periods():
    """Draw Fig. 5: first-mode periods of the 168 designs on the spectrum shape.

    The curve is ShellBench's alpha(T)/alpha_max for the anchor site (Tg);
    markers are the baseline designs' T1 read from results/s5_plateau.csv.
    S5 passes when every T1 is at or below Tg, where the equivalent static
    load at the plateau value is not below the spectral value.

    Returns:
        Dict of the plotted numbers (also written to figures/fig05_s5_periods.json).
    """
    from shellform.s5 import alpha_shape, spectrum_constants

    style.apply()
    tg, t0 = spectrum_constants()
    rows = [r for r in read_csv(S5_FILE)]
    tag = record_tag(rows, S5_FILE)
    t = np.linspace(0.0, 1.5 * tg, 400)
    fig, ax = plt.subplots(figsize=style.size("full", 0.36))
    ax.axvspan(0, tg, color=style.BAND, lw=0, zorder=0)
    ax.plot(t, [alpha_shape(v, tg) for v in t], color=style.INK, lw=1.0, zorder=2)
    ax.axvline(tg, color=style.INK_2, lw=0.6, ls=(0, (3, 2)), zorder=1)
    ax.text(tg + 0.004, 1.13, r"$T_g$" + f" = {tg:g} s", fontsize=style.TEXT_PT - 0.5, color=style.INK_2,
            va="top")
    ax.text(0.5 * tg + 0.12, 1.09, r"S5 holds where $T_1 \leq T_g$", fontsize=style.TEXT_PT - 0.5,
            color=style.INK_2, ha="center", va="top")
    ax.text(1.5 * tg - 0.005, alpha_shape(1.5 * tg, tg) + 0.07, r"$\alpha(T)/\alpha_{max}$",
            fontsize=style.TEXT_PT - 0.5, color=style.INK, ha="right", va="bottom")
    summary = {"shellbench_tag": tag, "record": f"results/{S5_FILE}", "tg_s": tg,
               "plateau_start_s": t0, "groups": {}}
    markers = {"corners": "o", "edges": "s"}
    for k, span in enumerate(SPANS_M):
        for sup in SUPPORTS:
            sel = [r for r in rows if float(r["span_m"]) == span and r["supports"] == sup]
            per = np.array([float(r["period_1_s"]) for r in sel])
            alp = np.array([float(r["alpha_shape"]) for r in sel])
            ax.scatter(per, alp, s=14, marker=markers[sup], color=style.ORDINAL[2][k],
                       edgecolors=style.SURFACE, linewidths=0.5, zorder=3,
                       label=f"{span:g} m, {SUPPORT_LABEL[sup]}  ($T_1$ {per.min():.3f}–{per.max():.3f} s)")
            summary["groups"][f"{span:g}m_{sup}"] = {"designs": len(sel), "t1_min_s": float(per.min()),
                                                     "t1_max_s": float(per.max()),
                                                     "s5_pass": all(r["s5_pass"] == "True" for r in sel)}
    ax.set_xlim(0, 1.5 * tg)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel(r"first-mode period $T_1$ [s]")
    ax.set_ylabel(r"$\alpha(T)/\alpha_{max}$ [-]")
    _style(ax)
    ax.legend(loc="lower right", fontsize=style.TEXT_PT - 0.5, handletextpad=0.3)
    fig.tight_layout()
    _save(fig, "fig05_s5_periods", summary,
          f"Record: results/{S5_FILE} (baseline, 168 designs). Spectrum from shellbench.seismic.")
    return summary


def main(argv=None):
    """Draw Figs. 2-5 (and Fig. 1, the gallery, unless --no-gallery)."""
    ap = argparse.ArgumentParser(prog="python -m shellform.figures")
    ap.add_argument("--no-gallery", action="store_true", help="skip Fig. 1 (needs form finding)")
    a = ap.parse_args(argv)
    if not a.no_gallery:
        from shellform.gallery import gallery

        for span in SPANS_M:
            gallery(span)
            print(f"wrote figures/gallery_{span:g}m.png (Fig. 1)")
    for f in (fig02_mechanism, fig03_strategy_difference, fig04_carbon_drivers, fig05_s5_periods):
        f()
        print(f"wrote figures/{f.__name__}.png/.pdf/.json")


if __name__ == "__main__":
    main()
