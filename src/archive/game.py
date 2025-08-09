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
import sys

class Game:
    def __init__(self, train: bool = False):
        pygame.init()
        self.train = train

        # --- basic pygame setup ---
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # --- world state ---
        self.grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        self.object_grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        self.tree = Resources("wood", quantity=10, color=FOREST_GREEN)

        # --- create NPC factories & lists ---
        self.enemy_factory  = npcFactory(self.surface)
        self.enemies_number = ENEMIES
        self.allies_number  = ALLIES

        # Q‑table shared by all SmartNPC allies
        self.shared_q_table = {}

        # instantiate enemies & allies
        # self.enemies = [NPC(self.surface, clan="RED") for _ in range(self.enemies_number)]
        self.default_enemies = [self.enemy_factory.create_npc("RED", npc_type="default") for _ in range(self.enemies_number)]
        self.enemies = [self.enemy_factory.create_npc("RED", npc_type="default"),\
        self.enemy_factory.create_npc("RED", npc_type="large"), \
        self.enemy_factory.create_npc("RED", npc_type="small")]
        self.allies  = [SmartNPC(self.surface, clan="BLUE", q_table=self.shared_q_table)
                        for _ in range(self.allies_number)]

        # the human player (only used in watch/play)
        self.player = Player(self.surface, "Josh", self.grid)
        self.hud    = HUD(self.player)

        # collision & targeting
        self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs, self.grid, self.object_grid)
        self.target_manager    = TargetManager(self.npcs, self.player)

        # define characters list once, and keep it in sync on reset
        if self.train:
            self.characters = self.npcs
        else:
            self.characters = self.npcs + [self.player]

        # resources
        self.resources = [self.tree]

        # initial spawn
        [r.spawn(self.collision_manager, self.grid) for r in self.resources]
        [c.spawn(self.collision_manager, self.grid) for c in self.characters]

    def player_move(self, event):
        if event.type == KEYDOWN:
            if   event.key == K_UP:    self.player.moving["up"]    = True
            elif event.key == K_DOWN:  self.player.moving["down"]  = True
            elif event.key == K_LEFT:  self.player.moving["left"]  = True
            elif event.key == K_RIGHT: self.player.moving["right"] = True
            elif event.key == K_SPACE: self.player.moving["space"] = True
            elif event.key == K_e:     self.hud.toggle_stats()
        elif event.type == KEYUP:
            if   event.key == K_UP:    self.player.moving["up"]    = False
            elif event.key == K_DOWN:  self.player.moving["down"]  = False
            elif event.key == K_LEFT:  self.player.moving["left"]  = False
            elif event.key == K_RIGHT: self.player.moving["right"] = False
            elif event.key == K_SPACE: self.player.moving["space"] = False

    def reset_npcs(self):
        """Recreate enemies & allies, and rebuild self.characters accordingly."""
        # self.enemies = [NPC(self.surface, clan="RED") for _ in range(self.enemies_number)]
        self.enemies = [self.enemy_factory.create_npc("RED", npc_type="default"), \
        self.enemy_factory.create_npc("RED", npc_type="large"), \
        self.enemy_factory.create_npc("RED", npc_type="small")]
        self.allies  = [SmartNPC(self.surface, clan="BLUE", q_table=self.shared_q_table)
                        for _ in range(self.allies_number)]
        self.npcs = self.enemies + self.allies

        if self.train:
            self.characters = self.npcs
        else:
            self.characters = self.npcs + [self.player]

    def reset_managers(self):
        self.grid.clear()
        self.object_grid.clear()
        self.collision_manager = CollisionManager(self.player, self.npcs, self.grid, self.object_grid)
        self.target_manager    = TargetManager(self.npcs, self.player)

    def spawn_characters(self):
        for npc in self.npcs:
            npc.spawn(self.collision_manager, self.grid)
        if not self.train:
            self.player.spawn(self.collision_manager, self.grid)

    def spawn_resources(self):
        self.tree = Resources("wood", quantity=10, color=FOREST_GREEN)
        [r.spawn(self.collision_manager, self.grid) for r in self.resources]

    def reset_game(self):
        """Called at start of each episode (train or watch)."""
        self.reset_npcs()
        for ally in self.allies:
            ally.q_table = self.shared_q_table
        self.reset_managers()
        self.spawn_characters()
        self.spawn_resources()

    def run_episode(self, episode, max_steps=2000, render=False):
        self.reset_game()
        step, done = 0, False

        while not done and step < max_steps:
            step += 1
            if render:
                self.clock.tick(FPS)

            # handle quit
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    return

            # remove dead NPCs
            self.npcs = [n for n in self.npcs if n.health > 0]

            # --- allies (RL) take actions ---
            for ally in self.allies:
                state  = ally.get_state(self.characters, self.resources)
                action = ally.choose_action(state, self.collision_manager)
                try:
                    reward, done = ally.act(action, self.collision_manager, self.npcs, self.grid)
                except TypeError:
                    # in case act() returned None
                    reward, done = 0, False
                next_s = ally.get_state(self.npcs, self.resources)
                ally.update_q_table(state, action, reward, next_s, training_mode=True)

            # --- enemies & (in watch) player update ---
            for enemy in self.enemies:
                enemy.update(self.characters, self.collision_manager)

            # rendering
            if render:
                self.surface.fill(GREEN)
                for r in self.resources: r.draw(self.surface)
                for n in self.npcs:       n.draw(self.surface)
                if not self.train:
                    self.player.update(self.collision_manager, self.grid)
                    self.player.draw(self.surface)
                pygame.display.update()

        print(f"Episode {episode+1} ended")

    def train_NPC(self, episodes=1000, max_steps=1000):
        for ep in range(episodes):
            print(f"=== Training Episode {ep+1} ===")
            self.run_episode(ep, max_steps, render=False)
        # save Q‑table
        with open('q_table.pkl','wb') as f:
            pickle.dump(self.shared_q_table, f)
        pygame.quit()

    def watch(self, watch_episodes=5, max_steps=500):
        # reload Q‑table
        with open('q_table.pkl','rb') as f:
            self.shared_q_table = pickle.load(f)

        # set play_mode for movement_control
        for ally in self.allies:
            ally.play_mode = True
            ally.epsilon   = 0.1

        for ep in range(watch_episodes):
            print(f"=== Watch Episode {ep+1} ===")
            self.run_episode(ep, max_steps, render=True)
        pygame.quit()

    def run(self):
        """Play Mode where you can play
        """
        with open('q_table.pkl', 'rb') as f:
            self.shared_q_table = pickle.load(f)

        self.reset_game()

        for npc in self.npcs:
            npc.play_mode = True 
            npc.epsilon = 0.3 # Default to 0.3

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                self.player_move(event)

            # Remove Dead NPCs
            for n in self.npcs:
                if n.health <= 0:
                    self.collision_manager.clear_position(n.x, n.y)
            self.npcs = [npc for npc in self.npcs if npc.health > 0]

            self.resources = [resource for resource in self.resources if resource.quantity > 0]
            for resource in self.resources:
                resource.update(self.collision_manager)

            for npc in self.allies:
                state = npc.get_state(self.npcs, self.resources)
                if state not in npc.q_table:
                    # If the state is new then we pick an action at random
                    action_index = random.randint(0, len(npc.actions) - 1)
                    npc.q_table[state] = [0] * len(npc.actions)
                
                print(f"State: {state}, Q-values: {npc.q_table[state]}")
                
                if random.uniform(0, 1) < npc.epsilon:
                    print('random action')
                    action = random.choice(npc.actions)
                else:
                    action_index = npc.q_table[state].index(max(npc.q_table[state]))
                    action = npc.actions[action_index]
                print(f"{npc.clan} NPC chooses action: {action}")

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