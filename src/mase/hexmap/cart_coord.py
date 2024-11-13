from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses


CartUnit = float
'''Unit in cartesian coordinates.'''

@dataclasses.dataclass(frozen=True, slots=True)
class CartCoord:
    '''Hexagonal position object.'''
    x: CartUnit
    y: CartUnit

    @classmethod
    def from_origin(cls) -> CartCoord:
        return cls(0, 0)

    def __add__(self, other: CartCoord) -> CartCoord:
        return self.__class__(self.x + other.x, self.y + other.y)
