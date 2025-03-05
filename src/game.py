import pygame 
from pygame.locals import *
from map import *
from collisionManager import *
from npc import *
from player import *

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(TITLE)
        self.enemies = [NPC(self.surface) for _ in range(3)]
        self.player = Player(self.surface, "Josh")
        self.collision_manager = CollisionManager(self.player, self.enemies)

    def run(self):
        running = True
        while running:
            pygame.time.delay(30)
            
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
                        pass

            self.clock.tick(FPS)

            # Update all NPCs
            for enemy in self.enemies:
                enemy.update(self.player, self.collision_manager)

            self.player.update(self.collision_manager)

            self.surface.fill(GREEN)
            # Draw all NPCs
            for enemy in self.enemies:
                enemy.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()
        pygame.quit()