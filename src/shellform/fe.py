"""CalculiX analysis of a form-found shell: static, modal and linear buckling.

ShellBench's CalculiX wrapper (floor-r2) is not tagged yet, and ShellForm
never runs untagged ShellBench code (stop-loss rule). Until floor-r2 is
tagged, this module writes and reads its own decks. It is replaced by, or
cross-checked against, floor-r2 once that tag exists.

Mesh: the force density grid (odd n per side) is cut into 8-node S8R shell
elements, each covering a 3 x 3 patch of grid nodes (the centre node unused).
Units: SI (m, N, kg, Pa).
"""

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class FEResult:
    """Results of one CalculiX run.

    Attributes:
        max_disp_m: Largest displacement magnitude in the static step [m].
        reaction_n: Sum of support reactions in the static step, (fx, fy, fz) [N].
            CalculiX leaves out of RF any load lumped directly onto a
            supported node, so with edge supports this sum is less than the
            weight; with corner supports it equals the weight (checked by test).
        weight_n: Self-weight applied, from density, g, thickness and area [N].
        periods_s: Natural periods, longest first [s].
        buckling_factors: Linear buckling load factors under the static load.
    """

    max_disp_m: float
    reaction_n: np.ndarray
    weight_n: float
    periods_s: np.ndarray
    buckling_factors: np.ndarray


def find_ccx():
    """Return the CalculiX executable path, or None if it is not installed."""
    return shutil.which("ccx")


def s8r_elements(n):
    """Return S8R connectivity (CalculiX node order, 1-based) for an n x n grid.

    Args:
        n: Grid nodes per side; must be odd.

    Returns:
        Integer array, shape ((n-1)/2 squared, 8).
    """
    if n % 2 == 0:
        raise ValueError("S8R meshing needs an odd number of grid nodes per side")

    def nid(i, j):
        return j * n + i + 1

    els = []
    for J in range(0, n - 1, 2):
        for I in range(0, n - 1, 2):
            els.append([nid(I, J), nid(I + 2, J), nid(I + 2, J + 2), nid(I, J + 2),
                        nid(I + 1, J), nid(I + 2, J + 1), nid(I + 1, J + 2), nid(I, J + 1)])
    return np.array(els)


def surface_area(xyz, n):
    """Return the area of the grid surface from its triangles [m2]."""
    p = xyz.reshape(n, n, 3)
    a, b, c, d = p[:-1, :-1], p[:-1, 1:], p[1:, 1:], p[1:, :-1]
    t1 = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=-1)
    t2 = 0.5 * np.linalg.norm(np.cross(c - a, d - a), axis=-1)
    return float((t1 + t2).sum())


def write_deck(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3,
               g=9.81, n_modes=3, n_buckle=2, clamp=False):
    """Return the CalculiX input deck text for one shell.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).
        fixed: 0-based indices of pinned nodes (translations fixed).
        thickness_m: Uniform shell thickness [m].
        e_pa, nu: Young's modulus [Pa] and Poisson's ratio [-].
        density_kg_m3: Mass density [kg/m3].
        g: Gravitational acceleration [m/s2].
        n_modes, n_buckle: Number of modes and buckling factors requested.
        clamp: Fix rotations too (used only by tests); shells are pinned.
    """
    els = s8r_elements(n)
    used = np.unique(els)
    lines = ["*NODE"]
    lines += [f"{k},{xyz[k-1,0]:.9e},{xyz[k-1,1]:.9e},{xyz[k-1,2]:.9e}" for k in used]
    lines.append("*ELEMENT,TYPE=S8R,ELSET=EALL")
    lines += [f"{e+1}," + ",".join(str(v) for v in row) for e, row in enumerate(els)]
    fixed_used = sorted(set(int(k) + 1 for k in fixed) & set(int(u) for u in used))
    lines.append("*NSET,NSET=FIX")
    lines += [",".join(str(v) for v in fixed_used[i:i + 16]) for i in range(0, len(fixed_used), 16)]
    lines.append("*NSET,NSET=NUSED")
    lines += [",".join(str(v) for v in used[i:i + 16]) for i in range(0, len(used), 16)]
    lines += ["*BOUNDARY", "FIX,1,6" if clamp else "FIX,1,3",
              "*MATERIAL,NAME=CONC", "*ELASTIC", f"{e_pa:.6e},{nu}",
              "*DENSITY", f"{density_kg_m3}",
              "*SHELL SECTION,ELSET=EALL,MATERIAL=CONC", f"{thickness_m}",
              "*STEP", "*STATIC", "*DLOAD", f"EALL,GRAV,{g},0,0,-1",
              "*NODE PRINT,NSET=FIX,TOTALS=ONLY", "RF",
              "*NODE PRINT,NSET=NUSED", "U", "*END STEP",
              "*STEP", "*FREQUENCY", f"{n_modes}", "*END STEP",
              "*STEP", "*BUCKLE", f"{n_buckle}", "*DLOAD", f"EALL,GRAV,{g},0,0,-1", "*END STEP"]
    return "\n".join(lines) + "\n"


