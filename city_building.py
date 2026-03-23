"""
city_building.py  –  blender city 07 radar

v07 additions:
  - run_seed passed in for per-run variation
  - radar dish: occasional tilted dish bolted onto an upper node
  - join_building: all meshes fused into one object post-generation
  - set_origin_to_base: origin placed at lowest face centre

Hierarchy (pre-join)
--------------------
  base
   └─ podium
       └─ L1
           ├─ L2a … L2n
           │   └─ L3a …
           └─ …
  antenna     (optional)
  dish stem   (optional, parented to chosen node)
   └─ dish bowl
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
# radar dish
# ─────────────────────────────────────────────────────────────────────────────

def _add_dish(building_idx, archetype_name, rng, params):
    """
    Occasionally bolt a radar dish onto an upper node.
    The dish is a cone (bowl) on a thin cylinder stem, tilted 30-45 degrees.
    Parented to its host node so it gets baked into the join.
    """
    # 45% chance (or archetype override) — bail out early if not this time
    if rng.random() > params["dish_probability"]:
        return

    # collect candidate nodes — mesh objects excluding base, podium, antenna
    prefix     = f"B{building_idx:02d}_"
    candidates = [
        o for o in bpy.data.objects
        if (o.name.startswith(prefix)
            and o.type == "MESH"
            and not any(x in o.name for x in ("base", "podium", "antenna")))
    ]

    if not candidates:
        return

    # prefer upper nodes — sort by Z, pick from top half
    candidates.sort(key=lambda o: o.location.z)
    top_half = candidates[len(candidates) // 2:]
    host     = rng.choice(top_half)

    host_scale  = min(abs(s) for s in host.scale)
    host_half_z = host.scale[2] * 0.5

    # ── stem ──────────────────────────────────────────────────────────────────
    sw      = params["dish_stem_w"]
    sh      = params["dish_stem_h"]
    stem_cz = _overlap_z(host.location.z, host_half_z, sh * 0.5, 0.15)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices = 12,
        radius   = sw * 0.5,
        depth    = sh,
        location = (host.location.x, host.location.y, stem_cz),
    )
    stem      = bpy.context.active_object
    stem.name = f"B{building_idx:02d}_{archetype_name}_dish_stem"

    mat = utils.ensure_material()
    if stem.data.materials:
        stem.data.materials[0] = mat
    else:
        stem.data.materials.append(mat)
    utils.mark_freestyle_edges(stem)

    stem.parent = host
    stem.matrix_parent_inverse = host.matrix_world.inverted()

    # ── bowl (cone open upward) ────────────────────────────────────────────────
    radius    = host_scale * params["dish_radius_frac"]
    depth     = params["dish_depth"]
    bowl_cz   = stem_cz + sh * 0.5 + depth * 0.5 - (depth * 0.1)

    bpy.ops.mesh.primitive_cone_add(
        vertices    = 24,
        radius1     = radius,   # open end
        radius2     = radius * 0.08,  # near-point at back
        depth       = depth,
        location    = (host.location.x, host.location.y, bowl_cz),
        rotation    = (math.pi, 0, 0),   # flip so open end faces up
    )
    bowl      = bpy.context.active_object
    bowl.name = f"B{building_idx:02d}_{archetype_name}_dish_bowl"

    if bowl.data.materials:
        bowl.data.materials[0] = mat
    else:
        bowl.data.materials.append(mat)
    utils.mark_freestyle_edges(bowl)

    bowl.parent = stem
    bowl.matrix_parent_inverse = stem.matrix_world.inverted()

    # ── tilt the stem (bowl follows as child) ─────────────────────────────────
    tilt_deg  = rng.uniform(params["dish_tilt_min"], params["dish_tilt_max"])
    tilt_axis = rng.uniform(0, math.tau)   # random compass direction for tilt

    stem.rotation_euler[0] = math.radians(tilt_deg) * math.cos(tilt_axis)
    stem.rotation_euler[1] = math.radians(tilt_deg) * math.sin(tilt_axis)
    stem.rotation_euler[2] = rng.uniform(0, math.tau)


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

    # ── radar dish ────────────────────────────────────────────────────────────
    _add_dish(building_idx, archetype_name, rng, params)

    # ── join all meshes into one, set origin to base ───────────────────────────
    joined = utils.join_building(building_idx, archetype_name)
    if joined:
        utils.set_origin_to_base(joined)
        return joined

    return base
