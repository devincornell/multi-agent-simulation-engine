
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
    
def check_valid_path(path: tuple[mase.HexCoord, ...]):
    for i in range(1, len(path)):
        assert(path[i] in path[i-1].neighbors())

def test_algorithms(verbose=False):
    random.seed(0)
    region = mase.HexCoord.origin().region(5)
    region_list = list(region)
    
    main_iter = range(len(region_list))
    if not verbose:
        main_iter = tqdm.tqdm(main_iter, ncols=100)
    for i in main_iter:
        start = datetime.datetime.now()
        all_dists = region_list[i].dikstra_shortest_path(region)
        delta1 = start-datetime.datetime.now()
        if verbose: print(f'i={i} dj: {delta1}')
        start = datetime.datetime.now()
        for j in range(len(region_list)):
            if i != j:
                sp = region_list[i].a_star(region_list[j])
                check_valid_path(sp)
                check_valid_path(all_dists[region_list[j]])
                print(f'\n\nsrc={region_list[i]}\ndest={region_list[j]}\n{sp=}\n{all_dists[region_list[j]]=}\n\n')
                assert_eq(len(sp), len(all_dists[region_list[j]]))
        delta2 = start-datetime.datetime.now()
        if verbose: print(f'i={i} astar: {delta2}\nratio: {delta1/delta2:04f} (dj/astar)\n')
        
        



if __name__ == '__main__':
    test_coords()
    test_algorithms()