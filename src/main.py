from pygame.locals import *
from characters import *
import os
import sys
# from game_archive import *
from game import *


if __name__ == "__main__":

    if "train" in sys.argv:
        # Headless mode only when training
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        game = Game()
        game.train(episodes=1000, max_steps=1000)

    elif "watch" in sys.argv:
        # Rendered graphics mode for watching
        if "SDL_VIDEODRIVER" in os.environ:
            del os.environ["SDL_VIDEODRIVER"]
        pygame.display.quit()
        pygame.display.init()
        pygame.init()

        game = Game()
        game.watch(watch_episodes=5, max_steps=2000)
    elif "play" in sys.argv:
        # IMPORTANT: remove dummy driver for play
        if "SDL_VIDEODRIVER" in os.environ:
            del os.environ["SDL_VIDEODRIVER"]
        pygame.display.quit()
        pygame.display.init()
        pygame.init()
        game = Game()
        game.play()

    else:
        print("Please specify 'train', 'play' or 'watch' mode.")
        print("Example:")
        print("    python3 src/main.py train")
        print("    python3 src/main.py watch")
        print("    python3 src/main.py play")