"""Reinforcement and support-zone take-off of one sized shell (Day 5).

File: src/shellform/steel.py

What this module does
---------------------
Pre-registration section 5 sizes the tension steel as A_s = T / f_y, with at
least rho_min. This module turns the CalculiX face stresses of every ULS load
case into a steel mass, and adds the concrete of the thickened corner
support zones (decision D4-2). The rules are decisions D5-1 to D5-5 in
docs/preregistration.md.

* Bar directions (D5-1) [J]: two orthogonal bar directions in every element,
  along the two grid lines of the force density network (in plan, x and y).
* Tension demand (D5-2): at each depth z through the thickness, the bar
  stress demand in direction 1 is sigma_11 + |tau_12| (tension positive),
  and the same for direction 2. This is the orthogonal reinforcement rule for
  in-plane stress (EN 1992-1-1:2004 informative Annex F, F.1, expressions
  (F.2) and (F.3), valid for sigma_Edx <= |tau_Edxy| with compression
  positive; checked by the assistant on 8 Nov 2026 in BS EN 1992-1-1:2004, Annex F,
  printed p. 211, (F.2)-(F.7); author to confirm), applied layer by layer with the linear stress profile
  between the two faces. The tension force per unit width T is the integral
  of the positive part of that demand over the thickness; A_s = T / f_y.
  Where sigma_Edx > |tau_Edxy| (compression positive), Annex F gives
  f'_tdx = 0 and f'_tdy = tau^2 / sigma_Edx - sigma_Edy, which is lower than
  the demand used here. That relief is not taken (conservative) [J].
* Minimum steel (D5-3): in both directions, everywhere, A_s >= rho_min t
  per unit width. rho_min = max(p, k f_t / f_y), with p and k read in place
  from ShellBench docs/floor_concept.md (GB 50010 Table 8.5.1 note 2, the
  slab rule applied to the shell, pre-registration section 5 [J]).
* Four seismic directions (D5-4) [J]: the seismic case is run in +x only
  (D4-1). The forms and the mesh are symmetric under the eight symmetries of
  the square, so the steel field of the -x, +y and -y cases is the +x field
  mapped by those symmetries, with the two bar directions swapped where the
  map swaps x and y. The design field is the largest over all images and all
  load cases.
* Support zones (D5-5) [J]: inside the corner zones left out of the
  compression check, an element whose face compression exceeds f_c is taken
  as thickened to t sigma_c / f_c (stress taken inversely proportional to
  thickness, which is exact for membrane action and conservative for
  bending). The extra concrete is counted. Its steel is the steel of the
  unthickened element.

No laps, anchorage or waste allowance is added to the steel [J]; the take-off
is net, for both strategies alike.

Units: SI (m, Pa, kg). Steel areas per unit width in m2/m.
"""

import re
from dataclasses import dataclass

import numpy as np

from shellform.fe import corner_zone, s8r_elements

#: Through-thickness points for the tension integral (D5-2). The demand is
#: piecewise linear in z, so 41 points give T to well under 0.1 % [J].
N_DEPTH_POINTS = 41


def rho_min_rule(floor_concept_text):
    """Read the shell minimum steel rule from ShellBench's floor concept, in place.

    The rule is written there as "the larger of p % and k f_t / f_y"
    (GB 50010 Table 8.5.1 note 2). Both terms are percentages: for C40 and
    HRB400, k f_t / f_y = 45 x 1.71 / 360 = 0.214 %, as that file states.

    Args:
        floor_concept_text: Text of ShellBench docs/floor_concept.md.

    Returns:
        (p, k): the fixed ratio as a fraction [-] and the coefficient k, in
        percent per unit f_t / f_y.
    """
    m = re.search(r"larger of\s*([\d.]+)\s*%\s*and\s*(\d+(?:\.\d+)?)\s*f_t\s*/\s*f_y", floor_concept_text)
    if not m:
        raise KeyError("minimum steel rule not found in floor_concept.md")
    return float(m.group(1)) / 100.0, float(m.group(2))


def rho_min(inp, floor_concept_text):
    """Return the minimum steel ratio of the shell, per direction [-].

    Args:
        inp: DesignInputs (f_t, f_y from ShellBench).
        floor_concept_text: Text of ShellBench docs/floor_concept.md.
    """
    p, k = rho_min_rule(floor_concept_text)
    return max(p, k * inp.f_t_pa / inp.f_y_pa / 100.0)


