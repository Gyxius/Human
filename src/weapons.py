from settings import *
import pygame
from sprites import *
import time

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
            pygame.draw.rect(surface, LIGHT_GREEN, self.attack_rect, 1)

    def deactivate(self):
        """Disables attack after a short time."""
        self.active = False

class NoWeapon(Weapons):
    """A melee weapon that swings in front of the player."""
    def __init__(self, owner):
        self.attack_duration = owner.attack_speed # 3 seconds before another attack
        self.attack_end_time = 0 # time when attack should stop
        super().__init__(owner, damage=owner.damage, attack_size=(BLOCK_SIZE, BLOCK_SIZE))

    def attack(self, character):
        """Triggers  attack in front of the player."""
        current_time = time.time()

        # If still active, prevent re-attacking
        if self.active and current_time < self.attack_end_time:
            return
        
        self.active = True
        self.attack_end_time = current_time + self.attack_duration

        if character.player:
            attack_offsets = {
                ("right", "up"): (1,-1),   # Top-right
                ("right", "down"): (1,1),      # Bottom-right
                ("left", "up"): (-1,-1), # Top-left
                ("left", "down"): (-1,1),  # Bottom-left
                ("right",): (1,0),           # Right
                ("left",): (-1,0),       # Left
                ("up",): (0,-1),         # Up
                ("down",): (0,1),           # Down
            }
            directions = tuple(dir for dir in ["right", "left", "up", "down"] if self.owner.moving[dir])
            
            x, y = self.owner.x, self.owner.y
            if directions in attack_offsets:
                dx, dy = attack_offsets[directions]
                x_rect = (x + dx)*BLOCK_SIZE
                y_rect = (y + dy)*BLOCK_SIZE
                self.attack_rect = pygame.Rect(x_rect, y_rect, *self.attack_size)
            else:
                self.attack_rect = None  # Prevent drawing empty attack
        else:
            pass

    def update(self):
        """Handles attack duration countdown."""
        if self.active and time.time() >= self.attack_end_time:
                self.deactivate()

    def deactivate(self):
        """Disable attack after timer expires."""
        self.active = False
        self.attack_rect = None  # Remove attack hitbox