"""
city_utils.py  –  blender city 07
Low-level Blender helpers.
"""

import bpy
import math

# ── material ──────────────────────────────────────────────────────────────────
_MAT_NAME  = "maquette_blue"
_MAT_COLOR = (0.55, 0.75, 0.92, 1.0)   # light blue RGBA


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
