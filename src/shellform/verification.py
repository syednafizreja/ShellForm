"""Verification add-ons of the check window (14 Nov 2026): V1 to V5.

File: src/shellform/verification.py

These are new verification and sensitivity outputs beside the frozen
record. None of them changes a sizing setting (lambda >= 5, L/300, t_min
50 mm), a pinned ShellBench value or a frozen result file. They were added
after the freeze and are not pre-registered (pre-registration amendment of
14 Nov 2026).

- V1 ``zoelly_benchmark``: linear buckling of a complete sphere under
  uniform external pressure, against the classical (Zoelly 1915) value
  p_cr = 2 E / sqrt(3 (1 - nu^2)) (t / R)^2. It checks the same CalculiX
  S8R + *BUCKLE path that sizes every ShellForm shell, on a problem with a
  closed-form answer.
- V2 ``h_convergence``: the sized SLS deflection and first buckling factor
  of chosen designs on four networks (21, 41, 61, 81 nodes per side), at the
  frozen sized thickness.
- V3 ``fdm_residual``: the residual of the assembled force density system,
  max |D x_free - (p_free - D_f x_fixed)|, for every form-found network.
- V4 ``energy_split``: membrane and bending shares of the strain energy of
  each sized design, under each ULS case, from the CalculiX face stresses.
- V5 ``formwork_bound``: whether adding a formwork (A5) term, with any
  factor and any number of reuses, can move a verdict across the 5 % rule.

Units: SI (m, N, Pa, kg, kgCO2e).
"""

import subprocess
import tempfile
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from shellform.fe import _blocks, find_ccx, parse_dat, plan_area, run_case, s8r_elements, surface_area
from shellform.formfind import plan_loads, solve
from shellform.sizing import DEFLECTION_SPAN_RATIO, ZONE_RADIUS_SPAN_RATIO, load_cases

# ---------------------------------------------------------------------------
# V1: Zoelly sphere benchmark
# ---------------------------------------------------------------------------

#: Acceptance limit of V1 (blueprint add-on 1, 13 Nov 2026) [-].
ZOELLY_TOLERANCE = 0.03


def zoelly_pressure(e_pa, nu, thickness_m, radius_m):
    """Return the classical buckling pressure of a complete sphere [Pa].

    p_cr = 2 E / sqrt(3 (1 - nu^2)) * (t / R)^2 (Zoelly 1915; Timoshenko &
    Gere 1961, Theory of Elastic Stability, 2nd ed., Section 11.7 [check
    the page in your copy]).

    Args:
        e_pa: Young's modulus [Pa].
        nu: Poisson's ratio [-].
        thickness_m: Shell thickness [m].
        radius_m: Sphere radius [m].
    """
    return 2.0 * e_pa / np.sqrt(3.0 * (1.0 - nu ** 2)) * (thickness_m / radius_m) ** 2


def cube_sphere(radius_m, m):
    """Return an S8R mesh of a complete sphere, built from the six faces of a cube.

    Each cube face carries an m x m patch of 8-node elements (a (2m+1) x
    (2m+1) node grid, centre nodes unused), mapped to the sphere by the
    equiangular projection so element sizes stay even. Shared nodes on cube
    edges are merged. Every element is ordered so that its normal points out.

    Args:
        radius_m: Sphere radius [m].
        m: Elements per cube-face edge.

    Returns:
        (nodes, shape (k, 3) [m]; elements, shape (6 m^2, 8), 1-based ids into nodes).
    """
    k = 2 * m + 1
    a = np.tan(np.linspace(-np.pi / 4, np.pi / 4, k))
    u, v = np.meshgrid(a, a)  # u varies along i (columns), v along j (rows)
    one = np.ones_like(u)
    faces = [(one, u, v), (-one, v, u), (u, one, v), (v, -one, u), (u, v, one), (v, u, -one)]
    local = s8r_elements(k)
    pts, conn = [], []
    for f, (x, y, z) in enumerate(faces):
        p = np.stack([x, y, z], -1).reshape(-1, 3)
        p = radius_m * p / np.linalg.norm(p, axis=1)[:, None]
        conn.append(local - 1 + f * k * k)
        pts.append(p)
    pts = np.vstack(pts)
    conn = np.vstack(conn)
    key = np.round(pts / radius_m, 9)
    _, first, inverse = np.unique(key, axis=0, return_index=True, return_inverse=True)
    nodes = pts[first]
    els = inverse.ravel()[conn] + 1
    # Outward normals: flip the order of any element whose normal points in.
    c = nodes[els[:, :4] - 1]
    normal = np.cross(c[:, 1] - c[:, 0], c[:, 3] - c[:, 0])
    inward = np.einsum("ij,ij->i", normal, c.mean(axis=1)) < 0
    flip = [0, 3, 2, 1, 7, 6, 5, 4]
    els[inward] = els[inward][:, flip]
    return nodes, els


