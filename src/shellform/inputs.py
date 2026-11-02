"""Design inputs for sizing, read from ShellBench at the pinned tag.

Nothing here is a hard-coded ShellBench value (docs/data_contract.md). Code
constants are imported from shellbench modules; the unit weight and roof
loads are read from ShellBench's ``docs/baseline_spec.md`` in place, by row ID,
and Poisson's ratio from ``notes/gb50010_design_values.md``.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class DesignInputs:
    """Material values, loads and factors used by the sizing loop (SI units).

    Attributes:
        e_pa: Concrete elastic modulus [Pa] (spec X4).
        nu: Poisson's ratio [-] (GB 50010 cl. 4.1.5, ShellBench notes).
        unit_weight_n_m3: Reinforced concrete unit weight [N/m3] (spec X7).
        g_m_s2: Gravitational acceleration [m/s2] (shellbench.seismic).
        sdl_pa: Roof superimposed dead load per plan area [Pa]: spec L2 roof
            dead load less the 0.12 m slab it includes (X7 x G10) [J].
        live_pa: Non-accessible roof live load per plan area [Pa] (spec L11).
        f_c_pa, f_t_pa, f_y_pa: Design strengths [Pa] (shellbench.checks).
        gamma_g, gamma_q: Gravity partial factors [-] (shellbench.combinations).
        gamma_eg, gamma_eh: Seismic combination factors, current code [-]
            (GB 55002-2021, shellbench.combinations *_CODE).
        psi_e_roof: Live load share in G_E for a roof [-] (shellbench.seismic).
        tg_s: Characteristic period of the anchor site [s] (shellbench.seismic).
        sources: Where each value came from.
    """

    e_pa: float
    nu: float
    unit_weight_n_m3: float
    g_m_s2: float
    sdl_pa: float
    live_pa: float
    f_c_pa: float
    f_t_pa: float
    f_y_pa: float
    gamma_g: float
    gamma_q: float
    gamma_eg: float
    gamma_eh: float
    psi_e_roof: float
    tg_s: float
    sources: dict

    @property
    def density_kg_m3(self):
        """Mass density from the unit weight [kg/m3]."""
        return self.unit_weight_n_m3 / self.g_m_s2

    def as_dict(self):
        """Return the inputs as a plain dict, for result files."""
        d = asdict(self)
        d["density_kg_m3"] = self.density_kg_m3
        return d


def spec_value(spec_text, row_id):
    """Return the leading number in the Value column of a baseline_spec row.

    Args:
        spec_text: Text of ShellBench's docs/baseline_spec.md.
        row_id: Row ID, such as "X7".

    Returns:
        The number as a float, in the units printed in that row.
    """
    m = re.search(r"^\|\s*" + re.escape(row_id) + r"\s*\|[^|]*\|\s*\**\s*([-+]?\d+(?:\.\d+)?)", spec_text, re.M)
    if not m:
        raise KeyError(f"row {row_id} not found in baseline_spec.md")
    return float(m.group(1))


def note_value(note_text, symbol):
    """Return the number in the Value column of a ShellBench notes table row.

    Args:
        note_text: Text of a ShellBench notes file.
        symbol: First column of the row, such as "ν_c".

    Returns:
        The number as a float, in the units printed in that row.
    """
    m = re.search(r"^\|\s*" + re.escape(symbol) + r"\s*\|\s*([-+]?\d+(?:\.\d+)?)", note_text, re.M)
    if not m:
        raise KeyError(f"row {symbol} not found in the ShellBench note")
    return float(m.group(1))


def shellbench_root():
    """Return the root folder of the installed (editable) ShellBench clone."""
    import shellbench

    return Path(shellbench.__file__).resolve().parents[2]


def rho_min_slab(f_t_pa, f_y_pa, concept_text=None):
    """Return the minimum steel ratio read from ShellBench's floor concept.

    The rule "the larger of a % and b f_t / f_y" is GB 50010 Table 8.5.1
    note 2; applying it to a shell is ShellBench's and ShellForm's reading [J].

    Args:
        f_t_pa, f_y_pa: Design strengths [Pa].
        concept_text: Text of docs/floor_concept.md; read in place if None.

    Returns:
        The ratio as a fraction [-].
    """
    if concept_text is None:
        concept_text = (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")
    m = re.search(r"the larger of ([\d.]+) % and (\d+) f_t / f_y", concept_text)
    if not m:
        raise KeyError("minimum steel rule not found in floor_concept.md")
    return max(float(m.group(1)), float(m.group(2)) * f_t_pa / f_y_pa) / 100.0


def load_carbon_factors(factor_set="GBT51366", concrete="C40", steel="HRB400"):
    """Read A1-A3 factors and steel density from ShellBench in place.

    Returns:
        Dict with concrete_kgco2e_m3, steel_kgco2e_kg, steel_density_kg_m3 and
        the names of the set and materials.
    """
    import shellbench.carbon as sb_carbon

    factors = sb_carbon.read_factors(shellbench_root() / "data" / "carbon_factors.csv")
    con, con_unit = factors[(factor_set, concrete)]
    bar, bar_unit = factors[(factor_set, steel)]
    return {"factor_set": factor_set, "concrete": concrete, "steel": steel,
            "concrete_kgco2e_m3": con * sb_carbon.CONVERSIONS[con_unit][1],
            "steel_kgco2e_kg": bar * sb_carbon.CONVERSIONS[bar_unit][1],
            "steel_density_kg_m3": sb_carbon.STEEL_DENSITY_KG_M3}


def load_inputs():
    """Read the design inputs from the installed, pinned ShellBench.

    Returns:
        DesignInputs.
    """
    import shellbench.anchor_frame as sb_frame
    import shellbench.carbon as sb_carbon
    import shellbench.checks as sb_checks
    import shellbench.combinations as sb_comb
    import shellbench.seismic as sb_seis

    spec = (shellbench_root() / "docs" / "baseline_spec.md").read_text(encoding="utf-8")
    design_values = (shellbench_root() / "notes" / "gb50010_design_values.md").read_text(encoding="utf-8")
    kn = 1.0e3
    unit_weight = spec_value(spec, "X7") * kn
    roof_dead = spec_value(spec, "L2") * kn
    sdl = roof_dead - unit_weight * sb_carbon.SLAB_T_M
    return DesignInputs(
        e_pa=sb_frame.E_KN_M2 * kn, nu=note_value(design_values, "ν_c"), unit_weight_n_m3=unit_weight,
        g_m_s2=sb_seis.G_ACCEL_M_S2, sdl_pa=sdl, live_pa=spec_value(spec, "L11") * kn,
        f_c_pa=sb_checks.FC_N_MM2 * 1e6, f_t_pa=sb_checks.FT_N_MM2 * 1e6, f_y_pa=sb_checks.FY_N_MM2 * 1e6,
        gamma_g=sb_comb.GAMMA_G, gamma_q=sb_comb.GAMMA_Q,
        gamma_eg=sb_comb.GAMMA_EG_CODE, gamma_eh=sb_comb.GAMMA_EH_CODE,
        psi_e_roof=sb_seis.LIVE_COMBINATION_COEFF_ROOF, tg_s=sb_seis.TG_ANCHOR_S,
        sources={"e_pa": "anchor_frame.E_KN_M2 (spec X4)", "nu": "notes/gb50010_design_values.md row ν_c (cl. 4.1.5)",
                 "unit_weight_n_m3": "baseline_spec.md X7", "g_m_s2": "seismic.G_ACCEL_M_S2",
                 "sdl_pa": "baseline_spec.md L2 - X7 x carbon.SLAB_T_M (G10) [J]",
                 "live_pa": "baseline_spec.md L11", "f_c_pa": "checks.FC_N_MM2 (X2)",
                 "f_t_pa": "checks.FT_N_MM2 (X3)", "f_y_pa": "checks.FY_N_MM2 (X5)",
                 "gamma_g": "combinations.GAMMA_G", "gamma_q": "combinations.GAMMA_Q",
                 "gamma_eg": "combinations.GAMMA_EG_CODE (GB 55002-2021 cl. 4.3.2)",
                 "gamma_eh": "combinations.GAMMA_EH_CODE (GB 55002-2021 cl. 4.3.2)",
                 "psi_e_roof": "seismic.LIVE_COMBINATION_COEFF_ROOF", "tg_s": "seismic.TG_ANCHOR_S"})
