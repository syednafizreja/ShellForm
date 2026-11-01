"""Thickness sizing of one shell (docs/preregistration.md, section 5).

Day 4 covers two of the pass/fail checks: linear buckling and deflection.
Compression and tension follow with the floor-r3 checks, so a thickness from
this module is a lower bound on the sized design, not the sized design.

Loads act per unit of surface area as a scaled body load (decision D4-4), and
the material density is the dead load G_E per unit volume of concrete (D4-5).
Each combination is then one acceleration vector. All numbers below the
thresholds come from ShellBench through shellform.sb_inputs.

Units: SI (m, N, kg, Pa).
"""

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from shellform.fe import analyse

# ShellForm's own pre-registered choices (section 5), not ShellBench values.
LAMBDA_MIN = 5.0          # λ_LBA limit [J]; sensitivity at 3 and 8
DEFLECTION_RATIO = 300.0  # L/300, GB 50010 Table 3.4.3 [check]
T_MIN_MM = 50             # minimum thickness [J]
T_STEP_MM = 5             # sizing step
T_MAX_SPAN_RATIO = 50.0   # infeasible beyond L/50
N_BUCKLE_MODES = 4        # enough to find a positive factor among mixed signs (D4-7)


@dataclass(frozen=True)
class ThicknessCheck:
    """Checks of one shell at one thickness.

    Attributes:
        thickness_m: Uniform thickness [m].
        lambda_gravity: Smallest positive buckling factor under 1.3 G + 1.5 Q [-].
        lambda_seismic: The same under 1.3 G_E + 1.4 E_h; NaN when Sa = 0 [-].
        max_deflection_m: Largest displacement under G + Q (D4-2) [m].
        period_1_s: First period with mass G_E [s].
    """

    thickness_m: float
    lambda_gravity: float
    lambda_seismic: float
    max_deflection_m: float
    period_1_s: float

    @property
    def lambda_governing(self):
        """Return the lower of the two buckling factors [-]."""
        return float(np.nanmin([self.lambda_gravity, self.lambda_seismic]))

    def passes(self, span_m, lambda_min=LAMBDA_MIN):
        """Return True if buckling and deflection pass at this thickness.

        Args:
            span_m: Span [m].
            lambda_min: Buckling limit [-].
        """
        return (self.lambda_governing >= lambda_min
                and self.max_deflection_m <= span_m / DEFLECTION_RATIO)


def effective_density(thickness_m, inputs):
    """Return the density that carries the dead load G_E [kg/m3] (D4-5)."""
    return dead_load_pa(thickness_m, inputs) / (inputs.g_m_s2 * thickness_m)


def dead_load_pa(thickness_m, inputs):
    """Return self-weight plus superimposed dead load per surface area [Pa]."""
    return inputs.unit_weight_n_m3 * thickness_m + inputs.superimposed_dead_pa


def combination_accels(thickness_m, sa_g, inputs, direction=(1.0, 0.0)):
    """Return the body accelerations for the three load cases [m/s2].

    Each is the load per surface area divided by the effective mass per
    surface area, so it scales with the effective density in the deck.

    Args:
        thickness_m: Uniform thickness [m].
        sa_g: Plateau spectral acceleration [g].
        inputs: DesignInputs.
        direction: Horizontal unit vector of the shaking (dx, dy).

    Returns:
        (G + Q, 1.3 G + 1.5 Q, 1.3 G_E + 1.4 E_h), each a 3-vector.
    """
    g = inputs.g_m_s2
    dead = dead_load_pa(thickness_m, inputs)
    q = inputs.roof_live_pa
    down = np.array([0.0, 0.0, -1.0])
    service = down * g * (dead + q) / dead
    gravity = down * g * (inputs.gamma_g * dead + inputs.gamma_q * q) / dead
    side = np.array([direction[0], direction[1], 0.0])
    seismic = g * (inputs.gamma_eg * down + inputs.gamma_eh * sa_g * side)
    return service, gravity, seismic


