from __future__ import annotations

import time
import math
import pygame
import typing
import dataclasses
import random
from pathlib import Path

import sys
sys.path.append('../src')
import mase

AgentID = int
TeamID = str

@classmethod
class AgentActionsRemaining:
    '''Number of moves and attacks remaining for an agent.'''
    attacks_remaining: int
    moves_remaining: int

    def taking_move(self, num_moves: int) -> None:
        '''Return a new state after taking a move.'''
        if self.moves_remaining < num_moves:
            raise AgentOutOfMoves()
        self.moves_remaining -= num_moves

    def taking_attack(self) -> None:
        '''Return a new state after taking an attack.'''
        if self.attacks_remaining == 0:
            raise AgentOutOfAttacks()
        self.attacks_remaining -= 1
    
    def use_all(self) -> None:
        '''Zero-out all remaining moves and attacks.'''
        self.attacks_remaining = 0
        self.moves_remaining = 0

@dataclasses.dataclass
class AgentState:
    '''State of an agent.'''
    id: AgentID
    team: TeamID
    level: int
    hp: int = 100

    
    ############################## change agent stats ##############################
    def die(self) -> None:
        self.hp = 0

    def receive_attack(self, attack_power: float) -> None:
        '''Receive an attack.'''
        self.hp -= attack_power
        if self.hp <= 0:
            self.hp = 0
    
    def level_up(self) -> None:
        '''Level up the agent.'''
        old_hp_percent = self.hp / self.max_hp()
        self.level += 1

    ############################## get status of agent ##############################
    def is_alive(self) -> bool:
        '''Check if the agent is alive.'''
        return self.hp > 0

    ############################## get stats ##############################
    def attack_distance(self) -> int:
        '''Get the attack distance of the agent.'''
        return 1
    
    def attack_power(self) -> float:
        '''Get the attack power of the agent.'''
        return self.level / 3

    def max_hp(self) -> int:
        '''Get the max hp of the agent.'''
        return 100 + 30 * self.level

    def max_actions_allowed(self) -> AgentActionsRemaining:
        '''Get the number of moves remaining for the agent.'''
        return AgentActionsRemaining(attacks_remaining=1, moves_remaining=self.level)

class AgentStates(dict[AgentID, AgentState]):
    '''Mapping from agent id to agent state.'''
    @classmethod
    def init(cls, num_agents: dict[TeamID, int], start_level: int = 1) -> AgentStates:
        '''Initialize all agents with the same level.'''
        agents = dict()
        current_id = 0
        for tid,num in num_agents.items():
            for i in range(num):
                agents[current_id] = AgentState(current_id, tid, start_level)
                current_id += 1
        return cls(agents)

@dataclasses.dataclass
class LocState:
    '''State of a location.'''
    pos: mase.HexCoord
    items: set[str]
    blocked: bool = False

    @classmethod
    def new_empty(cls, pos: mase.HexCoord) -> LocState:
        '''Create an empty location state.'''
        return cls(pos, set())

class LocStates(dict[mase.HexCoord, LocState]):
    '''Mapping from locationt to location state.'''
    @classmethod
    def init(cls, map_size: int) -> LocStates:
        '''Initialize all locations with no items.'''
        locs = dict()
        for pos in mase.HexCoord.origin().region(map_size):
            locs[pos] = LocState.new_empty(pos)
        return cls(locs)

class AgentIsAlreadyAtLocation(Exception):
    pass
class AnotherAgentIsAtTargetLocation(Exception):
    pass
class AgentDoesNotExist(Exception):
    pass
class LocationDoesNotExist(Exception):
    pass
class AgentDoesNotBelongToTeam(Exception):
    pass
class AgentOutOfMoves(Exception):
    pass
class AgentOutOfAttacks(Exception):
    pass
class TargetAgentDoesNotExist(Exception):
    pass
class AgentNotOnMap(Exception):
    pass
class NoRouteToTarget(Exception):
    pass
class CantAttackSameTeam(Exception):
    pass
class TargetTooFarAwayForAttack(Exception):
    pass
class AgentIsDead(Exception):
    pass

@dataclasses.dataclass
class GameState:
    agents: AgentStates
    locations: LocStates
    map: mase.ObjectMapper[AgentID, mase.HexCoord]

    @classmethod
    def new(cls, num_agents: dict[TeamID, int], map_size: int):
        '''Create a new agent.'''
        agent_states = AgentStates.init(num_agents, start_level=1)
        location_states = LocStates.init(map_size)

        # put agents in random locations
        agent_locations = mase.ObjectMapper()
        for agent_id in agent_states.keys():
            while True:
                pos = random.choice(location_states.keys())
                if not len(agent_locations.get_objs(pos)):
                    agent_locations.add_obj(agent_id, pos)
                    break
        return cls(
            agents=agent_states,
            locations=location_states,
            map = agent_locations,
        )
    
    def get_ctrlr(self, team_id: TeamID) -> TeamCtrlr:
        '''Get a controller for a team.'''
        return TeamCtrlr.start_turn(team_id=team_id, game=self)


