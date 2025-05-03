import pygame 
from pygame.locals import *
from map import *
from collisionManager import *
from targetManager import *
from smartnpc import *
from npcFactory import *
from player import *
from grid import *
from resources import *
from hud import *
import pickle
import random

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        self.grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        self.object_grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        pygame.display.set_caption(TITLE)
        self.tree = Resources("wood", quantity = 10, color = FOREST_GREEN)
        self.enemy_factory = npcFactory(self.surface)
        self.enemies = [
            self.enemy_factory.create_npc("RED"),
            # self.enemy_factory.create_npc("RED", "large"),
            # self.enemy_factory.create_npc("RED", "small")
            ]
        self.shared_q_table = {}
        self.enemies_number = 1
        self.allies_number = 1
        self.allies = [SmartNPC(self.surface, clan = "BLUE", q_table=self.shared_q_table) for _ in range(1)]
        self.player = Player(self.surface, "Josh", self.grid)
        self.hud = HUD(self.player)
        self.npcs = self.enemies + self.allies
        # self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs, self.grid, self.object_grid)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters =  self.npcs + [self.player]
        self.resources = [self.tree]
        [resource.spawn(self.collision_manager, self.grid) for resource in self.resources]
        [character.spawn(self.collision_manager, self.grid) for character in self.characters] # Spawn the characters 

    def player_move(self, event):
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
                pass

    def reset_npcs(self):
        """Recrete enemies and allies while resetting the q table for the allies
        """
        # Recreate NPC objects
        self.enemies = [NPC(self.surface, clan="RED") for _ in range(self.enemies_number)]
        self.allies = [SmartNPC(self.surface, clan="BLUE", q_table=self.shared_q_table) for _ in range(self.allies_number)]
        # Reinitialize npcs list
        self.npcs = self.enemies + self.allies

    def reset_managers(self):
        """Reset the collision managers with the characters and grid as well as the target manager
        """
        # Reinitialize managers
        self.collision_manager = CollisionManager(self.player, self.npcs, self.grid, self.object_grid)
        self.target_manager = TargetManager(self.npcs, self.player)

    def spawn_characters(self):
        # Respawn characters
        for npc in self.npcs:
            npc.spawn(self.collision_manager, self.grid)

        self.player.spawn(self.collision_manager, self.grid)

    def reset_game(self):
        self.reset_npcs()
        for npc in self.allies:
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

            for npc in self.allies:
                # state = npc.get_state(self.npcs)
                state = npc.get_state(self.characters)
                action = npc.choose_action(state, self.collision_manager)
                reward, done = npc.act(action, self.collision_manager, self.npcs, self.grid)
                # reward, done = npc.act(action, self.collision_manager, self.characters)
                next_state = npc.get_state(self.npcs)
                # next_state = npc.get_state(self.characters)
                npc.update_q_table(state, action, reward, next_state, training_mode=True)

            # Render only if required
            if render:
                self.surface.fill(GREEN)
                for npc in self.npcs:
                    npc.draw(self.surface)
                self.player.update(self.collision_manager,  self.grid)
                self.player.draw(self.surface)
                pygame.display.update()

        print(f"Episode {episode + 1} ended")

    def train_NPC(self, episodes=1000, max_steps=1000):
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
            for npc in self.allies:
                npc.q_table = self.shared_q_table
            self.reset_managers()
            self.spawn_characters()

            self.run_episode(ep, max_steps=max_steps, render=True)

        pygame.quit()

    def run(self):
        with open('q_table.pkl', 'rb') as f:
            self.shared_q_table = pickle.load(f)
            
        for npc in self.npcs:
            npc.play_mode = True 
            npc.epsilon = 0.5

        self.reset_managers()

        running = True
        while running:
            # pygame.time.delay(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                self.player_move(event)
            # self.clock.tick(FPS)
            self.npcs = [npc for npc in self.npcs if npc.health > 0]
            self.resources = [resource for resource in self.resources if resource.quantity > 0]
            for resource in self.resources:
                resource.update(self.collision_manager)
            for npc in self.allies:
                state = npc.get_state(self.npcs)
                # state = npc.get_state(self.characters)
                if state not in npc.q_table:
                    # If the state is new then we pick an action at random
                    action_index = random.randint(0, len(npc.actions) - 1)
                    npc.q_table[state] = [0] * len(npc.actions)
                
                # print(f"State: {state}, Q-values: {npc.q_table[state]}")
                
                if random.uniform(0, 1) < npc.epsilon:
                    action = random.choice(npc.actions)
                else:
                    action_index = npc.q_table[state].index(max(npc.q_table[state]))
                    action = npc.actions[action_index]
                # print(f"{npc.clan} NPC chooses action: {action}")

                npc.act(action, self.collision_manager, self.npcs, self.grid)

            for npc in self.enemies:
                npc.update(self.characters, self.collision_manager)

            self.player.update(self.collision_manager, self.grid)
            # self.grid.update_grid(self.characters)
            self.surface.fill(GREEN)

            # self.grid.draw_grid(self.surface)
            self.grid.print_grid()
            # Draw all the resources

            for resource in self.resources:
                resource.draw(self.surface)
            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            self.hud.draw(self.surface)
            pygame.display.update()
        pygame.quit()