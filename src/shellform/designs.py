"""Build the network and mid-surface of one design case.

Moved here from scripts/day04_size_10m.py on 2 Nov so that the Day 4 sizing
and the Day 5 steel take-off build exactly the same forms.
"""

from shellform.formfind import corner_network_for_inset, form_to_rise, square_network
from shellform.strategies import seismic_mid_surface

N_GRID = 41                     # pre-registration section 3 (41 x 41 network)
CORNER_EDGE_INSET_RATIO = 0.10  # decision D3-1 [J]


def form(case):
    """Return (network, gravity form, mid-surface) for one design case.

    Args:
        case: Dict with span_m, rise_ratio, supports, strategy and sa_g
            (shellform.design_space).

    Returns:
        (network, gravity form nodes (n*n, 3), mid-surface nodes (n*n, 3)) [m].
    """
    span, rise = case["span_m"], case["rise_ratio"] * case["span_m"]
    if case["supports"] == "corners":
        net, grav, _ = corner_network_for_inset(span, N_GRID, rise, CORNER_EDGE_INSET_RATIO)
    else:
        net = square_network(span, N_GRID, "edges")
        grav = form_to_rise(net, rise)
    mid = grav.copy() if case["strategy"] == "gravity" else seismic_mid_surface(grav, case["sa_g"], rise)
    return net, grav, mid
