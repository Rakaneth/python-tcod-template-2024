from gamemap import GameMap
from tiles import SHROUD
from geom import Point
from tcod.console import Console
from typing import Tuple

import numpy as np
import textwrap
import swatch as sw

MAP_W = 25
MAP_H = 20
SCR_W = 40
SCR_H = 30
MSG_W = MAP_W
MSG_H = 10


class Camera:
    """Defines a viewport for the visible map."""

    def __init__(self, width: int, height: int):
        self.center = Point(0, 0)
        self.width = width
        self.height = height

    def __cam_calc(self, p: int, m: int, s: int) -> int:
        return sorted((p - s // 2, 0, max(0, m - s)))[1]

    def start_point(self, m: GameMap):
        left = self.__cam_calc(self.center.x, m.width, self.width)
        top = self.__cam_calc(self.center.y, m.height, self.height)
        return Point(left, top)

    def in_view(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


def draw_on_map(
    x: int,
    y: int,
    glyph: int,
    cam: Camera,
    con: Console,
    m: GameMap,
    fg: Tuple[int, int, int] = None,
):
    st = cam.start_point(m)
    sx = x - st.x
    sy = y - st.y
    if cam.in_view(sx, sy):
        cell = con.rgb[sx, sy]
        cell["ch"] = glyph
        if fg is not None:
            cell["fg"] = fg


def draw_map(m: GameMap, cam: Camera, con: Console):
    st = cam.start_point(m)
    x_end = st.x + min(m.width, cam.width)
    y_end = st.y + min(m.height, cam.height)
    s_xend = x_end - st.x
    s_yend = y_end - st.y
    viewport = m.tiles[st.x : x_end, st.y : y_end]
    vw_visible = m.visible[st.x : x_end, st.y : y_end]
    vw_explored = m.explored[st.x : x_end, st.y : y_end]

    con.rgb[0:s_xend, 0:s_yend] = np.select(
        condlist=[(not m.dark) or vw_visible, vw_explored],
        choicelist=[viewport["light"], viewport["dark"]],
        default=SHROUD,
    )


def draw_dmap(m: GameMap, cam: Camera, con: Console):
    st = cam.start_point(m)
    x_end = st.x + min(m.width, cam.width)
    y_end = st.y + min(m.height, cam.height)
    for y in np.arange(st.y, y_end):
        for x in np.arange(st.x, x_end):
            d = m.dist[x, y]
            if d < 10:
                draw_on_map(x, y, str(d), cam, con, m)


def draw_bar(
    x: int,
    y: int,
    bar_cur: int,
    bar_max: int,
    width: int,
    fill_color: Tuple[int, int, int],
    empty_color: Tuple[int, int, int],
    con: Console,
    draw_values: bool = False,
):
    ratio = bar_cur / bar_max
    ch = 0x2588
    fill_w = int(min(ratio, 1.0) * width)
    con.draw_rect(x, y, width, 1, ch, fg=empty_color)
    con.draw_rect(x, y, fill_w, 1, ch, fg=fill_color)
    if draw_values:
        s = f"{bar_cur}/{bar_max}"
        sx = (width - len(s)) // 2
        if sx >= 0:
            con.print(sx + x, y, s)


def measure(text: str, w: int):
    return len(textwrap.wrap(text, w))


class UIElement:
    """Base UI element class."""

    def __init__(
        self,
        con: Console,
        w: int,
        h: int,
        *,
        x: int,
        y: int,
        title: str = "",
        options: list[str] = None,
    ):
        self.console = con
        self.width = w
        self.height = h
        self.x = (con.width - self.width) // 2 if x is None else x
        self.y = (con.height - self.height) // 2 if y is None else y
        self.title = title
        self.options = options

    def draw(self):
        raise NotImplementedError()


class Selector(UIElement):
    """Base class for elements that select."""

    def __init__(
        self,
        con: Console,
        w: int,
        h: int,
        *,
        x: int,
        y: int,
        title: str = "",
        options: list[str] = None,
    ):
        super().__init__(con, w, h, x=x, y=y, title=title, options=options)
        self.index = 0

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1

    def move_down(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0

    @property
    def selected(self) -> str:
        return self.options[self.index]


LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec efficitur mi. Aenean et nulla non velit tempor pellentesque. Nullam ornare quis tellus at malesuada. Aenean eu ligula orci. Quisque nibh eros, blandit non odio quis, pretium tincidunt felis. Nulla bibendum velit non nulla tincidunt, at tempor ex vestibulum. Donec pulvinar dolor tellus, sit amet pellentesque erat ullamcorper quis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ornare libero congue elit aliquet dapibus. Cras dapibus in purus quis luctus."""  # noqa: E501

SMALL_PARA = """This is a long bit of text that might be expected to present as a single dialog or textbox. It is not, however, quite so long as the Lorem Ipsum."""  # noqa: E501


class Menu(Selector):
    """
    Describes an in-game menu.
    """

    def __init__(
        self,
        options: list[str],
        con: Console,
        *,
        x: int = None,
        y: int = None,
        title: str = "",
    ) -> None:
        w = max(map(len, options))
        width = max(w, len(title)) + 4
        height = len(options) + 2
        super().__init__(con, width, height, x=x, y=y, title=title, options=options)
        self.index = 0

    def draw(self):
        self.console.draw_frame(self.x, self.y, self.width, self.height, self.title)
        bg = sw.BLACK
        for i, opt in enumerate(self.options):
            if i == self.index:
                fg = sw.TARGET
            else:
                fg = sw.WHITE
            self.console.print(self.x + 1, self.y + i + 1, opt, fg, bg)


class TextBox(UIElement):
    """Describes a box with text and optional title."""

    def __init__(
        self,
        con: Console,
        w: int,
        h: int,
        text: str,
        *,
        x: int = None,
        y: int = None,
        title: str = "",
    ):
        super().__init__(con, w, h, x=x, y=y, title=title)
        self.text = text

    def draw(self):
        self.console.draw_frame(self.x, self.y, self.width, self.height, self.title)
        self.console.print_box(
            self.x + 1, self.y + 1, self.width - 2, self.height - 2, self.text
        )


class Dialog(Selector):
    """Describes a text box with choices."""

    def __init__(
        self,
        con: Console,
        w: int,
        text: str,
        options: list[str],
        *,
        x: int = None,
        y: int = None,
        title: str = "",
    ):
        h = min(len(textwrap.wrap(text, w - 2)) + 3 + len(options), con.height - 4)
        self.text = text
        super().__init__(con, w, h, x=x, y=y, title=title, options=options)

    def draw(self):
        bg = sw.BLACK
        opts_y = (self.y + self.height - 1) - len(self.options)
        self.console.draw_frame(self.x, self.y, self.width, self.height, self.title)
        self.console.print_box(
            self.x + 1,
            self.y + 1,
            self.width - 2,
            self.height - len(self.options) - 1,
            self.text,
        )
        for i, opt in enumerate(self.options):
            if i == self.index:
                fg = sw.TARGET
            else:
                fg = sw.WHITE
            self.console.print(self.x + 1, i + opts_y, opt, fg, bg)


class YesNoMenu(Menu):
    def __init__(
        self, con: Console, *, x: int = None, y: int = None, title: str = ""
    ) -> None:
        super().__init__(["Yes", "No"], con, x=x, y=y, title=title)

    @property
    def confirmed(self) -> bool:
        return self.selected == "Yes"


class MenuWithValues(Menu):
    def __init__(
        self, con, opts_dict: dict, *, x: int = None, y: int = None, title: str = None
    ):
        super().__init__(list(opts_dict.keys()), con, x=x, y=y, title=title)
        self.opts_dict = opts_dict

    @property
    def selected_val(self):
        return self.opts_dict[self.selected]
