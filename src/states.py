from abc import ABC, abstractmethod
import random
from settings import *
from collisionManager import *

class NpcState(ABC):
    def __init__(self, character):
        self.character = character  # The NPC using this state (enemy, ally, etc.)

    @abstractmethod
    def move(self, player, collision_manager):
        pass


class IdleState(NpcState):
    def __init__(self, character):
        super().__init__(character)
        self.move_timer = 0  # Initialize the timer
        self.direction = (0, 0)  # Start standing still

    def move(self, player, collision_manager):
        if self._enemy_is_close(player):
            print(f"{self.character.name} sees an enemy! Switching to FollowingState.")
            self.character.set_state(FollowingState(self.character))
        self._move_randomly(collision_manager)
        
    def _enemy_is_close(self, player):
        dx = player.xPosition - self.character.xPosition
        dy = player.yPosition - self.character.yPosition
        distance = (dx**2 + dy**2) ** 0.5
        return distance < self.character.vision  # Detection range
    
    def _move_randomly(self, collision_manager):
        # Check if it's time to pick a new action (move or idle)
        if self.move_timer <= 0:
            # 30% chance to idle (stand still), 70% chance to move
            if random.random() < 0.3:
                self.direction = (0, 0)  # Stand still
            else:
                # Pick one of the 4 cardinal directions (no diagonal)
                self.direction = random.choice([
                    (0, -1),  # Up
                    (0, 1),   # Down
                    (-1, 0),  # Left
                    (1, 0)    # Right
                ])

            # Set timer for how long to keep moving or standing still
            self.move_timer = random.randint(30, 100)  # Frames until next decision

        # Apply movement only if the NPC is moving
        if self.direction != (0, 0):
            dx = self.direction[0] * self.character.speed
            dy = self.direction[1] * self.character.speed
            if not collision_manager.is_colliding_circle(self.character, dx, dy):
                self.character.xPosition += dx
                self.character.yPosition += dy

        # Decrement timer each frame
        self.move_timer -= 1



class FollowingState(NpcState):
    def move(self, player, collision_manager):
        dx = 0
        dy = 0
        if player.xPosition > self.character.xPosition + RADIUS_SIZE:
            dx = self.character.speed
        elif player.xPosition + RADIUS_SIZE < self.character.xPosition:
            dx = -self.character.speed
        if player.yPosition > self.character.yPosition + RADIUS_SIZE:
            dy = self.character.speed
        elif player.yPosition + RADIUS_SIZE < self.character.yPosition:
            dy = -self.character.speed

        if not collision_manager.is_colliding_circle(self.character, dx, dy):
            self.character.xPosition += dx
            self.character.yPosition += dy

        if self._player_is_far(player):
            print(f"{self.character.name} lost sight of the player. Switching to IdleState.")
            self.character.set_state(IdleState(self.character))

    def _player_is_far(self, player):
        dx = player.xPosition - self.character.xPosition
        dy = player.yPosition - self.character.yPosition
        distance = (dx**2 + dy**2) ** 0.5
        return distance > self.character.vision  # Lose sight range