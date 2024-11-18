import typing
import dataclasses
import battlegame
import random


@dataclasses.dataclass
class AIRed:
    turn_ct: int = 0

    def __call__(self, ctrlr: battlegame.TeamCtrlr):
        print(f'==================== {ctrlr.team_id} Turn ====================')
        for agent in ctrlr.agents(team_id=ctrlr.team_id):
            # move randomly
            possible_moves = agent.identify_possible_moves()
            move_list = list(possible_moves.keys())
            move_choice = random.choice(move_list)
            print(f'{move_list=}')
            print(agent.loc.pos, move_choice)
            agent.action_move(move_choice)

            # attack anything nearby
            targets = agent.identify_possible_attack_targets()
            if len(targets) > 0:
                agent.action_attack(random.choice(targets))
        
        self.turn_ct += 1

@dataclasses.dataclass
class Team:
    player: typing.Callable[[battlegame.TeamCtrlr],None]
    size: int

teams = {
    'red': Team(AIRed(), 1),
    'blue': Team(AIRed(), 1),
}


def main():
    game = battlegame.BattleGame.new(
        num_agents={tid:team.size for tid,team in teams.items()}, 
        map_size=10,
    )

    game.run(
        players = {tid:team.player for tid,team in teams.items()},
        max_turns=1000,
    )


if __name__ == '__main__':
    main()


