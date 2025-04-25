import pygame
from settings import *

class CollisionManager:
    def __init__(self, player, npcs, grid, obstacles=None):
        self.player = player
        self.npcs = npcs
        self.obstacles = obstacles or []
        self.grid = grid

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
    
    def grid_colliding_circle(self, character, x, y, grid):
        """
        Check if `character`'s future grid position overlap with any other character.
        """

        if (x < 0 or x > grid.grid_width or y < 0 or y> grid.grid_height):
            return True  # Block movement outside screen

        # Check all NPCs
        for npc in self.npcs:
            if character.id != npc.id and npc.x == x and npc.y == y:
                return True
            
        if character.id != self.player.id and self.player.x == x and self.player.y == y:
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
    
    
    def rectangle_collision(self, rect):
        """
        Check if a rectangle collides with any NPC circle.
        Add collided NPCs to self.npcs_attacked.
        Return the set containing all the nps attacked
        """
        rect_x, rect_y, rect_w, rect_h = rect.x, rect.y, rect.width, rect.height
        self.npcs_attacked = set()
        
        for circle in self.npcs:
            circle_distance_x = abs(circle.xPosition - (rect_x + rect_w / 2))
            circle_distance_y = abs(circle.yPosition - (rect_y + rect_h / 2))

            # Quick rejection if too far
            if circle_distance_x > (rect_w / 2 + RADIUS_SIZE):
                continue
            if circle_distance_y > (rect_h / 2 + RADIUS_SIZE):
                continue

            # Inside rectangle check (side touching)
            if circle_distance_x <= (rect_w / 2):
                self.npcs_attacked.add(circle)
                continue
            if circle_distance_y <= (rect_h / 2):
                self.npcs_attacked.add(circle)
                continue

            # Corner collision check (circle corner overlap)
            cornerDistance_sq = (circle_distance_x - rect_w / 2)**2 + (circle_distance_y - rect_h / 2)**2

            if cornerDistance_sq <= (RADIUS_SIZE**2):
                self.npcs_attacked.add(circle)
        return self.npcs_attacked 