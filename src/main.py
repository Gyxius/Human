from pygame.locals import *
from characters import *
from game import *
import sys
import os

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

    elif "watch" in sys.argv:
        # Rendered graphics mode for watching
        if "SDL_VIDEODRIVER" in os.environ:
            del os.environ["SDL_VIDEODRIVER"]
        pygame.display.quit()
        pygame.display.init()
        pygame.init()
        game = Game()
        if len(sys.argv) > 2:
            try:
                nb_episodes = int(sys.argv[2])
                game.watch(watch_episodes=nb_episodes, max_steps=2000)
            except:
                print("There's an error with the second parameters which is the episodes")
        else:
            game.watch(watch_episodes=5, max_steps=2000)
    else:
        game = Game()
        game.run()