import pygame
from healthbar import *
import os

"""
hud.py
-------
HUD stands for Heads-Up Display.

Responsibilities:
    - Draw the player’s healthbar at the top of the screen, with color changes
      based on health thresholds.
    - Render the player’s collected wood count in a consistent position.
    - Provide a single, centralized place for all on-screen UI elements.

Usage:
    hud = HUD(player)
    hud.draw(surface)  # call once per frame, after drawing characters and resources
"""


class HUD:
    def __init__(self, player, font_size=24):
        self.player = player
        img_path = os.path.join("assets", "images", "gold.png")
        self.gold_icon = pygame.image.load(img_path)
        self.font = pygame.font.Font('freesansbold.ttf', 20)

    def draw(self, surface):
        self.draw_healthbar(surface)
        self.draw_wood(surface)
        self.draw_gold(surface)

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
        text = self.font.render('Wood: ' + str(self.player.wood), True, BLACK)
        textRect = text.get_rect()
        posx = 10
        posy = 60
        textRect = (posx, posy)
        surface.blit(text, textRect)

    def draw_gold(self, surface):
        # Draws on the screens the amount of gold the player has
        icon_size = 16
        icon = pygame.transform.scale(self.gold_icon, (icon_size, icon_size))
        posx = 10
        posy = 40
        surface.blit(icon, (posx, posy))
        font = pygame.font.Font('freesansbold.ttf', 15)
        text = font.render(f"{self.player.gold}", True, BLACK)
        surface.blit(text, (posx + icon_size, posy + 2))