@dataclasses.dataclass
class TeamCtrlr:
    '''Keep track of moves from a particular team.'''
    team_id: TeamID
    game: GameState
    remaining_moves: dict[AgentID, AgentActionsRemaining]

    @classmethod
    def start_turn(cls, team_id: TeamID, game: GameState) -> typing.Self:
        '''Start the turn for the team.'''
        #remaining_moves = {aid: 1 for aid in game.agents.keys() if game.agents[aid].team == team_id}
        cls(
            team_id=team_id,
            game=game,
            remaining_moves={aid: game.agents[aid].max_actions_allowed() for aid in game.agents.keys() if game.agents[aid].team == team_id and game.agents[aid].is_alive()}
        )
    
    ############################## available moves ##############################
    def attack(self, agent_id: AgentID, target_id: AgentID) -> int:
        '''Have one agent attack another.'''
        agent, loc = self.get_agent_state(agent_id, require_sameteam=True, require_alive=True)
        target_agent, target_loc = self.get_agent_state(target_id, require_alive=True)
        
        if target_agent.team == self.team_id:
            raise CantAttackSameTeam()
        
        if loc.pos.distance(target_loc.pos) > agent.attack_distance():
            raise TargetTooFarAwayForAttack()
        


    def kill_agent(self, agent_id: AgentID) -> None:
        '''Kill an agent.
        Description: changes agent stats, removes agent from the map, and removes
            agent from the remaining moves.
        '''
        agent = self.agents[agent_id]
        agent.die()
        self.map.remove_obj(agent_id)
        del self.remaining_moves[agent_id]


    def move_agent(self, agent_id: AgentID, new_pos: mase.HexCoord):
        '''Move an agent to a new position.
        Description: implements a lot of checks against remaining turns and 
            agent/location states. Most of this function is game logic.
        '''
        # check agent being moved
        agent, old_loc = self.get_agent_state(agent_id)
        if agent.team != self.team_id:
            raise AgentDoesNotBelongToTeam()
        
        if new_pos not in self.locations:
            raise LocationDoesNotExist()
        
        if len(self.map.get_objs(new_pos)):
            raise AnotherAgentIsAtTargetLocation()
                
        move_through_set = self.get_valid_move_through_set()

        # check if there is a shortest path, get it if there is
        try:
            shortest_path = old_loc.pos.a_star(new_pos, move_through_set)
        except mase.NoPathFound:
            raise NoRouteToTarget(
                f'Agent {agent_id} tried to move from '
                f'{old_loc.pos} to {new_pos}, but there is no path.'
            )

        # change game state to reflect the move, rais exception if issue
        self.remaining_moves[agent_id].taking_move(len(shortest_path) - 1)
        self.map.move_obj(agent_id, new_pos)

    ############################## get agents from this and other teams ##############################
    def get_valid_move_to_set(self) -> set[mase.HexCoord]:
        '''Get locations that player can move to.'''
        move_coords = set()
        for pos, loc in self.game.locations.items():
            if not loc.blocked and not len(self.game.map.get_objs(pos)):
                move_coords.add(pos)
        
        return move_coords

    def get_valid_move_through_set(self) -> set[mase.HexCoord]:
        '''Get locations that player can move through.'''
        move_coords = set()
        for pos, loc in self.game.locations.items():
            if not loc.blocked:
                
                # check for other-team agents
                exist_agents = self.game.map.get_objs(pos)
                if not any([self.game.agents[aid].team != self.team_id for aid in exist_agents]):
                    move_coords.add(pos)
    
        return move_coords
    
    def _get_target_move_loc(self, new_pos: mase.HexCoord) -> LocState:
        '''Get the new position of an agent, checking to make sure everything is good.'''
        try:
            loc = self.locations[new_pos]
        except KeyError:
            raise LocationDoesNotExist()
        
        if len(self.map.get_objs(new_pos)):
            raise AnotherAgentIsAtTargetLocation()

        return loc
    
    def get_agent_state(self, 
        agent_id: AgentID, 
        require_sameteam: bool = False,
        require_alive: bool = True,
    ) -> tuple[AgentState, LocState]:
        '''Get the agent and its location, checking to make sure everything is good.'''
        try:
            agent = self.agents[agent_id]
        except KeyError:
            raise AgentDoesNotExist()
        
        try:
            agent_pos: mase.HexCoord = self.map.get_coord(agent_id)
        except mase.ObjectIsNotOnMap:
            raise AgentNotOnMap()
        
        try:
            loc = self.locations[agent_pos]
        except KeyError:
            raise LocationDoesNotExist()
        
        if require_sameteam:
            if agent.team != self.team_id:
                raise AgentDoesNotBelongToTeam()
            
        if require_alive:
            if not agent.is_alive():
                raise AgentIsDead()

        return agent, loc

        
    ############################## get agents from this and other teams ##############################
    def get_other_team_agents(self, other_team_id: TeamID|None = None, require_alive: bool = True) -> set[AgentID]:
        '''Get the agents of this team.'''
        if other_team_id is None:
            return self.get_agents(lambda agent: agent.team != self.team_id and (not require_alive or agent.is_alive()))
        else:
            return self.get_agents(lambda agent: agent.team == other_team_id and (not require_alive or agent.is_alive()))
    
    def get_team_agents(self, require_alive: bool = True) -> set[AgentID]:
        '''Get the agents of a team.'''
        return self.get_agents(lambda agent: agent.team == self.team_id and (not require_alive or agent.is_alive()))

    def get_agents(self, filter_criteria: typing.Callable[[AgentState],bool]) -> dict[AgentID, AgentState]:
        '''Get all agents.'''
        return {aid: agent for aid, agent in self.game.agents.items() if filter_criteria(agent)}

    @property
    def agents(self) -> dict[AgentID, AgentState]:
        '''Get all agents.'''
        return self.game.agents
    
    @property
    def locations(self) -> dict[mase.HexCoord, LocState]:
        '''Get all locations.'''
        return self.game.locations
    
    @property
    def map(self) -> mase.ObjectMapper[AgentID, mase.HexCoord]:
        '''Get the agent locations.'''
        return self.game.map


def main():
    teams = ['red', 'blue']
    game = GameState.new({tid:10 for tid in teams}, map_size=30)
    for tid in teams:
        ctrlr = game.get_ctrlr(tid)
        print(ctrlr)




if __name__ == '__main__':
    main()