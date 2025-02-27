import pygame 
from pygame.locals import *
from characters import *

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface.fill(WHITE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(TITLE)

        self.player = Player(self.surface, "Josh")
        self.enemy = Enemies(self.surface)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()