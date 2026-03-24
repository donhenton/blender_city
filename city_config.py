"""
city_config.py  –  blender city 11
Base parameters plus soft archetype overrides.
"""

# ── grid / layout ─────────────────────────────────────────────────────────────
GRID_ROWS    = 3
GRID_COLS    = 3
GRID_SPACING = 8.0

# ── base platform ─────────────────────────────────────────────────────────────
BASE_SIZE    = (2.2, 2.2, 0.25)

# ── recursion ─────────────────────────────────────────────────────────────────
MAX_DEPTH    = 2

# ── default (fallback) parameters ────────────────────────────────────────────
DEFAULTS = dict(
    l1_scale        = (1.0,  1.0,  1.0),
    l1_overlap      = 0.35,
    podium_scale    = (1.6, 1.6, 0.5),
    podium_overlap  = 0.40,
    antenna         = False,
    antenna_h_min   = 0.8,
    antenna_h_max   = 1.4,
    antenna_w       = 0.08,
    children_d1     = [1, 2, 2, 3, 3],
    children_d2     = [0, 1, 1, 2],
    scale_min       = 0.60,
    scale_max       = 0.70,
    overlap         = 0.40,
    xy_drift        = 0.25,
    rot_z_max       = 30.0,

    # ── shaft detail protrusions ──────────────────────────────────────────────
    # gate: set True on archetypes with a tall thin L1 shaft
    shaft_details           = False,
    # how many protrusions to add — pool to draw from
    shaft_detail_count      = [2, 2, 3, 4],
    # protrusion XY as fraction of L1's XY scale
    shaft_detail_xy_frac    = 0.50,
    # protrusion Z as fraction of its own XY size — keeps them flat
    shaft_detail_z_frac     = 0.25,
    # how far the protrusion overlaps into the shaft face (0-1)
    shaft_detail_overlap    = 0.38,
)

# ── archetypes ────────────────────────────────────────────────────────────────
ARCHETYPES = {

    "spire": dict(
        l1_scale     = (0.7, 0.7, 2.2),
        l1_overlap   = 0.25,
        podium_scale = (1.2, 1.2, 0.8),
        podium_overlap = 0.35,
        antenna      = True,
        antenna_h_min = 1.2,
        antenna_h_max = 2.0,
        children_d1  = [1, 2, 2, 3],
        children_d2  = [0, 0, 1],
        scale_min    = 0.50,
        scale_max    = 0.62,
        overlap      = 0.25,
        xy_drift     = 0.10,
        rot_z_max    = 15.0,
    ),

    "my_spire": dict(
        l1_scale     = (0.7, 0.7, 3.2),
        l1_overlap   = 0.25,
        podium_scale = (1.2, 1.2, 0.8),
        podium_overlap = 0.35,
        antenna      = False,
        antenna_h_min = 1.2,
        antenna_h_max = 2.0,
        children_d1  = [1, 2, 2, 3],
        children_d2  = [1, 1, 1],
        scale_min    = 0.20,
        scale_max    = 0.62,
        overlap      = 0.1,
        xy_drift     = 0.2,
        rot_z_max    = 15.0,

        # shaft detail overrides
        shaft_details        = True,
        shaft_detail_count   = [3, 4, 4, 5],
        shaft_detail_xy_frac = 0.70,
        shaft_detail_z_frac  = 0.65,
        shaft_detail_overlap = 0.38,
    ),

    "ziggurat": dict(
        l1_scale     = (1.6, 1.6, 0.5),
        l1_overlap   = 0.40,
        podium_scale = (2.0, 2.0, 0.35),
        podium_overlap = 0.45,
        antenna      = False,
        children_d1  = [2, 3, 3],
        children_d2  = [1, 2, 2],
        scale_min    = 0.64,
        scale_max    = 0.70,
        overlap      = 0.55,
        xy_drift     = 0.15,
        rot_z_max    = 20.0,
    ),

    "crown": dict(
        l1_scale     = (1.0, 1.0, 1.4),
        l1_overlap   = 0.30,
        podium_scale = (1.5, 1.5, 0.6),
        podium_overlap = 0.38,
        antenna      = True,
        antenna_h_min = 0.6,
        antenna_h_max = 1.0,
        children_d1  = [2, 3, 3],
        children_d2  = [0, 1, 1],
        scale_min    = 0.60,
        scale_max    = 0.68,
        overlap      = 0.35,
        xy_drift     = 0.50,
        rot_z_max    = 35.0,
    ),

    "slab": dict(
        l1_scale     = (2.0, 0.6, 1.2),
        l1_overlap   = 0.35,
        podium_scale = (2.1, 0.9, 0.45),
        podium_overlap = 0.40,
        antenna      = False,
        children_d1  = [1, 2, 2],
        children_d2  = [0, 1, 1],
        scale_min    = 0.58,
        scale_max    = 0.68,
        overlap      = 0.40,
        xy_drift     = 0.30,
        rot_z_max    = 25.0,
    ),

    "wild": dict(
        l1_scale     = (1.0, 1.0, 1.0),
        l1_overlap   = 0.30,
        podium_scale = (1.7, 1.7, 0.55),
        podium_overlap = 0.38,
        antenna      = True,
        antenna_h_min = 1.0,
        antenna_h_max = 2.4,
        children_d1  = [1, 2, 3, 3],
        children_d2  = [0, 1, 2, 2],
        scale_min    = 0.45,
        scale_max    = 0.75,
        overlap      = 0.45,
        xy_drift     = 0.60,
        rot_z_max    = 45.0,
    ),
}

# ── 9-slot archetype assignment ───────────────────────────────────────────────
SLOT_ARCHETYPES = [
    "spire",
    "ziggurat",
    "crown",
    "slab",
    "spire",
    "ziggurat",
    "crown",
    "slab",
    "wild",
]


def get_params(archetype_name):
    """Return a fully-resolved param dict for the given archetype."""
    overrides = ARCHETYPES.get(archetype_name, {})
    params    = dict(DEFAULTS)
    params.update(overrides)
    return params
