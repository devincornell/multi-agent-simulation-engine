from __future__ import annotations
import typing
import heapq

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


# FROM THE LLM:
# Example usage:
# start = BaseCoord(...)
# allowed_pos = {...}
# shortest_paths = dijkstra(start, allowed_pos)
# for goal in shortest_paths:
#     path = reconstruct_path(start, goal, shortest_paths)
#     print(f"Path from {start} to {goal}: {path}")

def dijkstra_shortest_path(
    start: BaseCoord,
    allowed_pos: typing.Optional[set[BaseCoord]] = None
) -> dict[BaseCoord, list[BaseCoord]]:
    '''Find the shortest path from the start to all other positions.'''
    shortest_path_tuples: dict[BaseCoord, list[BaseCoord]] = {}
    shortest_paths = _dijkstra(start, allowed_pos)
    for goal in shortest_paths:
        path = _reconstruct_path(start, goal, shortest_paths)
        shortest_path_tuples[goal] = path
    return shortest_path_tuples

def _dijkstra(
    start: BaseCoord,
    allowed_pos: typing.Optional[set[BaseCoord]] = None
) -> dict[BaseCoord, tuple[float, typing.Optional[BaseCoord]]]:
    '''Find the shortest path from the start to all other positions.'''
    
    allowed_pos = set(allowed_pos) if allowed_pos is not None else None
    distances: dict[BaseCoord, float] = {start: 0}
    previous_nodes: dict[BaseCoord, typing.Optional[BaseCoord]] = {start: None}
    priority_queue: list[tuple[float, int, BaseCoord]] = [(0, 0, start)]
    counter = 0

    while priority_queue:
        current_distance, _, current_node = heapq.heappop(priority_queue)

        if allowed_pos is not None and current_node not in allowed_pos:
            continue

        for neighbor in current_node.neighbors():
            if allowed_pos is not None and neighbor not in allowed_pos:
                continue

            distance = current_distance + 1  # Assuming each edge has a weight of 1
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, counter, neighbor))
                counter += 1

    return {node: (dist, previous_nodes[node]) for node, dist in distances.items()}

def _reconstruct_path(
    start: BaseCoord,
    goal: BaseCoord,
    previous_nodes: dict[BaseCoord, typing.Optional[BaseCoord]]
) -> list[BaseCoord]:
    '''Reconstruct the path from start to goal using the previous_nodes dictionary.'''
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous_nodes[current][1]
    path.reverse()
    return path if path[0] == start else []

