import pygame
from healthbar import *
import os
import settings

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
        gold_img_path = os.path.join("assets", "images", "gold.png")
        self.gold_icon = pygame.image.load(gold_img_path)
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        wood_img_path = os.path.join("assets", "images", "wood.png")
        self.wood_icon = pygame.image.load(wood_img_path)
        self.show_stats = False

    def draw(self, surface):
        self.draw_healthbar(surface)
        self.draw_wood(surface)
        self.draw_gold(surface)
        if self.show_stats:
            self.draw_stats(surface)

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
        icon_size = 16
        icon = pygame.transform.scale(self.wood_icon, (icon_size, icon_size))
        posx = 40
        posy = 40
        surface.blit(icon, (posx, posy))
        font = pygame.font.Font('freesansbold.ttf', 15)
        text = font.render(f"{self.player.wood}", True, BLACK)
        surface.blit(text, (posx + icon_size, posy + 2))

    def draw_gold(self, surface):
        icon_size = 16
        icon = pygame.transform.scale(self.gold_icon, (icon_size, icon_size))
        posx = 10
        posy = 40
        surface.blit(icon, (posx, posy))
        font = pygame.font.Font('freesansbold.ttf', 15)
        text = font.render(f"{self.player.gold}", True, BLACK)
        surface.blit(text, (posx + icon_size, posy + 2))

    def toggle_stats(self):
        self.show_stats = not self.show_stats

    def draw_stats(self, surface):
        # 1) draw a semi-transparent background
        size_panel_x = 150
        size_panel_y = 200
        panel = pygame.Surface((size_panel_x, size_panel_y), flags=pygame.SRCALPHA)
        panel.fill((0,0,0,180))            # RGBA with alpha
        positionX = WIDTH - size_panel_x
        positionY = 50
        surface.blit(panel, (positionX, positionY))      # position it

        # 2) render each stat line by line
        font = pygame.font.Font(None, 24)
        stats = [
            f"HP: {self.player.health}/{self.player.max_health}",
            f"MP: {self.player.magic}/{self.player.max_magic}",
            f"Speed: {self.player.speed}",
            f"Stamina: {self.player.stamina}",
            f"Attack: {self.player.attack}",
            f"Defense: {self.player.defense}",
            # …etc…
        ]
        y = 60
        for line in stats:
            txt = font.render(line, True, (255,255,255))
            surface.blit(txt, (positionX + 10, y))
            y += 28

