import random
import time
import math
import pygame
import typing
import dataclasses
from pathlib import Path

import sys
sys.path.append('../src')
import mase

def test_coords():
    random.seed(0)
    int_pos = mase.HexCoord.origin().region(100)
    rand_pos = [mase.HexCoord.from_rq(random.random(), random.random()) for _ in range(100)]
    positions = list(int_pos) + rand_pos

    for pos in positions:
        c = pos.to_cartesian()
        h = c.to_hex()
        print(h, pos)
        assert(h.isclose(pos))


if __name__ == '__main__':
    test_coords()