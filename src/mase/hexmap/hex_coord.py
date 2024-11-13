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

from .cart_coord import CartCoord, CartUnit

HexUnit = int


HEX_DIRECTIONS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
]

#HEX_POS_DIRECTIONS = [typing.Self(*coords) for coords in HEX_DIRECTIONS]
class NoPathFound(Exception):
    @classmethod
    def from_src_and_dest(cls, src: typing.Self, dest: typing.Self) -> typing.Self:
        return cls(f'No path found from {src} to {dest}.')


@dataclasses.dataclass(frozen=True, slots=True)
class HexCoord:
    '''Hexagonal position object.'''
    q: HexUnit
    r: HexUnit
    s: HexUnit

    @classmethod
    def from_origin(cls) -> typing.Self:
        return cls(0, 0, 0)
    
    @classmethod
    def from_xy(cls, x: CartUnit, y: CartUnit) -> typing.Self:
        '''Create a hexagonal position from cartesian coordinates. UNTESTED: written by AI.'''
        q = x
        r = y - (x + (x&1)) / 2
        return cls(q, r, -q-r)


    ################################ Work with Coordinates ################################
    def coords_xy(self) -> CartCoord:
        return CartCoord(self.x, self.y)
    
    @property
    def x(self) -> CartUnit:
        return self.q

    @property
    def y(self) -> CartUnit:
        return self.r + (self.q + (self.q&1)) / 2
    
    def coords(self) -> tuple[HexUnit, HexUnit, HexUnit]:
        return (self.q, self.r, self.s)

    ################################ Neighbors and regions ################################
    def region_sorted(self, target: typing.Self, dist: int = 1) -> list[typing.Self]:
        '''Return direct neighbors sorted by distance from target.'''
        return list(sorted(self.neighbors(dist), key=lambda n: target.distance(n)))

    def region(self, dist: int = 1) -> typing.Set[typing.Self]:
        '''Get points within a given distance.'''
        positions = set()
        for q in range(-dist, dist+1):
            for r in range(max(-dist, -q-dist), 1+min(dist, -q+dist)):
                s = -q - r
                if not (q == 0 and r == 0):
                    positions.add(self.offset(q,r,s))
        return positions

    def neighbors(self) -> list[typing.Self]:
        '''Get the six neighboring coordinates.'''
        return {self.offset(*coords) for coords in HEX_DIRECTIONS}

    def offset(self, offset_q: int, offset_r: int, offset_s: int):
        '''Get a new object with the specified offset coordinates.'''
        return self.__class__(self.q+offset_q, self.r+offset_r, self.s+offset_s)
    
    ################################ Distances and math ################################
    def distance(self, other: typing.Self) -> HexUnit:
        return (math.fabs(self.q-other.q) + math.fabs(self.r-other.r) + math.fabs(self.s-other.s))/2
    
    ################################ pathfinding ################################
    def a_star(
        self, 
        goal: typing.Self, 
        allowed_pos: typing.Optional[set[typing.Self]] = None, 
        max_dist: typing.Optional[int] = None
    ) -> list[typing.Self]:
        '''Compute the A-star algorithm on a hex grid.'''

        open_set: list[typing.Self] = [self]
        came_from: dict[typing.Self, typing.Self] = {}
        g_score: dict[typing.Self,int] = {self: 0}
        f_score: dict[typing.Self, float] = {self: self.distance(goal)}

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



    ################################ Depricated Pathfinding ################################

    def pathfind_dfs(self, target: typing.Self, useset: typing.Set[typing.Self] = None, 
            max_dist: int = None, verbose: bool = False) -> typing.List[typing.Self]:
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


    def shortest_path_length(self, target: typing.Self, avoidset: set) -> int:
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
    
    def fringe(self, others: typing.Set[typing.Self], dist: int = 1) -> typing.Set[typing.Self]:
        '''Get positions on the fringe of the provided nodes.'''
        others = others | set([self])
        fringe = set()
        for pos in others:
            fringe |= pos.neighbors(dist)
        return fringe - others

    def pathfind_dfs_avoid(self, target: typing.Self, avoidset: set = None, max_dist: int = None, verbose: bool = False) -> typing.List[typing.Self]:
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