def element_frames(xyz, n):
    """Return the two bar directions of every S8R element (D5-1).

    Direction 1 follows the grid line through the element centre in i (plan
    x), from mid-side node 8 to node 6; direction 2 is in the tangent plane,
    normal to direction 1 (close to plan y).

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).

    Returns:
        (e1, e2), each of shape (n_el, 3), unit vectors.
    """
    els = s8r_elements(n) - 1
    a = xyz[els[:, 5]] - xyz[els[:, 7]]
    b = xyz[els[:, 6]] - xyz[els[:, 4]]
    normal = np.cross(a, b)
    normal /= np.linalg.norm(normal, axis=1, keepdims=True)
    e1 = a / np.linalg.norm(a, axis=1, keepdims=True)
    e2 = np.cross(normal, e1)
    return e1, e2


def element_areas(xyz, n):
    """Return the surface area of every S8R element (its 3 x 3 node patch) [m2]."""
    p = xyz.reshape(n, n, 3)
    a, b, c, d = p[:-1, :-1], p[:-1, 1:], p[1:, 1:], p[1:, :-1]
    cell = (0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=-1)
            + 0.5 * np.linalg.norm(np.cross(c - a, d - a), axis=-1))  # (n-1, n-1), [j, i]
    m = (n - 1) // 2
    return cell.reshape(m, 2, m, 2).sum(axis=(1, 3)).ravel()  # element order: J outer, I inner


def _tensor(c):
    """Return 3 x 3 stress tensors from components (sxx, syy, szz, sxy, sxz, syz)."""
    xx, yy, zz, xy, xz, yz = (c[..., k] for k in range(6))
    return np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1),
                     np.stack([xz, yz, zz], -1)], -2)


def tension_per_width(face_stress_pa, e1, e2, thickness_m):
    """Return the bar tension force per unit width in both directions (D5-2).

    Args:
        face_stress_pa: Face stresses, shape (n_el, 2, 6) [Pa] (fe.CaseResult).
        e1, e2: Bar directions, shape (n_el, 3).
        thickness_m: Shell thickness [m].

    Returns:
        Array of shape (n_el, 2): T in directions 1 and 2 [N/m].
    """
    s = _tensor(face_stress_pa)  # (n_el, 2, 3, 3)
    s11 = np.einsum("ei,efij,ej->ef", e1, s, e1)
    s22 = np.einsum("ei,efij,ej->ef", e2, s, e2)
    s12 = np.einsum("ei,efij,ej->ef", e1, s, e2)
    w = np.linspace(0.0, 1.0, N_DEPTH_POINTS)  # 0 = face 0, 1 = face 1

    def lin(v):
        return v[:, :1] * (1.0 - w) + v[:, 1:] * w  # (n_el, N)

    tau = np.abs(lin(s12))
    out = []
    for snn in (s11, s22):
        demand = np.clip(lin(snn) + tau, 0.0, None)
        out.append(np.trapezoid(demand, dx=thickness_m / (N_DEPTH_POINTS - 1), axis=1))
    return np.stack(out, axis=1)


def symmetric_envelope(field, n):
    """Return the largest value over the eight symmetry images of the square (D5-4).

    Args:
        field: Per-element values in directions 1 and 2, shape (n_el, 2),
            element order J outer, I inner.
        n: Grid nodes per side (odd).

    Returns:
        Array of shape (n_el, 2).
    """
    m = (n - 1) // 2
    fx, fy = field[:, 0].reshape(m, m), field[:, 1].reshape(m, m)  # [J, I]
    ex, ey = fx.copy(), fy.copy()
    for flip in (False, True):
        ax, ay = (fx.T, fy.T) if flip else (fx, fy)
        if flip:
            ax, ay = ay, ax  # a transpose swaps x and y
        for k in range(4):
            rx, ry = np.rot90(ax, k), np.rot90(ay, k)
            if k % 2:
                rx, ry = ry, rx  # a quarter turn swaps x and y
            ex, ey = np.maximum(ex, rx), np.maximum(ey, ry)
    return np.stack([ex.ravel(), ey.ravel()], axis=1)


