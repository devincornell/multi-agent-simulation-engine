from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses


CartUnit = int
'''Unit in cartesian coordinates.'''

@dataclasses.dataclass(frozen=True, slots=True)
class CartCoord:
    '''Hexagonal position object.'''
    q: CartUnit
    r: CartUnit

    @classmethod
    def from_origin(cls) -> CartCoord:
        return cls(0, 0)

    def __add__(self, other: CartCoord) -> CartCoord:
        return CartCoord(self.q + other.q, self.r + other.r)
