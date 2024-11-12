import random
import typing
import copy
import dataclasses

from .errors import *
#from .agentstate import AgentID, AgentState
from .agent import AgentID, AgentState


class AgentStatePool(typing.Dict[AgentID, AgentState]):
    '''Keeps track of agent states.
    '''
    ##################### View-Related Functions #####################
    def agents(self, filter_criteria: typing.Callable = lambda astate: True):
        '''Get the agents after applying filter criteria.'''
        return [astate for astate in self.values() if filter_criteria(astate)]
    
    ##################### Add/Remove Functions #####################
    def add_agent(self, agent_id: AgentID, agent_state: AgentState):
        if agent_id in self:
            raise AgentExistsError(f'The agent {agent_id} already exists in this pool.')
        self[agent_id] = agent_state
        
    def remove_agent(self, agent_id: AgentID):
        try:
            del self[agent_id]
        except KeyError:
            raise AgentDoesNotExistError(f'The agent {agent_id} does not exist in this pool.')
        
    def get_agent(self, agent_id: AgentID) -> AgentState:
        try:
            return self[agent_id]
        except KeyError:
            raise AgentDoesNotExistError(f'The agent {agent_id} does not exist in this pool.')

    ##################### Activation Functions #####################
    def random_activation(self) -> typing.List[AgentID]:
        '''Get agent ids in a random order.'''
        return list(random.sample(self.keys(), len(self)))
    
    def ordered_activation(self, sort_key: typing.Callable):
        '''Activate agents according to some sorting criteria.'''
        
    ##################### View-Related Functions #####################
    def deepcopy(self):
        return copy.deepcopy(self)
    
    def get_info(self):
        return {aid: state.get_info() for aid, state in self.items()}
