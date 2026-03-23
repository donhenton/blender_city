"""
city_building.py  –  blender city 04

Fractal building generator driven by soft archetype parameters.

v04 change: children always intersect their parent by overlap_factor.
Child Z centre is placed so that (overlap * child_half_z) is buried
inside the parent. This eliminates all floating regardless of parent
scale uniformity — no matrix or world_top_z calculation needed.

Hierarchy
---------
  base  (platform)
   └─ L1  (shaped by archetype l1_scale, overlaps into base)
       ├─ L2a … L2n   (sparse, overlap into L1)
       │   └─ L3a …   (sparser, overlap into L2)
       ├─ L2b
       └─ …
"""

import bpy
import random
import city_config as cfg
import city_utils  as utils


# ─────────────────────────────────────────────────────────────────────────────

def _pick_children(pool, rng):
    return rng.choice(pool)


def _spawn_children(parent_obj, parent_scale, depth, rng, params, building_idx, node_path):
    """
    Recursively spawn children intersecting parent_obj.

    parent_scale : uniform float – drives XY drift and child shrinkage
    depth        : 1 = L2, 2 = L3
    params       : fully-resolved archetype param dict

    Z placement: child centre = parent centre + parent_half_z + child_half_z
                               - (overlap * child_half_z * 2)
    i.e. child rises above parent top by (1 - overlap) of its own height,
    with the overlap fraction buried inside. Simple, robust, no matrix needed.
    """
    if depth > cfg.MAX_DEPTH:
        return

    pool = params["children_d1"] if depth == 1 else params["children_d2"]
    n    = _pick_children(pool, rng)

    parent_half_z = parent_scale * 0.5

    for i in range(n):

        # ── scale ─────────────────────────────────────────────────────────────
        sf           = rng.uniform(params["scale_min"], params["scale_max"])
        child_scale  = parent_scale * sf
        child_half_z = child_scale * 0.5

        # ── overlap placement ─────────────────────────────────────────────────
        overlap   = params["overlap"]
        drift     = parent_scale * params["xy_drift"]
        dx        = rng.uniform(-drift, drift)
        dy        = rng.uniform(-drift, drift)

        # child centre: rise from parent centre to parent top, then overlap back
        child_cz = (parent_obj.location.z
                    + parent_half_z
                    + child_half_z
                    - (overlap * child_half_z * 2))

        loc = (
            parent_obj.location.x + dx,
            parent_obj.location.y + dy,
            child_cz,
        )

        # ── rotation ──────────────────────────────────────────────────────────
        rot_z = rng.uniform(-params["rot_z_max"], params["rot_z_max"])

        # ── name ──────────────────────────────────────────────────────────────
        label = f"B{building_idx:02d}_{node_path}_c{i}"

        child = utils.add_cube(
            name      = label,
            location  = loc,
            scale     = (child_scale, child_scale, child_scale),
            rot_z_deg = rot_z,
            parent    = parent_obj,
        )

        _spawn_children(
            parent_obj   = child,
            parent_scale = child_scale,
            depth        = depth + 1,
            rng          = rng,
            params       = params,
            building_idx = building_idx,
            node_path    = f"{node_path}_c{i}",
        )


# ─────────────────────────────────────────────────────────────────────────────

def generate_building(centre_x, centre_y, building_idx, archetype_name):
    """
    Build one fractal building centred at (centre_x, centre_y).
    Returns the base object.
    """
    params = cfg.get_params(archetype_name)
    seed   = cfg.BASE_SEED + building_idx * 97
    rng    = random.Random(seed)

    # ── base platform ─────────────────────────────────────────────────────────
    bx, by, bz = cfg.BASE_SIZE
    base_cz    = bz * 0.5
    base = utils.add_cube(
        name     = f"B{building_idx:02d}_{archetype_name}_base",
        location = (centre_x, centre_y, base_cz),
        scale    = cfg.BASE_SIZE,
    )

    # ── L1 – overlaps into base top ───────────────────────────────────────────
    lx, ly, lz = params["l1_scale"]
    l1_overlap = params["l1_overlap"]
    l1_half_z  = lz * 0.5
    base_top   = base_cz + bz * 0.5

    l1_cz  = base_top + l1_half_z - (l1_overlap * l1_half_z * 2)
    l1_rot = rng.uniform(-params["rot_z_max"] * 0.4, params["rot_z_max"] * 0.4)

    l1 = utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_L1",
        location  = (
            centre_x + rng.uniform(-0.15, 0.15),
            centre_y + rng.uniform(-0.15, 0.15),
            l1_cz,
        ),
        scale     = (lx, ly, lz),
        rot_z_deg = l1_rot,
        parent    = base,
    )

    # uniform scale passed to recursion: drives drift + shrinkage
    l1_uniform = (lx + ly + lz) / 3.0

    # ── L2 … L3 recursion ─────────────────────────────────────────────────────
    _spawn_children(
        parent_obj   = l1,
        parent_scale = l1_uniform,
        depth        = 1,
        rng          = rng,
        params       = params,
        building_idx = building_idx,
        node_path    = "L1",
    )

    return base
