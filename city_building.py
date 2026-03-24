"""
city_building.py  –  blender city 11

v10 addition:
  - shaft detail protrusions: small flat cubes extruding from L1 faces
    at upper and mid zones, breaking the blank shaft silhouette.
    Gated by shaft_details param — only active on archetypes that need it.

Hierarchy (pre-join)
--------------------
  base
   └─ podium
       └─ L1  (+optional shaft detail protrusions on faces)
           ├─ L2a … L2n
           │   └─ L3a …
           └─ …
  antenna  (optional)
"""

import bpy
import math
import random
import city_config as cfg
import city_utils  as utils


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pick_children(pool, rng):
    return rng.choice(pool)


def _overlap_z(parent_cz, parent_half_z, child_half_z, overlap):
    return parent_cz + parent_half_z + child_half_z - (overlap * child_half_z * 2)


# ─────────────────────────────────────────────────────────────────────────────
# recursion
# ─────────────────────────────────────────────────────────────────────────────

def _spawn_children(parent_obj, parent_scale, depth, rng, params, building_idx, node_path):
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
# shaft detail protrusions
# ─────────────────────────────────────────────────────────────────────────────

def _add_shaft_details(l1, building_idx, archetype_name, rng, params):
    """
    Add small flat cubes extruding from L1 shaft faces to break the silhouette.

    Protrusions are placed in two height zones:
      upper: 60-85% of shaft height  (just below crown mass)
      mid:   30-55% of shaft height  (equipment level)

    Each protrusion overlaps into a random ±X or ±Y face.
    """
    lx, ly, lz = params["l1_scale"]
    l1_cz      = l1.location.z
    l1_half_z  = lz * 0.5
    l1_bottom  = l1_cz - l1_half_z
    l1_height  = lz

    xy_frac    = params["shaft_detail_xy_frac"]
    z_frac     = params["shaft_detail_z_frac"]
    overlap    = params["shaft_detail_overlap"]
    count      = rng.choice(params["shaft_detail_count"])

    # height zones as fractions of shaft
    zones = [
        (0.60, 0.85),   # upper
        (0.30, 0.55),   # mid
    ]

    # available faces as (axis, sign, shaft_half_extent, protrusion_depth)
    # sign +1 or -1 determines which side of shaft
    faces = [
        ("x", +1, lx * 0.5),
        ("x", -1, lx * 0.5),
        ("y", +1, ly * 0.5),
        ("y", -1, ly * 0.5),
    ]

    used_faces = []

    for i in range(count):
        # pick zone, then random height within it
        zone      = rng.choice(zones)
        z_frac_pos = rng.uniform(zone[0], zone[1])
        prot_z    = l1_bottom + l1_height * z_frac_pos

        # pick a face not already used at this approximate height
        available = [f for f in faces if f not in used_faces]
        if not available:
            used_faces = []
            available  = faces
        face = rng.choice(available)
        used_faces.append(face)

        axis, sign, shaft_half = face

        # protrusion dimensions — flat relative to XY
        p_xy = min(lx, ly) * xy_frac
        p_z  = p_xy * z_frac

        # depth of protrusion beyond shaft face
        p_depth = p_xy * 0.8

        # protrusion centre: shaft face + (depth/2) - overlap
        face_pos     = shaft_half
        prot_half_d  = p_depth * 0.5
        overlap_dist = overlap * p_depth

        if axis == "x":
            px = l1.location.x + sign * (face_pos + prot_half_d - overlap_dist)
            py = l1.location.y + rng.uniform(-ly * 0.15, ly * 0.15)
        else:
            px = l1.location.x + rng.uniform(-lx * 0.15, lx * 0.15)
            py = l1.location.y + sign * (face_pos + prot_half_d - overlap_dist)

        label = f"B{building_idx:02d}_shaft_d{i}"

        utils.add_cube(
            name      = label,
            location  = (px, py, prot_z),
            scale     = (p_xy if axis == "y" else p_depth,
                         p_xy if axis == "x" else p_depth,
                         p_z),
            rot_z_deg = rng.uniform(-8.0, 8.0),   # slight rotation for life
            parent    = l1,
        )


# ─────────────────────────────────────────────────────────────────────────────
# antenna
# ─────────────────────────────────────────────────────────────────────────────

def _add_antenna(building_idx, archetype_name, rng, params):
    prefix  = f"B{building_idx:02d}_"
    members = [o for o in bpy.data.objects
               if o.name.startswith(prefix) and "base" not in o.name]

    if not members:
        return

    highest     = max(members, key=lambda o: o.location.z)
    h           = rng.uniform(params["antenna_h_min"], params["antenna_h_max"])
    w           = params["antenna_w"]
    half_h      = h * 0.5
    host_half_z = highest.scale[2] * 0.5

    antenna_cz = _overlap_z(highest.location.z, host_half_z, half_h, 0.20)

    utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_antenna",
        location  = (highest.location.x, highest.location.y, antenna_cz),
        scale     = (w, w, h),
        rot_z_deg = 0.0,
        parent    = highest,
    )


# ─────────────────────────────────────────────────────────────────────────────
# main entry
# ─────────────────────────────────────────────────────────────────────────────

def generate_building(centre_x, centre_y, building_idx, archetype_name, run_seed):
    """
    Build one fractal building centred at (centre_x, centre_y).
    Returns the joined single-mesh object.
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

    # ── podium ────────────────────────────────────────────────────────────────
    px, py, pz = params["podium_scale"]
    pod_half_z = pz * 0.5
    pod_cz     = _overlap_z(base_cz, bz * 0.5, pod_half_z, params["podium_overlap"])

    podium = utils.add_cube(
        name      = f"B{building_idx:02d}_{archetype_name}_podium",
        location  = (centre_x, centre_y, pod_cz),
        scale     = (px, py, pz),
        rot_z_deg = 0.0,
        parent    = base,
    )

    # ── L1 ────────────────────────────────────────────────────────────────────
    lx, ly, lz = params["l1_scale"]
    l1_half_z  = lz * 0.5
    l1_cz      = _overlap_z(pod_cz, pod_half_z, l1_half_z, params["l1_overlap"])
    l1_rot     = rng.uniform(-params["rot_z_max"] * 0.4, params["rot_z_max"] * 0.4)

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

    # ── shaft detail protrusions (before recursion so they're mid-stack) ──────
    if params["shaft_details"]:
        _add_shaft_details(l1, building_idx, archetype_name, rng, params)

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

    # ── antenna ───────────────────────────────────────────────────────────────
    if params["antenna"]:
        _add_antenna(building_idx, archetype_name, rng, params)

    # ── join and set origin ───────────────────────────────────────────────────
    joined = utils.join_building(building_idx, archetype_name)
    if joined:
        utils.set_origin_to_base(joined)
        return joined

    return base
