import typing
import dataclasses
import battlegame
import random


@dataclasses.dataclass
class RandomAI:
    turn_ct: int = 0

    def __call__(self, ctrlr: battlegame.TeamCtrlr, verbose: bool = False):
        if verbose: print(f'==================== {ctrlr.team_id} Turn {self.turn_ct} ====================')
        for agent in ctrlr.agents(team_id=ctrlr.team_id):
            # move randomly
            possible_moves = agent.calc_valid_moves()
            if len(possible_moves) > 0:
                move_dest = random.choice(list(possible_moves.keys()))
                agent.action_move(move_dest)
                if verbose: print(f'Moved {agent.loc.pos} -> {move_dest}')

            # attack anything nearby
            targets = agent.identify_possible_targets()
            if len(targets) > 0:
                target = random.choice(targets)
                agent.action_attack(target)
                if verbose: print(f'Attacked {agent.id} -> {target}')
        
        self.turn_ct += 1
        if verbose: print(f'{ctrlr.game.get_team_counts()=}')

@dataclasses.dataclass
class Team:
    player: typing.Callable[[battlegame.TeamCtrlr],None]
    size: int

teams = {
    'red': Team(RandomAI(), 10),
    'blue': Team(RandomAI(), 10),
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


