"""
city_building.py  –  blender city 06

v05 additions:
  - podium  : a shaped cube between base and L1, grounding each building
  - antenna : thin vertical spire placed on the highest node post-recursion

Hierarchy
---------
  base
   └─ podium  (overlaps into base)
       └─ L1  (overlaps into podium, shaped by archetype)
           ├─ L2a … L2n
           │   └─ L3a …
           └─ …
  antenna     (parented to highest node, overlaps slightly)
"""

import bpy
import random
import city_config as cfg
import city_utils  as utils


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pick_children(pool, rng):
    return rng.choice(pool)


def _overlap_z(parent_cz, parent_half_z, child_half_z, overlap):
    """
    Return child centre Z so it intersects parent by the overlap fraction
    of its own half-height.
    """
    return parent_cz + parent_half_z + child_half_z - (overlap * child_half_z * 2)


# ─────────────────────────────────────────────────────────────────────────────
# recursion
# ─────────────────────────────────────────────────────────────────────────────

def _spawn_children(parent_obj, parent_scale, depth, rng, params, building_idx, node_path):
    """
    Recursively spawn children intersecting parent_obj.
    parent_scale drives XY drift and child shrinkage (uniform float).
    Z placement always uses _overlap_z on parent's local centre.
    """
    if depth > cfg.MAX_DEPTH:
        return

    pool = params["children_d1"] if depth == 1 else params["children_d2"]
    n    = _pick_children(pool, rng)

    parent_half_z = parent_scale * 0.5

    for i in range(n):

        sf           = rng.uniform(params["scale_min"], params["scale_max"])
        child_scale  = parent_scale * sf
        child_half_z = child_scale * 0.5

        drift = parent_scale * params["xy_drift"]
        dx    = rng.uniform(-drift, drift)
        dy    = rng.uniform(-drift, drift)

        child_cz = _overlap_z(
            parent_obj.location.z, parent_half_z, child_half_z, params["overlap"]
        )

        rot_z = rng.uniform(-params["rot_z_max"], params["rot_z_max"])
        label = f"B{building_idx:02d}_{node_path}_c{i}"

        child = utils.add_cube(
            name      = label,
            location  = (parent_obj.location.x + dx,
                         parent_obj.location.y + dy,
                         child_cz),
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
# antenna
# ─────────────────────────────────────────────────────────────────────────────

def _add_antenna(building_idx, archetype_name, rng, params):
    """
    Find the highest object belonging to this building and place a thin
    vertical antenna on top of it, overlapping slightly.
    """
    prefix  = f"B{building_idx:02d}_"
    members = [o for o in bpy.data.objects
               if o.name.startswith(prefix) and "base" not in o.name]

    if not members:
        return

    # highest by location.z (good enough – avoids matrix complexity)
    highest = max(members, key=lambda o: o.location.z)

    h          = rng.uniform(params["antenna_h_min"], params["antenna_h_max"])
    w          = params["antenna_w"]
    half_h     = h * 0.5
    # small fixed overlap into the host node
    antenna_overlap = 0.20
    host_half_z = highest.scale[2] * 0.5

    antenna_cz = _overlap_z(
        highest.location.z, host_half_z, half_h, antenna_overlap
    )

    utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_antenna",
        location  = (highest.location.x,
                     highest.location.y,
                     antenna_cz),
        scale     = (w, w, h),
        rot_z_deg = 0.0,
        parent    = highest,
    )


# ─────────────────────────────────────────────────────────────────────────────
# main entry
# ─────────────────────────────────────────────────────────────────────────────

def generate_building(centre_x, centre_y, building_idx, archetype_name,run_seed):
    """
    Build one fractal building centred at (centre_x, centre_y).
    Returns the base object.
    """
    params = cfg.get_params(archetype_name)
    seed   = run_seed + building_idx * 97
    rng    = random.Random(seed)

    # ── base ──────────────────────────────────────────────────────────────────
    bx, by, bz = cfg.BASE_SIZE
    base_cz    = bz * 0.5
    base = utils.add_cube(
        name     = f"B{building_idx:02d}_{archetype_name}_base",
        location = (centre_x, centre_y, base_cz),
        scale    = cfg.BASE_SIZE,
    )

    # ── podium – overlaps into base ───────────────────────────────────────────
    px, py, pz  = params["podium_scale"]
    pod_half_z  = pz * 0.5
    pod_cz      = _overlap_z(base_cz, bz * 0.5, pod_half_z, params["podium_overlap"])

    podium = utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_podium",
        location  = (centre_x, centre_y, pod_cz),
        scale     = (px, py, pz),
        rot_z_deg = 0.0,
        parent    = base,
    )

    # ── L1 – overlaps into podium ─────────────────────────────────────────────
    lx, ly, lz  = params["l1_scale"]
    l1_half_z   = lz * 0.5
    l1_cz       = _overlap_z(pod_cz, pod_half_z, l1_half_z, params["l1_overlap"])
    l1_rot      = rng.uniform(-params["rot_z_max"] * 0.4, params["rot_z_max"] * 0.4)

    l1 = utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_L1",
        location  = (centre_x + rng.uniform(-0.15, 0.15),
                     centre_y + rng.uniform(-0.15, 0.15),
                     l1_cz),
        scale     = (lx, ly, lz),
        rot_z_deg = l1_rot,
        parent    = podium,
    )

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

    # ── antenna (optional, post-recursion) ────────────────────────────────────
    if params["antenna"]:
        _add_antenna(building_idx, archetype_name, rng, params)

    joined = utils.join_building(building_idx, archetype_name)
    if joined:
        utils.set_origin_to_base(joined)
        return joined
    return base
