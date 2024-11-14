from __future__ import annotations

import numpy as np
import typing
import math
#import itertools
import math
import dataclasses

#from .position import Position
#from .algorithms import a_star

#from .cart_coord import CartCoord, CartUnit
#from .rad_coord import RadialCoord




##################################################### Hexagonal #####################################################
SQRT_THREE = math.sqrt(3)
HEX_DIRECTIONS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
]


class NoPathFound(Exception):
    @classmethod
    def from_src_and_dest(cls, src: typing.Self, dest: typing.Self) -> typing.Self:
        return cls(f'No path found from {src} to {dest}.')


@dataclasses.dataclass(frozen=True, slots=True)
class HexCoord:
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
            === FLAT TOP ===

            Premise: given q and r, we can calculate x and y.
            x = 3/2 * q
            y = √3 * (r + q/2)

            # cartesian to hex: given x and y, calculate q and r
            # q is easy - inverse of 2/3.
            q = 2/3 * x

            # r is harder: invert the previous function
            y = √3 * (r + q/2) 
            r + q/2 = y / √3 divide by √3 and flip sides
            r + (2/3)x/2 = y / √3
            r + (1/3)x = y / √3
            r = y/√3 - x/3


            === NON FLAT TOP ===
            premis: given q and r, we can calculate x and y.
            x = √3 * (q + r/2)
            y = 3/2 * r

            # cartesian to hex: given x and y, calculate q and r
            # q is easy - inverse of √3.
            r = (2/3)y

            # r is harder: invert the previous function
            x/√3 = q + r/2
            x/√3 = q + (2/3)y/2 # replace r with (2/3)y
            q = x/√3 - y/3 # move y/3 to the other side
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
    
    ################################ Convert between coordinate systems ################################
    def to_cartesian(self, flat_top: bool = True) -> CartCoord:
        '''Convert hexagonal position to cartesian coordinates.'''
        return CartCoord.from_hex(self, flat_top=flat_top)
    
    def to_radial(self) -> RadialCoord:
        '''Convert hexagonal position to radial coordinates.'''
        return RadialCoord.from_hex(self)
    
    def as_tuple(self) -> tuple[float, float, float]:
        return dataclasses.astuple(self)
    
    ################################ comparisons ################################
    def isclose(self, other: typing.Self, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> bool:
        '''Check if two hexagonal positions are close.'''
        return all([
            math.isclose(self.q, other.q, rel_tol=rel_tol, abs_tol=abs_tol),
            math.isclose(self.r, other.r, rel_tol=rel_tol, abs_tol=abs_tol),
            math.isclose(self.s, other.s, rel_tol=rel_tol, abs_tol=abs_tol),
        ])


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
    
    ################################ Distances and math ################################
    def distance(self, other: typing.Self) -> float:
        return (math.fabs(self.q-other.q) + math.fabs(self.r-other.r) + math.fabs(self.s-other.s))/2
    
    ################################ pathfinding ################################
    def a_star(
        self, 
        goal: typing.Self, 
        allowed_pos: typing.Optional[set[typing.Self]] = None, 
        max_dist: typing.Optional[int] = None
    ) -> list[typing.Self]:
        '''Compute the A-star algorithm on a hex grid.'''

        open_set: list[typing.Self] = [self]
        came_from: dict[typing.Self, typing.Self] = {}
        g_score: dict[typing.Self,int] = {self: 0}
        f_score: dict[typing.Self, float] = {self: self.distance(goal)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            open_set.remove(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self)
                path.reverse()
                return path

            for neighbor in current.neighbors():
                if allowed_pos is not None and neighbor not in allowed_pos:
                    continue

                tentative_g_score = g_score[current] + 1

                if max_dist is not None and tentative_g_score > max_dist:
                    continue

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + neighbor.distance(goal)
                    if neighbor not in open_set:
                        open_set.append(neighbor)

        raise NoPathFound.from_src_and_dest(self, goal)



    ################################ Depricated Pathfinding ################################

    def pathfind_dfs(self, target: typing.Self, useset: typing.Set[typing.Self] = None, 
            max_dist: int = None, verbose: bool = False) -> typing.List[typing.Self]:
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


    def shortest_path_length(self, target: typing.Self, avoidset: set) -> int:
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
    
    def fringe(self, others: typing.Set[typing.Self], dist: int = 1) -> typing.Set[typing.Self]:
        '''Get positions on the fringe of the provided nodes.'''
        others = others | set([self])
        fringe = set()
        for pos in others:
            fringe |= pos.neighbors(dist)
        return fringe - others

    def pathfind_dfs_avoid(self, target: typing.Self, avoidset: set = None, max_dist: int = None, verbose: bool = False) -> typing.List[typing.Self]:
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



##################################################### Cartesian #####################################################

@dataclasses.dataclass(frozen=True, slots=True)
class CartCoord:
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
                x_{\text{cartesian}} &= \sqrt{3} \left(q + \frac{r}{2}\right) \\
                y_{\text{cartesian}} &= \frac{3}{2} r
            Formulas for flat-topped grid:
                x &= \text{size} \times \left( \dfrac{3}{2} \times q \right) \\
                y &= \text{size} \times \left( \sqrt{3} \times \left( r + \dfrac{q}{2} \right) \right)
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
class RadialCoord:
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

