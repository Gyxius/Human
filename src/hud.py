import pygame
from healthbar import *

class HUD:
    def __init__(self, player, font_size=24):
        self.player = player
    
    def draw(self, surface):
        self.draw_healthbar(surface)
        self.draw_wood(surface)

    def draw_healthbar(self, surface):
        posx = 10
        posy = 10
        width = self.player.health
        height = 25
        rect = pygame.Rect(posx, posy, width, height)
        color = GREEN_HEALTH
        if self.player.health <= 60:
            color = YELLOW_HEALTH
        if self.player.health <= 40:
            color = ORANGE_HEALTH
        if self.player.health <= 20:
            color = RED_HEALTH
        pygame.draw.rect(surface, color, rect, width=0)
        return rect
    
    def draw_wood(self, surface):
        font = pygame.font.Font('freesansbold.ttf', 20)
        text = font.render('Wood: ' + str(self.player.wood), True, BLACK)
        textRect = text.get_rect()
        posx = 10
        posy = 50
        textRect = (posx, posy)
        surface.blit(text, textRect)
