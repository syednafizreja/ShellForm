"""A1-A3 embodied carbon of one shell, with the +/-25 % factor band (Day 5).

File: src/shellform/carbon.py

The factors are ShellBench's, read in place from ``data/carbon_factors.csv``
in the pinned clone with ShellBench's own reader
(``shellbench.carbon.read_factors``). The concrete grade, bar steel and
steel density are ShellBench's too (``shellbench.carbon``). ShellForm writes
no factor (CLAUDE.md rule 2). Up to ShellBench v0.2.0 the source column of
the rows used here said the official-copy check was open, so every carbon
number was provisional. From v0.3.0 it records the check as closed
(6 Nov 2026). ``factor_status`` reads that column in place, so result files
state the status the pinned file gives, not a typed-in one (Day 11).

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


#: Phrases in a source note that mark a factor as not yet checked against the
#: official copy (as worded in ShellBench's file up to v0.2.0).
OPEN_MARKERS = ("to confirm", "check open")


def factor_status(set_name=FACTOR_SET):
    """Return the check status of the two factors used, read from ShellBench's file.

    Reads the "source [text]" column of the concrete and bar-steel rows of
    set_name in ShellBench's ``data/carbon_factors.csv``, in place.

    Returns:
        "confirmed: ..." if neither source note contains an OPEN_MARKERS
        phrase, else "provisional: ..."; the text names the rows.
    """
    import csv

    import shellbench.carbon as sb

    want = {sb.CONCRETE_GRADE, sb.BAR_STEEL}
    with open(factors_path(), newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["set [text]"] == set_name and r["material [text]"] in want]
    if {r["material [text]"] for r in rows} != want:
        raise ValueError(f"{set_name}: rows for {sorted(want)} not found in {factors_path()}")
    open_rows = [r["material [text]"] for r in rows
                 if any(m in r["source [text]"].lower() for m in OPEN_MARKERS)]
    names = " and ".join(sorted(want))
    if open_rows:
        return (f"provisional: ShellBench's source note for {', '.join(sorted(open_rows))} "
                f"({set_name}) says the official-copy check is open")
    return f"confirmed: ShellBench's source notes for {names} ({set_name}) record the official-copy check as closed"


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
