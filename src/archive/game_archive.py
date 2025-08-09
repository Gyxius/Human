import pygame 
from pygame.locals import *
from map import *
from collisionManager import *
from targetManager import *
from smartnpc import *
from npcFactory import *
from player import *

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(GREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(TITLE)
        self.enemy_factory = npcFactory(self.surface)
        # self.enemies = [
        #     self.enemy_factory.create_npc("RED"),
        #     # self.enemy_factory.create_npc("RED", "large"),
        #     # self.enemy_factory.create_npc("RED", "small")
        #     ]
        
        self.enemies = [SmartNPC(self.surface, clan = "RED") for _ in range(1)]
        self.allies = [SmartNPC(self.surface, clan = "BLUE") for _ in range(1)]

        # self.allies = [NPC(self.surface, clan = "BLUE") for _ in range(1)]
        self.player = Player(self.surface, "Josh")
        self.npcs = self.enemies + self.allies
        # self.npcs = self.enemies + self.allies
        self.collision_manager = CollisionManager(self.player, self.npcs)
        self.target_manager = TargetManager(self.npcs, self.player)
        self.characters =  self.npcs + [self.player]
        [character.spawn(self.collision_manager) for character in self.characters] # Spawn the characters 

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

            self.npcs = [npc for npc in self.npcs if npc.health > 0]
            
            # Update all NPCs
            for npc in self.npcs:
                state = npc.get_state(self.npcs)
                # npc.update(self.characters, self.collision_manager)
                action = random.choice(npc.actions)
                reward = npc.act(action, self.collision_manager, self.npcs)
                npc.total_reward += reward
                print(f"NPC {npc.id} state: {state}, action: {action}, reward: {reward}")

            self.player.update(self.collision_manager)

            self.surface.fill(GREEN)
            # Draw all NPCs
            for npc in self.npcs:
                npc.draw(self.surface)

            self.player.draw(self.surface)
            pygame.display.update()
        pygame.quit()