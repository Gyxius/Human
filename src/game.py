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
        self.shared_q_table = {}


        # Create NPCs
        self.enemies_number = 2
        self.allies_number = 2
        self.enemies = [SmartNPC(self.surface, clan="RED", q_table=self.shared_q_table) for _ in range(self.enemies_number)]
        self.allies = [SmartNPC(self.surface, clan="BLUE", q_table=self.shared_q_table) for _ in range(self.allies_number)]

        self.player = Player(self.surface, "Josh")
        self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters = self.npcs + [self.player]
        # Spawn characters
        for character in self.characters:
            character.spawn(self.collision_manager)

    def reset_npcs(self):
        # Recreate NPC objects
        self.enemies = [SmartNPC(self.surface, clan="RED", q_table=self.shared_q_table) for _ in range(self.enemies_number)]
        self.allies = [SmartNPC(self.surface, clan="BLUE", q_table=self.shared_q_table) for _ in range(self.allies_number)]
        # Reinitialize npcs list
        self.npcs = self.enemies + self.allies

    def reset_managers(self):
        # Reinitialize managers
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)

    def spawn_characters(self):
        # Respawn characters
        for npc in self.npcs:
            npc.spawn(self.collision_manager)

        self.player.spawn(self.collision_manager)

    def reset_game(self):
        self.reset_npcs()
        for npc in self.npcs:
            npc.q_table = self.shared_q_table  # Re-assign just in case

        self.reset_managers()
        self.spawn_characters()

    def run_episode(self, episode, max_steps=2000, render=False):
        self.reset_game()
        step_count = 0
        done = False
        running = True

        while running and not done and step_count < max_steps:
            step_count += 1

            if render:
                self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    done = True

            self.npcs = [npc for npc in self.npcs if npc.health > 0]

            for npc in self.npcs:
                # state = npc.get_state(self.npcs)
                state = npc.get_state(self.characters)
                action = npc.choose_action(state, self.collision_manager)
                reward, done = npc.act(action, self.collision_manager, self.npcs)
                # reward, done = npc.act(action, self.collision_manager, self.characters)
                next_state = npc.get_state(self.npcs)
                # next_state = npc.get_state(self.characters)
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
            print(f"=== Episode {ep + 1} ===")
            self.run_episode(ep, max_steps=max_steps, render=False)

        # Save shared Q-table at the end of training
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(self.shared_q_table, f)
        pygame.quit()

    def watch(self, watch_episodes=5, max_steps=500):
        # os.environ["SDL_VIDEODRIVER"] = "x11"  # Use default video driver
        pygame.display.quit()
        pygame.display.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Watch Trained NPCs")

        with open('q_table.pkl', 'rb') as f:
            self.shared_q_table = pickle.load(f)

        for ep in range(watch_episodes):
            self.reset_npcs()
            for npc in self.npcs:
                npc.q_table = self.shared_q_table
            self.reset_managers()
            self.spawn_characters()

            self.run_episode(ep, max_steps=max_steps, render=True)

        pygame.quit()

    def play(self):
        with open('q_table.pkl', 'rb') as f:
            self.shared_q_table = pickle.load(f)
        # Reset the game and assign Q-tables to fresh NPCs
        # self.reset_game()  # Ensures NPCs are recreated
        self.reset_npcs()
        for npc in self.npcs:
            npc.q_table = self.shared_q_table
            npc.epsilon = 0.5

        self.reset_managers()
        self.spawn_characters()

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
                # state = npc.get_state(self.characters)
                if state not in npc.q_table:
                    # If the state is new then we pick an action at random
                    action_index = random.randint(0, len(npc.actions) - 1)
                    npc.q_table[state] = [0] * len(npc.actions)
                
                print(f"State: {state}, Q-values: {npc.q_table[state]}")
                
                if random.uniform(0, 1) < npc.epsilon:
                    action = random.choice(npc.actions)
                else:
                    action_index = npc.q_table[state].index(max(npc.q_table[state]))
                    action = npc.actions[action_index]
                print(f"{npc.clan} NPC chooses action: {action}")

                npc.act(action, self.collision_manager, self.npcs)
                # npc.act(action, self.collision_manager, self.characters)


            self.player.update(self.collision_manager)

            self.surface.fill(GREEN)

            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()

        pygame.quit()