@dataclass
class SteelTakeOff:
    """Steel and support-zone concrete of one sized shell.

    Attributes:
        steel_kg: Total reinforcement mass [kg].
        steel_min_kg: Mass if every element carried rho_min only [kg].
        steel_above_min_kg: steel_kg less steel_min_kg [kg].
        steel_from_seismic_kg: Steel added by the seismic case over the ULS
            gravity case alone [kg] (0 at Sa = 0).
        demand_kg: Mass of T / f_y alone, without rho_min [kg]; shows how far
            the demand sits below the minimum.
        demand_from_seismic_kg: demand_kg less the demand of the ULS gravity
            case alone [kg].
        zone_concrete_m3: Extra concrete of the thickened support zones [m3].
        zone_elements: Number of zone elements thickened [-].
        zone_t_max_m: Largest thickened zone thickness [m] (t if none).
        max_as_mm2_m: Largest steel area per unit width, either direction [mm2/m].
        rho_min: Minimum steel ratio used, per direction [-].
        governing_case: Load case that gives the most steel ("" if rho_min governs everywhere).
    """

    steel_kg: float
    steel_min_kg: float
    steel_above_min_kg: float
    steel_from_seismic_kg: float
    demand_kg: float
    demand_from_seismic_kg: float
    zone_concrete_m3: float
    zone_elements: int
    zone_t_max_m: float
    max_as_mm2_m: float
    rho_min: float
    governing_case: str


def take_off(xyz, n, thickness_m, case_results, inp, rho_min_ratio, steel_density_kg_m3, zone_radius_m):
    """Return the steel and support-zone take-off of one sized shell.

    Args:
        xyz: Mid-surface grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).
        thickness_m: Sized uniform thickness [m].
        case_results: dict load-case name -> fe.CaseResult at thickness_m;
            must hold "uls_gravity", and "uls_seismic_px" when Sa > 0.
        inp: DesignInputs (f_y, f_c from ShellBench).
        rho_min_ratio: Minimum steel ratio per direction [-] (rho_min).
        steel_density_kg_m3: Steel density [kg/m3] (shellbench.carbon).
        zone_radius_m: Corner support-zone radius [m] (D4-2).

    Returns:
        SteelTakeOff.
    """
    e1, e2 = element_frames(xyz, n)
    area = element_areas(xyz, n)
    as_min = rho_min_ratio * thickness_m
    as_case = {}
    for name, res in case_results.items():
        t = tension_per_width(res.face_stress_pa, e1, e2, thickness_m)
        as_case[name] = symmetric_envelope(t / inp.f_y_pa, n)
    req = np.max(np.stack(list(as_case.values())), axis=0)
    design = np.maximum(req, as_min)
    grav = np.maximum(as_case["uls_gravity"], as_min)

    def mass(a):
        return float((a.sum(axis=1) * area).sum() * steel_density_kg_m3)

    steel = mass(design)
    steel_min = mass(np.full_like(design, as_min))
    gov = ""
    if (req > as_min).any():
        totals = {k: (np.maximum(v, as_min) - as_min).sum(axis=1) @ area for k, v in as_case.items()}
        gov = max(totals, key=totals.get)

    near = corner_zone(xyz, n, zone_radius_m)
    comp = np.zeros(len(area))
    for res in case_results.values():
        s = _tensor(res.face_stress_pa)
        comp = np.maximum(comp, -np.linalg.eigvalsh(s)[..., 0].min(axis=1))
    over = near & (comp > inp.f_c_pa)
    t_zone = np.where(over, thickness_m * comp / inp.f_c_pa, thickness_m)
    return SteelTakeOff(
        steel_kg=steel, steel_min_kg=steel_min, steel_above_min_kg=steel - steel_min,
        steel_from_seismic_kg=steel - mass(grav),
        demand_kg=mass(req), demand_from_seismic_kg=mass(req) - mass(as_case["uls_gravity"]),
        zone_concrete_m3=float(((t_zone - thickness_m) * area).sum()),
        zone_elements=int(over.sum()), zone_t_max_m=float(t_zone.max()),
        max_as_mm2_m=float(design.max() * 1e6), rho_min=rho_min_ratio, governing_case=gov)
