from __future__ import annotations
from typing import TYPE_CHECKING

import ui
import queries as q
import components as comps

from geom import Direction
from gamemap import GameMap
from screen import Screen, ScreenNames
from tcod.ecs import Entity

if TYPE_CHECKING:
    from engine import Engine


class MapScreen(Screen):
    """Describes a map screen."""

    def __init__(self, engine: Engine):
        super().__init__(ScreenNames.MAP, engine)
        self.camera = ui.Camera(ui.MAP_W, ui.MAP_H)

    @property
    def player(self) -> Entity:
        return q.player(self.world)

    @property
    def cur_map(self) -> GameMap:
        return q.cur_map(self.world)

    def render(self):
        pos = self.player.components[comps.Location]
        render = self.player.components[comps.Renderable]
        ui.draw_map(self.cur_map, self.camera, self.root_console)
        ui.draw_on_map(
            pos.x,
            pos.y,
            render.ch,
            self.camera,
            self.root_console,
            self.cur_map,
            render.fg,
        )

    def update(self):
        pos = self.player.components[comps.Location]
        self.cur_map.update_fov(pos)
        self.camera.center = pos

    def on_up(self):
        self.player.components[comps.Location] += Direction.UP
        self.engine.should_update = True

    def on_down(self):
        self.player.components[comps.Location] += Direction.DOWN
        self.engine.should_update = True

    def on_left(self):
        self.player.components[comps.Location] += Direction.LEFT
        self.engine.should_update = True

    def on_right(self):
        self.player.components[comps.Location] += Direction.RIGHT
        self.engine.should_update = True

    def on_cancel(self):
        self.engine.running = False
        self.engine.should_update = False
