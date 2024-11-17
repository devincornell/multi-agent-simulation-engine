
import datetime
import random
import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import pytest
import tqdm

import sys
sys.path.append('../src')
import mase

def test_coords():
    random.seed(0)
    int_pos = mase.HexCoord.origin().region(20)
    rand_pos = [mase.HexCoord.from_rq(random.random(), random.random()) for _ in range(100)]
    positions = list(int_pos) + rand_pos

    for pos in positions:
        c = pos.to_cartesian()
        h = c.to_hex()
        print(h, pos)
        assert(h.isclose(pos))

def assert_eq(a, b):
    if not (a == b):
        raise ValueError(f'Assert equal error:\n{a=}\n{b=}')
    
def check_valid_path(path: list[mase.HexCoord]):
    #print(path)
    for i in range(1, len(path)):
        #print(path[i], path[i-1].neighbors())
        assert(path[i] in path[i-1].neighbors())

def test_algorithms(verbose=False):
    random.seed(0)
    region = mase.HexCoord.origin().region(5)
    #assert(mase.HexCoord.origin() in region)
    region_list = list(region)
    
    main_iter = range(len(region_list))
    if not verbose:
        main_iter = tqdm.tqdm(main_iter, ncols=100)

    for i in main_iter:
        all_dists = region_list[i].dijkstra(region)

        # starting path should be in returned distances
        assert(region_list[i] in region)
        assert(region_list[i] in all_dists)
        assert_eq(len(region), len(all_dists))
        
        for j in range(len(region_list)):
            if i != j:
                assert(region_list[j] in region)
                sp = region_list[i].a_star(region_list[j], allowed_pos=region)
                check_valid_path(sp)
                check_valid_path(all_dists[region_list[j]])
                
                #print(f'\n\nas={sp}\ndj={all_dists[region_list[j]]}\n\n')
                assert_eq(len(sp), len(all_dists[region_list[j]]))
                
                    
        
        



if __name__ == '__main__':
    test_coords()
    test_algorithms()