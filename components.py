from dataclasses import dataclass
from typing import Tuple
from geom import Point
from gamemap import GameMap


@dataclass
class Renderable:
    ch: int
    fg: Tuple[int, int, int]


# Global Resources
SaveFile = ("save_file", str)
GameVersion = ("version", str)

# Named components
Location = ("location", Point)
Name = ("name", str)
Description = ("desc", str)
GameMapComp = ("game_map", GameMap)
MapId = ("map_id", str)
