# distutils: language = c++
from __future__ import annotations

#%%cython

import numpy as np
import typing
import math
#import itertools
import math
#import dataclasses
#from libcpp.set cimport set as cpp_set
#cimport libcpp.set.set
from .errors import *
from .position import Position
#from libc.math cimport sin
from .algorithms import a_star
import time

class HexPos(Position):

    def __init__(self, q: int, r: int, s: int):
        self.q = q
        self.r = r
        self.s = s

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    @property
    def x(self):
        return self.q

    @property
    def y(self):
        return self.r + (self.q + (self.q&1)) / 2

    def coords_xy(self):
        return (self.x, self.y)

    def coords(self):
        return (self.q, self.r, self.s)

    def __eq__(self, other):
        return self.coords() == other.coords()

    def __repr__(self):
        return f'{self.coords()}'

    def dist(self, other) -> int:
        return int((math.fabs(self.q-other.q) + math.fabs(self.r-other.r) + math.fabs(self.s-other.s))//2)

    def offset(self, offset_q: int, offset_r: int, offset_s: int):
        '''Get a new object with the specified offset coordinates.'''
        return self.__class__(self.q+offset_q, self.r+offset_r, self.s+offset_s)

    def neighbors(self, dist: int = 1) -> typing.Set[HexPos]:
        '''Get neighborhood within a given distance.'''
        positions = set()
        for q in range(-dist, dist+1):
            for r in range(max(-dist, -q-dist), 1+min(dist, -q+dist)):
                s = -q - r
                if not (q == 0 and r == 0):
                    positions.add(self.offset(q,r,s))
        return positions

    def sorted_neighbors(self, target: HexPos, dist: int = 1) -> typing.List[HexPos]:
        '''Return direct neighbors sorted by distance from target.'''
        return list(sorted(self.neighbors(dist), key=lambda n: target.dist(n)))
    
    def shortest_path(self, target: HexPos, allowed_pos: typing.Set[HexPos] = None, 
            max_dist: int = None, verbose: bool = False) -> typing.List[HexPos]:
        '''Uses A* to find the shortest path between this position in the target, and None if there is no path.'''
        return a_star(self, target, allowed_pos, max_dist=max_dist, verbose=verbose)

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