def sphere_deck(nodes, els, thickness_m, e_pa, nu, pressure_pa, n_buckle=4):
    """Return a CalculiX deck: static step and linear buckling under external pressure.

    Six translations are fixed in a statically determinate way (north pole x, y;
    south pole x, y, z; one equator node y), so uniform pressure meets no
    support reaction and the membrane state is the exact uniform one.
    With the outward element normals of :func:`cube_sphere`, CalculiX's
    shell pressure P acts along the normal, so the external pressure is
    written as a negative P (checked: the static step then moves every node
    inward by the membrane value p R^2 (1 - nu) / (2 E t)).

    Args:
        nodes, els: Mesh of :func:`cube_sphere`.
        thickness_m, e_pa, nu: Section and material [m, Pa, -].
        pressure_pa: Reference external pressure [Pa].
        n_buckle: Buckling factors requested.
    """
    r = np.linalg.norm(nodes[0])
    north = int(np.argmax(nodes[:, 2])) + 1
    south = int(np.argmin(nodes[:, 2])) + 1
    east = int(np.argmin(np.linalg.norm(nodes - np.array([r, 0.0, 0.0]), axis=1))) + 1
    lines = ["*NODE"] + [f"{i+1},{p[0]:.12e},{p[1]:.12e},{p[2]:.12e}" for i, p in enumerate(nodes)]
    lines.append("*ELEMENT,TYPE=S8R,ELSET=EALL")
    lines += [f"{e+1}," + ",".join(str(v) for v in row) for e, row in enumerate(els)]
    lines.append("*NSET,NSET=NUSED")
    ids = np.unique(els)
    lines += [",".join(str(v) for v in ids[i:i + 16]) for i in range(0, len(ids), 16)]
    lines += ["*BOUNDARY", f"{north},1,2", f"{south},1,3", f"{east},2,2",
              "*MATERIAL,NAME=MAT", "*ELASTIC", f"{e_pa:.6e},{nu}",
              "*SHELL SECTION,ELSET=EALL,MATERIAL=MAT", f"{thickness_m}",
              "*STEP", "*STATIC", "*DLOAD", f"EALL,P,{-pressure_pa:.9e}",
              "*NODE PRINT,NSET=NUSED", "U", "*END STEP",
              "*STEP", "*BUCKLE", f"{n_buckle}", "*DLOAD", f"EALL,P,{-pressure_pa:.9e}", "*END STEP"]
    return "\n".join(lines) + "\n"