_NUM = r"[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?"


def parse_dat(text):
    """Return (max displacement, reaction totals, frequencies [Hz], buckling factors) from a .dat file."""
    steps = re.split(r"S T E P\s+\d+", text)
    static = steps[1] if len(steps) > 1 else text
    tot = re.search(r"total force \(fx,fy,fz\)[^\n]*\n\s*\n?\s*(" + _NUM + r")\s+(" + _NUM + r")\s+(" + _NUM + r")", static)
    reaction = np.array([float(tot.group(k)) for k in (1, 2, 3)]) if tot else np.full(3, np.nan)
    disp_block = static.split("displacements", 1)[1] if "displacements" in static else ""
    rows = re.findall(r"^\s*\d+\s+(" + _NUM + r")\s+(" + _NUM + r")\s+(" + _NUM + r")\s*$", disp_block, re.M)
    u = np.array(rows, dtype=float) if rows else np.zeros((1, 3))
    freq = []
    m = re.search(r"E I G E N V A L U E   O U T P U T(.*?)(?:\n\s*\n\s*\n|P A R T I C)", text, re.S)
    if m:
        for row in re.findall(r"^\s*\d+\s+(" + _NUM + r")\s+(" + _NUM + r")\s+(" + _NUM + r")", m.group(1), re.M):
            freq.append(float(row[2]))
    buck = []
    b = re.search(r"B U C K L I N G   F A C T O R   O U T P U T(.*?)(?:E I G E N V A L U E    N U M B E R|$)", text, re.S)
    if b:
        buck = [float(v) for v in re.findall(r"^\s*\d+\s+(" + _NUM + r")\s*$", b.group(1), re.M)]
    return float(np.linalg.norm(u, axis=1).max()), reaction, np.array(freq), np.array(buck)


def analyse(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, g=9.81, workdir=None, ccx=None):
    """Run static, modal and buckling analyses of one shell in CalculiX.

    Args:
        xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, g: As for :func:`write_deck`.
        workdir: Folder for the deck and outputs; a temporary folder if None.
        ccx: CalculiX executable; found on PATH if None.

    Returns:
        FEResult.

    Raises:
        RuntimeError: If CalculiX is missing or fails.
    """
    ccx = ccx or find_ccx()
    if ccx is None:
        raise RuntimeError("CalculiX (ccx) not found on PATH")
    work = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="shellform_"))
    work.mkdir(parents=True, exist_ok=True)
    (work / "shell.inp").write_text(write_deck(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, g))
    run = subprocess.run([ccx, "shell"], cwd=work, capture_output=True, text=True)
    dat = work / "shell.dat"
    if not dat.exists() or "Job finished" not in run.stdout:
        raise RuntimeError(f"CalculiX failed:\n{run.stdout[-2000:]}\n{run.stderr[-2000:]}")
    umax, reaction, freq, buck = parse_dat(dat.read_text())
    weight = density_kg_m3 * g * thickness_m * surface_area(xyz, n)
    periods = np.sort(1.0 / freq)[::-1] if len(freq) else np.array([])
    return FEResult(umax, reaction, weight, periods, buck)


# ---------------------------------------------------------------------------
# Load-case runs for sizing (Day 4)
# ---------------------------------------------------------------------------

#: Consistent nodal shares of a uniform load on an 8-node serendipity element:
#: corners -1/12, mid-side nodes 1/3 of the element total (exact for a flat
#: parallelogram; used here per projected plan area).
S8R_LOAD_SHARES = np.array([-1.0, -1.0, -1.0, -1.0, 4.0, 4.0, 4.0, 4.0]) / 12.0


@dataclass
class CaseResult:
    """Results of one load case (static plus linear buckling).

    Attributes:
        buckling_factor: First positive linear buckling factor under the case loads [-].
        max_disp_m: Largest displacement magnitude [m].
        max_uz_m: Largest vertical displacement magnitude [m].
        compression_pa: Largest principal compressive stress on either face,
            outside the corner support zones [Pa] (positive number).
        compression_support_pa: The same, inside the corner support zones [Pa].
        tension_pa: Largest principal tensile stress on either face, all elements [Pa].
        sls_disp_m: Largest displacement magnitude under the SLS loads [m], or nan.
        periods_s: Natural periods, longest first [s] (empty unless requested).
        face_stress_pa: Stress components on both faces per element, shape
            (n_el, 2, 6), order sxx, syy, szz, sxy, sxz, syz, in element order [Pa].
    """

    buckling_factor: float
    max_disp_m: float
    max_uz_m: float
    compression_pa: float
    compression_support_pa: float
    tension_pa: float
    sls_disp_m: float
    periods_s: np.ndarray
    face_stress_pa: np.ndarray = None


