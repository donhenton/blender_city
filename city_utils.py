"""
city_utils.py  –  blender city 06
Low-level Blender helpers.
"""

import bpy
import math
import mathutils

# ── material ──────────────────────────────────────────────────────────────────
_MAT_NAME  = "maquette_blue"
_MAT_COLOR = (0.25, 0.55, 0.92, 1.0)   # light blue RGBA

def mark_freestyle_edges(obj):
    """Mark all edges on obj for freestyle rendering."""
    for edge in obj.data.edges:
        edge.use_freestyle_mark = True

def set_origin_to_base(obj):
    """
    Set object origin to the centre of the lowest face (base of pedestal).
    """
    bbox_world = [obj.matrix_world @ mathutils.Vector(corner)
                  for corner in obj.bound_box]
    min_z = min(v.z for v in bbox_world)

    origin = mathutils.Vector((
        obj.location.x,
        obj.location.y,
        min_z,
    ))

    # translate the mesh data by the inverse offset
    offset = obj.matrix_world.inverted() @ origin
    obj.data.transform(mathutils.Matrix.Translation(-offset))
    obj.location = origin

def join_building(building_idx, archetype_name):
    """
    Join all mesh objects belonging to this building into one object.
    Returns the joined object or None if no members found.
    """
    prefix  = f"B{building_idx:02d}_"
    members = [o for o in bpy.data.objects
               if o.name.startswith(prefix) and o.type == "MESH"]

    if not members:
        return None

    bpy.ops.object.select_all(action="DESELECT")
    for obj in members:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = members[0]

    bpy.ops.object.join()

    joined      = bpy.context.active_object
    joined.name = f"B{building_idx:02d}_{archetype_name}"

    with bpy.context.temp_override(
        active_object    = joined,
        object           = joined,
        selected_objects = [joined],
    ):
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True
        )

    return joined

def ensure_material():
    """
    Return the shared maquette material, creating it once if needed.
    Uses nodes / principled BSDF so it responds to Blender lighting.
    """
    mat = bpy.data.materials.get(_MAT_NAME)
    if mat is None:
        mat = bpy.data.materials.new(name=_MAT_NAME)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = _MAT_COLOR
            bsdf.inputs["Roughness"].default_value  = 0.4
            bsdf.inputs["Specular IOR Level"].default_value = 0.3
    return mat


# ── scene ─────────────────────────────────────────────────────────────────────

def clear_scene():
    """Remove all mesh objects, text objects, and the maquette material."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.data.objects):
        if obj.type in ("MESH", "FONT"):
            bpy.data.objects.remove(obj, do_unlink=True)
    old = bpy.data.materials.get(_MAT_NAME)
    if old:
        bpy.data.materials.remove(old)


# ── cube ──────────────────────────────────────────────────────────────────────

def add_cube(name, location=(0, 0, 0), scale=(1, 1, 1), rot_z_deg=0.0, parent=None):
    """
    Add a unit cube with the given world transform and assign the shared material.
    Returns the new object.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler[2] = math.radians(rot_z_deg)

    mat = ensure_material()
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
        
    mark_freestyle_edges(obj)
    return obj


# ── label ─────────────────────────────────────────────────────────────────────

def add_label(text, centre_x, centre_y, building_idx):
    """
    Place a centred text object just below the base of a building.

    Displays archetype name and building index, e.g. "spire · B03".
    No material assigned — renders in default grey, reads clearly.
    Faces the default Y-forward direction (visible from front/perspective).
    """
    import city_config as cfg

    label_text = f"{text}  ·  B{building_idx:02d}"
    y_offset   = -(cfg.BASE_SIZE[1] * 0.5 + 0.6)   # just south of the base

    bpy.ops.object.text_add(location=(centre_x, centre_y + y_offset, 0.0))
    obj      = bpy.context.active_object
    obj.name = f"B{building_idx:02d}_label"

    td = obj.data
    td.body        = label_text
    td.align_x     = "CENTER"
    td.size        = 0.45
    td.extrude     = 0.04    # slight depth so it catches light
    td.bevel_depth = 0.01    # softens the edges a touch

    return obj


# ── geometry ──────────────────────────────────────────────────────────────────

def world_top_z(obj):
    """
    World-space Z of the top face of a cube, using the object's actual Z scale.
    Cube local geometry spans -0.5 to +0.5 before scale.
    """
    return obj.location.z + abs(obj.scale[2]) * 0.5
