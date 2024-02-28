import os
import pickle
import tcod
import ui
import factory as fac
import components as comps

from tcod.console import Console
from tcod.ecs import World
from screen import Screen
from mapscreen import MapScreen
from titlescreen import TitleScreen
from constants import SAVING, VERSION
from datetime import datetime


class VersionMismatchError(Exception):
    pass


class Engine:
    """Runs the game."""

    def __init__(self) -> None:
        tileset = tcod.tileset.load_tilesheet(
            "./assets/font/Bisasam_20x20.png", 16, 16, tcod.tileset.CHARMAP_CP437
        )
        self.root_console = Console(ui.SCR_W, ui.SCR_H, order="F")
        self.context = tcod.context.new(
            columns=ui.SCR_W, rows=ui.SCR_H, tileset=tileset, vsync=True
        )
        self.running = True
        self.world = World()
        self.screens = dict()
        self.screen_stack: list[Screen] = list()
        self.should_update = True

    def __del__(self):
        self.context.close()

    @property
    def cur_screen(self) -> Screen:
        return self.screen_stack[-1]

    def register_screen(self, sc: Screen):
        self.screens[sc.name] = sc

    def push(self, scr_id: str):
        new_scr = self.screens[scr_id]
        self.screen_stack.append(new_scr)
        new_scr.on_enter()


    def pop(self, scr_id: str = None):
        if scr_id:
            scr = self.screens[scr_id]
            scr.on_exit()
            self.screen_stack.remove(scr)
            return

        popped = self.screen_stack.pop()
        popped.on_exit()

    def setup(self):
        if not os.path.exists("saves"):
            os.mkdir("saves")
        self.register_screen(MapScreen(self))
        self.register_screen(TitleScreen(self))
        self.push("title")

    def input(self):
        for evt in tcod.event.wait():
            self.context.convert_event(evt)
            self.cur_screen.dispatch(evt)

    def update(self):
        if self.should_update:
            self.cur_screen.update()
            self.should_update = False

    def draw(self):
        self.root_console.clear()
        for sc in self.screen_stack:
            sc.render()
        self.context.present(self.root_console)

    def run(self):
        while self.running:
            self.input()
            self.update()
            self.draw()

        self.save_game()

    def new_game(self, hero_id: str):
        self.world = World()
        tm = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.world[None].components[comps.SaveFile] = f"{hero_id}-{tm}"
        self.world[None].components[comps.GameVersion] = VERSION
        fac.build_all_maps(self.world)
        player = fac.make_creature(self.world, hero_id, True)
        fac.place_entity(self.world, player, "cave")

    def save_game(self):
        if SAVING:
            save_file = self.world[None].components.get(comps.SaveFile)
            if save_file:
                with open(f"saves/{save_file}.sav", "wb") as f:
                    pickle.dump(self.world, f)

    def load_game(self, world: World):
        if SAVING:
            self.world = world
