"""First gallery: the gravity form and how the seismic-aware form differs from it.

One figure per span, figures/gallery_<span>m.png, at the middle rise
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
shellform.designs.form, the same builder the runs use. The footer names the
ShellBench tag and the record files; figures/gallery_<span>m.json holds the
plotted summary numbers.

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


def grid(xyz):
    """Return X, Y, Z arrays (n, n) of a node array (n*n, 3)."""
    return (xyz[:, k].reshape(N_GRID, N_GRID) for k in range(3))


def gallery(span):
    """Draw and save the gallery of one span.

    Returns:
        Dict of the plotted summary numbers (also written to the JSON file).
    """
    rec = record(span)
    tag = record_tag(rec)
    fig = plt.figure(figsize=(16, 7.6))
    summary = {"shellbench_tag": tag, "span_m": span, "rise_ratio": GALLERY_RISE,
               "grid_n": N_GRID, "record": [f"results/day04_sizing_{span:g}m.csv",
                                            f"results/day05_steel_carbon_{span:g}m.csv"],
               "rows": {}}
    for i, sup in enumerate(SUPPORTS):
        _, grav, _ = form(_case(span, sup, "gravity", 0.0))
        X, Y, Zg = grid(grav)
        g0 = rec[design_id(span, sup, GALLERY_RISE, "gravity", 0.0)]
        ax = fig.add_subplot(2, 4, 4 * i + 1, projection="3d")
        ax.plot_surface(X, Y, Zg, cmap="Greys", linewidth=0, antialiased=True, alpha=0.9)
        ax.set_box_aspect((1, 1, 0.45))
        ax.set_title(f"{sup}, gravity form (Sa 0)\n{label(g0)}", fontsize=9)
        ax.set_xlabel("x [m]", fontsize=8)
        ax.set_ylabel("y [m]", fontsize=8)
        ax.set_zlabel("z [m]", fontsize=8)
        ax.tick_params(labelsize=7)
        row = {"gravity_sa0": g0["design_id"], "seismic": {}}
        mid_row = N_GRID // 2
        axs = fig.add_subplot(2, 4, 4 * i + 4)
        axs.plot(X[mid_row], SECTION_EXAGGERATION * Zg[mid_row], "k-", lw=1.5, label="gravity")
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
            axs.plot(X[mid_row], SECTION_EXAGGERATION * Zs[mid_row], ["--", ":"][j], lw=1.3,
                     color=["#1f77b4", "#d62728"][j], label=f"seismic-aware, Sa {sa:.1f} g")
        lim = max(float(np.abs(d).max()) for d in dzs) or 1.0
        for j, (sa, dz) in enumerate(zip(GALLERY_SA, dzs)):
            axp = fig.add_subplot(2, 4, 4 * i + 2 + j)
            cs = axp.contourf(X, Y, dz, levels=np.linspace(-lim, lim, 21), cmap="RdBu_r")
            axp.set_aspect("equal")
            s_rec = rec[design_id(span, sup, GALLERY_RISE, "seismic", sa)]
            axp.set_title(f"{sup}, seismic-aware − gravity, Sa {sa:.1f} g\n{label(s_rec)}", fontsize=9)
            axp.set_xlabel("x [m]", fontsize=8)
            axp.set_ylabel("y [m]", fontsize=8)
            axp.tick_params(labelsize=7)
            cb = fig.colorbar(cs, ax=axp, shrink=0.85)
            cb.set_label("Δz [mm]", fontsize=8)
            cb.ax.tick_params(labelsize=7)
        axs.set_title(f"{sup}, section y = 0", fontsize=9)
        axs.set_xlabel("x [m]", fontsize=8)
        axs.set_ylabel(f"z × {SECTION_EXAGGERATION:g} [m]", fontsize=8)
        axs.tick_params(labelsize=7)
        axs.set_aspect("equal")
        axs.legend(fontsize=7, loc="lower center")
        summary["rows"][sup] = row
    fig.suptitle(f"ShellForm gallery, span {span:g} m, rise/span {GALLERY_RISE}", fontsize=12)
    fig.text(0.01, 0.005, f"ShellBench {tag}. Numbers in titles from "
             f"{summary['record'][0]} and {summary['record'][1]} (provisional). "
             "Written by python -m shellform.gallery.", fontsize=7)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97), h_pad=3.0)
    out = ROOT / "figures" / f"gallery_{span:g}m.png"
    fig.savefig(out, dpi=150, metadata={"Description": f"ShellBench {tag}"})
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
