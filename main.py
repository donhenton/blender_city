"""
main.py  –  blender city 07
Open in Blender's text editor, save the file, then press Run Script.
All modules must be in the same folder as this file.
"""

import bpy
import os
import sys

# ── path resolution ───────────────────────────────────────────────────────────
_dir = os.path.dirname(bpy.context.space_data.text.filepath)
if _dir not in sys.path:
    sys.path.append(_dir)

# ── local modules ─────────────────────────────────────────────────────────────
import importlib
import city_config   as cfg
import city_utils    as utils
import city_boolean  as booleans
import city_building as building
import city_grid     as grid

for mod in (cfg, utils, booleans, building, grid):
    importlib.reload(mod)

# ── run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    utils.clear_scene()
    grid.generate_city()
    print("blender city 07 – done.")
