"""Figures of the check-window add-ons (14 Nov 2026): Fig. 6 and Fig. S1.

File: src/shellform/verify_figures.py

- Fig. 6, ``fig06_carbon_stability``: carbon per m2 of plan against the
  first linear buckling factor for every sized design, with the
  non-dominated (Pareto) front. Corner-supported shells are shown at the
  three buckling thresholds of the sensitivity runs (lambda >= 3, 5, 8),
  joined design by design, so the panel shows what stability costs. Every
  point is a frozen record value (batch_all.csv, sens_lam3.csv,
  sens_lam8.csv); nothing is recomputed.
- Fig. S1, ``figS1_verification``: the verification add-ons V1-V5
  (shellform.verification), from the record files that
  scripts/day17_verification.py writes.

Look: shellform.style and docs/visual_style.md. Strategy colours keep their
meaning (gravity-only blue, filled; seismic-aware orange, open). Every
figure writes its plotted numbers to JSON and names the ShellBench tag in
the JSON and in the image metadata.

Usage: python scripts/day17_figures.py
"""

import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter  # noqa: E402

from shellform import style  # noqa: E402
from shellform.design_space import SPANS_M, SUPPORTS  # noqa: E402
from shellform.figures import FIGURES, RESULTS, SUPPORT_LABEL, _panel_title, _style, record_tag  # noqa: E402
from shellform.pipeline import MEANINGFUL_DIFFERENCE  # noqa: E402
from shellform.sizing import LAMBDA_MIN  # noqa: E402

SCRIPT = "scripts/day17_figures.py"
SUPPORT_MARKER = {"corners": "o", "edges": "s"}
THRESHOLD_FILES = {3.0: "sens_lam3.csv", LAMBDA_MIN: "batch_all.csv", 8.0: "sens_lam8.csv"}


def read(name):
    """Read results/<name> as a list of dicts (text values)."""
    with open(RESULTS / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(fig, stem, summary, provenance):
    """Write PNG (600 dpi), vector PDF and the plotted numbers as JSON; provenance in metadata."""
    tag = summary["shellbench_tag"]
    fig.savefig(FIGURES / f"{stem}.png", dpi=style.DPI,
                metadata={"Title": stem, "Description": f"ShellBench {tag}. {provenance}", "Software": SCRIPT})
    fig.savefig(FIGURES / f"{stem}.pdf",
                metadata={"Title": stem, "Subject": f"ShellBench {tag}. {provenance}", "Creator": SCRIPT,
                          "CreationDate": None})
    plt.close(fig)
    (FIGURES / f"{stem}.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")


def pareto_front(lam, carbon):
    """Return the indices of the non-dominated points, by rising lambda.

    A point is dominated if another point has a buckling factor at least as
    high and carbon at least as low, and is better in one of the two.
    """
    lam, carbon = np.asarray(lam, float), np.asarray(carbon, float)
    keep = []
    for i in range(len(lam)):
        better = (lam >= lam[i]) & (carbon <= carbon[i]) & ((lam > lam[i]) | (carbon < carbon[i]))
        if not better.any():
            keep.append(i)
    return sorted(keep, key=lambda i: lam[i])


def _strategy_scatter(ax, x, y, strategy, marker, size=14, z=4):
    """Scatter with the strategy roles: gravity filled blue, seismic open orange."""
    if strategy == "gravity":
        ax.scatter(x, y, s=size, marker=marker, color=style.GRAVITY, edgecolors=style.SURFACE,
                   linewidths=0.4, zorder=z)
    else:
        ax.scatter(x, y, s=size, marker=marker, facecolors="none", edgecolors=style.SEISMIC,
                   linewidths=0.7, zorder=z + 0.5)


def _log_x(ax):
    """Label a log x axis with plain numbers (3, 5, 10, 30, ...)."""
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 3.0, 5.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())


