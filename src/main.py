from pygame.locals import *
from characters import *
from game import *
import sys

if __name__ == "__main__":
    if "train" in sys.argv:
        pygame.init()
        game = Game()
        if len(sys.argv) > 2:
            try:
                nb_episodes = int(sys.argv[2])
                game.train(episodes=nb_episodes, max_steps=1000)
            except:
                print("There's an error with the second parameters which is the episodes")
        else:
            game.train_NPC(episodes=1000, max_steps=1000)
    else:
        game = Game()
        game.run()