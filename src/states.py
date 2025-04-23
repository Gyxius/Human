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
        self.health_timer = 0  # Initialize the timer
        self.direction = (0, 0)  # Start standing still

    def move(self, characters, collision_manager):
        # The npc checks each character to see if an enemy is close 
        # print(self.character.clan)
        for character in characters:
            # print(character.clan)
            if not character.alive:  # Skip dead characters
                continue
            if character.clan != self.character.clan and self._enemy_is_close(character):
                print(f"{self.character.name} sees an enemy! Switching to FollowingState.")
                self.character.set_state(FollowingState(self.character))
                self.character.target = [character]
        self._move_randomly(collision_manager)
        self._regenerate_health()

    def _regenerate_health(self):
        # Decrease the health timer
        if self.health_timer > 0:
            self.health_timer -= 1
        else:
            # Regenerate health when timer hits 0
            if self.character.health < 100:
                self.character.health += 2
            self.health_timer = 100  # Reset timer
        
    def _enemy_is_close(self, enemy):
        # The NPC notices  or not an enemy(player) within his range
        dx = enemy.xPosition - self.character.xPosition
        dy = enemy.yPosition - self.character.yPosition
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
    def move(self, characters, collision_manager):
        # Now follows the target
        dx = 0
        dy = 0
        target = self.character.target[0]
        if target.xPosition > self.character.xPosition + RADIUS_SIZE:
            dx = self.character.speed
        elif target.xPosition + RADIUS_SIZE < self.character.xPosition:
            dx = -self.character.speed
        if target.yPosition > self.character.yPosition + RADIUS_SIZE:
            dy = self.character.speed
        elif target.yPosition + RADIUS_SIZE < self.character.yPosition:
            dy = -self.character.speed

        if not collision_manager.is_colliding_circle(self.character, dx, dy):
            self.character.xPosition += dx
            self.character.yPosition += dy

        if self._target_is_far(target):
            # print(f"{self.character.name} lost sight of the target. Switching to IdleState.")
            self.character.set_state(IdleState(self.character))

        if target.health < 0:
            # print(f"{self.character.name} lost sight of the target. Switching to IdleState.")
            self.character.set_state(IdleState(self.character))

        if self._target_is_close(target):
            # print(f"{self.character.name} is next to the target. Switching to CloseState.")
            self.character.set_state(CloseState(self.character))

    def _target_is_far(self, player):
        dx = player.xPosition - self.character.xPosition
        dy = player.yPosition - self.character.yPosition
        distance = (dx**2 + dy**2) ** 0.5
        return distance > self.character.vision  # Lose sight range
    
    def _target_is_close(self, player):
        dx = player.xPosition - self.character.xPosition
        dy = player.yPosition - self.character.yPosition
        distance = (dx**2 + dy**2) ** 0.5
        return distance <= 2.2*RADIUS_SIZE # Quite close

class CloseState(NpcState):
    def move(self, characters, collision_manager):
        target = self.character.target[0]
        if self._target_is_far(target):
            # print(f"{self.character.name} target is far. Switching to Following State.")
            self.character.set_state(FollowingState(self.character))

    def _target_is_far(self, target):
        dx = target.xPosition - self.character.xPosition
        dy = target.yPosition - self.character.yPosition
        distance = (dx**2 + dy**2) ** 0.5
        return distance > 2.2*RADIUS_SIZE 


# In States Class
# Once an npc gets close enough to a player
# He will go from Following to Closestate
# In Npc Class
# He will be able to attack the player using the weapons 
# In Player Class
# The player will take damage