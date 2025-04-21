import pygame 
from settings import *


class Healthbar: 
    def __init__(self, character, height = 10, x_offset = -20, y_offset = 30):
        self.character = character
        # self.width = self.character.health
        self.height = height
        self.y_offset = y_offset
        self.x_offset = x_offset
    
    def draw(self, surface):
        rect = pygame.Rect(self.character.xPosition + self.x_offset, self.character.yPosition + self.y_offset, self.character.health // 2, self.height)
        color = GREEN_HEALTH
        if self.character.health <= 60:
            color = YELLOW_HEALTH
            print("here")
        if self.character.health <= 40:
            color = ORANGE_HEALTH
        if self.character.health <= 20:
            color = RED_HEALTH
        print(self.character.health )
        pygame.draw.rect(surface, color, rect, width=0)
        return rect
        