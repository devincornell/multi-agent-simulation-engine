from __future__ import annotations
import typing

from .base_coord import BaseCoord

class NoPathFound(Exception):
    @classmethod
    def from_src_and_dest(cls, src: typing.Self, dest: typing.Self) -> typing.Self:
        o = cls(f'No path found from {src} to {dest}.')
        o.src = src
        o.dest = dest
        return o

class SourceIsSameAsDest(Exception):
    @classmethod
    def from_src(cls, src: typing.Self) -> typing.Self:
        o = cls(f'No path found from {src}.')
        o.src = src
        return o


def a_star(
    start: BaseCoord,
    goal: BaseCoord, 
    allowed_pos: typing.Optional[set[BaseCoord]] = None, 
    max_dist: typing.Optional[int] = None
) -> list[BaseCoord]:
    '''Find a shortest path between this point and another. Positions should be one unit apart..'''
    if start == goal:
        raise SourceIsSameAsDest.from_src(start)
    allowed_pos = set(allowed_pos) if allowed_pos is not None else None

    open_set: list[BaseCoord] = [start]
    came_from: dict[BaseCoord, BaseCoord] = {}
    g_score: dict[BaseCoord,int] = {start: 0}
    f_score: dict[BaseCoord, float] = {start: start.distance(goal)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
        open_set.remove(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor in current.neighbors():
            if allowed_pos is not None and neighbor not in allowed_pos:
                continue

            tentative_g_score = g_score[current] + 1

            if max_dist is not None and tentative_g_score > max_dist:
                continue

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + neighbor.distance(goal)
                if neighbor not in open_set:
                    open_set.append(neighbor)

    raise NoPathFound.from_src_and_dest(start, goal)
