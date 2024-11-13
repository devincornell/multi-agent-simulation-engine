
from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses

from .cart_coord import CartCoord


@dataclasses.dataclass(frozen=True, slots=True)
class RadialCoord:
    '''Hexagonal position object.'''
    rho: float
    theta: float

    def to_cart(cls) -> CartCoord:
        return CartCoord(
            x = rho, 
            theta = theta,
        )




