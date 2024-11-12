import dataclasses
import typing

from .hexmap import HexMap
from .position import HexPos
from .agentstatepool import AgentStatePool, AgentID

@dataclasses.dataclass
class ABModel:
    '''Serves to integrate AgentStatePool and HexMap functionality.'''
    map: HexMap
    pool: AgentStatePool
    
    
    ############################# Finding Nearest Agents/Positions #############################
    def nearest_agents(self, agent_id: AgentID, agent_filter: typing.Callable = lambda agent: True):
        '''Get agents nearest to the provided agent after filtering criteria.'''
        target = self.map.get_agent_pos(agent_id)
        sortkey = lambda pos: target.dist(pos)
        return [self.pool[aid] for aid in self.map.agents(sortkey) if agent_filter(self.pool[aid])]

    def nearest_agents_pos(self, target: tuple, agent_filter: typing.Callable = lambda agent: True):
        '''Get agents nearest to the provided position after filtering criteria.'''
        target = self.map.PositionType(*target)
        sortkey = lambda pos: target.dist(pos)
        return [self.pool[aid] for aid in self.map.agents(sortkey) if agent_filter(self.pool[aid])]
        
    def nearest_locs(self, agent_id: AgentID, loc_filter: typing.Callable = lambda agent: True):
        '''Get locations nearest to the provided position after filtering criteria.'''
        target = self.map.PositionType(*target)
        sortkey = lambda pos: target.dist(pos)
        return [self.pool[aid] for loc in self.map.locations(filter=loc_filter, sortkey=sortkey)]

        
    #locations
    #def nearest_agents_base(self, target: HexPos, agent_criteria: typing.Callable = lambda agent: True):
    #    sort = lambda loc: target.dist(loc)
    #    filt = lambda loc: len(loc.agents)
    #    locs = self.map.locations(filter=filt, sort=sort)
        
        #sortkey = lambda aid, pos: target.dist(pos)
        #nearest_ids = [aid for aid,pos in sorted(self.map.agent_pos.items(), key=sortkey)]
        #return [self.pool[aid] for aid in nearest_ids if agent_criteria(self.pool[aid])]
    
    ############################# User Interface #############################
    def pathfind_dfs(self, agent_id: AgentID, target: tuple, avoid_positions: typing.Set[tuple]):
        '''Find the first path from source to target using dfs.
        Args:
            avoid_positions: set of positions to avoid when pathfinding.
        '''
        avoidset = {self.PositionType(*pos) for pos in avoid_positions}
        source_pos, target_pos = self.map.get_agent_pos(agent_id), self.PositionType(*target)
        return source_pos.pathfind_dfs(target_pos, avoidset)
        
    def nearest_locations(self, position: tuple, criteria: typing.Callable = lambda loc: True):
        '''Get locations nearest to the provided position after filtering criteria.'''
        target = self.PositionType(*position)
        sortkey = lambda pos, loc: target.dist(pos)
        return [pos for pos,loc in sorted(self.locs.items(), key=sortkey) if criteria(loc)]




