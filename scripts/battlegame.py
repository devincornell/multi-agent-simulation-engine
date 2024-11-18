from __future__ import annotations
import collections
import time
import math
import pygame
import typing
import dataclasses
import random
from pathlib import Path

import tqdm

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

    def using_move_action(self, num_moves: int) -> None:
        '''Return a new state after taking a move.'''
        if self.moves_remaining < num_moves:
            raise AgentOutOfMoves()
        self.moves_remaining -= num_moves

    def using_attack_action(self) -> None:
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

class GameException(Exception):
    pass
class AgentIsAlreadyAtLocation(GameException):
    pass
class AnotherAgentIsAtTargetLocation(GameException):
    pass
class AgentDoesNotExist(GameException):
    pass
class LocationDoesNotExist(GameException):
    pass
class AgentDoesNotBelongToTeam(GameException):
    pass
class AgentOutOfMoves(GameException):
    pass
class AgentOutOfAttacks(GameException):
    pass
class TargetAgentDoesNotExist(GameException):
    pass
class AgentNotOnMap(GameException):
    pass
class NoRouteToTarget(GameException):
    pass
class CantAttackSameTeam(GameException):
    pass
class CantAttackSelf(GameException):
    pass
class TargetTooFarAwayForAttack(GameException):
    pass
class AgentIsDead(GameException):
    pass
class TargetLocationIsBlocked(GameException):
    pass
class TargetIsTooFar(GameException):
    pass
class TargetIsAlreadyDead(GameException):
    pass

class InvalidTargetLocation:
    pass