def fig06_carbon_stability():
    """Draw Fig. 6: carbon against the first buckling factor, with the Pareto front.

    Returns:
        Dict of the plotted numbers (also written to figures/fig06_carbon_stability.json).
    """
    style.apply()
    runs = {lam: read(f) for lam, f in THRESHOLD_FILES.items()}
    tag = record_tag(runs[LAMBDA_MIN], "batch_all.csv")
    for lam, rows in runs.items():
        if record_tag(rows, THRESHOLD_FILES[lam]) != tag:
            raise ValueError("record files name different ShellBench tags")
    fig, axes = plt.subplots(1, 2, figsize=style.size("full", 0.44), sharey=False)
    summary = {"shellbench_tag": tag, "record": [f"results/{f}" for f in THRESHOLD_FILES.values()],
               "panels": {}}
    for j, span in enumerate(SPANS_M):
        ax = axes[j]
        pts, panel = [], {"front": [], "points": 0}
        # Hairline paths: one corner-shell design across the three thresholds.
        base_ids = [r["design_id"] for r in runs[LAMBDA_MIN] if float(r["span_m"]) == span]
        by = {lam: {r["design_id"]: r for r in rows} for lam, rows in runs.items()}
        for d in base_ids:
            if by[LAMBDA_MIN][d]["supports"] != "corners":
                continue
            xs = [float(by[lam][d]["buckling_factor"]) for lam in sorted(runs)]
            ys = [float(by[lam][d]["carbon_gbt51366_kgco2e_m2"]) for lam in sorted(runs)]
            ax.plot(xs, ys, color=style.AXIS, lw=0.45, zorder=2)
        for lam in sorted(runs):
            for r in runs[lam]:
                if float(r["span_m"]) != span:
                    continue
                if r["supports"] == "edges" and lam != LAMBDA_MIN:
                    continue  # edge shells sit on t_min at every threshold: same points
                x, y = float(r["buckling_factor"]), float(r["carbon_gbt51366_kgco2e_m2"])
                big = lam == LAMBDA_MIN
                _strategy_scatter(ax, x, y, r["strategy"], SUPPORT_MARKER[r["supports"]],
                                  size=13 if big else 7, z=4 if big else 3)
                pts.append((x, y, r["design_id"], lam))
        lam_all = [p[0] for p in pts]
        c_all = [p[1] for p in pts]
        front = pareto_front(lam_all, c_all)
        fx = [lam_all[i] for i in front]
        fy = [c_all[i] for i in front]
        ax.step(fx, fy, where="post", color=style.INK, lw=0.9, zorder=2.5)
        for lam in sorted(runs):
            if lam != LAMBDA_MIN:
                ax.axvline(lam, color=style.BAND_EDGE, lw=0.5, ls=(0, (3, 2)), zorder=1)
        ax.axvline(LAMBDA_MIN, color=style.INK_2, lw=0.6, zorder=1)
        ymax = max(c_all)
        for lam in sorted(runs):
            ax.text(lam, 1.0, f"λ ≥ {lam:g}", transform=ax.get_xaxis_transform(), rotation=90,
                    fontsize=style.TEXT_PT - 1.0, color=style.INK_2 if lam == LAMBDA_MIN else style.MUTED,
                    ha="right", va="top")
        e = [p for p in pts if "-edges-" in p[2]]
        ax.annotate("edge supports: on the\nminimum thickness, λ₁ well above 5", (max(p[0] for p in e), max(p[1] for p in e)),
                    xytext=(4, 14), textcoords="offset points", fontsize=style.TEXT_PT - 0.5, color=style.INK_2,
                    ha="right", va="bottom")
        _log_x(ax)
        ax.set_xlim(2.4, 400 if span == SPANS_M[0] else 100)
        ax.set_ylim(0, ymax * 1.1)
        ax.set_xlabel(r"first linear buckling factor $\lambda_1$ [-]")
        if j == 0:
            ax.set_ylabel("carbon per m² of plan [kgCO₂e/m²]")
        n_base = sum(1 for p in pts if p[3] == LAMBDA_MIN)
        _panel_title(ax, "ab"[j], f"{span:g} m span",
                     f"{n_base} sized designs at λ ≥ 5 · corner shells also at λ ≥ 3 and 8")
        _style(ax)
        panel["points"] = len(pts)
        seen = set()
        front = [i for i in front if not ((round(pts[i][0], 4), round(pts[i][1], 4)) in seen
                                          or seen.add((round(pts[i][0], 4), round(pts[i][1], 4))))]
        panel["front"] = [{"design_id": pts[i][2], "lambda_min_run": pts[i][3], "lambda_1": round(pts[i][0], 4),
                           "carbon_kgco2e_m2": round(pts[i][1], 4)} for i in front]
        sup_range = {}
        for sup in SUPPORTS:
            sel = [r for r in runs[LAMBDA_MIN] if float(r["span_m"]) == span and r["supports"] == sup]
            sup_range[sup] = {"lambda_1": [min(float(r["buckling_factor"]) for r in sel),
                                           max(float(r["buckling_factor"]) for r in sel)],
                              "carbon_kgco2e_m2": [min(float(r["carbon_gbt51366_kgco2e_m2"]) for r in sel),
                                                   max(float(r["carbon_gbt51366_kgco2e_m2"]) for r in sel)]}
        panel["baseline_ranges"] = sup_range
        summary["panels"][f"{span:g}m"] = panel
    h = [plt.Line2D([], [], ls="", marker="o", ms=4.2, color=style.GRAVITY, mec=style.SURFACE, mew=0.4),
         plt.Line2D([], [], ls="", marker="o", ms=4.2, mfc="none", mec=style.SEISMIC, mew=0.7),
         plt.Line2D([], [], ls="", marker="o", ms=4.2, mfc="none", mec=style.INK_2, mew=0.6),
         plt.Line2D([], [], ls="", marker="s", ms=4.0, mfc="none", mec=style.INK_2, mew=0.6),
         plt.Line2D([], [], color=style.INK, lw=0.9),
         plt.Line2D([], [], color=style.AXIS, lw=0.6)]
    labels = [style.STRATEGY_LABEL["gravity"], style.STRATEGY_LABEL["seismic"], "corner supports",
              "edge supports", "non-dominated (Pareto) front", "same design at λ ≥ 3, 5, 8"]
    fig.legend(h, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=6, fontsize=style.TEXT_PT - 0.5,
               columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.93), w_pad=2.0)
    save(fig, "fig06_carbon_stability", summary,
         "Records: results/batch_all.csv, sens_lam3.csv, sens_lam8.csv (freeze-2026-11-09).")
    return summary


