"""Design inputs read from the pinned ShellBench clone, never typed here.

Python constants are imported from ShellBench. Values that ShellBench v0.1.0
holds only in its documents (Poisson's ratio, unit weight, roof loads) are
read in place from those documents at run time (docs/data_contract.md,
section 1). A missing or renamed row stops the run instead of falling back to
a default.

Units: SI (N, m, Pa).
"""

import re
from dataclasses import dataclass
from pathlib import Path

import shellbench
import shellbench.anchor_frame as sb_frame
import shellbench.carbon as sb_carbon
import shellbench.combinations as sb_comb
import shellbench.seismic as sb_seismic

_NUM = r"([0-9]+(?:\.[0-9]+)?)"


@dataclass(frozen=True)
class DesignInputs:
    """ShellBench values used by the shell analysis.

    Attributes:
        e_pa: Concrete Young's modulus [Pa] (spec X4, anchor_frame.E_KN_M2).
        nu: Concrete Poisson's ratio [-] (notes/gb50010_design_values.md).
        unit_weight_n_m3: Concrete unit weight [N/m3] (spec X7).
        superimposed_dead_pa: Roof dead load less its slab [Pa] (spec L2; D4-3).
        roof_live_pa: Non-accessible roof live load [Pa] (spec L11).
        g_m_s2: Gravitational acceleration [m/s2] (seismic.G_ACCEL_M_S2).
        gamma_g, gamma_q: Gravity combination factors [-].
        gamma_eg, gamma_eh: Code seismic combination factors [-].
    """

    e_pa: float
    nu: float
    unit_weight_n_m3: float
    superimposed_dead_pa: float
    roof_live_pa: float
    g_m_s2: float
    gamma_g: float
    gamma_q: float
    gamma_eg: float
    gamma_eh: float


def clone_root() -> Path:
    """Return the root folder of the installed ShellBench clone."""
    return Path(shellbench.__file__).resolve().parents[2]


def _row_value(path: Path, key: str, pattern: str) -> float:
    """Return the number found by a table-row pattern in a ShellBench file.

    Args:
        path: The file, read as UTF-8.
        key: Row key, for the error message.
        pattern: Regular expression with one group, the number.

    Raises:
        ValueError: If the row is not found exactly once.
    """
    hits = re.findall(pattern, path.read_text(encoding="utf-8"), re.M)
    if len(hits) != 1:
        raise ValueError(f"expected one row {key} in {path}, found {len(hits)}")
    return float(hits[0])


def spec_value(key: str) -> float:
    """Return the value in the third column of a docs/baseline_spec.md row.

    Args:
        key: Row key, such as "X7".
    """
    path = clone_root() / "docs" / "baseline_spec.md"
    return _row_value(path, key, rf"^\|\s*{key}\s*\|[^|]*\|\s*{_NUM}")


def poisson_ratio() -> float:
    """Return ν_c from ShellBench's notes/gb50010_design_values.md."""
    path = clone_root() / "notes" / "gb50010_design_values.md"
    return _row_value(path, "ν_c", rf"^\|\s*ν_c\s*\|\s*{_NUM}")


def load_inputs() -> DesignInputs:
    """Return the design inputs from the pinned ShellBench clone."""
    unit_weight = spec_value("X7") * 1.0e3
    roof_dead = spec_value("L2") * 1.0e3
    return DesignInputs(
        e_pa=sb_frame.E_KN_M2 * 1.0e3,
        nu=poisson_ratio(),
        unit_weight_n_m3=unit_weight,
        superimposed_dead_pa=roof_dead - sb_carbon.SLAB_T_M * unit_weight,
        roof_live_pa=spec_value("L11") * 1.0e3,
        g_m_s2=sb_seismic.G_ACCEL_M_S2,
        gamma_g=sb_comb.GAMMA_G,
        gamma_q=sb_comb.GAMMA_Q,
        gamma_eg=sb_comb.GAMMA_EG_CODE,
        gamma_eh=sb_comb.GAMMA_EH_CODE,
    )
