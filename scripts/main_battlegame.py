import typing
import dataclasses
import battlegame
import random


@dataclasses.dataclass
class RandomAI:
    verbose: bool = False
    turn_ct: int = 0

    def __call__(self, ctrlr: battlegame.TeamCtrlr, ):
        if self.verbose: print(f'==================== {ctrlr.team_id} ({self.__class__.__name__}) Turn {self.turn_ct} ====================')
        for agent in ctrlr.agents(team_id=ctrlr.team_id):
            if True:
                if self.verbose:
                    print(f'{agent=}')
                    print(f'{len(ctrlr.game.locations)=}')
                    print('blocked:', sum(loc.blocked for loc in ctrlr.game.locations.values()))
                    print('no agents:', sum(not len(ctrlr.game.get_loc_agents(loc.pos)) for loc in ctrlr.game.locations.values()))
                    print('no agents and not blocked:', sum(not len(ctrlr.game.get_loc_agents(loc.pos)) and not loc.blocked for loc in ctrlr.game.locations.values()))
                    can_move_through = ctrlr.game.valid_move_through_set(agent.id, consider_agents=True)
                    print(f'{len(can_move_through)=}')
                    break

            possible_moves = agent.calc_valid_moves()
            #print(f'{len(possible_moves)=}')
            if len(possible_moves) > 0:
                move_dest = random.choice(list(possible_moves.keys()))
                if self.verbose: print(f'Agent {agent.id}: moved {agent.loc.pos} -> {move_dest}')
                agent.action_move(move_dest, path=possible_moves[move_dest])
                

            # attack anything nearby
            targets = agent.identify_possible_targets()
            if len(targets) > 0:
                target = random.choice(targets)
                agent.action_attack(target)
                if self.verbose: print(f'Agent {agent.id}: attacked {target}')
        
        self.turn_ct += 1
        if self.verbose: print(f'{ctrlr.game.get_team_counts()=}')

@dataclasses.dataclass
class AttackAI:
    turn_ct: int = 0

    def __call__(self, ctrlr: battlegame.TeamCtrlr, verbose: bool = True):
        if verbose: print(f'==================== {ctrlr.team_id} ({self.__class__.__name__}) Turn {self.turn_ct} ====================')
        for agent in ctrlr.agents(team_id=ctrlr.team_id):

            # attack anything nearby
            targets = agent.identify_possible_targets()
            if len(targets) > 0:
                target = random.choice(targets)
                agent.action_attack(target)
                if verbose: print(f'Agent {agent.id}: attacked {target}')

            # otherwise plan out moves
            #search_criteria = lambda loc: any([a for a in ctrlr.game.get_loc_agents(loc.pos) if a.team != ctrlr.team_id])
            reachable_locations = agent.calc_reachable_paths(consider_agents=True)
            print(f'found {len(reachable_locations)} reachable locations')
            target_paths: list[tuple] = list()
            for ptarget in ctrlr.agents(lambda agent: agent.id != ctrlr.team_id):
                if ptarget.loc.pos in reachable_locations and len(path := reachable_locations[ptarget.loc.pos]) > 2:
                    target_paths.append((ptarget, path))
            print(f'found {len(target_paths)} reachable targets')
            
            if len(target_paths) > 0:
                #sorted_targets = list(sorted(target_paths, key=lambda x: len(x[1])))
                target, full_path = min(target_paths, key=lambda x: len(x[1]))
                num_moves = min(agent.state.move_distance(), len(full_path)-1)
                goal, path = full_path[num_moves], full_path[:num_moves+1]
                print(f'{agent.loc.pos=}\n{target.loc.pos=}\n{full_path=}\n{num_moves}\n{goal=}\n{path=}')
                #if verbose: print(f'{num_moves=}, {path}')
                if verbose: print(f'Agent {agent.id} moved towards {target.id} ({target.state.team}): {agent.loc.pos} -> {goal}')
                agent.action_move(goal, path=path)
            else:
                possible_moves = agent.calc_valid_moves()
                if len(possible_moves) > 0:
                    move_dest = random.choice(list(possible_moves.keys()))
                    if verbose: print(f'Agent {agent.id} moved randomly: {agent.loc.pos} -> {move_dest}')
                    agent.action_move(move_dest, path=possible_moves)
        
        self.turn_ct += 1
        if verbose: print(f'{ctrlr.game.get_team_counts()=}')



@dataclasses.dataclass
class Team:
    player: typing.Callable[[battlegame.TeamCtrlr],None]
    size: int

teams = {
    'blue': Team(RandomAI(), 20),
    'red': Team(AttackAI(), 20),
}


def main():
    game = battlegame.BattleGame.new(
        num_agents={tid:team.size for tid,team in teams.items()}, 
        map_size=10,
        random_seed=1,
        agent_start_level=3,
    )

    result = game.run(
        players = {tid:team.player for tid,team in teams.items()},
        max_turns=100000,
    )
    print(result)


if __name__ == '__main__':
    main()


