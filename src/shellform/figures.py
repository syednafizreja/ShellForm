"""Paper figures, drawn from the committed record in results/ (Day 11).

Every figure here reads only files in results/ (and ShellBench, for the
compressive strength and the design spectrum), so no number in a figure is
typed by hand. Each figure is written as PNG (600 dpi) and PDF to figures/,
with a JSON file of the plotted numbers beside it. Every JSON and every
figure footer names the ShellBench tag that the record files carry.

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

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
BASELINE_FILE = "batch_all.csv"
CELLS_FILE = "sensitivity_cells.csv"
VARIANT_FILES = {"lam3": "sens_lam3.csv", "lam8": "sens_lam8.csv", "mesh61": "sens_mesh61.csv"}
S5_FILE = "s5_plateau.csv"

#: Categorical colours in fixed order (dataviz reference palette, light mode,
#: slots 1-4). Identity is never colour alone: every series also has its own
#: marker and a legend entry.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d9d8d4"
BAND = "#e8e7e3"
DPI = 600  # raster for print (manuscript workflow skill, section 6); PDF is vector

CHECKS = (  # (key, legend label, marker); order fixes the colour slot
    ("buckling", r"buckling: $\lambda_{min}/\lambda$", "o"),
    ("t_min", r"minimum thickness: $t_{min}/t$", "s"),
    ("compression", r"compression: $\sigma_c/f_c$", "^"),
    ("deflection", r"deflection: $\delta/(L/300)$", "D"),
)


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
    """Apply the recessive grid and axis style to one axes."""
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK_2)
    ax.tick_params(labelsize=7, colors=INK_2)


def _save(fig, stem, summary, footer):
    """Write the figure as PNG and PDF and its plotted numbers as JSON."""
    fig.text(0.01, 0.005, footer, fontsize=6, color=INK_2)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"{stem}.{ext}", dpi=DPI,
                    metadata={"Title": stem, "Subject": f"ShellBench {summary['shellbench_tag']}",
                              "CreationDate": None}
                    if ext == "pdf" else {"Description": f"ShellBench {summary['shellbench_tag']}"})
    plt.close(fig)
    (FIGURES / f"{stem}.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")


def fig02_mechanism(f_c_pa=None):
    """Draw Fig. 2: demand/limit ratio of each check against Sa.

    Rows: support case; columns: span. Each design is one marker per check
    (filled: gravity form; open: seismic-aware form; the three rises are
    shown side by side with a small offset in Sa). The dashed line at 1 is
    the limit; the check that sits on it sets the thickness.

    Returns:
        Dict of the plotted numbers (also written to figures/fig02_mechanism.json).
    """
    if f_c_pa is None:
        from shellform.inputs import load_inputs

        f_c_pa = load_inputs().f_c_pa
    rows = read_csv(BASELINE_FILE)
    tag = record_tag(rows, BASELINE_FILE)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6), sharex=True, sharey=True)
    summary = {"shellbench_tag": tag, "record": f"results/{BASELINE_FILE}",
               "f_c_pa": f_c_pa, "lambda_min": LAMBDA_MIN, "t_min_m": THICKNESS_MIN_M,
               "deflection_span_ratio": DEFLECTION_SPAN_RATIO, "panels": {}}
    offsets = dict(zip(RISE_RATIOS, (-0.018, 0.0, 0.018)))
    for i, sup in enumerate(SUPPORTS):
        for j, span in enumerate(SPANS_M):
            ax = axes[i, j]
            sel = [r for r in rows if r["supports"] == sup and float(r["span_m"]) == span]
            panel = {"designs": len(sel), "governing": {}, "ratio_range": {}}
            for c in sel:
                panel["governing"][c["governing_check"]] = panel["governing"].get(c["governing_check"], 0) + 1
            for k, (key, lab, mk) in enumerate(CHECKS):
                vals = []
                for strat, filled in (("gravity", True), ("seismic", False)):
                    pts = [(float(r["sa_g"]) + offsets[float(r["rise_ratio"])], ratios(r, f_c_pa)[key])
                           for r in sel if r["strategy"] == strat]
                    vals += [v for _, v in pts]
                    x, y = zip(*pts)
                    ax.scatter(x, y, s=14, marker=mk, lw=0.8, color=SERIES[k],
                               facecolors=SERIES[k] if filled else "none", zorder=3,
                               label=lab if (i, j, strat) == (0, 0, "gravity") else None)
                panel["ratio_range"][key] = [min(vals), max(vals)]
            ax.axhline(1.0, color=INK, lw=0.8, ls="--", zorder=2)
            ax.set_yscale("log")
            ax.set_ylim(5e-4, 2.0)
            gov = "; ".join(f"{k} {v}" for k, v in sorted(panel["governing"].items()))
            ax.set_title(f"{span:g} m span, {sup} supported\ngoverning: {gov}", fontsize=8, color=INK)
            _style(ax)
            if i == 1:
                ax.set_xlabel(r"$S_a$ [g]", fontsize=8, color=INK)
            if j == 0:
                ax.set_ylabel("demand / limit [-]", fontsize=8, color=INK)
            summary["panels"][f"{span:g}m_{sup}"] = panel
    axes[0, 0].set_xticks(SA_LEVELS_G)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    handles.append(plt.Line2D([], [], color=INK_2, marker="o", ls="", mfc="none", ms=4))
    labels.append("open marker: seismic-aware form")
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
    _save(fig, "fig02_mechanism", summary,
          f"ShellBench {tag}. Record: results/{BASELINE_FILE} (168 designs). "
          "Rises 0.10/0.15/0.20 offset left to right in Sa. Written by scripts/day11_figures.py.")
    return summary


def fig03_strategy_difference():
    """Draw Fig. 3: (seismic - gravity) / gravity carbon per cell against Sa.

    The marker is the central factor set; the vertical bar spans the four
    corners of the factor band. The grey band is the pre-registered 5 % rule
    ("no meaningful difference" inside it).

    Returns:
        Dict of the plotted numbers (also written to figures/fig03_strategy_difference.json).
    """
    cells = [c for c in read_csv(CELLS_FILE) if c["variant"] == "baseline"]
    rows = read_csv(BASELINE_FILE)
    tag = record_tag(rows, BASELINE_FILE)
    corners = [f"rel_{b}" for b in band_corners()]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=True, sharey=True)
    summary = {"shellbench_tag": tag, "record": [f"results/{CELLS_FILE}", f"results/{BASELINE_FILE}"],
               "meaningful_difference": MEANINGFUL_DIFFERENCE, "panels": {}}
    offsets = dict(zip(RISE_RATIOS, (-0.018, 0.0, 0.018)))
    markers = ("o", "s", "^")
    for i, sup in enumerate(SUPPORTS):
        for j, span in enumerate(SPANS_M):
            ax = axes[i, j]
            ax.axhspan(-100 * MEANINGFUL_DIFFERENCE, 100 * MEANINGFUL_DIFFERENCE, color=BAND, zorder=1)
            panel = {"verdicts": {}, "rel_central_pct": {}}
            for k, rise in enumerate(RISE_RATIOS):
                sel = [c for c in cells if c["supports"] == sup and float(c["span_m"]) == span
                       and float(c["rise_ratio"]) == rise]
                x = np.array([float(c["sa_g"]) + offsets[rise] for c in sel])
                y = np.array([100 * float(c["rel_central"]) for c in sel])
                lo = np.array([100 * min(float(c[b]) for b in corners) for c in sel])
                hi = np.array([100 * max(float(c[b]) for b in corners) for c in sel])
                ax.vlines(x, lo, hi, color=SERIES[k], lw=0.8, zorder=2)
                ax.scatter(x, y, s=16, marker=markers[k], color=SERIES[k], zorder=3,
                           label=f"rise/span {rise:.2f}" if (i, j) == (0, 0) else None)
                panel["rel_central_pct"][f"{rise:.2f}"] = [round(v, 4) for v in y]
                for c in sel:
                    v = c["verdict_central"]
                    panel["verdicts"][v] = panel["verdicts"].get(v, 0) + 1
            ax.axhline(0, color=INK_2, lw=0.6, zorder=2)
            verd = "; ".join(f"{k} {v}" for k, v in sorted(panel["verdicts"].items()))
            ax.set_title(f"{span:g} m span, {sup} supported\n{verd}", fontsize=8, color=INK)
            _style(ax)
            if i == 1:
                ax.set_xlabel(r"$S_a$ [g]", fontsize=8, color=INK)
            if j == 0:
                ax.set_ylabel("seismic-aware vs gravity form\ncarbon difference [%]", fontsize=8, color=INK)
            summary["panels"][f"{span:g}m_{sup}"] = panel
    axes[0, 0].set_xticks(SA_LEVELS_G)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    handles.append(plt.Rectangle((0, 0), 1, 1, color=BAND))
    labels.append(f"±{100 * MEANINGFUL_DIFFERENCE:g} %: no meaningful difference")
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.02, 1, 0.92))
    _save(fig, "fig03_strategy_difference", summary,
          f"ShellBench {tag}. Record: results/{CELLS_FILE} (baseline rows). Vertical bars: range over the four "
          "corners of the ±25 % factor band (mostly hidden by the markers). Written by scripts/day11_figures.py.")
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


def fig04_carbon_drivers():
    """Draw Fig. 4: the range of carbon ratio caused by each driver.

    One panel per support case; one horizontal bar per driver and span. A bar
    from a to b means the driver moves carbon per m2 by a factor between a
    and b over the pre-registered design space.

    Returns:
        Dict of the plotted numbers (also written to figures/fig04_carbon_drivers.json).
    """
    tag, ranges = driver_ranges()
    drivers = list(ranges)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=True, sharex=True)
    summary = {"shellbench_tag": tag,
               "record": [f"results/{BASELINE_FILE}", f"results/{CELLS_FILE}"]
               + [f"results/{f}" for f in VARIANT_FILES.values()],
               "ranges": {d: {f"{s:g}m_{sup}": v for (s, sup), v in r.items()} for d, r in ranges.items()}}
    y = np.arange(len(drivers))[::-1]
    for i, sup in enumerate(SUPPORTS):
        ax = axes[i]
        ax.axvspan(1 - MEANINGFUL_DIFFERENCE, 1 + MEANINGFUL_DIFFERENCE, color=BAND, zorder=1)
        ax.axvline(1.0, color=INK_2, lw=0.6, zorder=2)
        for k, span in enumerate(SPANS_M):
            dy = 0.15 if k == 0 else -0.15
            for yi, d in zip(y, drivers):
                lo, hi = ranges[d][(span, sup)]
                ax.plot([lo, hi], [yi + dy, yi + dy], color=SERIES[k], lw=3.0, solid_capstyle="round",
                        zorder=3, label=f"{span:g} m span" if (i, yi) == (0, y[0]) else None)
                ax.plot([lo, hi], [yi + dy] * 2, ls="", marker="|", color=SERIES[k], ms=6, zorder=3)
        ax.set_yticks(y)
        ax.set_yticklabels(drivers, fontsize=7)
        ax.set_title(f"{sup} supported", fontsize=8, color=INK)
        ax.set_xlabel("carbon per m² of plan, ratio [-]", fontsize=8, color=INK)
        _style(ax)
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(plt.Rectangle((0, 0), 1, 1, color=BAND))
    labels.append(f"±{100 * MEANINGFUL_DIFFERENCE:g} %")
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    _save(fig, "fig04_carbon_drivers", summary,
          f"ShellBench {tag}. Records: results/{BASELINE_FILE}, {CELLS_FILE}, sens_*.csv. "
          "Written by scripts/day11_figures.py.")
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

    tg, t0 = spectrum_constants()
    rows = [r for r in read_csv(S5_FILE)]
    tag = record_tag(rows, S5_FILE)
    t = np.linspace(0.0, 1.5 * tg, 400)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(t, [alpha_shape(v, tg) for v in t], color=INK, lw=1.2, label=r"$\alpha(T)/\alpha_{max}$",
            zorder=2)
    ax.axvline(tg, color=INK_2, lw=0.6, ls="--")
    ax.text(tg, 1.05, r" $T_g$", fontsize=7, color=INK_2)
    summary = {"shellbench_tag": tag, "record": f"results/{S5_FILE}", "tg_s": tg,
               "plateau_start_s": t0, "groups": {}}
    k = 0
    for span in SPANS_M:
        for sup in SUPPORTS:
            sel = [r for r in rows if float(r["span_m"]) == span and r["supports"] == sup]
            per = np.array([float(r["period_1_s"]) for r in sel])
            alp = np.array([float(r["alpha_shape"]) for r in sel])
            ax.scatter(per, alp, s=14, marker="osD^"[k], color=SERIES[k], zorder=3,
                       label=f"{span:g} m, {sup} (T1 {per.min():.3f}-{per.max():.3f} s)")
            summary["groups"][f"{span:g}m_{sup}"] = {"designs": len(sel), "t1_min_s": float(per.min()),
                                                     "t1_max_s": float(per.max()),
                                                     "s5_pass": all(r["s5_pass"] == "True" for r in sel)}
            k += 1
    ax.set_xlim(0, 1.5 * tg)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("first-mode period T1 [s]", fontsize=8, color=INK)
    ax.set_ylabel(r"$\alpha(T)/\alpha_{max}$ [-]", fontsize=8, color=INK)
    _style(ax)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "fig05_s5_periods", summary,
          f"ShellBench {tag}. Record: results/{S5_FILE} (baseline, 168 designs). Spectrum from "
          "shellbench.seismic. Written by scripts/day11_figures.py.")
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
