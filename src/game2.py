import os
os.environ["SDL_VIDEODRIVER"] = "dummy"  # Headless mode for faster training

import pygame
from pygame.locals import *
from map import *
from collisionManager import *
from targetManager import *
from smartnpc import *
from npcFactory import *
from player import *
import pickle
import random

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(TITLE)

        # Create NPCs
        self.enemies = [SmartNPC(self.surface, speed=1, clan="RED") for _ in range(4)]
        self.allies = [SmartNPC(self.surface, speed=1, clan="BLUE") for _ in range(4)]

        self.player = Player(self.surface, "Josh")
        self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters = self.npcs + [self.player]

        # Spawn characters
        for character in self.characters:
            character.spawn(self.collision_manager)

    def reset(self):
        # Save Q-tables
        saved_q_tables = [npc.q_table for npc in self.npcs]

        # Save to file
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(saved_q_tables, f)

        # Recreate NPC objects
        self.enemies = [SmartNPC(self.surface, speed=5, clan="RED") for _ in range(4)]
        self.allies = [SmartNPC(self.surface, speed=5, clan="BLUE") for _ in range(4)]

        # Reinitialize npcs list
        self.npcs = self.enemies + self.allies

        # Load Q-tables
        with open('q_table.pkl', 'rb') as f:
            saved_q_tables = pickle.load(f)

        for npc, q_table in zip(self.npcs, saved_q_tables):
            npc.q_table = q_table

        # Reinitialize managers
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)

        # Respawn characters
        for npc in self.npcs:
            npc.spawn(self.collision_manager)

        self.player.spawn(self.collision_manager)

    def run_episode(self, episode, max_steps=2000, render=False):
        self.reset()
        step_count = 0
        done = False
        running = True

        while running and not done and step_count < max_steps:
            step_count += 1

            # Skip FPS limit for faster training
            if render:
                self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    done = True

            self.npcs = [npc for npc in self.npcs if npc.health > 0]

            for npc in self.npcs:
                state = npc.get_state(self.npcs)
                action = npc.choose_action(state)
                reward, done = npc.act(action, self.collision_manager, self.npcs)
                next_state = npc.get_state(self.npcs)
                npc.update_q_table(state, action, reward, next_state, training_mode=True)

            # Render only if required
            if render:
                self.surface.fill(GREEN)
                for npc in self.npcs:
                    npc.draw(self.surface)
                self.player.update(self.collision_manager)
                self.player.draw(self.surface)
                pygame.display.update()

        print(f"Episode {episode + 1} ended")

    def train(self, episodes=1000, max_steps=1000):
        for ep in range(episodes):
            render = (ep % 100 == 0)  # Render only every 100 episodes
            print(f"=== Episode {ep + 1} ===")
            self.run_episode(ep, max_steps=max_steps, render=False)
        pygame.quit()

    def watch(self, watch_episodes=5, max_steps=500):
        # os.environ["SDL_VIDEODRIVER"] = "x11"  # Use default video driver
        pygame.display.quit()
        pygame.display.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Watch Trained NPCs")

        with open('q_table.pkl', 'rb') as f:
            saved_q_tables = pickle.load(f)

        for ep in range(watch_episodes):
            self.reset()
            for npc, q_table in zip(self.npcs, saved_q_tables):
                npc.q_table = q_table
            self.run_episode(ep, max_steps=max_steps, render=True)
        pygame.quit()


    def play(self):
        # Load the trained Q-tables
        with open('q_table.pkl', 'rb') as f:
            saved_q_tables = pickle.load(f)
        
        print(saved_q_tables)


        # Reset the game and assign Q-tables to fresh NPCs
        self.reset()  # Ensures NPCs are recreated

        for npc, q_table in zip(self.npcs, saved_q_tables):
            npc.q_table = q_table

        running = True
        while running:
            # pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.moving["up"] = True
                    elif event.key == pygame.K_DOWN:
                        self.player.moving["down"] = True
                    elif event.key == pygame.K_LEFT:
                        self.player.moving["left"] = True
                    elif event.key == pygame.K_RIGHT:
                        self.player.moving["right"] = True
                    elif event.key == pygame.K_SPACE:
                        self.player.moving["space"] = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player.moving["up"] = False
                    elif event.key == pygame.K_DOWN:
                        self.player.moving["down"] = False
                    elif event.key == pygame.K_LEFT:
                        self.player.moving["left"] = False
                    elif event.key == pygame.K_RIGHT:
                        self.player.moving["right"] = False
                    elif event.key == pygame.K_SPACE:
                        self.player.moving["space"] = False

            self.clock.tick(FPS)

            self.npcs = [npc for npc in self.npcs if npc.health > 0]

            # Update all NPCs using the trained Q-table
            for npc in self.npcs:
                state = npc.get_state(self.npcs)
                if state not in npc.q_table:
                    npc.q_table[state] = [0] * len(npc.actions)
                
                print(f"State: {state}, Q-values: {npc.q_table[state]}")
                
                if random.uniform(0, 1) < npc.epsilon:
                    action = random.choice(npc.actions)
                else:
                    action_index = npc.q_table[state].index(max(npc.q_table[state]))
                    action = npc.actions[action_index]
                print(f"{npc.clan} NPC chooses action: {action}")

                # Optional: print action for debugging
                # print(f"{npc.clan} NPC chooses action: {action}")

                npc.act(action, self.collision_manager, self.npcs)

            self.player.update(self.collision_manager)

            self.surface.fill(GREEN)

            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()

        pygame.quit()
# --- Main Script ---

if __name__ == "__main__":
    import sys

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
        print("Please specify 'train' or 'watch' mode.")
        print("Example:")
        print("    python script.py train")
        print("    python script.py watch")