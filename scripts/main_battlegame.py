
import battlegame


def main():
    game = battlegame.BattleGame.new(
        num_agents={0: 10, 1: 10}, 
        map_size=10,
    )

    for i, ctrlr in game.take_turns():
        print(ctrlr)
        break



if __name__ == '__main__':
    main()