def smallest_positive(factors):
    """Return the smallest positive buckling factor, or NaN if none (D4-7)."""
    positive = [float(f) for f in factors if f > 0.0]
    return min(positive) if positive else float("nan")


def check_thickness(xyz, n, fixed, thickness_m, sa_g, inputs, direction=(1.0, 0.0), workdir=None):
    """Run the Day 4 checks on one shell at one thickness.

    Args:
        xyz: Mid-surface grid, shape (n*n, 3) [m].
        n: Nodes per side (odd).
        fixed: 0-based indices of pinned nodes.
        thickness_m: Uniform thickness [m].
        sa_g: Plateau spectral acceleration [g].
        inputs: DesignInputs.
        direction: Horizontal unit vector of the shaking.
        workdir: Folder kept for the CalculiX files; a temporary one is
            deleted if None.

    Returns:
        ThicknessCheck.
    """
    temp = None if workdir else tempfile.mkdtemp(prefix="shellform_")
    work = Path(workdir or temp)
    rho = effective_density(thickness_m, inputs)
    service, gravity, seismic = combination_accels(thickness_m, sa_g, inputs, direction)
    common = (xyz, n, fixed, thickness_m, inputs.e_pa, inputs.nu, rho)
    try:
        main = analyse(*common, g=inputs.g_m_s2, workdir=work / "gravity", n_modes=1,
                       n_buckle=N_BUCKLE_MODES, static_accel=service, buckle_accel=gravity)
        lam_s = float("nan")
        if sa_g > 0.0:
            side = analyse(*common, g=inputs.g_m_s2, workdir=work / "seismic", n_modes=0,
                           n_buckle=N_BUCKLE_MODES, static_accel=False, buckle_accel=seismic)
            lam_s = smallest_positive(side.buckling_factors)
    finally:
        if temp:
            shutil.rmtree(temp, ignore_errors=True)
    return ThicknessCheck(thickness_m, smallest_positive(main.buckling_factors), lam_s,
                          main.max_disp_m, float(main.periods_s[0]))


def governing_check(result, span_m, lambda_min=LAMBDA_MIN):
    """Return what sets the thickness of a passing design.

    Args:
        result: ThicknessCheck.
        span_m: Span [m].
        lambda_min: Buckling limit [-].

    Returns:
        "minimum_thickness" if the design sits at T_MIN_MM, otherwise whichever
        of "buckling" and "deflection" is closest to its limit.
    """
    if round(result.thickness_m * 1.0e3) <= T_MIN_MM:
        return "minimum_thickness"
    use_buckling = lambda_min / result.lambda_governing
    use_deflection = result.max_deflection_m * DEFLECTION_RATIO / span_m
    return "buckling" if use_buckling >= use_deflection else "deflection"


def size_shell(xyz, n, fixed, span_m, sa_g, inputs, lambda_min=LAMBDA_MIN):
    """Return the smallest thickness that passes, in the pre-registered steps.

    Scans upwards from T_MIN_MM, so the answer is the first pass, as section 5
    defines it, with no assumption that the checks improve with thickness.

    Args:
        xyz, n, fixed: As for :func:`check_thickness`.
        span_m: Span [m].
        sa_g: Plateau spectral acceleration [g].
        inputs: DesignInputs.
        lambda_min: Buckling limit [-].

    Returns:
        (feasible, ThicknessCheck at the passing thickness, or at the last
        thickness tried if none passes).
    """
    t_max_mm = int(round(span_m / T_MAX_SPAN_RATIO * 1.0e3))
    result = None
    for t_mm in range(T_MIN_MM, t_max_mm + 1, T_STEP_MM):
        result = check_thickness(xyz, n, fixed, t_mm / 1.0e3, sa_g, inputs)
        if result.passes(span_m, lambda_min):
            return True, result
    return False, result