def figS1_verification():
    """Draw Fig. S1: the verification add-ons V1-V5 in six panels.

    Returns:
        Dict of the plotted numbers (also written to figures/figS1_verification.json).
    """
    from shellform.verification import FDM_RESIDUAL_TOLERANCE, H_TOLERANCE, ZOELLY_TOLERANCE

    style.apply()
    v1, v2, v3 = read("verify_v1_zoelly.csv"), read("verify_v2_hconv.csv"), read("verify_v3_fdm_residual.csv")
    v4, v5 = read("verify_v4_energy.csv"), read("verify_v5_formwork.csv")
    tags = {record_tag(r, n) for r, n in ((v1, "v1"), (v2, "v2"), (v3, "v3"), (v4, "v4"), (v5, "v5"))}
    if len(tags) != 1:
        raise ValueError(f"verification files name different tags: {tags}")
    tag = tags.pop()
    summary = {"shellbench_tag": tag, "record": [f"results/verify_v{k}_{n}.csv" for k, n in
                                                 ((1, "zoelly"), (2, "hconv"), (3, "fdm_residual"),
                                                  (4, "energy"), (5, "formwork"))], "panels": {}}
    fig, axes = plt.subplots(2, 3, figsize=style.size("full", 0.66))
    tones = style.ORDINAL[2]

    def band(ax, half, horizontal=True):
        """Draw the acceptance band +-half as a warm grey wash with hairline edges."""
        (ax.axhspan if horizontal else ax.axvspan)(-half, half, color=style.BAND, lw=0, zorder=0)
        for b in (-half, half):
            (ax.axhline if horizontal else ax.axvline)(b, color=style.BAND_EDGE, lw=0.5, zorder=1)

    # a: Zoelly sphere
    ax = axes[0, 0]
    band(ax, 100 * ZOELLY_TOLERANCE)
    ax.axhline(0, color=style.AXIS, lw=0.6, zorder=1)
    pa = {}
    for k, rt in enumerate(sorted({float(r["r_over_t"]) for r in v1})):
        sel = sorted([r for r in v1 if float(r["r_over_t"]) == rt], key=lambda r: int(r["elements"]))
        x = [int(r["elements"]) for r in sel]
        y = [100 * float(r["relative_error"]) for r in sel]
        ax.plot(x, y, color=tones[k], lw=0.9, marker=style.ORDINAL_MARKER[k], ms=3.4, mec=style.SURFACE,
                mew=0.4, zorder=3, label=f"R/t = {rt:g}")
        ax.annotate(f"R/t = {rt:g}", (x[-1], y[-1]), xytext=(4, 0), textcoords="offset points",
                    fontsize=style.TEXT_PT - 0.5, color=tones[k], va="center")
        pa[f"R/t={rt:g}"] = {"elements": x, "error_pct": [round(v, 3) for v in y]}
    ax.set_xscale("log")
    ax.set_xticks([384, 864, 1536, 3456])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(300, 6000)
    ax.set_ylim(-4, 5)
    ax.set_xlabel("S8R elements on the sphere [-]")
    ax.set_ylabel(r"$p_{cr}$, FE vs closed form [%]")
    _panel_title(ax, "a", "Sphere under pressure (Zoelly)", f"band: ±{100 * ZOELLY_TOLERANCE:g} %")
    summary["panels"]["a_zoelly"] = pa

    # b, c: h-convergence
    ids = sorted({r["design_id"] for r in v2})
    for ax, key, lab, letter, title in ((axes[0, 1], "buckling_factor", r"$\lambda_1$", "b", "Buckling factor"),
                                        (axes[0, 2], "sls_deflection_m", r"$\delta_{SLS}$", "c",
                                         "SLS deflection")):
        band(ax, 100 * H_TOLERANCE)
        ax.axhline(0, color=style.AXIS, lw=0.6, zorder=1)
        pb = {}
        for d in ids:
            sel = sorted([r for r in v2 if r["design_id"] == d], key=lambda r: int(r["n"]))
            finest = float(sel[-1][key])
            x = [int(r["elements"]) for r in sel]
            y = [100 * (float(r[key]) / finest - 1) for r in sel]
            strat = "gravity" if "-gravity-" in d else "seismic"
            sup = "corners" if "-corners-" in d else "edges"
            ls = "-" if d.startswith("L10") else (0, (3, 1.5))
            col = style.STRATEGY[strat]
            ax.plot(x, y, color=col, lw=0.8, ls=ls, zorder=3)
            if strat == "gravity":
                ax.plot(x, y, ls="", marker=SUPPORT_MARKER[sup], ms=3.2, color=col, mec=style.SURFACE, mew=0.3,
                        zorder=4)
            else:
                ax.plot(x, y, ls="", marker=SUPPORT_MARKER[sup], ms=3.2, mfc=style.SURFACE, mec=col, mew=0.6,
                        zorder=4)
            pb[d] = {"elements": x, "change_vs_finest_pct": [round(v, 3) for v in y]}
        ax.axvline(400, color=style.INK_2, lw=0.5, ls=(0, (1, 1.5)), zorder=1)
        if letter == "b":
            ax.text(400 * 1.06, 0.97, "record\n(41 × 41)", transform=ax.get_xaxis_transform(), ha="left",
                    va="top", fontsize=style.TEXT_PT - 1.0, color=style.INK_2)
        ax.set_xscale("log")
        ax.set_xticks([100, 400, 900, 1600])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel("S8R elements on the shell [-]")
        ax.set_ylabel(f"{lab} vs finest network [%]")
        _panel_title(ax, letter, f"{title}, sized thickness", f"band: ±{100 * H_TOLERANCE:g} % · 8 designs")
        summary["panels"][f"{letter}_{key}"] = pb

    # d: FDM residual
    ax = axes[1, 0]
    pd = {}
    xs = np.arange(len(v3))
    order = sorted(range(len(v3)), key=lambda i: (v3[i]["span_m"], v3[i]["supports"], float(v3[i]["rise_ratio"]),
                                                   float(v3[i]["sa_g"])))
    for pos, i in enumerate(order):
        r = v3[i]
        k = 0 if r["span_m"].startswith("10") else 1
        ax.scatter(pos, float(r["residual_inf_n"]), s=7, marker=SUPPORT_MARKER[r["supports"]], color=tones[k],
                   edgecolors=style.SURFACE, linewidths=0.3, zorder=3)
    ax.axhline(FDM_RESIDUAL_TOLERANCE, color=style.INK_2, lw=0.6, zorder=2)
    ax.text(len(v3) - 1, FDM_RESIDUAL_TOLERANCE * 1.4, f"limit {FDM_RESIDUAL_TOLERANCE:g} N", ha="right",
            va="bottom", fontsize=style.TEXT_PT - 0.5, color=style.INK_2)
    ax.set_yscale("log")
    ax.set_ylim(1e-15, 1e-9)
    ax.set_xlim(-2, len(v3) + 1)
    ax.set_xticks([])
    ax.set_xlabel("form-finding solve (84: 4 families × 3 rises × 7 Sa) [-]")
    ax.set_ylabel(r"$\|Dx - p\|_\infty$ [N]")
    worst = max(float(r["residual_inf_n"]) for r in v3)
    _panel_title(ax, "d", "Force density residual", f"worst {worst:.1e} N · unit nodal weight 1 N")
    pd["worst_residual_n"] = worst
    summary["panels"]["d_fdm_residual"] = pd

    # e: membrane share
    ax = axes[1, 1]
    pe = {}
    for r in v4:
        for case, marker_open in (("uls_gravity", False), ("uls_seismic_px", True)):
            col = f"membrane_share_{case}"
            if not r.get(col):
                continue
            x = float(r["sa_g"]) + (0.012 if r["strategy"] == "seismic" else -0.012)
            y = 100 * float(r[col])
            if case == "uls_gravity" and float(r["sa_g"]) > 0:
                continue  # the gravity case is the same for every Sa: show it once, at Sa = 0
            _strategy_scatter(ax, x, y, r["strategy"], SUPPORT_MARKER[r["supports"]], size=8, z=3)
    for sup in SUPPORTS:
        for case in ("uls_gravity", "uls_seismic_px"):
            vals = [100 * float(r[f"membrane_share_{case}"]) for r in v4
                    if r["supports"] == sup and r.get(f"membrane_share_{case}")]
            pe[f"{sup}_{case}_pct"] = [round(min(vals), 2), round(max(vals), 2)]
    ax.set_xticks([0, 0.2, 0.4, 0.6])
    ax.set_xlim(-0.05, 0.65)
    ax.set_ylim(70, 101)
    ax.set_xlabel(r"$S_a$ of the ULS case [g]  (0: ULS gravity)")
    ax.set_ylabel(r"membrane share $U_m/U$ [%]")
    _panel_title(ax, "e", "Membrane share of strain energy", "168 sized designs")
    summary["panels"]["e_membrane_share"] = pe

    # f: formwork bound
    ax = axes[1, 2]
    half = 100 * MEANINGFUL_DIFFERENCE
    ax.axvspan(-half, half, color=style.BAND, lw=0, zorder=0)
    for b in (-half, half):
        ax.axvline(b, color=style.BAND_EDGE, lw=0.5, zorder=1)
    ax.axhline(0, color=style.AXIS, lw=0.6, zorder=1)
    ax.axvline(0, color=style.AXIS, lw=0.6, zorder=1)
    for r in v5:
        k = 0 if r["span_m"].startswith("10") else 1
        ax.scatter(100 * float(r["rel_carbon"]), 100 * float(r["rel_formwork_area"]), s=9,
                   marker=SUPPORT_MARKER[r["supports"]], color=tones[k], edgecolors=style.SURFACE, linewidths=0.3,
                   zorder=3)
    wa = max(abs(float(r["rel_formwork_area"])) for r in v5)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("A1–A3 carbon, seismic vs gravity [%]")
    ax.set_ylabel("formwork area, seismic vs gravity [%]")
    _panel_title(ax, "f", "Formwork (A5) cannot flip a verdict",
                 f"84 cells · area difference at most {100 * wa:.1f} %")
    summary["panels"]["f_formwork"] = {"worst_rel_formwork_area_pct": round(100 * wa, 3),
                                       "cells_safe_for_any_formwork": sum(r["verdict_safe_for_any_formwork"] == "True"
                                                                          for r in v5)}
    for ax in axes.ravel():
        _style(ax)
    axes[1, 0].grid(False, axis="x")
    h = [plt.Line2D([], [], ls="", marker="o", ms=4, color=style.GRAVITY, mec=style.SURFACE, mew=0.3),
         plt.Line2D([], [], ls="", marker="o", ms=4, mfc=style.SURFACE, mec=style.SEISMIC, mew=0.6),
         plt.Line2D([], [], ls="", marker="o", ms=4, mfc="none", mec=style.INK_2, mew=0.6),
         plt.Line2D([], [], ls="", marker="s", ms=3.8, mfc="none", mec=style.INK_2, mew=0.6),
         plt.Line2D([], [], color=tones[0], lw=2), plt.Line2D([], [], color=tones[1], lw=2),
         plt.Line2D([], [], color=style.INK_2, lw=0.8), plt.Line2D([], [], color=style.INK_2, lw=0.8, ls=(0, (3, 1.5)))]
    labels = [style.STRATEGY_LABEL["gravity"], style.STRATEGY_LABEL["seismic"], "corner supports", "edge supports",
              "10 m span (d, f)", "20 m span (d, f)", "b, c: 10 m", "b, c: 20 m"]
    fig.legend(h, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=8, fontsize=style.TEXT_PT - 1.0,
               columnspacing=0.9, handlelength=1.6)
    fig.tight_layout(rect=(0, 0, 1, 0.955), h_pad=2.2, w_pad=1.2)
    save(fig, "figS1_verification", summary,
         "Records: results/verify_v1..v5 (scripts/day17_verification.py); sized thicknesses from "
         "results/batch_all.csv (freeze-2026-11-09).")
    return summary


def main():
    """Draw Fig. 6 and Fig. S1."""
    for f in (fig06_carbon_stability, figS1_verification):
        f()
        print(f"wrote figures/{f.__name__}.png/.pdf/.json")


if __name__ == "__main__":
    main()
