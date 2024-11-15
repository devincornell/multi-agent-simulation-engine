from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses

##################################################### Hexagonal #####################################################
class BaseCoord:
    '''Base class for hexagonal, cartesian, and radial coordinates.
    Description: has neighbors and distance methods. Make this a protocol
        someday.
    '''
    def neighbors(self) -> list[typing.Self]:
        raise NotImplementedError
    
    def distance(self, other: typing.Self) -> float:
        raise NotImplementedError

    def as_tuple(self) -> tuple[float, float]:
        return dataclasses.astuple(self)
