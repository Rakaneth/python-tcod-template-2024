import components as comps

from tcod.ecs import World, Entity
from gamemap import GameMap


def player(w: World) -> Entity:
    return w["player"]


def get_map(w: World, map_id: str = None) -> GameMap:
    return w[map_id].components[comps.GameMapComp]


def cur_map(w: World) -> GameMap:
    cur_map_id = player(w).components[comps.MapId]
    return get_map(w, cur_map_id)
