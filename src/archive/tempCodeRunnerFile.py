import pygame 
from pygame.locals import *
from map import *
from collisionManager import *
from targetManager import *
from smartnpc import *
from npcFactory import *
from player import *
import random

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(TITLE)
        
        # Create NPCs
        self.enemies = [SmartNPC(self.surface, speed = 5, clan="RED") for _ in range(1)]
        self.allies = [SmartNPC(self.surface, speed = 5, clan="BLUE") for _ in range(1)]

        self.player = Player(self.surface, "Josh")
        self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters = self.npcs + [self.player]

        # Spawn characters
        for character in self.characters:
            character.spawn(self.collision_manager)

    def reset(self):
        for npc in self.npcs:
            npc.reset(self.collision_manager)
        return

    def run_episode(self, max_steps=100):
        self.reset()
        step_count = 0
        done = False

        while not done and step_count < max_steps:
            step_count += 1
            self.clock.tick(FPS)

            self.npcs = [npc for npc in self.npcs if npc.health > 0]

            for npc in self.npcs:
                state = npc.get_state(self.npcs)
                action = npc.choose_action(state)  # <-- USE THIS instead of random.choice
                reward, done = npc.act(action, self.collision_manager, self.npcs)
                next_state = npc.get_state(self.npcs)
                npc.update_q_table(state, action, reward, next_state)  # <-- VERY IMPORTANT
                npc.total_reward += reward

            # Update and draw
            self.surface.fill(GREEN)
            for npc in self.npcs:
                npc.draw(self.surface)
            self.player.update(self.collision_manager)
            self.player.draw(self.surface)
            pygame.display.update()

        return

    def train(self, episodes=10):
        for ep in range(episodes):
            print(f"=== Episode {ep + 1} ===")
            self.run_episode(max_steps=100)
        pygame.quit()

# --- Main Script ---

if __name__ == "__main__":
    game = Game()
    game.train(episodes=5)