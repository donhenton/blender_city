"""
city_grid.py  –  blender city 05
Stamps 9 buildings across a 3x3 grid, one archetype per slot.
"""

import city_config   as cfg
import city_building as building


def generate_city():
    """Generate GRID_ROWS × GRID_COLS archetype buildings."""
    idx = 0
    for row in range(cfg.GRID_ROWS):
        for col in range(cfg.GRID_COLS):
            cx         = col * cfg.GRID_SPACING
            cy         = row * cfg.GRID_SPACING
            archetype  = cfg.SLOT_ARCHETYPES[idx]
            building.generate_building(cx, cy, idx, archetype)
            print(f"  [{idx+1}/9] {archetype} at ({cx:.1f}, {cy:.1f})")
            idx += 1

    print(f"Done – {idx} buildings placed.")
