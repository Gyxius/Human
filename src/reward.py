import pygame
from settings import *

class Reward:
    def __init__(self):
        self.total_reward = 0
        self.font = pygame.font.Font('freesansbold.ttf', 20)

    def reward(self, value, reason=""):
        self.total_reward += value
        print(f"Reward {value} for {reason} -> Total: {self.total_reward}")

    def reset(self):
        self.total_reward = 0

    def get_reward(self):
        return self.total_reward
    
    def draw(self, posx, posy, surface):
        text = self.font.render(str(self.total_reward), True, BLACK, WHITE)
        textRect = text.get_rect()
        textRect.center = (posx, posy)
        surface.blit(text, textRect)

