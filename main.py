"""
main.py  –  blender city 11
Open in Blender's text editor, save the file, then press Run Script.
All modules must be in the same folder as this file.
"""
import bpy
import os
import sys
import random
import time

# ── path resolution ───────────────────────────────────────────────────────────
_dir = os.path.dirname(bpy.context.space_data.text.filepath)
if _dir not in sys.path:
    sys.path.append(_dir)

# ── local modules ─────────────────────────────────────────────────────────────
import importlib
import city_config   as cfg
import city_utils    as utils
import city_building as building
import city_grid     as grid

for mod in (cfg, utils, building, grid):
    importlib.reload(mod)

# ── run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    utils.clear_scene()
    run_seed = int(time.time())
    print(f"blender city 11 – run seed: {run_seed}")
    #grid.generate_city(run_seed)
    grid.generate_individual_groups("my_spire")
    print("blender city 11 – done.")
