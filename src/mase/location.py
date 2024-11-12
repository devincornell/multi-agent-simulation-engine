import dataclasses
import math
import typing
import copy

#from .position import Position
from .position import HexPos
#from .agentid import AgentID
from .agent import Agent, AgentSet

#MapType = typing.TypeVar('MapType')

@dataclasses.dataclass
class LocationState:
    '''Maintains state for each location.'''
    def deepcopy(self):
        '''Create a copy of itself for sharing with the user.'''
        return copy.deepcopy(self)
    
    def get_info(self) -> typing.Dict:
        '''Get info for data collection.'''
        #raise NotImplementedError('Must implement get_info() in the LocationState object implementation.')
        return {}

class Location:
    __slots__ = ['pos', 'state', 'agents']
    pos: HexPos
    state: LocationState
    agents: AgentSet

    def __init__(self, pos: HexPos, state: type = None, agents: AgentSet = None):
        '''
        Args:
            state: custom game state.
        '''
        self.pos = pos
        self.state = copy.copy(state) if state is not None else None
        self.agents = AgentSet(copy.copy(agents)) if agents is not None else AgentSet()
        
    def __repr__(self):
        return f'{self.__class__.__name__}(pos={self.pos}, state={self.state}, agents={self.agents})'
        
    ############################# Working With Resources #############################    
    def __contains__(self, agent: Agent) -> bool:
        '''Check if this location contains the agent.'''
        return agent in self.agents
    
    @property
    def num_agents(self):
        '''Get number of agents in this location.'''
        return len(self.agents)
        
    ############################# Utility #############################    
    def get_info(self) -> typing.Dict:
        '''Get a dict of info about this location.'''
        q, r, s = self.pos.coords()
        return {
            #'q': q, 'r': r, 's': s, 
            'coords': self.pos.coords(),
            #'x': self.pos.x, 'y': self.pos.y, 
            'xy': self.pos.coords_xy(),
            'agents': [a.id for a in self.agents], 
            **self.state.get_info()
        }
    
    ############################# Manipulating Agents #############################
    def add_agent(self, agent: Agent):
        '''Adds agent to this location.'''
        self.agents.add(agent)
        
    def remove_agent(self, agent: Agent):
        '''Removes agent to this location.'''
        self.agents.remove(agent)
        

        

class Locations(typing.List):
    #def __call__(self, **kwargs):
    #    return self.__class__(sorted(self, **kwargs))
    
    def filter(self, func: typing.Callable):
        return self.__class__([l for l in self if func(l)])

#@dataclasses.dataclass
#class LocationView(Location):
#    '''Can be shared with user without modifying original.'''
#    __slots__ = ['pos', 'state', 'agents']
#    pos: typing.Tuple
#    state: LocationState
#    agents: typing.Set[AgentID]
    