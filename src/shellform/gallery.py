"""First gallery: the gravity form and how the seismic-aware form differs from it.

One figure per span, figures/gallery_<span>m.png and .pdf, at the middle rise
(rise/span 0.15). One row per support case:

1. the gravity form (strategy 1) in 3D;
2. and 3. a plan map of the height change of the seismic-aware form
   (strategy 2) against the gravity form, z_seismic - z_gravity [mm], at
   Sa = 0.3 g and 0.6 g;
4. the section through the middle of the plan (y = 0), gravity form and
   both seismic forms, with the vertical scale exaggerated.

Each panel title gives the sized thickness, the buckling factor and the
carbon per m2 of plan area of that design, read from the committed record
(results/day04_sizing_<span>m.csv and results/day05_steel_carbon_<span>m.csv),
so the gallery shows no number that is not in results/. Forms come from
shellform.designs.form, the same builder the runs use. The image metadata
names the ShellBench tag and the record files; figures/gallery_<span>m.json
holds the plotted summary numbers.

Usage: python -m shellform.gallery [--span 10 20]
"""

import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from shellform.design_space import SUPPORTS, design_id  # noqa: E402
from shellform.designs import N_GRID, form  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from shellform import style  # noqa: E402
from shellform.pipeline import ROOT  # noqa: E402

GALLERY_RISE = 0.15          # middle pre-registered rise ratio [J]
GALLERY_SA = (0.3, 0.6)      # pre-registered S4 Sa and the largest Sa level [J]
SECTION_EXAGGERATION = 3.0   # vertical scale of the section panel [J], stated in its label


def _case(span, supports, strategy, sa):
    """Return the design_space-style dict of one design."""
    return dict(design_id=design_id(span, supports, GALLERY_RISE, strategy, sa), span_m=span,
                supports=supports, rise_ratio=GALLERY_RISE, strategy=strategy, sa_g=sa)


def record(span):
    """Return {design_id: merged record row} from the committed Day 4-6 files of one span."""
    tag = f"{span:g}m"
    rec = {}
    for name in (f"day04_sizing_{tag}.csv", f"day05_steel_carbon_{tag}.csv"):
        with open(ROOT / "results" / name, newline="") as f:
            for r in csv.DictReader(f):
                rec.setdefault(r["design_id"], {}).update(r)
    return rec


def record_tag(rec):
    """Return the one ShellBench tag the record rows name (Day 11: the gallery
    names the record's tag, not the pin, so a pin move before a rerun of the
    record cannot mislabel it).

    Raises:
        ValueError: If the rows name no tag or more than one.
    """
    tags = {r.get("shellbench_tag", "") for r in rec.values()}
    if len(tags) != 1 or "" in tags:
        raise ValueError(f"record names ShellBench tags {sorted(tags)}; expected one")
    return tags.pop()


def label(rec_row):
    """Return the short panel label (t, lambda, carbon) of one record row."""
    t = float(rec_row["thickness_m"]) * 1e3
    lam = float(rec_row["buckling_factor"])
    c = float(rec_row["carbon_gbt51366_kgco2e_m2"])
    return f"t {t:.0f} mm, λ {lam:.1f}, {c:.1f} kgCO₂e/m²"


SUPPORT_LABEL = {"corners": "Corner supports", "edges": "Edge supports"}


def _title(ax, letter, title, sub):
    """Write the panel letter, title and muted subtitle above an axes (2D or 3D)."""
    put = ax.text2D if hasattr(ax, "text2D") else ax.text
    put(-0.04, 1.13, letter, transform=ax.transAxes, fontsize=style.LETTER_PT, fontweight="semibold",
        color=style.INK, ha="right", va="bottom")
    put(0.0, 1.13, title, transform=ax.transAxes, fontsize=style.TITLE_PT - 0.5, fontweight="medium",
        color=style.INK, ha="left", va="bottom")
    put(0.0, 1.03, sub, transform=ax.transAxes, fontsize=style.TEXT_PT - 1.5, color=style.MUTED,
        ha="left", va="bottom")


def grid(xyz):
    """Return X, Y, Z arrays (n, n) of a node array (n*n, 3)."""
    return (xyz[:, k].reshape(N_GRID, N_GRID) for k in range(3))


