"""Steel, support-zone concrete and carbon of one sized shell (Day 5).

Turns the stress fields of the ULS load cases into quantities, by the rules
in docs/preregistration.md (2 Nov 2026 amendment, D5-1 to D5-6):

- T1, T2: tensile resultants per unit width, from sorted in-plane principal
  stresses integrated through the thickness (D5-1).
- A_s = max(T / f_y, rho_min t) in each of two directions, element by element,
  enveloped over gravity and all four seismic directions (D5-2, D5-3).
- t_e = t max(1, compression / f_c), element by element (D5-4).
- Carbon per m2 of covered plan area, with the +/-25 % band (P3, D5-5).

Stress components come in CalculiX order: sxx, syy, szz, sxy, sxz, syz.
"""

from dataclasses import asdict, dataclass
from itertools import product

import numpy as np

from shellform.fe import plan_load_shares, principal_stresses, s8r_elements

N_LAYERS = 20       # D5-1: layers sampled through the thickness
FACTOR_BAND = 0.25  # pre-registration decision P3: +/-25 % on each factor
SAME_CARBON_RATIO = 0.05  # pre-registration section 7: "no meaningful difference"


def element_areas(xyz, n):
    """Return the surface area of each S8R element [m2].

    Uses the two triangles per grid cell of fe.surface_area, so the sum equals
    that function's result.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).

    Returns:
        Array of shape ((n-1)/2 squared,), in element order.
    """
    p = xyz.reshape(n, n, 3)
    a, b, c, d = p[:-1, :-1], p[:-1, 1:], p[1:, 1:], p[1:, :-1]
    cell = (0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=-1)
            + 0.5 * np.linalg.norm(np.cross(c - a, d - a), axis=-1))
    m = (n - 1) // 2
    return cell.reshape(m, 2, m, 2).sum(axis=(1, 3)).ravel()


def covered_plan_area(xyz, n):
    """Return the plan area the mesh covers [m2] (D5-5)."""
    return float(plan_load_shares(xyz, n).sum())


def element_axes(xyz, n):
    """Return two unit tangent vectors per element, from its corner nodes.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).

    Returns:
        (e1, e2), each of shape (n_el, 3).
    """
    c = xyz[s8r_elements(n)[:, :4] - 1]
    normal = np.cross(c[:, 2] - c[:, 0], c[:, 3] - c[:, 1])
    normal /= np.linalg.norm(normal, axis=1, keepdims=True)
    e1 = c[:, 1] - c[:, 0]
    e1 -= (e1 * normal).sum(axis=1, keepdims=True) * normal
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    return e1, np.cross(normal, e1)


def in_plane_stress(faces, e1, e2):
    """Return the in-plane stress components of each element on both faces.

    Args:
        faces: Stress components, shape (n_el, 2, 6) [Pa].
        e1, e2: Unit tangents, shape (n_el, 3).

    Returns:
        Array of shape (n_el, 2, 3): s11, s22, s12 [Pa].
    """
    xx, yy, zz, xy, xz, yz = (faces[..., k] for k in range(6))
    t = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1),
                  np.stack([xz, yz, zz], -1)], -2)
    a, b = e1[:, None, :, None], e2[:, None, :, None]
    ta, tb = t @ a, t @ b
    dot = lambda u, v: (u * v).sum(axis=-2)[..., 0]
    return np.stack([dot(a, ta), dot(b, tb), dot(a, tb)], axis=-1)


def tension_resultants(plane, t, layers=N_LAYERS):
    """Return the tensile resultants per unit width of each element (D5-1).

    Args:
        plane: In-plane stresses, shape (n_el, 2, 3) [Pa].
        t: Thickness [m].
        layers: Number of equal layers through the thickness.

    Returns:
        Array of shape (n_el, 2): T1 >= T2 [N/m].
    """
    z = ((np.arange(layers) + 0.5) / layers)[None, :, None]
    s = (1.0 - z) * plane[:, :1, :] + z * plane[:, 1:, :]
    mean = 0.5 * (s[..., 0] + s[..., 1])
    radius = np.hypot(0.5 * (s[..., 0] - s[..., 1]), s[..., 2])
    high = np.clip(mean + radius, 0.0, None)
    low = np.clip(mean - radius, 0.0, None)
    return np.stack([high.mean(axis=1), low.mean(axis=1)], axis=1) * t


def element_compression(faces):
    """Return the largest principal compression of each element, either face [Pa]."""
    return np.clip(-principal_stresses(faces)[..., 0].min(axis=1), 0.0, None)


def seismic_images(field):
    """Return a +x element field and its -x, +y and -y images.

    Both strategies' forms are symmetric under the mirrors and 90 degree
    rotations of the square plan (D4-1), so the other directions are grid
    images of the +x field (D5-2). The field must be invariant per element,
    such as a principal value, not a component in fixed axes.

    Args:
        field: Array with the element index first, on a square element grid.

    Returns:
        List of four arrays of the same shape.
    """
    m = int(round(np.sqrt(field.shape[0])))
    f = field.reshape((m, m) + field.shape[1:])
    swap = np.swapaxes(f, 0, 1)
    images = (f, f[:, ::-1], swap, swap[::-1])
    return [g.reshape(field.shape) for g in images]


