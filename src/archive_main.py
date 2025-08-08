#!/usr/bin/env python3
from pygame.locals import *
from characters import *
from game import *
import sys
import os

def train():
    game = Game(True)
    pygame.init()
    DEFAULT_EPISODES = 1000
    MAX_STEPS = 3000
    if len(sys.argv) > 2:
        raw = sys.argv[2]
        try:
            nb_episodes = int(raw)
        except ValueError as e:
            print(f"Error: could not parse number of episodes ('{raw}') as an integer:\n  {e}")
            sys.exit(1)
        else:
            game.train_NPC(episodes=nb_episodes, max_steps=MAX_STEPS)
    else:
        game.train_NPC(episodes=DEFAULT_EPISODES, max_steps=MAX_STEPS)

def watch():
    # Ensure we get a real window for rendering
    if "SDL_VIDEODRIVER" in os.environ:
        del os.environ["SDL_VIDEODRIVER"]
    pygame.display.quit()
    pygame.display.init()
    pygame.init()

    game = Game(True)

    DEFAULT_WATCH = 5
    MAX_STEPS    = 2000

    if len(sys.argv) > 2:
        raw = sys.argv[2]
        try:
            nb_episodes = int(raw)
        except ValueError as e:
            print(f"Error: could not parse number of watch‑episodes ('{raw}') as an integer:\n  {e}")
            sys.exit(1)
        else:
            game.watch(watch_episodes=nb_episodes, max_steps=MAX_STEPS)
    else:
        game.watch(watch_episodes=DEFAULT_WATCH, max_steps=MAX_STEPS)

def play():
    game = Game(False)
    game.run()

if __name__ == "__main__":
    if "train" in sys.argv:
        train()

    elif "watch" in sys.argv:
        watch()

    else:
        play()