"""
city_utils.py  –  blender city 05
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
    """Remove all mesh objects and the maquette material from the scene."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)
    # clean up old material so colour changes in config take effect on re-run
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

    # assign shared material
    mat = ensure_material()
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()

    return obj


# ── geometry ──────────────────────────────────────────────────────────────────

def world_top_z(obj):
    """
    World-space Z of the top face of a cube, using the object's actual Z scale.
    Cube local geometry spans -0.5 to +0.5 before scale.
    """
    return obj.location.z + abs(obj.scale[2]) * 0.5
