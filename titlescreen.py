from __future__ import annotations
import pickle
import re
from typing import TYPE_CHECKING
from components import GameVersion, Name
from constants import VERSION

import ui
import glob

from screen import Screen, ScreenNames
from tcod.ecs import World

if TYPE_CHECKING:
    from engine import Engine


def _load_world(fn: str) -> World:
    world: World = None
    with open(fn, "rb") as f:
        world = pickle.load(f)

    return world


class TitleScreen(Screen):
    """For choosing a new game or title screen."""

    def __init__(self, engine: Engine):
        super().__init__(ScreenNames.TITLE, engine)
        self.load_choices = dict()
        self.new_choices = {"Thrakir": "warrior", "Rikkas": "dwarf", "Falwyn": "druid"}
        self.menu: ui.Menu = None

    def on_enter(self):
        file_list = sorted(glob.glob("saves/*.sav"))
        world_list = [_load_world(file) for file in file_list]
        last_name = ""
        counter = 1
        for w in world_list:
            fn = w["player"].components[Name]
            if w[None].components[GameVersion] == VERSION:
                if fn == last_name:
                    counter += 1
                    fn = f"{fn}-{counter}"
                else:
                    last_name = fn
                    counter = 1
            self.load_choices[fn] = w

        new_game_list = [f"New Game - {hero}" for hero in self.new_choices.keys()]
        save_games = list(self.load_choices.keys())
        self.menu = ui.Menu(
            new_game_list + save_games + ["Exit Game"],
            self.root_console,
            title="Select File",
        )

    def on_down(self):
        self.menu.move_down()

    def on_up(self):
        self.menu.move_up()

    def on_confirm(self):
        result = self.menu.selected
        mo = re.search(r"New Game - (?P<hero>(Thrakir|Rikkas|Falwyn))", result)

        if mo:
            self.engine.new_game(self.new_choices[mo.group("hero")])
        elif result == "Exit Game":
            raise SystemExit()
        else:
            self.engine.load_game(self.load_choices[result])

        self.engine.pop()
        self.engine.push("map")
        self.engine.should_update = True

    def render(self):
        self.menu.draw()
