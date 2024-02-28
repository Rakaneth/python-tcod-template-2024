import components as comps
import queries as q
import yaml

from tcod.ecs import World, Entity
from gamemap import GameMap, drunk_walk, arena
from geom import Point
from random import randint


class GameData:
    """Describes game data, stored in YAML files."""

    def __init__(self, fn: str):
        with open(fn, "r") as f:
            self.data = yaml.load(f, yaml.SafeLoader)


DATAFOLDER = "./assets/data/"

CHARDATA = GameData(f"{DATAFOLDER}chardata.yml")
MAPDATA = GameData(f"{DATAFOLDER}/mapdata.yml")


def make_creature(w: World, build_id: str, player: bool = False):
    template = CHARDATA.data[build_id]
    ch = ord(template["ch"])
    fg = tuple(template["fg"])
    nm = template["name"]
    tags = template.get("tags", list())
    desc = template["desc"]
    base_tags = ["blocker", "actor"]
    e = None

    c = {
        comps.Renderable: comps.Renderable(ch, fg),
        comps.Location: Point(0, 0),
        comps.Name: nm,
        comps.Description: desc,
    }

    if player:
        e = w["player"]
    else:
        e = w.new_entity()

    e.components.update(c)

    for tag in base_tags + tags:
        e.tags.add(tag)

    if player:
        e.tags.add("player")

    return e


def add_map(w: World, m: GameMap):
    # w[None].components[(m.id, GameMap)] = m
    m_entity = w[m.id]
    m_entity.components[comps.GameMapComp] = m


def place_entity(w: World, e: Entity, map_id: str, pt: Point = None):
    e.components[comps.MapId] = map_id
    m = q.get_map(w, map_id)
    if pt is None:
        pt = m.get_random_floor()

    # while len(list(blockers_at(w, pt))) > 0:
    #     pt = m.get_random_floor()

    e.components[comps.Location] = pt

    # write_log(
    #     w, "factory", f"Adding entity {e.components[comps.Name]} to {map_id} at {pt}"
    # )


def make_map(build_id: str) -> GameMap:
    """Creates a map based on map data."""
    template = MAPDATA.data[build_id]
    gen = template["gen"]
    w_low, w_high = template["width"]
    h_low, h_high = template["height"]
    tier = template["tier"]
    dark = template.get("dark", False)
    name = template["name"]

    width = randint(w_low, w_high)
    height = randint(h_low, h_high)
    cov = 0.3 + 0.1 * tier
    m = None

    match gen:
        case "drunkard":
            m = drunk_walk(build_id, name, width, height, cov, dark)
        case "arena":
            m = arena(build_id, name, width, height, dark)
        case _:
            raise NotImplementedError(f"Map type {gen} not yet implemented.")

    return m


def build_all_maps(w: World):
    for map_id in MAPDATA.data.keys():
        # write_log(w, "factory", f"Building map {map_id}")
        m = make_map(map_id)
        add_map(w, m)