@dataclasses.dataclass
class GameState:
    agents: AgentStates
    locations: LocStates
    map: mase.ObjectMapper[AgentID, mase.HexCoord]

    @classmethod
    def new(cls, num_agents: dict[TeamID, int], map_size: int, random_seed: int = 0, blocked_prob: float = 0.2, agent_start_level: int = 1) -> typing.Self:
        '''Initialize a new game state.'''
        random.seed(random_seed)

        agent_states = AgentStates.init(num_agents, start_level=agent_start_level)
        location_states = LocStates.init(map_size)

        # block off random locations
        
        for pos in location_states.keys():
            if random.uniform(0, 1) < blocked_prob:
                location_states[pos].blocked = True

        # put agents in random locations
        agent_locations = mase.ObjectMapper()
        for agent_id in agent_states.keys():
            while True:
                pos = random.choice(list(location_states.keys()))
                if not len(agent_locations.get_objs(pos)) and not location_states[pos].blocked:
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
    def plan_attack(
        self, 
        agent_id: AgentID, 
        target_id: AgentID,
    ) -> tuple[AgentState, AgentState, float]:
        '''Perform checks for attack from one agent to another.
        Returns:
            agent, target_agent, attack_power
        '''
        if agent_id == target_id:
            raise CantAttackSelf()

        agent, loc = self.get_agent_and_loc(agent_id)

        try:
            target_agent, target_loc = self.get_agent_and_loc(target_id)
        except AgentIsDead:
            raise TargetIsAlreadyDead()

        if agent.team == target_agent.team:
            raise CantAttackSameTeam()
        
        if loc.pos.distance(target_loc.pos) > agent.attack_distance():
            #print(loc.pos, target_loc.pos)
            #print(loc.pos.distance(target_loc.pos), agent.attack_distance())
            raise TargetTooFarAwayForAttack()
        
        return agent, target_agent, agent.attack_power()

    def plan_move(
        self, 
        agent_id: AgentID, 
        new_pos: mase.HexCoord, 
        agent_team_id: TeamID | None = None,
        max_dist: int | None = None,
    ) -> tuple[AgentState, list[mase.HexCoord]]:
        '''Get plan and perform checks for moving an agent to a new location.
        Description: Use when trying to move an agent, because it will perform all the general checks.
        Args:
            agent_id: id of the agent to move.
            new_pos: position to move to.
            agent_team_id: team of the agent (if you want to perform checks)
        Returns: shortest path from an agent to a location, raise exceptions if there is no path.
        '''
        agent, old_loc = self.get_agent_and_loc(agent_id)

        if agent_team_id is not None and agent_team_id != agent.team:
            raise AgentDoesNotBelongToTeam()

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
        
        #print(shortest_path)
        if max_dist is not None and (len(shortest_path)-1) > max_dist:
            raise TargetIsTooFar()
        
        return agent, shortest_path

    def kill_agent(self, agent_id: AgentID) -> None:
        '''Take agent off the map and change agent state.
        Description: changes agent stats, removes agent from the map.
        '''
        self.map.remove_obj(agent_id)
        self.agents[agent_id].die()

    ################################## paths and valid moves ##############################
    def valid_move_to_set(self, agent_id: AgentID, max_moves: int|None = None) -> dict[mase.HexCoord, list[mase.HexCoord]]:
        '''Get positions that an agent can move to and the paths they would take.'''
        agent, loc = self.get_agent_and_loc(agent_id)
        move_through_set = [pos for pos, loc in self.locations.items() if self.check_agent_can_move_through(agent_id, pos)]
        sps = loc.pos.dijkstra(
            allowed_pos=move_through_set,
            max_dist=max_moves, 
        )
        valid_moves: dict[mase.HexCoord, list[mase.HexCoord]] = dict()
        for pos, sp in sps.items():
            if len(sp) and (max_moves is None or (len(sp)-1) <= max_moves) and self.check_agent_can_move_to(agent_id, pos):
                valid_moves[pos] = sp
        return valid_moves
        
    def check_agent_can_move_to(self, agent_id: AgentID, pos: mase.HexCoord) -> bool:
        '''Check if an agent can move to a location. Does not consider distance/path.
        Description: checks if the location is blocked or if there is another agent there.
        '''
        #agent, loc = self.get_agent_and_loc(agent_id)
        loc = self.locations[pos]
        if loc.blocked or len(self.map.get_objs(pos)):
            return False
        return True

    def valid_move_through_set(
        self, 
        agent_id: AgentID, 
        consider_agents: bool = False, 
        max_dist: int|None = None
    ) -> set[mase.HexCoord]:
        '''Get locations that player can move through. Much simpler'''
        move_coords = set()
        for pos, loc in self.locations.items():
            if self.check_agent_can_move_through(agent_id=agent_id, pos=pos, consider_agents=consider_agents, max_dist=max_dist):
                move_coords.add(pos)
    
        return move_coords

    def check_agent_can_move_through(
        self, 
        agent_id: AgentID, 
        pos: mase.HexCoord, 
        consider_agents: bool = False, 
        max_dist: int|None = None
    ) -> bool:
        '''Check if an agent can move through a location, consider agents/teams or distance.
        Description: checks if the location is blocked or if there is another agent there.
        '''
        agent, loc = self.get_agent_and_loc(agent_id)
        if loc.blocked or loc.pos.distance(pos) > max_dist:
            return False
        if not consider_agents or any([self.agents[aid].team != agent.team for aid in self.map.get_objs(pos)]):
            return False
        return True
    
    ################################## pathfinding ##############################
    def calc_shortest_path(
        self,
        pos: mase.HexCoord, 
        goal: mase.HexCoord,
        valid_move_through: typing.Callable[[LocState],bool] = lambda x: True,
        valid_move_to: typing.Callable[[LocState],bool] = lambda x: True,
        max_dist: int|None = None,
    ) -> dict[mase.HexCoord, list[mase.HexCoord]]:
        '''Calculate shortest path from one position to another, considering rules for valid positions.
        Args:
            pos: position to start from.
            can_move_through: function to check if a location can be moved through.
            can_move_to: function to check if the location can be moved to.
            max_dist: maximum distance to calculate.
        '''
        if not valid_move_to(self.locations[pos]):
            raise InvalidTargetLocation()
        
        return pos.a_star(
            goal=goal,
            allowed_pos=set([pos for pos, loc in self.locations.items() if valid_move_through(loc)]),
            max_dist=max_dist,
        )

    def calc_all_paths(
        self,
        pos: mase.HexCoord, 
        valid_move_through: typing.Callable[[LocState],bool] = lambda x: True,
        valid_move_to: typing.Callable[[LocState],bool] = lambda x: True,
        max_dist: int|None = None,
    ) -> dict[mase.HexCoord, list[mase.HexCoord]]:
        '''Calculate paths from one position to all others, considering rules for valid positions.
        Args:
            pos: position to start from.
            can_move_through: function to check if a location can be moved through.
            can_move_to: function to check if a location can be moved to.
            max_dist: maximum distance to calculate.
        '''
        paths = pos.dijkstra(
            allowed_pos=set([pos for pos, loc in self.locations.items() if valid_move_through(loc)]),
            max_dist=max_dist,
        )
        return {dest:path for dest,path in paths.items() if valid_move_to(self.locations[dest])}

    ################################## get agent and location information ##############################
    def get_agent_and_loc(self, 
        agent_id: AgentID, 
    ) -> tuple[AgentState, LocState]:
        '''Get the agent and its location, make sure agent is alive and on map.'''
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
    
    def get_team_counts(self) -> dict[TeamID, int]:
        '''Get the number of agents on each team.'''
        cts = collections.Counter()
        for agent in self.agents.values():
            if agent.is_alive():
                cts[agent.team] += 1
        return dict(cts)


