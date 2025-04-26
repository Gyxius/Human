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

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        self.grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        pygame.display.set_caption(TITLE)
        self.tree = Resources("wood", quantity = 10, color = FOREST_GREEN)
        self.enemy_factory = npcFactory(self.surface)
        self.enemies = [
            self.enemy_factory.create_npc("RED"),
            # self.enemy_factory.create_npc("RED", "large"),
            # self.enemy_factory.create_npc("RED", "small")
            ]
    
        self.allies = [NPC(self.surface, clan = "BLUE") for _ in range(1)]
        self.player = Player(self.surface, "Josh", self.grid)
        self.npcs = self.enemies + self.allies
        # self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs, self.grid)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters =  self.npcs + [self.player]
        self.tree.spawn(self.collision_manager, self.grid)
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

    def run(self):
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
                
            for npc in self.npcs:
                npc.update(self.characters, self.collision_manager)

            self.player.update(self.collision_manager, self.grid)
            # self.grid.update_grid(self.characters)
            self.surface.fill(GREEN)

            # self.grid.draw_grid(self.surface)
            # self.grid.print_grid()
            # Draw all the resources

            for resource in self.resources:
                resource.draw(self.surface)
            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()
        pygame.quit()