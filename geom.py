from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    """Simple X,Y data. Includes convenience functions."""

    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self) -> str:
        return f"{self.x},{self.y}"
    
    def dist(self, other: Point) -> int:
        """Manhattan distance between this point and other."""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def adj(self, other: Point) -> bool:
        return self.dist(other) == 1


class Direction:
    NONE = Point(0, 0)
    LEFT = Point(-1, 0)
    DOWN = Point(0, 1)
    RIGHT = Point(1, 0)
    UP = Point(0, -1)


@dataclass
class Rect:
    """Describes a rectangle with four points."""

    x1: int
    y1: int
    x2: int
    y2: int

    @staticmethod
    def from_xywh(x: int, y: int, w: int, h: int) -> Rect:
        return Rect(
            x1=x,
            y1=y,
            x2=x + w - 1,
            y2=y + h - 1,
        )

    def intersect(self, other: Rect) -> bool:
        if self.x1 > other.x2:
            return False
        if self.x2 < other.x1:
            return False
        if self.y1 > other.y2:
            return False
        if self.y2 < other.y2:
            return False

        return True

    @property
    def width(self) -> int:
        return self.x2 - self.x1 + 1

    @property
    def height(self) -> int:
        return self.y2 - self.y1 + 1

    @property
    def center(self) -> Point:
        return Point((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def is_perimeter(self, x: int, y: int) -> bool:
        if x == self.x1:
            return True
        if x == self.x2:
            return True
        if y == self.y1:
            return True
        if y == self.y2:
            return True

        return False

    @property
    def perimeter(self) -> List[Point]:
        return [
            Point(x, y)
            for x in range(self.x1, self.x2 + 1)
            for y in range(self.y1, self.y2 + 1)
            if self.is_perimeter(x, y)
        ]

    @property
    def interior(self) -> List[Point]:
        return [
            Point(x, y)
            for x in range(self.x1, self.x2 + 1)
            for y in range(self.y1, self.y2 + 1)
            if not self.is_perimeter(x, y)
        ]
