# distutils: language = c++
from __future__ import annotations


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

from .position import Position
    

def reconstruct_path(came_from: typing.Dict[Position,float], current: Position):
    total_path = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path.append(current)
    return list(reversed(total_path))

def a_star(source: Position, target: Position, allowed_pos: typing.Set[Position], 
        max_dist: int = None, verbose: bool = False) -> typing.List[Position]:
    '''Heuristic-based shortest path algorthm A*.
    pseudocode here: https://en.wikipedia.org/wiki/A*_search_algorithm
    '''
    
    if max_dist is None:
        max_dist = 1e9 # real big
    
    if source.dist(target) > max_dist:
        raise ValueError(f'Target {source}->{target} (dist={source.dist(target)}) is outside maximum distance of {max_dist}.')
    
    #if target not in allowed_pos:
    #    raise ValueError(f'Target {target} must appear in allowed_pos: {allowed_pos=}.')

    allowed_pos = set(allowed_pos)
    allowed_pos.add(target)
    open_set = set([source])
    
    #For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start to n currently known.
    came_from = dict()
    
    # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
    #g_scores = {pos: math.inf for pos in allowed_pos}
    g_scores = {source: 0}
    f_scores = {source: source.dist(target)}

    if verbose:
        print(f'{source=}, {target=}, {len(allowed_pos)=}')


    while len(open_set):
        current = min([(p,f_scores.get(p, math.inf)) for p in open_set], key=lambda pd: pd[1])[0]

        if current == target:
            if verbose: print(f'found target!!!')
            return reconstruct_path(came_from, current)
        
        open_set.remove(current)
        
        neighbors = current.neighbors(dist=1) & allowed_pos
        
        if verbose:
            print(f'iteration:\n\t{current=}\n\t{open_set=}\n\t{f_scores=}\n\n\t{g_scores=}\n\t{came_from=}\n\n\t{neighbors=}\n')
        
        for neighbor in neighbors:
            est_g_score = g_scores.get(current, math.inf) + 1
            if est_g_score < g_scores.get(neighbor, math.inf):
                # This path to neighbor is better than any previous one. Record it!
                came_from[neighbor] = current
                g_scores[neighbor] = est_g_score
                f_scores[neighbor] = est_g_score + neighbor.dist(target)
                
                open_set.add(neighbor)
    return None
                