@dataclass
class Quantities:
    """Material quantities of one sized shell.

    Attributes:
        concrete_uniform_m3: Concrete at the uniform thickness [m3].
        concrete_added_m3: Concrete added by the thickening rule [m3].
        steel_kg: Steel by D5-2 and D5-3 [kg].
        steel_kg_min_only: Steel if rho_min governed everywhere [kg].
        steel_kg_each_face: Steel if rho_min t applies on each face [kg].
        steel_zone_kg: Part of steel_kg inside the corner zones [kg].
        tension_governed_share: Share of area in which T / f_y exceeds
            rho_min t_e in the first direction [-].
        plan_area_m2: Covered plan area [m2].
    """

    concrete_uniform_m3: float
    concrete_added_m3: float
    steel_kg: float
    steel_kg_min_only: float
    steel_kg_each_face: float
    steel_zone_kg: float
    tension_governed_share: float
    plan_area_m2: float

    @property
    def concrete_m3(self):
        """Total concrete [m3]."""
        return self.concrete_uniform_m3 + self.concrete_added_m3

    def as_dict(self):
        """Return the quantities as a plain dict, with the total concrete."""
        return dict(asdict(self), concrete_m3=self.concrete_m3)


def shell_quantities(xyz, n, t, gravity_faces, seismic_faces, f_c_pa, f_y_pa, rho_min,
                     steel_density_kg_m3, zone=None):
    """Return the quantities of one sized shell.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).
        t: Uniform thickness [m].
        gravity_faces: ULS gravity stresses, shape (n_el, 2, 6) [Pa].
        seismic_faces: ULS seismic +x stresses, same shape, or None at Sa = 0.
        f_c_pa, f_y_pa: Design strengths [Pa].
        rho_min: Minimum steel ratio [-].
        steel_density_kg_m3: Steel density [kg/m3].
        zone: Boolean mask of corner-zone elements, or None.

    Returns:
        Quantities.
    """
    e1, e2 = element_axes(xyz, n)
    area = element_areas(xyz, n)
    fields, comps = [tension_resultants(in_plane_stress(gravity_faces, e1, e2), t)], [element_compression(gravity_faces)]
    if seismic_faces is not None:
        fields += seismic_images(tension_resultants(in_plane_stress(seismic_faces, e1, e2), t))
        comps += seismic_images(element_compression(seismic_faces))
    tension = np.max(fields, axis=0)
    t_e = t * np.maximum(1.0, np.max(comps, axis=0) / f_c_pa)
    a_t = tension / f_y_pa
    a_min = rho_min * t_e[:, None]

    def mass(a_s, where=None):
        per_el = a_s.sum(axis=1) * area * steel_density_kg_m3
        return float(per_el.sum() if where is None else per_el[where].sum())

    a_s = np.maximum(a_t, a_min)
    return Quantities(
        concrete_uniform_m3=float((t * area).sum()),
        concrete_added_m3=float(((t_e - t) * area).sum()),
        steel_kg=mass(a_s),
        steel_kg_min_only=mass(np.repeat(a_min, 2, axis=1)),
        steel_kg_each_face=mass(np.maximum(a_t, 2.0 * a_min)),
        steel_zone_kg=mass(a_s, np.zeros(len(area), bool) if zone is None else zone),
        tension_governed_share=float(area[a_t[:, 0] > a_min[:, 0]].sum() / area.sum()),
        plan_area_m2=covered_plan_area(xyz, n))


def carbon_kg(concrete_m3, steel_kg, factors, concrete_scale=1.0, steel_scale=1.0):
    """Return A1-A3 carbon [kgCO2e].

    Args:
        concrete_m3: Concrete [m3].
        steel_kg: Steel [kg].
        factors: Output of inputs.load_carbon_factors.
        concrete_scale, steel_scale: Factor-band multipliers [-].
    """
    return (concrete_m3 * factors["concrete_kgco2e_m3"] * concrete_scale
            + steel_kg * factors["steel_kgco2e_kg"] * steel_scale)


def band_corners():
    """Return the four (concrete, steel) multipliers of the factor band (P3)."""
    return list(product((1.0 - FACTOR_BAND, 1.0 + FACTOR_BAND), repeat=2))


def cheaper_strategy(gravity, seismic):
    """Apply the 5 % decision rule of pre-registration section 7.

    Args:
        gravity, seismic: Carbon of the two strategies, any common unit.

    Returns:
        "gravity", "seismic", or "no meaningful difference". The difference
        is taken relative to the lower of the two.
    """
    if abs(seismic - gravity) < SAME_CARBON_RATIO * min(gravity, seismic):
        return "no meaningful difference"
    return "seismic" if seismic < gravity else "gravity"