def gallery(span):
    """Draw and save the gallery of one span (PNG 600 dpi and vector PDF).

    Layout (docs/visual_style.md): one row per support case; columns are the
    gravity form in 3D, the height change of the seismic-aware form at the
    two Sa levels (shared diverging scale per row), and the mid-plan section.

    Returns:
        Dict of the plotted summary numbers (also written to the JSON file).
    """
    from matplotlib.colors import LightSource

    style.apply()
    rec = record(span)
    tag = record_tag(rec)
    fig = plt.figure(figsize=style.size("full", 0.56))
    gs = fig.add_gridspec(2, 6, width_ratios=(1.15, 1, 1, 0.05, 0.22, 1.2), wspace=0.18, hspace=0.75,
                          left=0.05, right=0.99, top=0.80, bottom=0.10)
    summary = {"shellbench_tag": tag, "span_m": span, "rise_ratio": GALLERY_RISE,
               "grid_n": N_GRID, "record": [f"results/day04_sizing_{span:g}m.csv",
                                            f"results/day05_steel_carbon_{span:g}m.csv"],
               "rows": {}}
    cmap = style.diverging_cmap()
    light = LightSource(azdeg=315, altdeg=40)
    letters = iter("abcdefgh")
    for i, sup in enumerate(SUPPORTS):
        _, grav, _ = form(_case(span, sup, "gravity", 0.0))
        X, Y, Zg = grid(grav)
        g0 = rec[design_id(span, sup, GALLERY_RISE, "gravity", 0.0)]
        ax = fig.add_subplot(gs[i, 0], projection="3d")
        rgb = light.shade(Zg, cmap=LinearSegmentedColormap.from_list("g", ["#c9d9ee", style.GRAVITY]),
                          vert_exag=2.0, blend_mode="soft")
        ax.plot_surface(X, Y, Zg, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=False,
                        shade=False, rasterized=True)
        ax.plot_wireframe(X, Y, Zg, rstride=5, cstride=5, color="white", linewidth=0.3, alpha=0.75)
        ax.set_box_aspect((1, 1, 0.42), zoom=1.3)
        ax.view_init(elev=24, azim=-58)
        ax.set_axis_off()
        _title(ax, next(letters), "gravity-only form, 3D", label(g0))
        fig.text(0.012, 0.5 * (gs[i, 0].get_position(fig).y0 + gs[i, 0].get_position(fig).y1),
                 SUPPORT_LABEL[sup], rotation=90, fontsize=style.TITLE_PT, fontweight="semibold",
                 color=style.INK, ha="left", va="center")
        row = {"gravity_sa0": g0["design_id"], "seismic": {}}
        mid_row = N_GRID // 2
        axs = fig.add_subplot(gs[i, 5])
        axs.plot(X[mid_row], SECTION_EXAGGERATION * Zg[mid_row], color=style.GRAVITY, lw=1.3,
                 label="gravity-only", zorder=3)
        dzs = []
        for j, sa in enumerate(GALLERY_SA):
            _, _, mid = form(_case(span, sup, "seismic", sa))
            _, _, Zs = grid(mid)
            dz = (Zs - Zg) * 1e3
            dzs.append(dz)
            s_rec = rec[design_id(span, sup, GALLERY_RISE, "seismic", sa)]
            g_rec = rec[design_id(span, sup, GALLERY_RISE, "gravity", sa)]
            row["seismic"][f"{sa:.1f}"] = {
                "design_id": s_rec["design_id"], "dz_min_mm": float(dz.min()), "dz_max_mm": float(dz.max()),
                "max_horizontal_shift_mm": float(np.abs(mid[:, :2] - grav[:, :2]).max() * 1e3),
                "seismic_kgco2e_m2": float(s_rec["carbon_gbt51366_kgco2e_m2"]),
                "gravity_kgco2e_m2": float(g_rec["carbon_gbt51366_kgco2e_m2"])}
            axs.plot(X[mid_row], SECTION_EXAGGERATION * Zs[mid_row], color=style.SEISMIC_STEPS[j], lw=1.0,
                     ls=("-", (0, (4, 1.5)))[j], label=f"seismic-aware, $S_a$ {sa:.1f} g", zorder=2 + j)
        lim = max(float(np.abs(d).max()) for d in dzs) or 1.0
        levels = np.linspace(-lim, lim, 25)
        for j, (sa, dz) in enumerate(zip(GALLERY_SA, dzs)):
            axp = fig.add_subplot(gs[i, 1 + j])
            cs = axp.contourf(X, Y, dz, levels=levels, cmap=cmap)
            axp.contour(X, Y, dz, levels=levels[::4], colors=style.INK, linewidths=0.2, alpha=0.35)
            axp.plot(np.r_[X[0], X[:, -1], X[-1, ::-1], X[::-1, 0]], np.r_[Y[0], Y[:, -1], Y[-1, ::-1], Y[::-1, 0]],
                     color=style.INK_2, lw=0.5)
            axp.set_aspect("equal")
            axp.grid(False)
            for s_ in axp.spines.values():
                s_.set_visible(False)
            axp.set_xticks([-span / 2, 0, span / 2])
            axp.set_yticks([-span / 2, 0, span / 2])
            axp.tick_params(labelsize=style.TEXT_PT - 1.5, length=1.5)
            axp.set_xlabel("x [m]", fontsize=style.TEXT_PT - 1, labelpad=1)
            if j == 0:
                axp.set_ylabel("y [m]", fontsize=style.TEXT_PT - 1, labelpad=0)
            s_rec = rec[design_id(span, sup, GALLERY_RISE, "seismic", sa)]
            _title(axp, next(letters), f"height change, $S_a$ {sa:.1f} g", label(s_rec))
        cax = fig.add_subplot(gs[i, 3])
        cb = fig.colorbar(cs, cax=cax, ticks=np.linspace(-lim, lim, 5))
        cb.outline.set_visible(False)
        cb.ax.tick_params(labelsize=style.TEXT_PT - 1.5, length=1.5)
        cb.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:+.0f}" if abs(v) > 1e-9 else "0"))
        cb.ax.set_title("Δz [mm]", fontsize=style.TEXT_PT - 1.5, color=style.INK_2, pad=4, loc="left")
        _title(axs, next(letters), "section through y = 0",
               f"vertical scale ×{SECTION_EXAGGERATION:g}")
        axs.set_xlabel("x [m]", fontsize=style.TEXT_PT - 1, labelpad=1)
        axs.set_ylabel(f"{SECTION_EXAGGERATION:g} z [m]", fontsize=style.TEXT_PT - 1, labelpad=1)
        axs.tick_params(labelsize=style.TEXT_PT - 1.5)
        axs.set_ylim(bottom=min(0.0, axs.get_ylim()[0]))
        if i == 0:
            fig.legend(*axs.get_legend_handles_labels(), loc="upper right", bbox_to_anchor=(0.99, 0.985),
                       ncol=3, fontsize=style.TEXT_PT - 1, handlelength=2.0)
        summary["rows"][sup] = row
    fig.text(0.012, 0.975, f"Span {span:g} m, rise/span {GALLERY_RISE:.2f}", fontsize=style.TITLE_PT + 1,
             fontweight="semibold", color=style.INK, va="top")
    fig.text(0.012, 0.93, "Δz: height of the seismic-aware form minus the gravity-only form. "
             "Subtitles: sized thickness t, buckling factor λ, carbon per m² of plan (GB/T 51366).",
             fontsize=style.TEXT_PT - 0.5, color=style.MUTED, va="top")
    prov = (f"ShellBench {tag}. Numbers in titles from {summary['record'][0]} and {summary['record'][1]}. "
            "Written by python -m shellform.gallery.")
    for ext in ("png", "pdf"):
        meta = ({"Title": f"gallery_{span:g}m", "Description": prov, "Software": "shellform.gallery"}
                if ext == "png" else {"Title": f"gallery_{span:g}m", "Subject": prov,
                                      "Creator": "shellform.gallery", "CreationDate": None})
        fig.savefig(ROOT / "figures" / f"gallery_{span:g}m.{ext}", dpi=style.DPI, metadata=meta)
    plt.close(fig)
    (ROOT / "figures" / f"gallery_{span:g}m.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main(argv=None):
    """Draw the gallery of each span given (default both)."""
    ap = argparse.ArgumentParser(prog="python -m shellform.gallery")
    ap.add_argument("--span", type=float, nargs="+", default=[10.0, 20.0])
    a = ap.parse_args(argv)
    for span in a.span:
        gallery(span)
        print(f"wrote figures/gallery_{span:g}m.png")


if __name__ == "__main__":
    main()
