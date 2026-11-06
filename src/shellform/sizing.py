"""Thickness sizing of one shell design (pre-registration section 5).

The sizing rule: the smallest uniform thickness, in 5 mm steps from 50 mm,
that passes every check in every load case. A design that fails at every
thickness up to span/50 is infeasible. The thresholds below are ShellForm's
pre-registered values (docs/preregistration.md, sections 5 and 7); loads,
strengths and factors come from ShellBench through shellform.inputs.

Load cases (factors from shellbench.combinations):
- ULS gravity: gamma_G (self-weight + SDL) + gamma_Q (roof live).
- ULS seismic, +x only: gamma_EG G_E vertical + gamma_EH Sa G_E horizontal,
  G_E = dead + psi_E live. Both strategies' forms are symmetric under the
  mirror and 90 degree rotations of the square plan, so +x stands for all
  four directions [J] (checked by test).
- SLS: characteristic self-weight + SDL + live, for the deflection limit.
  The pre-registration names the quasi-permanent combination; its live
  factor is not in ShellBench yet, so the characteristic value (live factor
  1, an upper bound) is used [J].
"""

from dataclasses import asdict, dataclass

import numpy as np

from shellform.fe import run_case

THICKNESS_MIN_M = 0.050      # pre-registration section 5 (t_min)
THICKNESS_STEP_M = 0.005     # pre-registration section 5 (5 mm steps)
LAMBDA_MIN = 5.0             # pre-registration section 5 (lambda_LBA)
DEFLECTION_SPAN_RATIO = 300  # pre-registration section 5 (L/300)
INFEASIBLE_SPAN_RATIO = 50   # pre-registration section 5 (span/50)
ZONE_RADIUS_SPAN_RATIO = 0.20  # decision D4-2 [J]: corner support zone radius / span


def load_cases(inp, sa_g):
    """Return the factored load cases for one design.

    Args:
        inp: DesignInputs.
        sa_g: Plateau spectral acceleration [g].

    Returns:
        (cases, sls): cases is a list of (name, accel, w_pa); sls is the
        (accel, w_pa) pair for the deflection check.
    """
    g = inp.g_m_s2
    cases = [("uls_gravity", (0.0, 0.0, -inp.gamma_g * g),
              (0.0, 0.0, -(inp.gamma_g * inp.sdl_pa + inp.gamma_q * inp.live_pa)))]
    if sa_g > 0.0:
        ge_area = inp.sdl_pa + inp.psi_e_roof * inp.live_pa
        cases.append(("uls_seismic_px",
                      (inp.gamma_eh * sa_g * g, 0.0, -inp.gamma_eg * g),
                      (inp.gamma_eh * sa_g * ge_area, 0.0, -inp.gamma_eg * ge_area)))
    sls = ((0.0, 0.0, -g), (0.0, 0.0, -(inp.sdl_pa + inp.live_pa)))
    return cases, sls


@dataclass
class Check:
    """Outcome of all checks at one thickness."""

    thickness_m: float
    passed: bool
    governing: str
    buckling_factor: float
    compression_pa: float
    compression_zone_pa: float
    tension_pa: float
    deflection_m: float


def check_thickness(xyz, n, fixed, span_m, t, inp, sa_g, workdir=None, lambda_min=LAMBDA_MIN):
    """Run every load case at thickness t and apply the checks.

    lambda_min is the buckling threshold; the default is the pre-registered
    LAMBDA_MIN, and only the sensitivity run of section 7 changes it (3, 8).

    Returns:
        Check, with governing naming the first failed check ("" if all pass).
    """
    cases, sls = load_cases(inp, sa_g)
    zone = ZONE_RADIUS_SPAN_RATIO * span_m
    res = {}
    for k, (name, acc, w) in enumerate(cases):
        res[name] = run_case(xyz, n, fixed, t, inp.e_pa, inp.nu, inp.density_kg_m3, acc, w,
                             sls=sls if k == 0 else None, zone_radius_m=zone,
                             workdir=None if workdir is None else f"{workdir}/{name}_{t*1e3:.0f}")
    lam = min(r.buckling_factor for r in res.values())
    comp = max(r.compression_pa for r in res.values())
    defl = res["uls_gravity"].sls_disp_m
    fails = []
    if lam < lambda_min:
        fails.append("buckling")
    if comp > inp.f_c_pa:
        fails.append("compression")
    if defl > span_m / DEFLECTION_SPAN_RATIO:
        fails.append("deflection")
    return Check(t, not fails, ",".join(fails), lam, comp,
                 max(r.compression_support_pa for r in res.values()),
                 max(r.tension_pa for r in res.values()), defl)


def thickness_grid(span_m):
    """Return the trial thicknesses, 50 mm to span/50 in 5 mm steps [m]."""
    k_max = int(np.floor((span_m / INFEASIBLE_SPAN_RATIO - THICKNESS_MIN_M) / THICKNESS_STEP_M + 1e-9))
    return THICKNESS_MIN_M + THICKNESS_STEP_M * np.arange(k_max + 1)


def size_design(xyz, n, fixed, span_m, inp, sa_g, workdir=None, lambda_min=LAMBDA_MIN):
    """Return the sized thickness of one design and the checks tried.

    The checks get easier as the thickness grows (buckling factor and stress
    margin rise), so the grid is searched by bisection [J]; the step below
    the answer is always checked and fails. lambda_min as in check_thickness.

    Returns:
        (Check at the sized thickness, or None if infeasible; dict t -> Check tried).
    """
    grid = thickness_grid(span_m)
    tried = {}

    def ok(i):
        t = round(float(grid[i]), 4)
        if t not in tried:
            tried[t] = check_thickness(xyz, n, fixed, span_m, t, inp, sa_g, workdir, lambda_min)
        return tried[t].passed

    if not ok(len(grid) - 1):
        return None, tried
    lo, hi = -1, len(grid) - 1  # grid[hi] passes; grid[lo] fails (or is below the grid)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return tried[round(float(grid[hi]), 4)], tried


def check_as_dict(c):
    """Return a Check as a plain dict."""
    return asdict(c)