def plan_load_shares(xyz, n):
    """Return consistent nodal weights for a unit load per plan area [m2 per node].

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).

    Returns:
        Array of shape (n*n,): the nodal share of a load of 1 Pa on plan area.
    """
    els = s8r_elements(n)
    w = np.zeros(n * n)
    for row in els:
        c = xyz[row[:4] - 1, :2]
        x, y = c[:, 0], c[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        w[row - 1] += area * S8R_LOAD_SHARES
    return w


def corner_zone(xyz, n, radius_m):
    """Return a boolean mask of S8R elements in the plan-corner support zones.

    Stresses near a point support (or where two pinned edges meet) are
    singular in a linear-elastic model and grow with mesh refinement. The
    sizing check leaves out elements whose plan centroid lies within radius_m
    of a plan corner node, and reports their stress separately (decision D4-2
    [J]); in practice these zones are thickened locally. The four corner
    elements are always in the zone.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).
        radius_m: Zone radius in plan [m].
    """
    els = s8r_elements(n)
    corners = np.array([0, n - 1, n * (n - 1), n * n - 1])
    cen = xyz[els[:, :4] - 1, :2].mean(axis=1)
    dist = np.linalg.norm(cen[:, None, :] - xyz[corners, :2][None], axis=2).min(axis=1)
    touch = np.array([bool(set((corners + 1).tolist()) & set(row.tolist())) for row in els])
    return touch | (dist <= radius_m)


def _grav_line(accel):
    """Return a *DLOAD GRAV line for an acceleration vector [m/s2]."""
    a = np.asarray(accel, float)
    mag = np.linalg.norm(a)
    d = a / mag
    return f"EALL,GRAV,{mag:.9e},{d[0]:.9e},{d[1]:.9e},{d[2]:.9e}"


def _cload_lines(shares, used, w_pa):
    """Return *CLOAD lines for a load per plan area w_pa = (wx, wy, wz) [Pa]."""
    lines = []
    for k in used:
        for dof, w in enumerate(w_pa, start=1):
            f = shares[k - 1] * w
            if w != 0.0 and f != 0.0:
                lines.append(f"{k},{dof},{f:.9e}")
    return lines


def write_case_deck(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3,
                    accel, w_pa, sls=None, n_modes=0, clamp=False):
    """Return a CalculiX deck for one load case: buckling, static, optional SLS and modes.

    Step order: BUCKLE first (so no earlier load acts as a preload), then
    STATIC under the same loads, then an optional SLS STATIC with new loads,
    then an optional FREQUENCY step (mass from density only).

    Args:
        xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3: As for write_deck.
        accel: Factored acceleration on the self-weight, (ax, ay, az) [m/s2].
        w_pa: Factored load per plan area on the nodes, (wx, wy, wz) [Pa].
        sls: Optional (accel, w_pa) pair for the serviceability case.
        n_modes: Number of natural modes to compute (0 for none).
        clamp: Fix rotations at the fixed nodes (tests only).
    """
    els = s8r_elements(n)
    used = np.unique(els)
    shares = plan_load_shares(xyz, n)
    base = write_deck(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, clamp=clamp)
    head = base.split("*STEP", 1)[0].splitlines()

    def loads(acc, w, new):
        op = ",OP=NEW" if new else ""
        out = [f"*DLOAD{op}", _grav_line(acc)]
        cl = _cload_lines(shares, used, w)
        out += [f"*CLOAD{op}"] + cl if cl else ([f"*CLOAD{op}"] if new else [])
        return out

    lines = head + ["*STEP", "*BUCKLE", "1"] + loads(accel, w_pa, False) + ["*END STEP"]
    lines += ["*STEP", "*STATIC"] + loads(accel, w_pa, True)
    lines += ["*NODE PRINT,NSET=NUSED", "U", "*EL PRINT,ELSET=EALL", "S", "*END STEP"]
    if sls is not None:
        lines += ["*STEP", "*STATIC"] + loads(sls[0], sls[1], True)
        lines += ["*NODE PRINT,NSET=NUSED", "U", "*END STEP"]
    if n_modes:
        lines += ["*STEP", "*FREQUENCY", f"{n_modes}", "*END STEP"]
    return "\n".join(lines) + "\n"


def _blocks(text, header):
    """Return the numeric rows that follow each occurrence of a .dat block header."""
    out = []
    for m in re.finditer(re.escape(header) + r"[^\n]*\n", text):
        rows = []
        for line in text[m.end():].splitlines():
            s = line.strip()
            if not s:
                if rows:
                    break
                continue
            if not re.match(r"^\d", s):
                break
            vals = []
            for v in s.split():
                try:
                    vals.append(float(v.replace("D", "E")))
                except ValueError:
                    break  # trailing element-set name, e.g. _shell_0000000001
            rows.append(vals)
        out.append(np.array(rows))
    return out


def surface_stress_components(stress_rows):
    """Return per-element stress components on both shell faces.

    CalculiX expands S8R into C3D20R with 2 x 2 x 2 integration points: the
    first four lie on one Gauss plane through the thickness, the last four on
    the other, at +-1/sqrt(3) of the half-thickness. Stresses are averaged in
    plane and extrapolated linearly to the faces (factor sqrt(3)).

    Args:
        stress_rows: Rows (elem, ip, sxx, syy, szz, sxy, sxz, syz) [Pa].

    Returns:
        (element ids, components array of shape (n_el, 2 faces, 6)) [Pa], in
        the row order sxx, syy, szz, sxy, sxz, syz.
    """
    elem = stress_rows[:, 0].astype(int)
    ids = np.unique(elem)
    s = stress_rows[:, 2:8].reshape(len(ids), 8, 6)
    lo, hi = s[:, :4].mean(axis=1), s[:, 4:].mean(axis=1)
    mid, half = 0.5 * (lo + hi), 0.5 * (hi - lo) * np.sqrt(3.0)
    return ids, np.stack([mid - half, mid + half], axis=1)


def principal_stresses(faces):
    """Return principal stresses, ascending, from stress components (..., 6) [Pa]."""
    xx, yy, zz, xy, xz, yz = (faces[..., k] for k in range(6))
    t = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1),
                  np.stack([xz, yz, zz], -1)], -2)
    return np.linalg.eigvalsh(t)


