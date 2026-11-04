"""scripts/day07_s4.py — Day 7, test S4 (closed-form lean of a parabolic arch).

Pre-registration section 8: if the full text of Michiels & Adriaenssens
(C&S 2018) is not available by 4 Nov, S4 is the closed-form lean of a
parabolic arch under uniform horizontal acceleration. It was not available,
so this script runs that fallback (amendment of 4 Nov 2026).

What it runs, for spans 10 m and 20 m (the two design spans):

- S4 (arch): a 2D chain of N_SEGMENTS equal plan segments, form-found with
  ShellForm's own solver (shellform.formfind) at rise-to-span 1/2, 1/4 and
  1/8 and Sa = 0.15, 0.30 and 0.45 g. These are the cases named in the
  abstract of Michiels & Adriaenssens, C&S 195 (2018) 85-98; the
  pre-registered case is 1/4 at 0.30 g. Each form is compared with the
  closed form (shellform.checks.leaned_parabola) node by node, and its
  support reactions with shellform.checks.leaned_arch_reactions.
- S4b (shells): every design shell family (both supports, rise 0.10, 0.15,
  0.20, Sa 0.1-0.6 g, 41 x 41 network as in shellform.designs) form-found
  with the lateral load, compared with the gravity form sheared by -Sa z
  (shellform.strategies.thrust_surface with lambda = 1). This links the arch
  result to the forms the design space uses.
- S2 on every form (equilibrium residual).

Pass (stated before the run, amendment of 4 Nov): every relative error
below 1e-9 (positions divided by span, forces divided by the total load).

No ShellBench value is used: S4 is geometry and statics only. The results
file still names the pinned ShellBench tag (CLAUDE.md, code standards).
Writes results/day07_s4_arch.csv, results/day07_s4_shells.csv and
results/day07_s4_meta.json.
"""

import csv
import json
from pathlib import Path

import numpy as np

from shellform.checks import (equilibrium_error, leaned_arch_reactions, leaned_parabola,
                              support_reactions)
from shellform.design_space import RISE_RATIOS, SA_LEVELS_G, SPANS_M, SUPPORTS
from shellform.designs import CORNER_EDGE_INSET_RATIO, N_GRID
from shellform.formfind import (Network, corner_network_for_inset, form_to_rise, plan_loads,
                                solve, square_network)
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.strategies import thrust_surface

ROOT = Path(__file__).resolve().parents[1]
N_SEGMENTS = N_GRID - 1                    # same node count per line as the shells (41)
ARCH_RISE_RATIOS = (1 / 2, 1 / 4, 1 / 8)   # Michiels & Adriaenssens 2018, abstract
ARCH_SA_G = (0.15, 0.30, 0.45)             # Michiels & Adriaenssens 2018, abstract
PRIMARY = (1 / 4, 0.30)                    # pre-registration section 8
TOLERANCE = 1e-9                           # amendment of 4 Nov 2026, set before the run
W_NODE_N = 1.0                             # weight per node; the form does not depend on it


def arch_network(span_m):
    """Return a straight 2D chain on the x axis from 0 to span_m.

    Args:
        span_m: Support distance [m].

    Returns:
        A Network with N_SEGMENTS equal segments, both ends pinned, q = -1 N/m.
    """
    x = np.linspace(0.0, span_m, N_SEGMENTS + 1)
    xyz = np.column_stack([x, np.zeros_like(x), np.zeros_like(x)])
    edges = np.column_stack([np.arange(N_SEGMENTS), np.arange(1, N_SEGMENTS + 1)])
    return Network(xyz, edges, np.full(N_SEGMENTS, -1.0), np.array([0, N_SEGMENTS]),
                   np.arange(1, N_SEGMENTS), np.zeros(N_SEGMENTS, bool))


