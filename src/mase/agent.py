from __future__ import annotations

import typing
import dataclasses
import random

if typing.TYPE_CHECKING:
    from .hexmap import HexMap
    from .location import Location, Locations
#from mase.position import HexPos

from .errors import *

from .position import HexPos
#
from .agentid import AgentID
#from .hexnetmap import HexNetMap
#from .agentpool import AgentPool
#AgentPoolType = typing.TypeVar('AgentPoolType')
#LocationType = typing.TypeVar('LocationType')
#HexMapType = typing.TypeVar('HexMapType')



#@dataclasses.dataclass
class AgentState:
    def get_info(self):
        '''Get info dictionary for final game output.'''
        raise NotImplementedError('Must implement get_info for the AgentState object.')
    
@dataclasses.dataclass
class Agent:
    '''Represents a single agent in the model. Interface over pool and map.'''
    id: AgentID
    state: AgentState
    _map: HexMap = None
    
    def __pos_init__(self):
        # make sure agent is in map
        pos = self.pos
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other: Agent):
        '''Compare ids.'''
        return (
            self.__class__ == other.__class__ and 
            self.id == other.id
        )
    
    
    def get_info(self) -> typing.Dict:
        return {
            'id': self.id, 
            'xy': self.pos.coords_xy(),
            'pqr': self.pos.coords(),
            **self.state.get_info()
        }
    
    ##################### Map Access Functions #####################
    @property
    def map(self) -> HexMap:
        '''Access the attached map or raise exception. For internal use.'''
        if self._map is not None:
            return self._map
        else:
            raise MapIsNotAttachedError(f'A map was not attached to this {self.__class__.__name__}.')
            
    @property
    def map_attached(self):
        '''Check if map is attached. For internal use.'''
        return self._map is not None

    def set_map(self, map: HexMap):
        '''Set reference to a map. For internal use.'''
        self._map = map
    
    @property
    def pos(self) -> HexPos:
        '''Agents current position.'''
        return self.map.agent_pos(self)
    
    @property
    def loc(self) -> Location:
        '''Location at Agents current position.'''
        return self.map.agent_loc(self)
    
    ##################### Utility Functions for User #####################
    def pathfind_dfs(self, target: HexPos, use_loc: typing.Callable = None, max_dist: int = None):
        '''Apply pathfinding algorithm where use_loc is used to determine '
            whether a location is traversable.
        '''
        return self.map.pathfind_dfs(src=self.pos, target=target, use_loc=use_loc, max_dist=max_dist)
    
    def nearest_agents(self) -> AgentSet:
        '''Get agents nearest to this agent after filtering criteria.'''
        sortkey = lambda a: self.pos.dist(a.pos)
        return AgentSet([a for a in sorted(self.map.agents(), key=sortkey) if a != self])

    def nearest_locations(self) -> Locations:
        '''Get locations nearest to this agent.'''
        sortkey = lambda loc: self.pos.dist(loc.pos)
        return list(sorted(self.map.locations(), key=sortkey))
    
    def neighbor_locs(self, dist: int = 1) -> Locations:
        '''Get locations within specified distance.'''
        return self.map.region_locs(self.pos, dist=dist)
        
    ##################### Pathfinding Functions #####################
    def shortest_path(self, target: HexPos, allowed_pos: typing.Set[HexPos], **kwargs):
        '''Use A* heuristic-based shortest path algorithm to find shortest path to target.'''
        return self.pos.shortest_path(target, allowed_pos=allowed_pos, **kwargs)
    
    def pathfind_dfs(self, target: HexPos, use_positions: typing.Set[HexPos]):
        '''Find the first path from source to target using dfs.
        Args:
            use_positions: valid movement positions.
        '''
        return self.pos.pathfind_dfs(target, use_positions)

    def pathfind_dfs_avoid(self, target: tuple, avoid_positions: typing.Set[HexPos]):
        '''Find the first path from source to target using dfs.
        Args:
            avoid_positions: set of positions to avoid when pathfinding.
        '''
        return self.pos.pathfind_dfs_avoid(target, avoid_positions)


class AgentSet(typing.Set[Agent]):
    def random_activation(self) -> typing.List[Agent]:
        '''Get agents in a random order.'''        
        return list(random.sample(list(self), len(self)))


