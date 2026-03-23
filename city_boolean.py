"""
city_boolean.py  –  blender city 07

Post-pass: bore random cylinder cutouts through building meshes.
Called once per building after all geometry (including antenna) is placed.
Remove the call in city_building.py to pull this feature entirely.

Strategy
--------
- Collect all MESH objects belonging to this building (by name prefix)
- Skip the antenna (too thin to cut usefully)
- For each cut: pick a random target, place a cylinder through it at a
  random angle, apply boolean difference, delete cutter
- Cylinder has 12 sides for clean geometry and lighter mesh
- Radius is a fraction of the target's smallest scale dimension
- Angle is random within cut_angle_max degrees of a random base axis
"""

import bpy
import math
import random
import city_config as cfg


# ── helpers ───────────────────────────────────────────────────────────────────

def _smallest_scale(obj):
    return min(abs(s) for s in obj.scale)


def _random_euler(rng, angle_max_deg):
    """
    Return a random Euler rotation within angle_max_deg of a randomly
    chosen world axis (X, Y, or Z). Gives varied but not purely wild angles.
    """
    base_axis = rng.choice(["X", "Y", "Z"])
    dev       = math.radians(rng.uniform(-angle_max_deg, angle_max_deg))

    if base_axis == "X":
        return (math.pi * 0.5 + dev,
                rng.uniform(0, math.tau),
                rng.uniform(0, math.tau))
    elif base_axis == "Y":
        return (rng.uniform(0, math.tau),
                math.pi * 0.5 + dev,
                rng.uniform(0, math.tau))
    else:
        return (rng.uniform(0, math.tau),
                rng.uniform(0, math.tau),
                dev)


def _make_cutter(location, rotation_euler, radius, depth, name):
    """Add a cylinder cutter and return the object."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices      = 12,
        radius        = radius,
        depth         = depth,
        location      = location,
        rotation      = rotation_euler,
    )
    obj      = bpy.context.active_object
    obj.name = name
    return obj


def _apply_boolean(target, cutter):
    """
    Add a boolean difference modifier to target using cutter,
    apply it immediately, then delete the cutter.
    """
    # make target active
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = target
    target.select_set(True)

    mod        = target.modifiers.new(name="bool_cut", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object    = cutter

    # hide cutter from boolean before applying
    cutter.hide_viewport = False

    bpy.ops.object.modifier_apply(modifier=mod.name)

    # delete cutter
    bpy.ops.object.select_all(action="DESELECT")
    cutter.select_set(True)
    bpy.ops.object.delete()


# ── main entry ────────────────────────────────────────────────────────────────

def apply_boolean_cuts(building_idx, archetype_name, rng, params):
    """
    Bore random cylinder cutouts through meshes of this building.

    building_idx   : used to filter objects by name prefix
    archetype_name : for cutter naming only
    rng            : seeded random instance (reproducible)
    params         : fully-resolved archetype param dict
    """
    prefix = f"B{building_idx:02d}_"

    # collect targets – mesh objects belonging to this building,
    # excluding antenna (too thin) and label text objects
    targets = [
        o for o in bpy.data.objects
        if (o.name.startswith(prefix)
            and o.type == "MESH"
            and "antenna" not in o.name)
    ]

    if not targets:
        return

    n_cuts         = rng.choice(params["cut_count_pool"])
    radius_frac    = params["cut_radius_frac"]
    angle_max      = params["cut_angle_max"]

    for i in range(n_cuts):
        target = rng.choice(targets)
        radius = _smallest_scale(target) * radius_frac

        # cutter depth: long enough to always pass fully through the target
        depth  = max(abs(s) for s in target.scale) * 3.0

        # position: random point near target centre with small XY scatter
        scatter = _smallest_scale(target) * 0.3
        loc = (
            target.location.x + rng.uniform(-scatter, scatter),
            target.location.y + rng.uniform(-scatter, scatter),
            target.location.z + rng.uniform(-scatter, scatter),
        )

        rot    = _random_euler(rng, angle_max)
        cname  = f"B{building_idx:02d}_cutter_{i}"
        cutter = _make_cutter(loc, rot, radius, depth, cname)

        try:
            _apply_boolean(target, cutter)
        except Exception as e:
            # boolean failed – clean up cutter and continue
            print(f"  boolean cut {i} on {target.name} failed: {e}")
            bpy.ops.object.select_all(action="DESELECT")
            if cutter.name in bpy.data.objects:
                cutter.select_set(True)
                bpy.ops.object.delete()