def surface_principal_stresses(stress_rows):
    """Return per-element principal stresses on both shell faces.

    Args:
        stress_rows: Rows (elem, ip, sxx, syy, szz, sxy, sxz, syz) [Pa].

    Returns:
        (element ids, principal stresses array of shape (n_el, 2 faces, 3)) [Pa].
    """
    ids, faces = surface_stress_components(stress_rows)
    return ids, principal_stresses(faces)


def run_case(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, accel, w_pa,
             sls=None, n_modes=0, workdir=None, ccx=None, clamp=False, zone_radius_m=0.0):
    """Run one load case in CalculiX and return the sizing quantities.

    Args:
        As for write_case_deck; workdir and ccx as for analyse.
        zone_radius_m: Radius of the corner support zones left out of the
            compression check [m] (see corner_zone).

    Returns:
        CaseResult.
    """
    ccx = ccx or find_ccx()
    if ccx is None:
        raise RuntimeError("CalculiX (ccx) not found on PATH")
    work = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="shellform_"))
    work.mkdir(parents=True, exist_ok=True)
    deck = write_case_deck(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3,
                           accel, w_pa, sls, n_modes, clamp)
    (work / "case.inp").write_text(deck)
    run = subprocess.run([ccx, "case"], cwd=work, capture_output=True, text=True)
    dat = work / "case.dat"
    if not dat.exists() or "Job finished" not in run.stdout:
        raise RuntimeError(f"CalculiX failed:\n{run.stdout[-2000:]}\n{run.stderr[-2000:]}")
    text = dat.read_text()
    _, _, freq, buck = parse_dat(text)
    pos = buck[buck > 0]
    disp = _blocks(text, "displacements (vx,vy,vz)")
    stress = _blocks(text, "stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz)")
    u = disp[0][:, 1:4]
    ids, faces = surface_stress_components(stress[0])
    p = principal_stresses(faces)
    near = corner_zone(xyz, n, zone_radius_m)[ids - 1]
    comp = -p[..., 0].min(axis=1)
    sls_disp = float(np.linalg.norm(disp[1][:, 1:4], axis=1).max()) if sls is not None else float("nan")
    periods = np.sort(1.0 / freq)[::-1] if len(freq) else np.array([])
    return CaseResult(
        buckling_factor=float(pos.min()) if len(pos) else float("inf"),
        max_disp_m=float(np.linalg.norm(u, axis=1).max()),
        max_uz_m=float(np.abs(u[:, 2]).max()),
        compression_pa=float(max(comp[~near].max(initial=0.0), 0.0)),
        compression_support_pa=float(max(comp[near].max(initial=0.0), 0.0)),
        tension_pa=float(max(p[..., 2].max(), 0.0)),
        sls_disp_m=sls_disp, periods_s=periods, face_stress_pa=faces)
