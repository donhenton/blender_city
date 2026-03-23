"""
city_config.py  –  blender city 04
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

    # L1 overlap into base: fraction of L1's Z half-height buried in base top
    l1_overlap      = 0.35,

    # children per node at each depth
    children_d1     = [1, 2, 2, 3, 3],
    children_d2     = [0, 1, 1, 2],

    # scale factor range (child relative to parent)
    scale_min       = 0.60,
    scale_max       = 0.70,

    # overlap: fraction of child's Z half-height buried into parent top
    # 0.0 = sits exactly on top,  0.5 = half buried,  1.0 = fully inside
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
        l1_scale    = (0.7, 0.7, 2.2),    # tall thin seed
        l1_overlap  = 0.25,
        children_d1 = [1, 2, 2, 3],
        children_d2 = [0, 0, 1],
        scale_min   = 0.50,
        scale_max   = 0.62,
        overlap     = 0.25,               # less buried – children read distinct
        xy_drift    = 0.10,
        rot_z_max   = 15.0,
    ),

    "ziggurat": dict(
        l1_scale    = (1.6, 1.6, 0.5),    # wide flat seed
        l1_overlap  = 0.40,
        children_d1 = [2, 3, 3],
        children_d2 = [1, 2, 2],
        scale_min   = 0.64,
        scale_max   = 0.70,
        overlap     = 0.55,               # deep overlap – layered slab feel
        xy_drift    = 0.15,
        rot_z_max   = 20.0,
    ),

    "crown": dict(
        l1_scale    = (1.0, 1.0, 1.4),
        l1_overlap  = 0.30,
        children_d1 = [2, 3, 3],
        children_d2 = [0, 1, 1],
        scale_min   = 0.60,
        scale_max   = 0.68,
        overlap     = 0.35,
        xy_drift    = 0.50,
        rot_z_max   = 35.0,
    ),

    "slab": dict(
        l1_scale    = (2.0, 0.6, 1.2),    # wide in X, thin in Y
        l1_overlap  = 0.35,
        children_d1 = [1, 2, 2],
        children_d2 = [0, 1, 1],
        scale_min   = 0.58,
        scale_max   = 0.68,
        overlap     = 0.40,
        xy_drift    = 0.30,
        rot_z_max   = 25.0,
    ),

    "wild": dict(
        l1_scale    = (1.0, 1.0, 1.0),
        l1_overlap  = 0.30,
        children_d1 = [1, 2, 3, 3],
        children_d2 = [0, 1, 2, 2],
        scale_min   = 0.45,
        scale_max   = 0.75,
        overlap     = 0.45,
        xy_drift    = 0.60,
        rot_z_max   = 45.0,
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
