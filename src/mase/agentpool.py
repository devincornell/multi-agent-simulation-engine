import dataclasses
import typing
import random
import copy

from matplotlib.colors import hexColorPattern

from .position import HexPos
from .hexmap import HexMap
from .agent import Agent, AgentState
from .agentid import AgentID
from .errors import *

@dataclasses.dataclass
class AgentPool:
    '''Contains set of agents.'''
    agents: typing.Dict[AgentID, Agent] = dataclasses.field(default_factory=dict)
    _map: HexMap = None
    
    ##################### Access to Agents #####################
    def __contains__(self, agent_id: AgentID):
        return agent_id in self.agents
    
    def __getitem__(self, agent_id: AgentID):
        try:
            return self.agents[agent_id]
        except KeyError:
            raise AgentDoesNotExistError(f'Could not retrieve agent: {agent_id} does not exist in this {self.__class__.__name__}.')
        
    def __iter__(self):
        return iter(self.agents.values())
    
    def __len__(self):
        return len(self.agents)
    
    @property
    def ids(self) -> typing.List[AgentID]:
        return list(self.agents.keys())
    
    ##################### Access to Map #####################
    def add_map(self, map):
        '''Add the map to this pool.'''
        self._map = map
    
    @property
    def map(self):
        if self._map is not None:
            return self._map
        else:
            MapIsNotAttachedError(f'Couldn\'t access map because it not attached to this {self.__class__.__name__}.')
            
    @property
    def map_attached(self):
        return self._map is not None
        
    ##################### Add/Remove Functions #####################
    def add_agent(self, agent_id: AgentID, agent_state: AgentState, pos: HexPos):
        '''Create new agent and add it to the pool.
        '''
        if agent_id in self.agents:
            raise AgentExistsError(f'The agent {agent_id} already exists in this pool.')

        agent = Agent(agent_id, copy.deepcopy(agent_state), self, self._map)
        if self.map_attached:
            self.map.add_agent(agent.id, pos)
        self.agents[agent.id] = agent
        
    def remove_agent(self, agent_id: AgentID):
        try:
            del self.agents[agent_id]
        except KeyError:
            raise AgentDoesNotExistError(f'The agent {agent_id} does not exist in this pool.')
        if self.map_attached:
            self.map.remove_agent(agent_id)
    
    ##################### Activation/Scheduling Functions #####################
    def random_activation(self) -> typing.List[AgentID]:
        '''Get agent ids in a random order.'''
        return list(random.sample(self.values(), len(self)))
        
    ##################### View-Related Functions #####################
    def deepcopy(self):
        return copy.deepcopy(self)
    
    def get_info(self):
        return [agent.get_info() for agent in self]










