import numpy as np
import swatch as sw

from typing import Tuple


render_dt = np.dtype([("ch", np.int32), ("fg", "3B"), ("bg", "3B")])

tile_dt = np.dtype(
    [
        ("walkable", bool),
        ("transparent", bool),
        ("dark", render_dt),
        ("light", render_dt),
    ]
)


def new_tile(
    *,
    walkable: int,
    transparent: int,
    dark=Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light=Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=render_dt)

TILE_WALL = new_tile(
    transparent=False,
    walkable=False,
    light=(ord("#"), sw.STONE, sw.BLACK),
    dark=(ord("#"), sw.STONE_DARKER, sw.BLACK),
)

TILE_FLOOR = new_tile(
    transparent=True,
    walkable=True,
    light=(ord("."), sw.STONE_LIGHT, sw.BLACK),
    dark=(ord("."), sw.STONE_DARK, sw.BLACK),
)
