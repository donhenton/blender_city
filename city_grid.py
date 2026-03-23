"""
city_grid.py  –  blender city 07 radar
Stamps 9 buildings across a 3x3 grid, one archetype per slot.
"""

import city_config   as cfg
import city_building as building
import city_utils    as utils


def generate_city(run_seed):
    """Generate GRID_ROWS x GRID_COLS archetype buildings with labels."""
    idx = 0
    for row in range(cfg.GRID_ROWS):
        for col in range(cfg.GRID_COLS):
            cx        = col * cfg.GRID_SPACING
            cy        = row * cfg.GRID_SPACING
            archetype = cfg.SLOT_ARCHETYPES[idx]
            building.generate_building(cx, cy, idx, archetype, run_seed)
            utils.add_label(archetype, cx, cy, idx)
            print(f"  [{idx+1}/9] {archetype} at ({cx:.1f}, {cy:.1f})")
            idx += 1

    print(f"Done – {idx} buildings placed.")
