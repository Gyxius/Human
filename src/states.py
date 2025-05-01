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
            dx = self.direction[0]
            dy = self.direction[1]
            if 0 <= self.character.y + dy < collision_manager.grid.grid_height and 0 <= self.character.x + dx < collision_manager.grid.grid_width:
                if collision_manager.grid.grid[self.character.y + dy][self.character.x + dx] == ' ':
                    collision_manager.grid.grid[self.character.y][self.character.x] = ' '
                    collision_manager.object_grid.grid[self.character.y][self.character.x] = None
                    self.character.x = dx + self.character.x
                    self.character.y = dy +  self.character.y
                    self.character.xPosition, self.character.yPosition = collision_manager.grid.grid_to_pixel(self.character.x, self.character.y)
                    collision_manager.grid.grid[self.character.y][self.character.x] = self.character.grid_character
                    collision_manager.object_grid.grid[self.character.y][self.character.x] = self.character

        # Decrement timer each frame
        self.move_timer -= 1

class FollowingState(NpcState):
    def move(self, characters, collision_manager):
        # Now follows the target
        dx = 0
        dy = 0
        target = self.character.target[0]
        if target.x > self.character.x:
            dx = 1
        elif target.x < self.character.x:
            dx = -1
        if target.y > self.character.y:
            dy = 1
        elif target.y < self.character.y:
            dy = -1

        if 0 <= self.character.y + dy < collision_manager.grid.grid_height and 0 <= self.character.x + dx < collision_manager.grid.grid_width:
            if collision_manager.grid.grid[self.character.y + dy][self.character.x + dx] == ' ':
                collision_manager.grid.grid[self.character.y][self.character.x] = ' '
                self.character.x = dx + self.character.x
                self.character.y = dy +  self.character.y
                self.character.xPosition, self.character.yPosition = collision_manager.grid.grid_to_pixel(self.character.x, self.character.y)
                collision_manager.grid.grid[self.character.y][self.character.x] = 'C'

        if self._target_is_far(target):
            print(f"{self.character.name} lost sight of the target. Switching to IdleState.")
            self.character.set_state(IdleState(self.character))

        if target.health < 0:
            print(f"{self.character.name} lost sight of the target. Switching to IdleState.")
            self.character.set_state(IdleState(self.character))

        if self._target_is_close(target):
            print(f"{self.character.name} is next to the target. Switching to CloseState.")
            self.character.set_state(CloseState(self.character))

    def _target_is_far(self, target, distance = 3):
        """ Check If the enemy is x case around using chebyshev distance """
        dx = target.x - self.character.x
        dy = target.y - self.character.y
        if max(abs(dx), abs(dy)) > distance:
            return True
        return False
    
    def _target_is_close(self, target):
        """ Check If the enemy is one case around using chebyshev distance """
        dx = target.x - self.character.x
        dy = target.y - self.character.y
        if max(abs(dx), abs(dy)) > 0:
            return True
        return False

class CloseState(NpcState):
    def move(self, characters, collision_manager):
        target = self.character.target[0]
        if self._target_is_far(target):
            # print(f"{self.character.name} target is far. Switching to Following State.")
            self.character.set_state(FollowingState(self.character))

    def _target_is_far(self, target, distance = 1):
        """ Check If the enemy is x case around using chebyshev distance """
        dx = target.x - self.character.x
        dy = target.y - self.character.y
        if max(abs(dx), abs(dy)) > distance:
            return True
        return False


# In States Class
# Once an npc gets close enough to a player
# He will go from Following to Closestate
# In Npc Class
# He will be able to attack the player using the weapons 
# In Player Class
# The player will take damage