def zoelly_benchmark(e_pa, nu, radius_m=5.0, thickness_m=0.1, m=16, workdir=None, ccx=None):
    """Run V1 on one mesh and return its outcome.

    Args:
        e_pa, nu: Material [Pa, -]; ShellForm passes ShellBench's concrete values.
        radius_m, thickness_m: Sphere radius and wall thickness [m]. The
            record runs R/t = 50 and 100. The sized shells have R/t of about
            78 to 520 by the circular-arc estimate R = ((L/2)^2 + f^2) / (2 f),
            so 100 lies inside that range and 50 is a thicker, harder case for
            the thin-shell formula [J].
        m: Elements per cube-face edge (6 m^2 elements in all).
        workdir, ccx: As for shellform.fe.analyse.

    Returns:
        Dict with m, elements, nodes, element size [m], R/t, p_cr closed form
        and FE [Pa], the relative error, the lowest buckling factors, the
        membrane radial displacement (FE and closed form) [m] and the pass flag.
    """
    ccx = ccx or find_ccx()
    if ccx is None:
        raise RuntimeError("CalculiX (ccx) not found on PATH")
    nodes, els = cube_sphere(radius_m, m)
    p_cl = zoelly_pressure(e_pa, nu, thickness_m, radius_m)
    p_ref = p_cl / 10.0  # reference load; the factor is then close to 10
    work = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="zoelly_"))
    work.mkdir(parents=True, exist_ok=True)
    (work / "sphere.inp").write_text(sphere_deck(nodes, els, thickness_m, e_pa, nu, p_ref))
    run = subprocess.run([ccx, "sphere"], cwd=work, capture_output=True, text=True)
    dat = work / "sphere.dat"
    if not dat.exists() or "Job finished" not in run.stdout:
        raise RuntimeError(f"CalculiX failed:\n{run.stdout[-2000:]}")
    text = dat.read_text()
    _, _, _, buck = parse_dat(text)
    u = _blocks(text, "displacements (vx,vy,vz)")[0]
    xyz = nodes[u[:, 0].astype(int) - 1]
    # Radial displacement relative to the body motion allowed by the supports.
    ur = np.einsum("ij,ij->i", u[:, 1:4] - u[:, 1:4].mean(axis=0), xyz) / radius_m
    pos = np.sort(buck[buck > 0])
    p_fe = float(pos[0] * p_ref)
    err = (p_fe - p_cl) / p_cl
    edge = 2 * np.pi * radius_m / (4 * m)
    return {"m": m, "elements": len(els), "nodes": len(nodes), "element_size_m": edge,
            "radius_m": radius_m, "thickness_m": thickness_m, "r_over_t": radius_m / thickness_m,
            "e_pa": e_pa, "nu": nu, "p_ref_pa": p_ref, "p_cr_closed_form_pa": p_cl, "p_cr_fe_pa": p_fe,
            "relative_error": err, "buckling_factors": ";".join(f"{b:.6g}" for b in pos),
            "membrane_ur_fe_m": float(ur.mean()), "membrane_ur_spread_m": float(np.ptp(ur)),
            "membrane_ur_closed_form_m": float(-p_ref * radius_m ** 2 * (1 - nu) / (2 * e_pa * thickness_m)),
            "passed": bool(abs(err) < ZOELLY_TOLERANCE)}


# ---------------------------------------------------------------------------
# V2: h-convergence of the sized checks
# ---------------------------------------------------------------------------

#: Networks of the h-study: nodes per side (S8R elements per side = (n - 1) / 2).
H_GRIDS = (21, 41, 61, 81)
#: Acceptance limit of V2 between the two finest networks (blueprint add-on 2) [-].
H_TOLERANCE = 0.015


