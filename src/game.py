import pygame 
from pygame.locals import *
from map import *
from collisionManager import *
from targetManager import *
from smartnpc import *
from npcFactory import *
from player import *
from grid import *

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        self.grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
        pygame.display.set_caption(TITLE)
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
            
            # Update all NPCs
            # reserved_tiles = set()
            self.grid.empty_grid(self.characters)
            for npc in self.npcs:
                # intended_x = npc.x
                # intended_y = npc.y
                # state = npc.get_state(self.npcs)
                npc.update(self.characters, self.collision_manager)
                    # After update, check if moved:
                # new_pos = (npc.x, npc.y)
                # if new_pos != (intended_x, intended_y):
                #     if new_pos in reserved_tiles:
                #         # Undo move if tile is taken
                #         npc.x, npc.y = intended_x, intended_y
                #         npc.xPosition, npc.yPosition = self.grid.grid_to_pixel(npc.x, npc.y)
                #     else:
                #         reserved_tiles.add(new_pos)

            self.player.update(self.collision_manager, self.grid)
            self.grid.update_grid(self.characters)
            self.surface.fill(GREEN)

            self.grid.draw_grid(self.surface)
            # self.grid.print_grid()
            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()
        pygame.quit()