from __future__ import annotations

from tcod.ecs import World
from tcod.event import EventDispatch, KeyDown, KeySym, MouseButtonUp, MouseMotion, Quit
from tcod.console import Console
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine


SIGNALS = {
    KeySym.w: "up",
    KeySym.UP: "up",
    KeySym.KP_8: "up",
    KeySym.a: "left",
    KeySym.LEFT: "left",
    KeySym.KP_4: "left",
    KeySym.s: "down",
    KeySym.DOWN: "down",
    KeySym.KP_2: "down",
    KeySym.d: "right",
    KeySym.RIGHT: "right",
    KeySym.KP_6: "right",
    KeySym.RETURN: "confirm",
    KeySym.KP_ENTER: "confirm",
    KeySym.SPACE: "wait",
    KeySym.ESCAPE: "cancel",
}


class ScreenNames:
    """Holds screen names."""

    TITLE = "title"
    MAP = "map"


class Screen(EventDispatch):
    """
    Describes a game screen, or part of a game screen.
    Meant to be used in a stack.
    """

    def __init__(self, name: str, engine: Engine):
        self.__name = name
        self.engine = engine

    # Properties

    @property
    def name(self) -> str:
        return self.__name

    @property
    def world(self) -> World:
        return self.engine.world

    @property
    def root_console(self) -> Console:
        return self.engine.root_console

    # API

    def render(self):
        self.root_console.print(f"This is the {self.name} screen.")

    def update(self):
        pass

    def on_up(self):
        pass

    def on_down(self):
        pass

    def on_left(self):
        pass

    def on_right(self):
        pass

    def on_confirm(self):
        pass

    def on_cancel(self):
        pass

    def on_wait(self):
        pass

    def on_click(self, x: int, y: int, button: int):
        pass

    def on_mouse_move(self, x: int, y: int):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    # base methods
    def ev_keydown(self, event: KeyDown):
        signal = SIGNALS.get(event.sym)
        match signal:
            case "up":
                return self.on_up()
            case "down":
                return self.on_down()
            case "left":
                return self.on_left()
            case "right":
                return self.on_right()
            case "confirm":
                return self.on_confirm()
            case "cancel":
                return self.on_cancel()
            case _:
                return None

    def ev_mousebuttonup(self, event: MouseButtonUp):
        return self.on_click(event.tile.x, event.tile.y, event.button)

    def ev_mousemotion(self, event: MouseMotion):
        return self.on_mouse_move(event.tile.x, event.tile.y)

    def ev_quit(self, event: Quit):
        self.engine.running = False