@dataclasses.dataclass(repr=False)
class AgentCtrlr:
    '''Extension of controller that makes it easy to access and manipulate agents.'''
    id: AgentID
    ctrlr: TeamCtrlr

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, pos={self.loc.pos}, state={self.state}, actions={self.actions})'
    
    ############################## take actions ##############################
    def action_attack(self, target_id: AgentID) -> None:
        '''Have one agent attack another.'''
        self.ctrlr.action_attack(self.id, target_id)

    def action_move(self, new_pos: mase.HexCoord) -> None:
        '''Move the agent to a new position.'''
        self.ctrlr.action_move(self.id, new_pos)

    ############################## get possible moves and attacks ##############################
    def identify_possible_moves(self) -> dict[mase.HexCoord, list[mase.HexCoord]]:
        '''Get the possible moves for the agent.'''
        return self.ctrlr.game.valid_move_to_set(self.id, self.state.move_distance())
    
    def identify_possible_attack_targets(self) -> list[AgentID]:
        '''Get the possible attacks for the agent.'''
        possible_attacks = list()
        for other_id, other in self.ctrlr.game.agents.items():
            if other_id != self.id and other.is_alive():
                try:
                    agent, target, attack_power = self.ctrlr.game.plan_attack(self.id, other_id)
                    possible_attacks.append(other_id)
                except (CantAttackSameTeam, TargetTooFarAwayForAttack, CantAttackSelf, TargetIsAlreadyDead):
                    pass
        return possible_attacks

    ############################## get game state ##############################
    @property
    def state(self) -> AgentState:
        '''Get the state of the agent.'''
        return self.ctrlr.game.agents[self.id]

    @property
    def actions(self) -> AgentActionsRemaining:
        '''Get the actions remaining for the agent.'''
        return self.ctrlr.actions[self.id]
    
    @property
    def loc(self) -> LocState:
        '''Get the location of the agent.'''
        pos = self.ctrlr.game.map.get_coord(self.id)
        return self.ctrlr.game.locations[pos]


