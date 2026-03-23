"""
city_utils.py  –  blender city 02
Low-level Blender helpers.
"""

import bpy
import math


def clear_scene():
    """Remove all mesh objects from the scene."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)


def add_cube(name, location=(0, 0, 0), scale=(1, 1, 1), rot_z_deg=0.0, parent=None):
    """
    Add a unit cube with the given world transform.
    Returns the new object.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler[2] = math.radians(rot_z_deg)

    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()

    return obj


def world_top_z(obj):
    """
    World-space Z of the top face of a cube.
    Cube local geometry spans -0.5 to +0.5 before scale.
    """
    return obj.location.z + abs(obj.scale[2]) * 0.5
