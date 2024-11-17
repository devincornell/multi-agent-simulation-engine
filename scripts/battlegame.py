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

@dataclasses.dataclass
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
    level: int = 1
    hp: int = 100

    ############################## modify agent stats ##############################
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
        self.hp = self.max_hp() * old_hp_percent

    ############################## get status of agent ##############################
    def is_alive(self) -> bool:
        '''Check if the agent is alive.'''
        return self.hp > 0

    ############################## get stats for actions ##############################
    def max_actions_allowed(self) -> AgentActionsRemaining:
        '''Get the number of moves remaining for the agent.'''
        if self.is_alive():
            return AgentActionsRemaining(
                attacks_remaining=1, 
                moves_remaining=self.move_distance(),
            )
        else:
            return AgentActionsRemaining(
                attacks_remaining=0, 
                moves_remaining=0,
            )

    def move_distance(self) -> int:
        '''Get the move distance of the agent.'''
        return self.level
    
    def attack_distance(self) -> int:
        '''Get the attack distance of the agent.'''
        return 1
    
    def attack_power(self) -> float:
        '''Get the attack power of the agent.'''
        return self.level / 3

    def max_hp(self) -> int:
        '''Get the max hp of the agent.'''
        return 100 + 30 * self.level

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
class TargetLocationIsBlocked(Exception):
    pass
class TargetIsTooFar(Exception):
    pass

@dataclasses.dataclass
class GameState:
    agents: AgentStates
    locations: LocStates
    map: mase.ObjectMapper[AgentID, mase.HexCoord]

    @classmethod
    def new(cls, num_agents: dict[TeamID, int], map_size: int, random_seed: int = 0) -> typing.Self:
        '''Initialize a new game state.'''
        random.seed(random_seed)

        agent_states = AgentStates.init(num_agents, start_level=1)
        location_states = LocStates.init(map_size)

        # put agents in random locations
        agent_locations = mase.ObjectMapper()
        for agent_id in agent_states.keys():
            while True:
                pos = random.choice(list(location_states.keys()))
                if not len(agent_locations.get_objs(pos)):
                    agent_locations.add_obj(agent_id, pos)
                    break
        return cls(
            agents=agent_states,
            locations=location_states,
            map = agent_locations,
        )
    
    def get_ctrlr(self, team_id: TeamID) -> TeamCtrlr:
        '''Get a controller for a particular team.'''
        return TeamCtrlr.start_turn(team_id=team_id, game=self)

    ################################## check to modify game state information ##############################
    def compute_attack_damage(self, agent_id: AgentID, target_id: AgentID) -> tuple[AgentState, AgentState, float]:
        '''Perform checks for attack from one agent to another.
        Returns:
            agent, target_agent, attack_power
        '''
        agent, loc = self.get_agent_and_loc(agent_id)
        target_agent, target_loc = self.get_agent_and_loc(target_id)
        
        if agent.team == target_agent.team:
            raise CantAttackSameTeam()
        
        if loc.pos.distance(target_loc.pos) > agent.attack_distance():
            raise TargetTooFarAwayForAttack()
        
        return agent, target_agent, agent.attack_power()

    def kill_agent(self, agent_id: AgentID) -> None:
        '''Take agent off the map and change agent state.
        Description: changes agent stats, removes agent from the map.
        '''
        self.map.remove_obj(agent_id)
        self.agents[agent_id].die()

    def compute_shortest_path(self, agent_id: AgentID, new_pos: mase.HexCoord, max_dist: int | None = None) -> bool:
        '''Perform checks for moving an agent to a new location.
        Description: Use when trying to move an agent, because it will perform all the general checks.
        Returns: shortest path from an agent to a location, raise exceptions if there is no path.
        '''
        agent, old_loc = self.get_agent_and_loc(agent_id)

        if old_loc.pos == new_pos:
            raise AgentIsAlreadyAtLocation()

        try:
            new_loc = self.locations[new_pos]
        except KeyError:
            raise LocationDoesNotExist()

        if new_loc.blocked:
            raise TargetLocationIsBlocked()

        if len(self.map.get_objs(new_pos)):
            raise AnotherAgentIsAtTargetLocation()

        # check if there is a shortest path, get it if there is
        try:
            shortest_path = old_loc.pos.a_star(
                goal=new_pos, 
                allowed_pos=self.valid_move_through_set(agent_id),
                max_dist=max_dist,
            )
        except mase.NoPathFound:
            raise NoRouteToTarget(
                f'Agent {agent_id} tried to move from '
                f'{old_loc.pos} to {new_pos}, but there is no path.'
            )
        
        if len(shortest_path) > max_dist:
            raise TargetIsTooFar()
        
        return shortest_path


    ################################## access game state information ##############################
    def valid_move_to_set(self, agent_id: AgentID, max_moves: int|None = None) -> dict[mase.HexCoord, list[mase.HexCoord]]:
        '''Get positions that an agent can move to and the paths they would take.'''
        agent, loc = self.get_agent_and_loc(agent_id)
        move_through_set = [pos for pos, loc in self.locations.items() if self.check_agent_can_move_through(agent_id, pos)]
        sps = loc.pos.dijkstra(
            allowed_pos=move_through_set,
            max_dist=max_moves, 
        )
        return {pos:sp for pos,sp in sps.items() if len(sp) and (max_moves is None or len(sp) <= max_moves)}
        
    def check_agent_can_move_to(self, agent_id: AgentID, pos: mase.HexCoord) -> bool:
        '''Check if an agent can move to a location. Does not consider distance/path.
        Description: checks if the location is blocked or if there is another agent there.
        '''
        agent, loc = self.get_agent_and_loc(agent_id)
        if loc.blocked or len(self.map.get_objs(pos)):
            return False
        return True

    def valid_move_through_set(self, agent_id: AgentID) -> set[mase.HexCoord]:
        '''Get locations that player can move through. Much simpler'''
        move_coords = set()
        for pos in self.locations.items():
            if self.check_agent_can_move_through(agent_id, pos):
                move_coords.add(pos)
    
        return move_coords

    def check_agent_can_move_through(self, agent_id: AgentID, pos: mase.HexCoord) -> bool:
        '''Check if an agent can move through a location. Does not consider distance/path.
        Description: checks if the location is blocked or if there is another agent there.
        '''
        agent, loc = self.get_agent_and_loc(agent_id)
        if loc.blocked or any([self.agents[aid].team != agent.team for aid in self.map.get_objs(pos)]):
            return False
        return True

    def get_agent_and_loc(self, 
        agent_id: AgentID, 
    ) -> tuple[AgentState, LocState]:
        '''Get the agent and its location, make sure agent is on map.'''
        try:
            agent = self.agents[agent_id]
        except KeyError:
            raise AgentDoesNotExist()
        
        try:
            agent_pos: mase.HexCoord = self.map.get_coord(agent_id)
        except mase.ObjectIsNotOnMap:
            raise AgentIsDead()
        
        # hopefully redundant (agent is missing from map iif dead)
        if not agent.is_alive():
            raise AgentIsDead()
        
        try:
            loc = self.locations[agent_pos]
        except KeyError:
            raise LocationDoesNotExist()
        

        return agent, loc



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
        return cls(
            team_id=team_id,
            game=game,
            remaining_moves={aid: game.agents[aid].max_actions_allowed() for aid in game.agents.keys() if game.agents[aid].team == team_id and game.agents[aid].is_alive()}
        )
    
    ############################## available moves ##############################
    def attack(self, agent_id: AgentID, target_id: AgentID) -> int:
        '''Have one agent attack another.'''
        agent, target, attack_power = self.game.compute_attack_damage(agent_id, target_id)
        
        # note that an attack action was taken and update agent state
        self.remaining_moves[agent_id].taking_attack()
        target.receive_attack(attack_power)
        if not target.is_alive():
            self.game.kill_agent(target_id)

    def move_agent(self, agent_id: AgentID, new_pos: mase.HexCoord):
        '''Move an agent to a new position.
        Description: implements a lot of checks against remaining turns and 
            agent/location states. Most of this function is game logic.
        '''
        # check agent being moved
        agent, old_loc, agent_actions = self.get_agent_state(agent_id)
        if agent.team != self.team_id:
            raise AgentDoesNotBelongToTeam()
        
        # raises any issues with the shortest path
        shortest_path = self.game.compute_shortest_path(agent_id, new_pos)

        # change game state to reflect the move, raise exception if issue
        agent_actions.taking_move(len(shortest_path) - 1)
        self.map.move_obj(agent_id, new_pos)

    ############################## get agents from this and other teams ##############################
    def valid_move_set(self, agent_id: AgentID) -> set[mase.HexCoord]:
        '''Get locations that an agent can move to.'''
        agent, loc, agent_actions = self.get_agent_state(agent_id)
        move_through_set = self.get_valid_move_through_set()
        shortest_paths = loc.pos.dijkstra(
            allowed_pos=move_through_set,
            max_dist=agent_actions.moves_remaining, 
        )
        return [pos for pos in shortest_paths.keys() if len(shortest_paths[pos]) <= agent_actions.moves_remaining]

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
    ) -> tuple[AgentState, LocState, AgentActionsRemaining]:
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
            
        remaining_moves = self.remaining_moves[agent_id]

        return agent, loc, remaining_moves

        
    ############################## get agents from this and other teams ##############################
    def get_other_team_agents(self, other_team_id: TeamID|None = None, require_alive: bool = True) -> dict[AgentID, AgentState]:
        '''Get the agents of this team.'''
        if other_team_id is None:
            return self.get_agents(lambda agent: agent.team != self.team_id and (not require_alive or agent.is_alive()))
        else:
            return self.get_agents(lambda agent: agent.team == other_team_id and (not require_alive or agent.is_alive()))
    
    def get_team_agents(self, require_alive: bool = True) -> dict[AgentID, AgentState]:
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



