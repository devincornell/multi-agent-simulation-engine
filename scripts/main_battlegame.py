
import battlegame
import random


def ai_red(ctrlr: battlegame.TeamCtrlr):
    for aid, agent in ctrlr.get_team_agents().items():
        possible_moves = ctrlr.valid_move_set(aid)
        ctrlr.move_agent(aid, possible_moves[0])



def main():
    game = battlegame.BattleGame.new(
        num_agents={0: 10, 1: 10}, 
        map_size=10,
    )

    team_ai = {0: ai_red, 1: ai_red}


    for ctrlr in game.take_turns():
        ai = team_ai[ctrlr.team_id]
        ai(ctrlr)


if __name__ == '__main__':
    main()


