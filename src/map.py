import pygame 
from settings import *
from characters import *

class Map:
    def __init__(self, surface):
        self.color = (206, 231, 65)
        self.name = "main"
        self.rect = (0, 0, WIDTH, HEIGHT)
        self.nb_enemies = 5
        pygame.draw.rect(surface, self.color, self.rect)
        self.surface = surface
        self.load_enemies()
        
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def load_enemies(self):
        self.enemies = [NPC(self.surface) for _ in range(3)]
