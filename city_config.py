"""
city_config.py  –  blender city 03
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

    # children per node at each depth
    # depth 1 (L2): pool to draw from
    # depth 2 (L3): pool to draw from
    children_d1     = [1, 2, 2, 3, 3],
    children_d2     = [0, 1, 1, 2],

    # scale factor range (child relative to parent)
    scale_min       = 0.60,
    scale_max       = 0.70,

    # Z lift range (fraction of parent scale)
    z_lift_min      = 0.80,
    z_lift_max      = 1.10,

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
        children_d1 = [1, 2, 2, 3],
        children_d2 = [0, 0, 1],           # tapers to nothing fast
        scale_min   = 0.50,
        scale_max   = 0.62,
        z_lift_min  = 1.2,
        z_lift_max  = 1.6,
        xy_drift    = 0.10,
        rot_z_max   = 15.0,
    ),

    "ziggurat": dict(
        l1_scale    = (1.6, 1.6, 0.5),    # wide flat seed
        children_d1 = [2, 3, 3],
        children_d2 = [1, 2, 2],
        scale_min   = 0.64,
        scale_max   = 0.70,
        z_lift_min  = 0.5,
        z_lift_max  = 0.8,
        xy_drift    = 0.15,
        rot_z_max   = 20.0,
    ),

    "crown": dict(
        l1_scale    = (1.0, 1.0, 1.4),    # slightly tall seed
        children_d1 = [2, 3, 3],
        children_d2 = [0, 1, 1],
        scale_min   = 0.60,
        scale_max   = 0.68,
        z_lift_min  = 0.3,
        z_lift_max  = 0.6,                 # low lift = children splay out
        xy_drift    = 0.50,
        rot_z_max   = 35.0,
    ),

    "slab": dict(
        l1_scale    = (2.0, 0.6, 1.2),    # wide in X, thin in Y
        children_d1 = [1, 2, 2],
        children_d2 = [0, 1, 1],
        scale_min   = 0.58,
        scale_max   = 0.68,
        z_lift_min  = 0.8,
        z_lift_max  = 1.1,
        xy_drift    = 0.30,
        rot_z_max   = 25.0,
    ),

    "wild": dict(
        l1_scale    = (1.0, 1.0, 1.0),    # neutral seed – chaos does the rest
        children_d1 = [1, 2, 3, 3],
        children_d2 = [0, 1, 2, 2],
        scale_min   = 0.45,
        scale_max   = 0.75,
        z_lift_min  = 0.3,
        z_lift_max  = 1.8,
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