@dataclasses.dataclass
class BattleGame:
    game_state: GameState
    team_list: list[TeamID]

    @classmethod
    def new(cls, num_agents: dict[TeamID, int], map_size: int, random_seed: int = 0) -> typing.Self:
        '''Create a new game.'''
        return cls(
            game_state=GameState.new(
                num_agents=num_agents, 
                map_size=map_size, 
                random_seed=random_seed
            ),
            team_list=list(num_agents.keys()),
        )
    
    def __iter__(self) -> typing.Iterator[typing.Self]:
        return self
    
    def take_turns(self) -> TurnTracker:
        '''Take turns for all teams.'''
        return TurnTracker(
            game_state=self.game_state, 
            teams=list(self.team_list), 
        )


@dataclasses.dataclass
class TurnTracker:
    game_state: GameState
    teams: list[TeamID]
    current_turn: int = 0

    def __iter__(self) -> typing.Iterator[TeamCtrlr]:
        return self

    def __next__(self) -> TeamCtrlr:
        '''Go to the next turn.'''
        ctrlr = self.game_state.get_ctrlr(self.get_current_team_id())
        self.current_turn += 1
        return ctrlr
    
    def get_current_team_id(self) -> TeamID:
        '''Get the current team id.'''
        return self.teams[(self.current_turn + 1) % len(self.teams)]
        




def main():
    teams = ['red', 'blue']
    game = GameState.new({tid:10 for tid in teams}, map_size=30)
    for tid in teams:
        ctrlr = game.get_ctrlr(tid)
        print(ctrlr)




if __name__ == '__main__':
    main()