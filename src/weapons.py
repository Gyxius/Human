from settings import *
import pygame
from sprites import *

class Weapons:
    """Base class for weapons."""
    def __init__(self, owner, damage, attack_size):
        self.owner = owner  # The player or NPC using this weapon
        self.damage = damage
        self.attack_size = attack_size  # Width & height of attack
        self.active = False  # Attack is inactive until triggered
        self.attack_rect = None  # The area where the attack happens

    def attack(self):
        """Defines how the weapon attacks."""
        raise NotImplementedError("Subclasses must implement this method.")

    def draw(self, surface):
        """Draws the attack area for debugging (optional)."""
        if self.active and self.attack_rect:
            pygame.draw.rect(surface, WHITE, self.attack_rect, 1)

    def deactivate(self):
        """Disables attack after a short time."""
        self.active = False


class NoWeapon(Weapons):
    """A melee weapon that swings in front of the player."""
    def __init__(self, owner):
        self.attack_duration = 1
        self.attack_timer = 0
        super().__init__(owner, damage=owner.damage, attack_size=(RADIUS_SIZE * 2, RADIUS_SIZE * 2))

    def attack(self):
        """Triggers sword attack in front of the player."""
        if self.attack_timer > 0:
            return  # Prevent spamming attack before previous one disappears
    
        if self.active:
            return  # ✅ Prevent repeat attack if it's already active
        
        self.active = True
        self.attack_timer = self.attack_duration
        x, y = self.owner.xPosition, self.owner.yPosition

        attack_offsets = {
            ("right", "up"): (RADIUS_SIZE, -3 * RADIUS_SIZE),   # Top-right
            ("right", "down"): (RADIUS_SIZE, RADIUS_SIZE),      # Bottom-right
            ("left", "up"): (-3 * RADIUS_SIZE, -3 * RADIUS_SIZE), # Top-left
            ("left", "down"): (-3 * RADIUS_SIZE, RADIUS_SIZE),  # Bottom-left
            ("right",): (RADIUS_SIZE, -RADIUS_SIZE),           # Right
            ("left",): (-3 * RADIUS_SIZE, -RADIUS_SIZE),       # Left
            ("up",): (-RADIUS_SIZE, -3 * RADIUS_SIZE),         # Up
            ("down",): (-RADIUS_SIZE, RADIUS_SIZE),           # Down
        }

        directions = tuple(dir for dir in ["right", "left", "up", "down"] if self.owner.moving[dir])

        if directions in attack_offsets:
            dx, dy = attack_offsets[directions]
            self.attack_rect = pygame.Rect(x + dx, y + dy, *self.attack_size)
        else:
            self.attack_rect = None  # Prevent drawing empty attack

    def update(self):
        """Handles attack duration countdown."""
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.deactivate()  # Call deactivate when timer reaches 0

    def deactivate(self):
        """Disable attack after timer expires."""
        self.active = False
        self.attack_rect = None  # Remove attack hitbox