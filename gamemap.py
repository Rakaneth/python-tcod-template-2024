import numpy as np
import tiles

from geom import Point, Rect
from random import choice
from tcod.path import maxarray, dijkstra2d
from tcod.map import compute_fov
from tcod.constants import FOV_DIAMOND


class GameMap:
    """Describes a game map."""

    def __init__(
        self,
        id: str,
        name: str,
        width: int,
        height: int,
        dark: bool = True,
    ):
        self.explored = np.zeros((width, height), dtype=bool, order="F")
        self.visible = np.zeros((width, height), dtype=bool, order="F")
        self.dist = maxarray((width, height), order="F")
        self.cost = np.zeros((width, height), dtype=np.int32, order="F")
        self.dark = dark
        self.__id = id
        self.__name = name
        self.__tiles = np.full((width, height), fill_value=tiles.TILE_WALL, order="F")

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def width(self) -> int:
        return self.__tiles.shape[0]

    @property
    def height(self) -> int:
        return self.__tiles.shape[1]

    @property
    def tiles(self) -> np.ndarray:
        return self.__tiles

    def update_cost(self):
        self.cost = np.select(
            condlist=[self.tiles["walkable"]], choicelist=[1], default=0
        )

    def update_dmap(self, *goals: Point):
        self.dist = maxarray((self.width, self.height), order="F")
        for goal in goals:
            self.dist[goal.x, goal.y] = 0
        dijkstra2d(self.dist, self.cost, True, out=self.dist)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        return self.__tiles[x, y]["walkable"]

    def transparent(self, x: int, y: int) -> bool:
        return self.__tiles[x, y]["transparent"]

    def carve(self, x: int, y: int):
        self.tiles[x, y] = tiles.TILE_FLOOR

    def carve_rect(self, r: Rect):
        self.tiles[r.x1 : r.x2 + 1, r.y1 : r.y2 + 1] = tiles.TILE_WALL
        self.tiles[r.x1 + 1 : r.x2, r.y1 + 1 : r.y2] = tiles.TILE_FLOOR

    def fill_rect(self, r: Rect):
        self.tiles[r.x1 : r.x2 + 1, r.y1 : r.y2 + 1] = tiles.TILE_WALL

    def neighbors(self, x: int, y: int):
        return [
            Point(i, j)
            for (i, j) in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if self.in_bounds(i, j)
        ]

    def on_edge(self, x: int, y: int) -> bool:
        return x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1

    def get_random_floor(self) -> Point:
        cands = [
            Point(x, y)
            for x in range(0, self.width)
            for y in range(0, self.height)
            if self.in_bounds(x, y)
            if self.walkable(x, y)
        ]

        return choice(cands)

    def update_fov(self, pt: Point, r: int = 8):
        self.visible = compute_fov(
            self.tiles["transparent"], (pt.x, pt.y), r, algorithm=FOV_DIAMOND
        )
        self.explored |= self.visible


def arena(id: str, name: str, width: int, height: int, dark: bool = True) -> GameMap:
    m = GameMap(id, name, width, height, dark)
    m.carve_rect(Rect.from_xywh(0, 0, width, height))
    m.update_cost()
    return m


def drunk_walk(
    id: str,
    name: str,
    width: int,
    height: int,
    coverage: float = 0.5,
    dark: bool = True,
) -> GameMap:
    m = GameMap(id, name, width, height, dark)
    x = m.width // 2
    y = m.height // 2
    pt = Point(x, y)
    stack = [pt]
    floors = 0
    desired = int(width * height * max(0.1, min(coverage, 1)))
    m.carve(x, y)

    def f(pt):
        return not (m.walkable(pt.x, pt.y) or m.on_edge(pt.x, pt.y))

    while floors < desired:
        cands = list(filter(f, m.neighbors(pt.x, pt.y)))
        if len(cands) > 0:
            pt = choice(cands)
            m.carve(pt.x, pt.y)
            stack.append(pt)
            floors += 1
        else:
            pt = stack.pop()

    m.update_cost()
    return m
