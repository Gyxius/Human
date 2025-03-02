import pygame
from settings import *

class CollisionManager:
    def __init__(self, player, npcs, obstacles=None):
        self.player = player
        self.npcs = npcs
        self.obstacles = obstacles or []

    def is_colliding_circle(self, character, dx, dy):
        """
        Check if `character`'s future position (after moving dx, dy) collides with any other character.
        """
        new_x = character.xPosition + dx
        new_y = character.yPosition + dy

        if (new_x - RADIUS_SIZE < 0 or new_x + RADIUS_SIZE > WIDTH or new_y - RADIUS_SIZE < 0 or new_y + RADIUS_SIZE > HEIGHT):
            return True  # Block movement outside screen

        # Check all NPCs
        for npc in self.npcs:
            if character.id != npc.id and self.circle_collision(new_x, new_y, npc):
                return True
            
        if character.id != self.player.id and self.circle_collision(new_x, new_y, self.player):
            return True

        return False

    @staticmethod
    def circle_collision(x1, y1, obj2):
        """
        Check if a circle centered at (x1, y1) overlaps with another circle (obj2).
        """
        dx = x1 - obj2.xPosition
        dy = y1 - obj2.yPosition
        distance = (dx**2 + dy**2)**0.5
        return distance <= (2 * RADIUS_SIZE)  # Total diameter (both radii)