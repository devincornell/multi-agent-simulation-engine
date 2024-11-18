from __future__ import annotations
import dataclasses
import typing
import heapq

from .base_coord import BaseCoord

class NoPathFound(Exception):
    src: BaseCoord
    dest: BaseCoord
    @classmethod
    def from_src_and_dest(cls, src: BaseCoord, dest: BaseCoord) -> typing.Self:
        o = cls(f'No path found from {src} to {dest}.')
        o.src = src
        o.dest = dest
        return o

class SourceIsSameAsDest(Exception):
    src: BaseCoord
    @classmethod
    def from_src(cls, src: BaseCoord) -> typing.Self:
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



def dijkstra(
    start: BaseCoord,
    allowed_pos: typing.Optional[set[BaseCoord]] = None,
    max_dist: typing.Optional[int] = None,
    include_start: bool = False,
) -> dict[BaseCoord, list[BaseCoord]]:
    '''Find the shortest path from the start to all other positions.'''
    shortest_path_tuples: dict[BaseCoord, list[BaseCoord]] = {}
    shortest_paths = _dijkstra(start=start, allowed_pos=allowed_pos, max_dist=max_dist)
    for goal in shortest_paths:
        path = _reconstruct_path(start=start, goal=goal, previous_nodes=shortest_paths)
        shortest_path_tuples[goal] = path
    
    if not include_start:
        del shortest_path_tuples[start]
    
    return shortest_path_tuples


@dataclasses.dataclass(frozen=True, slots=True, order=True)
class DistCoordPair:
    '''A pair of a distance and a coordinate.
    Description: created to be used in the priority queue in the Dijkstra 
        algorithm without trying to compare the coordinates.
    '''
    dist: float
    coord: BaseCoord = dataclasses.field(compare=False)

def _dijkstra(
    start: BaseCoord,
    allowed_pos: typing.Optional[set[BaseCoord]] = None,
    max_dist: typing.Optional[int] = None,
) -> dict[BaseCoord, tuple[float, typing.Optional[BaseCoord]]]:
    '''Find the shortest path from the start to all other positions.
    Returns: a dictionary of the form {node: (distance, previous_node)}.
        More work needs to be done to make paths as list.
    '''
    allowed_pos = set(allowed_pos) if allowed_pos is not None else None
    distances: dict[BaseCoord, float] = {start: 0} # minimum dist from start to all other nodes
    previous_nodes: dict[BaseCoord, typing.Optional[BaseCoord]] = {start: None}
    priority_queue: list[DistCoordPair] = [DistCoordPair(dist=0, coord=start)]

    while priority_queue:
        #current_distance, current_node = dataclasses.astuple(heapq.heappop(priority_queue))
        dist_coord_pair: DistCoordPair = heapq.heappop(priority_queue)
        current_distance = dist_coord_pair.dist
        current_node = dist_coord_pair.coord

        if allowed_pos is not None and current_node not in allowed_pos:
            continue

        for neighbor in current_node.neighbors():
            distance = current_distance + 1  # Assuming each edge has a weight of 1
            if max_dist is not None and distance > max_dist:
                continue
            
            if allowed_pos is not None and neighbor not in allowed_pos:
                continue
            
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, DistCoordPair(dist=distance, coord=neighbor))

    return {node: (dist, previous_nodes[node]) for node, dist in distances.items()}

def _reconstruct_path(
    start: BaseCoord,
    goal: BaseCoord,
    previous_nodes: dict[BaseCoord, tuple[float, BaseCoord | None]],
) -> list[BaseCoord]:
    '''Reconstruct the path from start to goal using the previous_nodes dictionary.'''
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous_nodes[current][1]
    path.reverse()
    return path if path[0] == start else []