@dataclasses.dataclass
class TeamCtrlr:
    '''Keep track of moves from a particular team.'''
    team_id: TeamID
    game: GameState
    actions: dict[AgentID, AgentActionsRemaining]

    @classmethod
    def start_turn(cls, team_id: TeamID, game: GameState) -> typing.Self:
        '''Start the turn for the team.'''
        return cls(
            team_id=team_id,
            game=game,
            actions={aid: game.agents[aid].max_actions_allowed() for aid in game.agents.keys() if game.agents[aid].team == team_id and game.agents[aid].is_alive()}
        )
    
    ############################## available actions ##############################
    def action_attack(self, agent_id: AgentID, target_id: AgentID) -> int:
        '''Have one agent attack another.'''
        agent, target, attack_power = self.game.plan_attack(agent_id, target_id)
        
        if self.team_id != agent.team:
            raise AgentDoesNotBelongToTeam()

        # note that an attack action was taken and update agent state
        self.actions[agent_id].using_attack_action()
        target.receive_attack(attack_power)
        if not target.is_alive():
            self.game.kill_agent(target_id)

    def action_move(self, agent_id: AgentID, new_pos: mase.HexCoord):
        '''Move an agent to a new position.
        Description: implements a lot of checks against remaining turns and 
            agent/location states. Most of this function is game logic.
        '''
        agent, loc = self.game.get_agent_and_loc(agent_id)
        if self.team_id != agent.team:
            raise AgentDoesNotBelongToTeam()

        # checking remaining moves because it requires less of a_star.
        agent_actions = self.actions[agent_id]

        agent, shortest_path = self.game.plan_move(
            agent_id=agent_id, 
            new_pos = new_pos, 
            agent_team_id=self.team_id,
            max_dist=agent_actions.moves_remaining,
        )
                
        # change game state to reflect the move, raise exception if issue
        agent_actions.using_move_action(len(shortest_path) - 1)
        self.game.map.move_obj(agent_id, new_pos)
        
    ############################## access agent interface ##############################
    def agents(self, 
        team_id: TeamID|None = None, 
        alive_only: bool = True, 
        filter_criteria: typing.Callable[[AgentCtrlr],bool] = lambda x: True
    ) -> list[AgentCtrlr]:
        '''Get all agents.'''
        agents: list[AgentCtrlr] = []
        for aid in self.game.agents:
            agent = self.get_agent(agent_id=aid)
            if filter_criteria(agent) and (team_id is None or agent.state.team == team_id) and (not alive_only or agent.state.is_alive()):
                agents.append(agent)
        return agents
    
    def get_agent(self, agent_id: AgentID) -> AgentCtrlr:
        '''Get an agent.'''
        return AgentCtrlr(id=agent_id, ctrlr=self)


class WinResult:
    pass
class Stalemate(WinResult):
    pass

@dataclasses.dataclass
class TeamWins(WinResult):
    team_id: TeamID
    remaining_agents: int = 0

@dataclasses.dataclass
class BattleGame:
    game_state: GameState
    team_list: list[TeamID]

    @classmethod
    def new(cls, num_agents: dict[TeamID, int], **kwargts) -> typing.Self:
        '''Create a new game.'''
        return cls(
            game_state=GameState.new(
                num_agents=num_agents, 
                **kwargts,
            ),
            team_list=list(num_agents.keys()),
        )
    
    def run(self, 
        players: dict[TeamID, typing.Callable[[TeamCtrlr],None]],
        max_turns: int = 1000,
        show_progress: bool = True,
    ) -> WinResult:
        '''Run the game.'''
        remaining_teams = list(players)
        i = 0

        class FakeCtx:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def update(*args):
                pass

        ctx_manager = tqdm.tqdm(ncols=80) if show_progress else FakeCtx()

        with ctx_manager as pbar:
            while len(remaining_teams) > 1:
                team_id = remaining_teams[i % len(remaining_teams)]
                
                # get the controller for the team
                ctrlr = self.game_state.get_ctrlr(team_id)
                
                # get the player for the team
                player = players[team_id]

                # run the player's turn
                player(ctrlr)

                # check if there is a winner
                remaining_teams = self.check_remaining_teams()

                i += 1
                if i > max_turns:
                    break

                pbar.update(1)
        
        if len(remaining_teams) == 0:
            return Stalemate()
        else:
            return TeamWins(remaining_teams[0], self.game_state.get_team_counts()[remaining_teams[0]])
        
    def take_turns(self) -> TurnTracker:
        '''Take turns for all teams.'''
        return TurnTracker(
            game_state=self.game_state, 
            teams=list(self.team_list), 
        )
    
    def check_remaining_teams(self) -> TeamID | None:
        '''Check if there is a winner.'''
        #team_alive = {team_id: False for team_id in self.team_list}
        remaining_teams = set()
        for agent in self.game_state.agents.values():
            if agent.is_alive():
                remaining_teams.add(agent.team)
        return list(remaining_teams)


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