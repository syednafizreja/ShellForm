"""A1-A3 embodied carbon of one shell, with the +/-25 % factor band (Day 5).

File: src/shellform/carbon.py

The factors are ShellBench's, read in place from ``data/carbon_factors.csv``
in the pinned clone with ShellBench's own reader
(``shellbench.carbon.read_factors``). The concrete grade, bar steel and
steel density are ShellBench's too (``shellbench.carbon``). ShellForm writes
no factor (CLAUDE.md rule 2). Every factor row in that file is marked
"author to confirm" in its source column; until the author confirms them,
every carbon number here is provisional.

Pre-registration section 6 and decision P3: one factor set (GB/T 51366),
and a band in which the concrete and steel factors move by +/-25 %
independently, giving four corners. Carbon is reported per m2 of plan area.

Units: concrete in m3, steel in kg, carbon in kgCO2e.
"""

from dataclasses import dataclass
from itertools import product

#: Relative half-width of the factor band (pre-registration decision P3).
FACTOR_BAND = 0.25
#: The one factor set of pre-registration section 6 (GB/T 51366-2019), named as
#: in ShellBench's file. Named explicitly since 6 Nov 2026 (Day 9): from tag
#: v0.2.0 the file also holds a second set (OVAL2023), so "the only set in the
#: file" no longer identifies it.
FACTOR_SET = "GBT51366"


@dataclass(frozen=True)
class Factors:
    """Carbon factors of one set, converted to the take-off units.

    Attributes:
        set_name: Factor set name as written in the ShellBench file.
        concrete_material: Concrete grade the factor belongs to.
        steel_material: Bar steel the factor belongs to.
        concrete_kgco2e_m3: Concrete factor [kgCO2e/m3].
        steel_kgco2e_kg: Steel factor [kgCO2e/kg].
        steel_density_kg_m3: Steel density [kg/m3].
    """

    set_name: str
    concrete_material: str
    steel_material: str
    concrete_kgco2e_m3: float
    steel_kgco2e_kg: float
    steel_density_kg_m3: float


def factors_path():
    """Return the path of ShellBench's carbon factor file in the pinned clone."""
    from shellform.inputs import shellbench_root

    return shellbench_root() / "data" / "carbon_factors.csv"


def load_factors(set_name=FACTOR_SET):
    """Read one factor set from ShellBench, in place.

    Args:
        set_name: Factor set; default FACTOR_SET. If None, the file must hold
            exactly one set.

    Returns:
        Factors.

    Raises:
        ValueError: If set_name is None and the file holds more than one set,
            or a factor is in a unit ShellBench's reader cannot convert.
    """
    import shellbench.carbon as sb

    table = sb.read_factors(factors_path())
    sets = sorted({s for s, _ in table})
    if set_name is None:
        if len(sets) != 1:
            raise ValueError(f"several factor sets {sets}; name one")
        set_name = sets[0]

    def per(material, qty_unit):
        value, unit = table[(set_name, material)]
        want, mult = sb.CONVERSIONS[unit]
        if want != qty_unit:
            raise ValueError(f"{material}: factor per {want}, take-off in {qty_unit}")
        return value * mult

    return Factors(set_name, sb.CONCRETE_GRADE, sb.BAR_STEEL,
                   per(sb.CONCRETE_GRADE, "m3"), per(sb.BAR_STEEL, "kg"), sb.STEEL_DENSITY_KG_M3)


def carbon_kgco2e(concrete_m3, steel_kg, f, concrete_scale=1.0, steel_scale=1.0):
    """Return A1-A3 carbon [kgCO2e] of a concrete volume and a steel mass.

    Args:
        concrete_m3: Concrete volume [m3].
        steel_kg: Steel mass [kg].
        f: Factors.
        concrete_scale, steel_scale: Multipliers on the two factors (band corners).
    """
    return concrete_m3 * f.concrete_kgco2e_m3 * concrete_scale + steel_kg * f.steel_kgco2e_kg * steel_scale


def band_corners():
    """Return the four band corners as {label: (concrete_scale, steel_scale)} (decision P3).

    Labels read c+s- for concrete +25 %, steel -25 %, and so on.
    """
    out = {}
    for c, s in product((-1, 1), (-1, 1)):
        label = f"c{'+' if c > 0 else '-'}s{'+' if s > 0 else '-'}"
        out[label] = (1.0 + c * FACTOR_BAND, 1.0 + s * FACTOR_BAND)
    return out
