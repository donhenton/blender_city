"""
city_building.py  –  blender city 02

Fractal building generator driven by soft archetype parameters.

Hierarchy
---------
  base  (platform)
   └─ L1  (shaped by archetype l1_scale)
       ├─ L2a … L2n   (sparse, archetype-biased)
       │   └─ L3a …   (sparser still)
       ├─ L2b
       └─ …
"""

import random
import math
import city_config as cfg
import city_utils  as utils


# ─────────────────────────────────────────────────────────────────────────────

def _pick_children(pool, rng):
    return rng.choice(pool)


def _spawn_children(parent_obj, parent_scale, depth, rng, params, building_idx, node_path):
    """
    Recursively spawn children on top of parent_obj.

    parent_scale : uniform float – effective world scale of the parent cube
    depth        : 1 = L2, 2 = L3
    params       : fully-resolved archetype param dict
    """
    if depth > cfg.MAX_DEPTH:
        return

    pool = params["children_d1"] if depth == 1 else params["children_d2"]
    n    = _pick_children(pool, rng)

    for i in range(n):

        # ── scale ─────────────────────────────────────────────────────────────
        sf          = rng.uniform(params["scale_min"], params["scale_max"])
        child_scale = parent_scale * sf
        s           = (child_scale, child_scale, child_scale)

        # ── position ──────────────────────────────────────────────────────────
        drift = parent_scale * params["xy_drift"]
        dx    = rng.uniform(-drift, drift)
        dy    = rng.uniform(-drift, drift)

        top_z  = utils.world_top_z(parent_obj)
        z_lift = rng.uniform(params["z_lift_min"], params["z_lift_max"]) * parent_scale
        loc    = (
            parent_obj.location.x + dx,
            parent_obj.location.y + dy,
            top_z + child_scale * 0.5 + z_lift * 0.12,
        )

        # ── rotation ──────────────────────────────────────────────────────────
        rot_z = rng.uniform(-params["rot_z_max"], params["rot_z_max"])

        # ── name ──────────────────────────────────────────────────────────────
        label = f"B{building_idx:02d}_{node_path}_c{i}"

        child = utils.add_cube(
            name      = label,
            location  = loc,
            scale     = s,
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

    archetype_name : key into city_config.ARCHETYPES
    Returns the base object.
    """
    params = cfg.get_params(archetype_name)

    # per-building reproducible seed
    seed = cfg.BASE_SEED + building_idx * 97
    rng  = random.Random(seed)

    # ── base platform ─────────────────────────────────────────────────────────
    bx, by, bz = cfg.BASE_SIZE
    base = utils.add_cube(
        name     = f"B{building_idx:02d}_{archetype_name}_base",
        location = (centre_x, centre_y, bz * 0.5),
        scale    = cfg.BASE_SIZE,
    )

    # ── L1 – archetype shapes the seed cube ───────────────────────────────────
    lx, ly, lz = params["l1_scale"]
    top_of_base = utils.world_top_z(base)

    # effective uniform scale for recursion is the average of l1 dims
    l1_uniform = (lx + ly + lz) / 3.0

    l1_loc = (
        centre_x + rng.uniform(-0.15, 0.15),
        centre_y + rng.uniform(-0.15, 0.15),
        top_of_base + lz * 0.5 + 0.05,
    )
    l1_rot = rng.uniform(-params["rot_z_max"] * 0.4, params["rot_z_max"] * 0.4)

    l1 = utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_L1",
        location  = l1_loc,
        scale     = (lx, ly, lz),
        rot_z_deg = l1_rot,
        parent    = base,
    )

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
