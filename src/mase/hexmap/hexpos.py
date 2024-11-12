# distutils: language = c++
from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses

#from .position import Position
#from .algorithms import a_star

HexUnit = int


HEX_DIRECTIONS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
]

#HEX_POS_DIRECTIONS = [HexPos(*coords) for coords in HEX_DIRECTIONS]
class NoPathFound(Exception):
    @classmethod
    def from_src_and_dest(cls, src: HexPos, dest: HexPos) -> typing.Self:
        return cls(f'No path found from {src} to {dest}.')


@dataclasses.dataclass(frozen=True, slots=True)
class HexPos:
    '''Hexagonal position object.'''
    q: HexUnit
    r: HexUnit
    s: HexUnit

    @classmethod
    def from_origin(cls) -> HexPos:
        return cls(0, 0, 0)


    ################################ Work with Coordinates ################################
    def coords_xy(self):
        return (self.x, self.y)
    
    @property
    def x(self):
        return self.q

    @property
    def y(self):
        return self.r + (self.q + (self.q&1)) / 2
    
    def coords(self):
        return (self.q, self.r, self.s)

    ################################ Neighbors and regions ################################
    def distance(self, other: typing.Self) -> int:
        return int((math.fabs(self.q-other.q) + math.fabs(self.r-other.r) + math.fabs(self.s-other.s))//2)
    
    def region_sorted(self, target: HexPos, dist: int = 1) -> typing.List[HexPos]:
        '''Return direct neighbors sorted by distance from target.'''
        return list(sorted(self.neighbors(dist), key=lambda n: target.dist(n)))

    def region(self, dist: int = 1) -> typing.Set[HexPos]:
        '''Get points within a given distance.'''
        positions = set()
        for q in range(-dist, dist+1):
            for r in range(max(-dist, -q-dist), 1+min(dist, -q+dist)):
                s = -q - r
                if not (q == 0 and r == 0):
                    positions.add(self.offset(q,r,s))
        return positions

    def neighbors(self) -> list[HexPos]:
        '''Get the six neighboring coordinates.'''
        return {self.offset(*coords) for coords in HEX_DIRECTIONS}

    def offset(self, offset_q: int, offset_r: int, offset_s: int):
        '''Get a new object with the specified offset coordinates.'''
        return self.__class__(self.q+offset_q, self.r+offset_r, self.s+offset_s)


    def a_star(
        self, 
        goal: HexPos, 
        allowed_pos: typing.Optional[set[HexPos]] = None, 
        max_dist: typing.Optional[int] = None
    ) -> list[HexPos]:
        '''Compute the A-star algorithm on a hex grid.'''

        open_set: list[HexPos] = [self]
        came_from: dict[HexPos, HexPos] = {}
        g_score: dict[HexPos,int] = {self: 0}
        f_score: dict[HexPos, float] = {self: self.distance(goal)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            open_set.remove(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self)
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

        raise NoPathFound.from_src_and_dest(self, goal)



    ################################ Pathfinding ################################

    def pathfind_dfs(self, target: HexPos, useset: typing.Set[HexPos] = None, 
            max_dist: int = None, verbose: bool = False) -> typing.List[HexPos]:
        '''Heuristic-based pathfinder. May not be shortest path.'''
        
        if max_dist is None:
            max_dist = 1e9 # real big
        
        if self.dist(target) > max_dist:
            raise ValueError(f'Target {self}->{target} (dist={self.dist(target)}) is outside maximum distance of {max_dist}.')

        useset = set(useset)
        visited = set([self])
        current_path: typing.List[self.__class__] = [self]

        finished = False
        while not finished:
            if verbose: print(f'status: {current_path}, {visited}')
            found_next = False
            for neighbor in current_path[-1].sorted_neighbors(target):
                if neighbor == target:
                    if verbose: print(f'found target {target}.')
                    current_path.append(neighbor)
                    found_next = True
                    finished = True
                    break
                    #return current_path + [neighbor]
                elif neighbor in useset and neighbor not in visited and self.dist(neighbor) <= max_dist:
                    current_path.append(neighbor)
                    visited.add(neighbor)
                    found_next = True
                    break
            
            # if none of these options are valid
            if not finished and not found_next:
                if verbose: print(f'reached dead end at {current_path[-1]}.')
                visited.add(neighbor)
                current_path.pop()

            if not len(current_path):
                return None

            if verbose: print('--------------------------------\n')
            
        return current_path


    def shortest_path_length(self, target: HexPos, avoidset: set) -> int:
        '''Calculate number of steps required to reach target.'''
        if target in avoidset:
            raise TargetInAvoidSet(f'Target {target} was found in avoidset.')
        
        ct = 0
        visited = set([self])
        while True:
            fringe = self.fringe(visited, 1) - avoidset
            ct += 1
            if target in fringe:
                #ct += 1
                return ct
            elif not len(fringe):
                return None
            else:
                visited |= fringe
    
    def fringe(self, others: typing.Set[HexPos], dist: int = 1) -> typing.Set[HexPos]:
        '''Get positions on the fringe of the provided nodes.'''
        others = others | set([self])
        fringe = set()
        for pos in others:
            fringe |= pos.neighbors(dist)
        return fringe - others

    def pathfind_dfs_avoid(self, target: HexPos, avoidset: set = None, max_dist: int = None, verbose: bool = False) -> typing.List[HexPos]:
        '''Heuristic-based pathfinder. May not be shortest path.'''
        if target in avoidset:
            raise TargetInAvoidSet(f'Target {target} was found in avoidset.')
        
        if max_dist is None:
            max_dist = 1e9 # real big
        
        if self.dist(target) > max_dist:
            raise ValueError(f'Target {self}->{target} (dist={self.dist(target)}) is outside maximum distance of {max_dist}.')

        avoidset = set(avoidset)
        visited = set([self])
        current_path: typing.List[self.__class__] = [self]

        finished = False
        while not finished:
            if verbose: print(f'status: {current_path}, {visited}')
            found_next = False
            for neighbor in current_path[-1].sorted_neighbors(target):
                if neighbor == target:
                    if verbose: print(f'found target {target}.')
                    current_path.append(neighbor)
                    found_next = True
                    finished = True
                    break
                    #return current_path + [neighbor]
                elif neighbor not in avoidset and neighbor not in visited and self.dist(neighbor) <= max_dist:
                    current_path.append(neighbor)
                    visited.add(neighbor)
                    found_next = True
                    break
            
            # if none of these options are valid
            if not finished and not found_next:
                if verbose: print(f'reached dead end at {current_path[-1]}.')
                visited.add(neighbor)
                current_path.pop()

            if not len(current_path):
                return None

            if verbose: print('--------------------------------\n')
            
        return current_path