def run_arch(span_m, rise_ratio, sa_g):
    """Form-find one leaned arch and compare it with the closed form.

    Args:
        span_m: Support distance [m].
        rise_ratio: Rise of the gravity form divided by span [-].
        sa_g: Horizontal acceleration in +x [g].

    Returns:
        Dict with the case, the crown lean and every relative error [-].
    """
    rise = rise_ratio * span_m
    net = arch_network(span_m)
    s = net.xyz[:, 0].copy()
    form = form_to_rise(net, rise, sa_x=sa_g)
    loads = plan_loads(net, w_node=W_NODE_N, sa_x=sa_g)
    x_cf, z_cf = leaned_parabola(span_m, rise, sa_g, s)
    pos_err = np.hypot(form[:, 0] - x_cf, form[:, 2] - z_cf).max() / span_m
    # The scaled force density sets the weight scale: form_to_rise uses w = 1 N.
    react = support_reactions(form, net.edges, net.q, net.fixed)
    cf = leaned_arch_reactions(span_m, rise, sa_g, N_SEGMENTS, W_NODE_N)
    w_total = (N_SEGMENTS - 1) * W_NODE_N
    got = {"h_left": react[0, 0], "h_right": -react[1, 0],
           "v_left": react[0, 2], "v_right": react[1, 2]}
    force_err = max(abs(got[k] - cf[k]) for k in cf) / w_total
    crown = N_SEGMENTS // 2
    return {"span_m": span_m, "rise_ratio": rise_ratio, "sa_g": sa_g,
            "primary": (rise_ratio, sa_g) == PRIMARY,
            "crown_lean_m": float(s[crown] - form[crown, 0]),
            "crown_lean_closed_form_m": sa_g * rise,
            "h_left_n": got["h_left"], "h_right_n": got["h_right"],
            "v_left_n": got["v_left"], "v_right_n": got["v_right"],
            "position_error_rel": float(pos_err), "reaction_error_rel": float(force_err),
            "s2_equilibrium_error": equilibrium_error(form, net.edges, net.q, loads, net.free)}


def gravity_net(span_m, supports, rise_m):
    """Return (network, gravity form) built as shellform.designs.form builds them.

    Args:
        span_m: Plan side [m].
        supports: "corners" or "edges".
        rise_m: Gravity rise [m].

    Returns:
        (Network with q scaled to the rise, gravity form nodes) [m].
    """
    if supports == "corners":
        net, grav, _ = corner_network_for_inset(span_m, N_GRID, rise_m, CORNER_EDGE_INSET_RATIO)
    else:
        net = square_network(span_m, N_GRID, "edges")
        grav = form_to_rise(net, rise_m)
    return net, grav


def run_shells():
    """Run S4b on every design shell family with a lateral load.

    Returns:
        List of dicts, one per (span, supports, rise ratio, Sa > 0).
    """
    rows = []
    for span in SPANS_M:
        for supports in SUPPORTS:
            for rr in RISE_RATIOS:
                net, grav = gravity_net(span, supports, rr * span)
                for sa in (a for a in SA_LEVELS_G if a > 0.0):
                    loads = plan_loads(net, sa_x=sa)
                    form = solve(net, loads)
                    sheared = thrust_surface(grav, sa, (1.0, 0.0), 1.0)
                    err = np.linalg.norm(form - sheared, axis=1).max() / span
                    rows.append({"span_m": span, "supports": supports, "rise_ratio": rr,
                                 "sa_g": sa, "max_lean_m": float(np.abs(form[:, 0] - grav[:, 0]).max()),
                                 "shear_error_rel": float(err),
                                 "s2_equilibrium_error": equilibrium_error(
                                     form, net.edges, net.q, loads, net.free)})
    return rows


def write_csv(path, rows):
    """Write a list of dicts to CSV with a header row."""
    with open(path, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)


def main() -> None:
    """Run S4 and S4b and write the results files."""
    check_pin()
    arch = [run_arch(span, rr, sa) for span in SPANS_M for rr in ARCH_RISE_RATIOS for sa in ARCH_SA_G]
    shells = run_shells()
    worst = {"arch_position": max(r["position_error_rel"] for r in arch),
             "arch_reaction": max(r["reaction_error_rel"] for r in arch),
             "arch_s2": max(r["s2_equilibrium_error"] for r in arch),
             "shell_shear": max(r["shear_error_rel"] for r in shells),
             "shell_s2": max(r["s2_equilibrium_error"] for r in shells)}
    passed = all(v < TOLERANCE for v in worst.values())
    out_dir = ROOT / "results"
    write_csv(out_dir / "day07_s4_arch.csv", arch)
    write_csv(out_dir / "day07_s4_shells.csv", shells)
    meta = {"shellbench_tag": SHELLBENCH_TAG,
            "test": "S4 fallback: closed-form lean of a parabolic arch (pre-registration section 8, "
                    "amendment of 4 Nov 2026)",
            "n_segments": N_SEGMENTS, "shell_grid_n": N_GRID, "tolerance": TOLERANCE,
            "arch_cases_source": "Michiels & Adriaenssens, C&S 195 (2018) 85-98, abstract: "
                                 "rise/span 1/2, 1/4, 1/8 at 0.15, 0.3, 0.45 g",
            "worst_errors": worst, "passed": passed,
            "n_arch_cases": len(arch), "n_shell_cases": len(shells)}
    (out_dir / "day07_s4_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
