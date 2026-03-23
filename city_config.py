"""
city_config.py  –  blender city 06
Base parameters plus soft archetype overrides.
"""

# ── grid / layout ─────────────────────────────────────────────────────────────
GRID_ROWS    = 3
GRID_COLS    = 3
GRID_SPACING = 8.0        # world units between building centres

# ── base platform (half-extents for scale) ────────────────────────────────────
BASE_SIZE    = (2.2, 2.2, 0.25)

# ── recursion ─────────────────────────────────────────────────────────────────
MAX_DEPTH    = 2          # L2 and L3

# ── master seed ───────────────────────────────────────────────────────────────
BASE_SEED    = 42         # change for a completely different sheet

# ── default (fallback) parameters ────────────────────────────────────────────
# These are used if an archetype doesn't override them.
DEFAULTS = dict(
    # L1 shape  (x, y, z scale multipliers – applied to a unit cube)
    l1_scale        = (1.0,  1.0,  1.0),

    # L1 overlap into podium top
    l1_overlap      = 0.35,

    # podium: (x, y, z) scale tuple, sits between base and L1
    podium_scale    = (1.6, 1.6, 0.5),
    # podium overlap into base top
    podium_overlap  = 0.40,

    # antenna: True = add a thin spire to the highest node after recursion
    antenna         = False,
    # antenna height range (world units, seeded per building)
    antenna_h_min   = 0.8,
    antenna_h_max   = 1.4,
    # antenna width (uniform XY)
    antenna_w       = 0.08,

    # children per node at each depth
    children_d1     = [1, 2, 2, 3, 3],
    children_d2     = [0, 1, 1, 2],

    # scale factor range (child relative to parent)
    scale_min       = 0.60,
    scale_max       = 0.70,

    # overlap: fraction of child's Z half-height buried into parent top
    overlap         = 0.40,

    # XY drift (fraction of parent scale)
    xy_drift        = 0.25,

    # Z rotation max degrees
    rot_z_max       = 30.0,
)

# ── archetypes ────────────────────────────────────────────────────────────────
# Each entry overrides only the keys it cares about.
# Everything else falls back to DEFAULTS above.
ARCHETYPES = {

    "spire": dict(
        l1_scale     = (0.7, 0.7, 2.2),
        l1_overlap   = 0.25,
        podium_scale = (1.2, 1.2, 0.8),   # narrow tall podium
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

    "ziggurat": dict(
        l1_scale     = (1.6, 1.6, 0.5),
        l1_overlap   = 0.40,
        podium_scale = (2.0, 2.0, 0.35),  # wide flat podium
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
        podium_scale = (2.1, 0.9, 0.45),  # matches slab footprint
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
# Two of each main type, one wild. Order = left-to-right, bottom-to-top in grid.
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
    params = dict(DEFAULTS)
    params.update(overrides)
    return params
