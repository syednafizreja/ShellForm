"""Design inputs for sizing, read from ShellBench at the pinned tag.

Nothing here is a hard-coded ShellBench value (docs/data_contract.md). Code
constants are imported from shellbench modules; the unit weight and roof
loads are read from ShellBench's ``docs/baseline_spec.md`` in place, by row ID.

The one value ShellBench does not yet give is Poisson's ratio of concrete.
It stays a placeholder marked [?] until a ShellBench tag provides it; the
linear-elastic shell results depend on it only weakly.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path

NU_PLACEHOLDER = 0.2  # [?] not in ShellBench v0.1.0; replace when a tag gives it


@dataclass(frozen=True)
class DesignInputs:
    """Material values, loads and factors used by the sizing loop (SI units).

    Attributes:
        e_pa: Concrete elastic modulus [Pa] (spec X4).
        nu: Poisson's ratio [-] ([?] placeholder).
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


def shellbench_root():
    """Return the root folder of the installed (editable) ShellBench clone."""
    import shellbench

    return Path(shellbench.__file__).resolve().parents[2]


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
    kn = 1.0e3
    unit_weight = spec_value(spec, "X7") * kn
    roof_dead = spec_value(spec, "L2") * kn
    sdl = roof_dead - unit_weight * sb_carbon.SLAB_T_M
    return DesignInputs(
        e_pa=sb_frame.E_KN_M2 * kn, nu=NU_PLACEHOLDER, unit_weight_n_m3=unit_weight,
        g_m_s2=sb_seis.G_ACCEL_M_S2, sdl_pa=sdl, live_pa=spec_value(spec, "L11") * kn,
        f_c_pa=sb_checks.FC_N_MM2 * 1e6, f_t_pa=sb_checks.FT_N_MM2 * 1e6, f_y_pa=sb_checks.FY_N_MM2 * 1e6,
        gamma_g=sb_comb.GAMMA_G, gamma_q=sb_comb.GAMMA_Q,
        gamma_eg=sb_comb.GAMMA_EG_CODE, gamma_eh=sb_comb.GAMMA_EH_CODE,
        psi_e_roof=sb_seis.LIVE_COMBINATION_COEFF_ROOF, tg_s=sb_seis.TG_ANCHOR_S,
        sources={"e_pa": "anchor_frame.E_KN_M2 (spec X4)", "nu": "[?] placeholder, not in ShellBench",
                 "unit_weight_n_m3": "baseline_spec.md X7", "g_m_s2": "seismic.G_ACCEL_M_S2",
                 "sdl_pa": "baseline_spec.md L2 - X7 x carbon.SLAB_T_M (G10) [J]",
                 "live_pa": "baseline_spec.md L11", "f_c_pa": "checks.FC_N_MM2 (X2)",
                 "f_t_pa": "checks.FT_N_MM2 (X3)", "f_y_pa": "checks.FY_N_MM2 (X5)",
                 "gamma_g": "combinations.GAMMA_G", "gamma_q": "combinations.GAMMA_Q",
                 "gamma_eg": "combinations.GAMMA_EG_CODE (GB 55002-2021 cl. 4.3.2)",
                 "gamma_eh": "combinations.GAMMA_EH_CODE (GB 55002-2021 cl. 4.3.2)",
                 "psi_e_roof": "seismic.LIVE_COMBINATION_COEFF_ROOF", "tg_s": "seismic.TG_ANCHOR_S"})