def h_point(case, thickness_m, n, inp):
    """Return the sized-check quantities of one design on one network.

    The form is found again on the n x n network (shellform.designs.form with
    grid_n = n), and every load case is run at the frozen sized thickness.

    Args:
        case: Design case dict (shellform.design_space).
        thickness_m: Frozen sized thickness [m].
        n: Nodes per side (odd).
        inp: DesignInputs.

    Returns:
        Dict: n, elements, lowest buckling factor over the ULS cases, SLS
        deflection [m], its ratio to L/300, and the largest compression
        outside the support zones [Pa].
    """
    from shellform.designs import form

    c = dict(case, grid_n=n)
    net, _, mid = form(c)
    span = case["span_m"]
    cases, sls = load_cases(inp, case["sa_g"])
    zone = ZONE_RADIUS_SPAN_RATIO * span
    res = [run_case(mid, n, net.fixed, thickness_m, inp.e_pa, inp.nu, inp.density_kg_m3, acc, w,
                    sls=sls if k == 0 else None, zone_radius_m=zone, n_buckle=4)
           for k, (_, acc, w) in enumerate(cases)]
    defl = res[0].sls_disp_m
    return {"n": n, "elements": ((n - 1) // 2) ** 2, "buckling_factor": min(r.buckling_factor for r in res),
            "sls_deflection_m": defl, "deflection_ratio": defl / (span / DEFLECTION_SPAN_RATIO),
            "compression_pa": max(r.compression_pa for r in res)}


# ---------------------------------------------------------------------------
# V3: residual of the assembled force density system
# ---------------------------------------------------------------------------


#: Acceptance limit of V3 [N], with unit nodal weights (blueprint add-on 3).
FDM_RESIDUAL_TOLERANCE = 1e-10


def fdm_residual(net, xyz, loads):
    """Return max |D x_free - (p_free - D_f x_fixed)| over x, y and z [N].

    D = C_f^T Q C_f and D_f = C_f^T Q C_x are assembled again here from the
    edges and force densities, independently of shellform.formfind.solve.

    Args:
        net: Network whose force densities were used to find xyz.
        xyz: Form-found coordinates, shape (n, 3) [m].
        loads: Nodal loads used, shape (n, 3) [N].
    """
    m, n = len(net.edges), len(xyz)
    C = sp.coo_matrix((np.tile([1.0, -1.0], m), (np.repeat(np.arange(m), 2), net.edges.ravel())),
                      shape=(m, n)).tocsr()
    Cf, Cx = C[:, net.free], C[:, net.fixed]
    Q = sp.diags(net.q)
    D, Df = Cf.T @ Q @ Cf, Cf.T @ Q @ Cx
    r = D @ xyz[net.free] - (np.asarray(loads)[net.free] - Df @ xyz[net.fixed])
    return float(np.abs(r).max())


def fdm_residual_of_case(case, sa_g=None):
    """Return (residual [N], largest nodal load [N]) for the form-finding of one design.

    For the gravity form the loads are the unit nodal weights; with sa_g the
    lateral load of Michiels & Adriaenssens is added, on the same network
    and force densities, and the form is solved again.
    """
    from shellform.designs import form

    net, grav, _ = form(dict(case, strategy="gravity", sa_g=0.0))
    loads = plan_loads(net, sa_x=sa_g or 0.0)
    xyz = grav if not sa_g else solve(net, loads)
    return fdm_residual(net, xyz, loads), float(np.abs(loads).max())


# ---------------------------------------------------------------------------
# V4: membrane and bending shares of the strain energy
# ---------------------------------------------------------------------------


def energy_density(s, e_pa, nu):
    """Return the complementary energy density of stress states s [J/m3].

    u = [(1 + nu) s:s - nu (tr s)^2] / (2 E), with s given as the six
    components (sxx, syy, szz, sxy, sxz, syz) in the last axis. The form is
    invariant, so global components can be used directly.
    """
    xx, yy, zz, xy, xz, yz = (s[..., k] for k in range(6))
    ss = xx ** 2 + yy ** 2 + zz ** 2 + 2 * (xy ** 2 + xz ** 2 + yz ** 2)
    tr = xx + yy + zz
    return ((1 + nu) * ss - nu * tr ** 2) / (2 * e_pa)


def element_areas(xyz, n):
    """Return the mid-surface area of each S8R element of the n x n grid [m2]."""
    els = s8r_elements(n)
    p = xyz[els[:, :4] - 1]
    t1 = 0.5 * np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1)
    t2 = 0.5 * np.linalg.norm(np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0]), axis=1)
    return t1 + t2


