"""Solver-independent checks for the seismic-aware form-finding (tests S2, S3, S4).

These functions do not form-find. They check a form produced by any
force density solver (ShellBench floor-r1, extended in ShellForm), so the
same checks run unchanged when the pin moves to a new ShellBench tag.

Conventions: nodal coordinates xyz [m] are an (n, 3) array; edges are
(m, 2) node index pairs; q [N/m] is the force density of each edge; loads
[N] are an (n, 3) array; ``free`` lists the indices of unsupported nodes.
"""

import numpy as np


def nodal_residuals(xyz, edges, q, loads, free):
    """Return the out-of-balance force at every free node [N].

    At a free node i, equilibrium in a force density network is
    sum_j q_ij (x_j - x_i) + p_i = 0 (Schek 1974).

    Args:
        xyz: Nodal coordinates, shape (n, 3) [m].
        edges: Node index pairs, shape (m, 2).
        q: Force density per edge, shape (m,) [N/m].
        loads: Nodal loads, shape (n, 3) [N].
        free: Indices of the free nodes.

    Returns:
        Residual force vectors at the free nodes, shape (len(free), 3) [N].
    """
    xyz = np.asarray(xyz, dtype=float)
    edges = np.asarray(edges, dtype=int)
    q = np.asarray(q, dtype=float)
    force = np.array(loads, dtype=float, copy=True)
    vec = xyz[edges[:, 1]] - xyz[edges[:, 0]]
    edge_force = q[:, None] * vec
    np.add.at(force, edges[:, 0], edge_force)
    np.add.at(force, edges[:, 1], -edge_force)
    return force[np.asarray(free, dtype=int)]


def equilibrium_error(xyz, edges, q, loads, free):
    """Return the largest free-node residual relative to the largest load (test S2).

    Args:
        xyz, edges, q, loads, free: As for :func:`nodal_residuals`.

    Returns:
        max |residual| / max |load| [-]. Test S2 passes below 1e-9.

    Raises:
        ValueError: If every load is zero, because the ratio is undefined.
    """
    residual = np.linalg.norm(nodal_residuals(xyz, edges, q, loads, free), axis=1)
    load_scale = np.linalg.norm(np.asarray(loads, dtype=float), axis=1).max()
    if load_scale == 0.0:
        raise ValueError("all loads are zero; the relative residual is undefined")
    return float(residual.max() / load_scale)


def rotate_z(vectors, angle_rad):
    """Rotate points or vectors about the vertical z axis.

    Args:
        vectors: Array of shape (n, 3).
        angle_rad: Rotation angle, anticlockwise seen from above [rad].

    Returns:
        Rotated array, shape (n, 3).
    """
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return np.asarray(vectors, dtype=float) @ rot.T


def rotation_error(solve, xyz_supports, loads, angle_rad):
    """Return the error of the rotation test (test S3).

    Rotating every load and every support about z by one angle must rotate
    the form by the same angle, because the force density equations are
    linear and isotropic in plan.

    Args:
        solve: Callable ``solve(xyz_supports, loads) -> xyz`` wrapping the
            form-finder under test, with connectivity and force densities
            fixed inside it.
        xyz_supports: Coordinates used for the support nodes, shape (n, 3)
            [m]; the solver reads only the support rows.
        loads: Nodal loads, shape (n, 3) [N].
        angle_rad: Rotation angle [rad].

    Returns:
        Largest node distance between the two forms, divided by the largest
        plan dimension of the form [-]. Test S3 passes below 1e-9.
    """
    base = solve(xyz_supports, loads)
    turned = solve(rotate_z(xyz_supports, angle_rad), rotate_z(loads, angle_rad))
    expected = rotate_z(base, angle_rad)
    size = np.ptp(base[:, :2], axis=0).max()
    return float(np.linalg.norm(turned - expected, axis=1).max() / size)


def leaned_parabola(span_m, rise_m, sa_g, s_m):
    """Return the closed-form thrust line of an arch under gravity plus Sa (test S4).

    A funicular under a uniform load per unit length of its parameter s,
    acting in one fixed direction, is a parabola whose axis is parallel to
    that load (statics of a cable with parallel loads). Gravity alone gives
    z(s) = 4 f s (L - s) / L^2 over the plan coordinate s. Adding a uniform
    horizontal acceleration Sa (in g) on the same weight tilts the load by
    atan(Sa), and the compression line leans into the load:
    x(s) = s - Sa z(s), z unchanged. Supports stay at s = 0 and s = L.

    Args:
        span_m: Distance between the two supports, L [m].
        rise_m: Rise of the gravity thrust line, f [m].
        sa_g: Horizontal acceleration, positive in +x [g].
        s_m: Plan coordinates of the gravity form, s in [0, L] [m].

    Returns:
        (x, z) of the leaned thrust line at each s [m].
    """
    s = np.asarray(s_m, dtype=float)
    z = 4.0 * rise_m * s * (span_m - s) / span_m**2
    return s - sa_g * z, z


def leaned_arch_reactions(span_m, rise_m, sa_g, n_segments, w_node):
    """Return the closed-form support reactions of a leaned nodal arch (test S4).

    The arch has n_segments equal plan segments, h = L / n_segments, and a
    weight w_node at each of the n_segments - 1 free nodes. The horizontal
    thrust of the gravity form is H_g = w L^2 / (8 f h), the discrete form of
    q L^2 / (8 f) with q = w / h. The lateral load Sa W (W = total free-node
    weight) is shared equally by the two supports, in the direction that
    resists it: the support on the far side of the load (+x for Sa > 0)
    pushes back harder, so H_left = H_g - Sa W / 2 and H_right = H_g + Sa W / 2
    (both as thrust magnitudes on the supports). The vertical reactions stay W / 2
    each, because the moment of the lateral load about one support,
    Sa w sum(z_i), is cancelled by the lean of the loads, w sum(Sa z_i).

    Args:
        span_m: Support distance L [m].
        rise_m: Gravity rise f [m].
        sa_g: Horizontal acceleration, positive in +x [g].
        n_segments: Number of equal plan segments (even, so a node sits at the crown).
        w_node: Weight per free node [N].

    Returns:
        Dict of h_left, h_right, v_left, v_right [N] (thrust and upward
        reaction magnitudes).
    """
    h = span_m / n_segments
    w_total = (n_segments - 1) * w_node
    h_g = w_node * span_m**2 / (8.0 * rise_m * h)
    return {"h_left": h_g - sa_g * w_total / 2.0, "h_right": h_g + sa_g * w_total / 2.0,
            "v_left": w_total / 2.0, "v_right": w_total / 2.0}


def support_reactions(xyz, edges, q, fixed):
    """Return the force each support must supply to the network [N].

    The reaction at a support balances the member forces meeting there,
    R_k = -sum_j q_kj (x_j - x_k); the load lumped on the support node itself
    is left out, so this is the reaction to the free-node loads only.

    Args:
        xyz: Nodal coordinates, shape (n, 3) [m].
        edges: Node index pairs, shape (m, 2).
        q: Force density per edge, shape (m,) [N/m].
        fixed: Indices of the supported nodes.

    Returns:
        Reaction vectors at the supports, shape (len(fixed), 3) [N].
    """
    zero = np.zeros_like(np.asarray(xyz, dtype=float))
    return -nodal_residuals(xyz, edges, q, zero, fixed)
