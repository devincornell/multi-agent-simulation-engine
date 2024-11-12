from __future__ import annotations


import copy
import dataclasses
import typing
import numpy as np

#from first.agentid import AgentID
#from .agentid import AgentID

#if typing.TYPE_CHECKING:
from .agent import Agent, AgentSet

from .location import Location, LocationState, Locations
from .position import HexPos
from .errors import *

class HexMap:
    pos_loc: typing.Dict[HexPos, Location]
    agent_positions: typing.Dict[Agent, HexPos]
    
    def __init__(self, radius: int, default_loc_state: LocationState = None):
        '''
        Args:
            movement_rule: function accepting three arguments: agent, current location, future location.
        '''
        self.radius = radius

        self.pos_loc = dict()
        self.agent_positions = dict()

        center = HexPos(0, 0, 0)
        valid_pos = center.neighbors(radius)
        valid_pos.add(center)
        self.border_pos = center.neighbors(radius+1) - valid_pos
        for pos in valid_pos:
            self.pos_loc[pos] = Location(pos, state=copy.deepcopy(default_loc_state))
    
    ############################# Dunders #############################    

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(size={self.radius})'

    def __getitem__(self, pos: HexPos) -> Location:
        return self.loc(pos)

    def __contains__(self, agent: Agent) -> bool:
        '''Check if the agent is on the map.'''
        return agent in self.agent_positions
    
    def __iter__(self) -> iter:
        return iter(self.pos_loc.values())
    
    def __len__(self) -> int:
        return len(self.pos_loc)
    
    ############################# Useful for User #############################            
    
    def region(self, center: HexPos, dist: int) -> set:
        '''Get set of positions within the given distance.'''
        return center.neighbors(dist) & set(self.pos_loc.keys())

    def region_locs(self, center: HexPos, dist: int) -> list:
        '''Get sequence of locations in the given region.'''
        return [self.loc(pos) for pos in self.region(center, dist)]
    
    def pathfind_dfs(self, src: HexPos, target: HexPos, use_loc: typing.Callable = None, max_dist: int = None):
        '''Apply pathfinding algorithm where use_loc is used to determine '
            whether a location is traversable.
        '''
        if use_loc is None:
            use_loc = lambda x: True
        useset = set(loc.pos for loc in self.locations() if use_loc(loc))
        return src.pathfind_dfs(target=target, useset=useset, max_dist=max_dist)
    
    ############################# Access/Lookup Locations/Positions/Agents #############################
    def loc(self, pos: HexPos) -> Location:
        '''Get the location at a given position.'''
        try:
            return self.pos_loc[pos]
        except KeyError:
            raise OutOfBoundsError(f'{pos} is out of bounds for map {self}.')
    
    def agent_loc(self, agent: Agent) -> Location:
        '''Get the location of the provided agent.'''
        return self.loc(self.agent_pos(agent))
    
    def agent_pos(self, agent: Agent) -> HexPos:
        '''Get the location of the provided agent.'''
        try:
            return self.agent_positions[agent]
        except KeyError:
            raise AgentDoesNotExistError(f'Agent {agent.id} does not exist on the map.')
        
    def positions(self) -> typing.Set[HexPos]:
        '''Get a set of positions in this map.'''
        return set(self.pos_loc.keys())
    
    def locations(self) -> Locations:
        '''Get locations associated with this lineup.'''
        return Locations(self.pos_loc.values())
    
    def agents(self) -> AgentSet:
        '''Get agents associated with this map.'''
        return AgentSet(self.agent_positions.keys())

    ############################# Manipulate Agents #############################
    
    def add_agent(self, agent: Agent, pos: HexPos):
        '''Add the agent to the map.'''
        if agent in self.agent_positions:
            raise AgentExistsError(f'The agent "{agent.id}" already exists on this map.')
        self.loc(pos).agents.add(agent)
        self.agent_positions[agent] = pos
        
    def remove_agent(self, agent: Agent):
        '''Remove the agent form the map.'''
        self.agent_loc(agent).agents.remove(agent)
        del self.agent_positions[agent]
        
    def move_agent(self, agent: Agent, new_pos: HexPos):
        '''Move the agent to a new location after checking rule.
        '''        
        self.remove_agent(agent)
        self.add_agent(agent, new_pos)
            
    ############################# Other Helpers #############################
    def get_info(self) -> typing.List[dict]:
        '''Get dictionary information about each location.'''
        return [loc.get_info() for loc in self.pos_loc.values()]
    
    