def energy_split(face_stress_pa, areas_m2, thickness_m, e_pa, nu):
    """Return (membrane energy, bending energy) [J] from face stresses.

    With stress linear through the thickness, s(z) = s_m + (2 z / t) s_b, the
    energy per unit area is t u(s_m) + (t / 3) u(s_b): the cross term
    integrates to zero. s_m is the mean of the two faces and s_b half their
    difference. Transverse shear energy is left out (thin shell) [J].

    Args:
        face_stress_pa: Shape (n_el, 2, 6), as CaseResult.face_stress_pa [Pa].
        areas_m2: Element areas in the same order [m2].
        thickness_m: Shell thickness [m].
        e_pa, nu: Material [Pa, -].
    """
    s_m = 0.5 * (face_stress_pa[:, 0] + face_stress_pa[:, 1])
    s_b = 0.5 * (face_stress_pa[:, 1] - face_stress_pa[:, 0])
    for s in (s_m, s_b):  # transverse shear is not part of either share
        s[:, 4:6] = 0.0
    um = float(np.sum(areas_m2 * thickness_m * energy_density(s_m, e_pa, nu)))
    ub = float(np.sum(areas_m2 * thickness_m / 3.0 * energy_density(s_b, e_pa, nu)))
    return um, ub


def energy_row(case, thickness_m, inp):
    """Return the membrane energy share of one sized design under each ULS case.

    Returns:
        Dict with the case keys, the thickness and, per ULS case, the
        membrane share Um / (Um + Ub) [-] and the total energy [J].
    """
    from shellform.designs import form, grid_n

    net, _, mid = form(case)
    n = grid_n(case)
    cases, _ = load_cases(inp, case["sa_g"])
    areas = element_areas(mid, n)
    row = {k: case[k] for k in ("design_id", "span_m", "supports", "rise_ratio", "strategy", "sa_g")}
    row["thickness_m"] = thickness_m
    for name, acc, w in cases:
        r = run_case(mid, n, net.fixed, thickness_m, inp.e_pa, inp.nu, inp.density_kg_m3, acc, w,
                     zone_radius_m=ZONE_RADIUS_SPAN_RATIO * case["span_m"])
        um, ub = energy_split(r.face_stress_pa, areas, thickness_m, inp.e_pa, inp.nu)
        row[f"membrane_share_{name}"] = um / (um + ub)
        row[f"energy_j_{name}"] = um + ub
    return row


# ---------------------------------------------------------------------------
# V5: formwork (A5) bound
# ---------------------------------------------------------------------------


def with_formwork(carbon_m2, formwork_area_m2_per_m2, phi):
    """Return carbon per m2 of plan with a formwork term added [kgCO2e/m2].

    Args:
        carbon_m2: A1-A3 carbon per m2 of plan [kgCO2e/m2].
        formwork_area_m2_per_m2: Formwork (soffit) area per m2 of plan [-];
            ShellForm takes it as the shell's surface area over its plan area.
        phi: Formwork carbon per m2 of formwork per use, F / N [kgCO2e/m2],
            for a factor F and N reuses. ShellForm supplies no F (CLAUDE.md
            rule 2), so phi is swept.
    """
    return carbon_m2 + phi * formwork_area_m2_per_m2


def formwork_bound(rel_carbon, rel_area):
    """Return the largest |relative difference| that any formwork term can produce.

    With a formwork term phi x A added to both strategies, the relative
    difference (C_s + phi A_s) / (C_g + phi A_g) - 1 is a weighted mean of
    the carbon difference C_s / C_g - 1 and the formwork-area difference
    A_s / A_g - 1 (the mediant inequality), so it lies between the two for
    every phi >= 0.

    Args:
        rel_carbon: Seismic minus gravity, relative, of A1-A3 carbon [-].
        rel_area: Seismic minus gravity, relative, of formwork area [-].
    """
    return max(abs(rel_carbon), abs(rel_area))
