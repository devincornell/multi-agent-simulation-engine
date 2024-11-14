from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses

from .algorithms import a_star

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


##################################################### Hexagonal #####################################################
SQRT_THREE = math.sqrt(3)
HEX_DIRECTIONS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
]

@dataclasses.dataclass(frozen=True, slots=True)
class HexCoord(BaseCoord):
    '''Cubic hexagonal position object. Supports floats or ints.'''
    q: float
    r: float
    s: float

    @classmethod
    def origin(cls) -> typing.Self:
        '''Get the origin coordinate.'''
        return cls(0, 0, 0)
    
    @classmethod
    def from_cartesian(cls, c: CartCoord, flat_top: bool = True) -> typing.Self:
        '''Convert hexagonal position to cartesian coordinates.
            For flat top:
                q = 2/3 * x
                r = y/√3 - x/3
            For pointy top:
                q = x/√3 - y/3
                r = (2/3)y
        '''

        if flat_top:
            return cls.from_rq(
                q = 2/3 * c.x,
                r = c.y / SQRT_THREE - c.x/3,
            )
        else:
            return cls.from_rq(
                q = c.x/SQRT_THREE - c.y/3,
                r = 2/3 * c.y,
            )
    
    @classmethod
    def from_rq(cls, r: float, q: float) -> typing.Self:
        '''Create a hexagonal position from r and q: r + q + s = 0.'''
        return cls(q, r, -q-r)
    
    ################################ Convert to other coordinate systems ################################
    def to_cartesian(self, flat_top: bool = True) -> CartCoord:
        '''Convert hexagonal position to cartesian coordinates.'''
        return CartCoord.from_hex(self, flat_top=flat_top)
    
    def to_radial(self) -> RadialCoord:
        '''Convert hexagonal position to radial coordinates.'''
        return RadialCoord.from_hex(self)
    
    def as_tuple(self) -> tuple[float, float, float]:
        return dataclasses.astuple(self)
    
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
    
    ################################ comparisons ################################
    def closest(self, positions: list[typing.Self]) -> typing.Self:
        '''Get the closest position to a list of positions.'''
        return min(positions, key=lambda pos: self.distance(pos))

    def distance(self, other: typing.Self) -> float:
        return (math.fabs(self.q-other.q) + math.fabs(self.r-other.r) + math.fabs(self.s-other.s))/2
    
    def isclose(self, other: typing.Self, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> bool:
        '''Check if two hexagonal positions are close.'''
        return all([
            math.isclose(self.q, other.q, rel_tol=rel_tol, abs_tol=abs_tol),
            math.isclose(self.r, other.r, rel_tol=rel_tol, abs_tol=abs_tol),
            math.isclose(self.s, other.s, rel_tol=rel_tol, abs_tol=abs_tol),
        ])

    ################################ pathfinding ################################
    def a_star(
        self, 
        goal: typing.Self, 
        allowed_pos: typing.Optional[set[typing.Self]] = None, 
        max_dist: typing.Optional[int] = None
    ) -> list[typing.Self]:
        '''Find a shortest path between this point and another. Positions should be one unit apart..'''
        return a_star(self, goal, allowed_pos=allowed_pos, max_dist=max_dist)

##################################################### Cartesian #####################################################

@dataclasses.dataclass(frozen=True, slots=True)
class CartCoord(BaseCoord):
    '''Hexagonal position object.'''
    x: float
    y: float

    @classmethod
    def origin(cls) -> CartCoord:
        return cls(0, 0)
    
    def from_radial(cls, radial: RadialCoord) -> typing.Self:
        '''Create a cartesian coordinate from a radial coordinate.'''
        return cls(
            x = radial.rho * math.cos(radial.theta),
            y = radial.rho * math.sin(radial.theta),
        )
    
    @classmethod
    def from_hex(cls, hexpos: HexCoord, flat_top: bool = True) -> typing.Self:
        '''Create a cartesian coordinate from a hexagonal position.
        Description:
            Formulas for pointy-topped grid:
                x = √(q + r/2)
                y = (3/2) * r
            Formulas for flat-topped grid:
                x = (3/2) * q
                y = √3 * (r + q/2)
        '''
        if flat_top:
            return cls(
                x = 3/2 * hexpos.q,
                y = SQRT_THREE * (hexpos.r + hexpos.q/2),
            )
        else:
            return cls(
                x = SQRT_THREE * (hexpos.q + hexpos.r/2),
                y = 3/2 * hexpos.r,
            )
    
    def to_hex(self, flat_top: bool = True) -> HexCoord:
        '''Convert cartesian coordinate to hexagonal position.'''
        return HexCoord.from_cartesian(self, flat_top=flat_top)

    def __add__(self, other: typing.Self) -> typing.Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __getitem__(self, key: int) -> float:
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError(f'Index {key} out of range for CartCoord.')
        
    def as_tuple(self) -> tuple[float, float]:
        return dataclasses.astuple(self)


##################################################### Radial #####################################################
@dataclasses.dataclass(frozen=True, slots=True)
class RadialCoord(BaseCoord):
    '''Hexagonal position object.'''
    rho: float
    theta: float

    def from_hex(cls, hexpos: HexCoord) -> RadialCoord:
        '''Create a radial coordinate from a hexagonal position.
        Description: 
            These are the formulas:
                \rho = \sqrt{3(q^2 + qr + r^2)}
                \theta = \arctan\left(\frac{\sqrt{3}(q + 2r)}{3q}\right)
        '''
        return cls(
            rho = math.sqrt(3 * (hexpos.q**2 + hexpos.r*hexpos.q + hexpos.r**2)),
            theta = math.atan2(SQRT_THREE * (hexpos.q + 2*hexpos.r) / 3*hexpos.q),
        )

