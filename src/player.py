from characters import *
from weapons import *
from settings import *

"""
player.py
----------

Responsibilities:
    - Handle player input & movement
    - Manage health regeneration
    - Perform attacks / mining
    - Expose `wood` & `gold` counters

Rendering is delegated to HUD.draw(), not here!
"""

class Player(Characters):
    def __init__(self, surface, name, grid):
        
        self.x = 0
        self.y = 0
        self.xPosition, self.yPosition = grid.grid_to_pixel(self.x, self.y)
        self.movement_speed = 200 # Milliseconds between each movement
        self.moving = {"up": False, "down": False, "left": False, "right": False, "space": False}
        self.color = LIGHT_GREEN
        self.sprite = Sprites.Circle(surface, color = self.color, posx = self.xPosition, posy = self.yPosition)
        self.clan = "BLUE"
        super().__init__(self.sprite, name)
        self.dx = 0
        self.dy = 0
        self.attack_sprite = None
        self.attack_speed = 1 # In seconds, the lower the better, how many seconds between each attack
        self.health_timer = 0 
        self.regeneration_time = 2
        self.player = True 
        self.damage = 30
        self.weapon = NoWeapon(self)
        self.healthbar = Healthbar(self)
        self.last_move_time = pygame.time.get_ticks()
        self.grid_character = 'P'

    def movement_control(func):
        def wrapper(self, *args, **kwargs):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time >= self.movement_speed: 
                func(self, *args, **kwargs)
                self.last_move_time = current_time 
        return wrapper

    def regenerate_health(self):
        # Decrease the health timer
        if self.health_timer > 0:
            self.health_timer -= 1
        else:
            # Regenerate health when timer hits 0
            if self.health < 100:
                self.health += self.regeneration_time
            self.health_timer = 100  # Reset timer

    @movement_control
    def move(self, collision_manager, grid):
        """
        Update the player's grid position based on current movement flags.

        Checks for collisions via the provided CollisionManager and only
        commits the move if the target cell is free.

        Parameters:
            collision_manager (CollisionManager):
                used to test and resolve collisions before moving.
            grid (Grid):
                the spatial grid in which the player's x/y coordinates live.

        Side-effects:
            - updates self.x, self.y, self.xPosition, self.yPosition
            - updates grid occupancy cells
        """
        dx = dy = 0 
        if self.moving["up"]:
            dy = -1
        if self.moving["down"]:
            dy =  1
        if self.moving["left"]:
            dx = - 1
        if self.moving["right"]:
            dx = 1

        self._attempt_move(dx, dy, collision_manager, grid)
        
    def _attempt_move(self, dx, dy, collision_manager, grid):
        """
        If (x+dx,y+dy) is on grid and empty, clear the old cell,
        update our x/y + pixel position, and occupy the new cell.
        """
        if 0 <= self.y + dy < collision_manager.grid.grid_height and 0 <= self.x + dx < collision_manager.grid.grid_width:
            if collision_manager.grid.grid[self.y + dy][self.x + dx] == ' ':
                collision_manager.grid.grid[self.y][self.x] = ' '
                collision_manager.object_grid.grid[self.y][self.x] = None
                self.x = dx + self.x
                self.y = dy +  self.y
                self.xPosition, self.yPosition = grid.grid_to_pixel(self.x, self.y)
                collision_manager.grid.grid[self.y][self.x] = self.grid_character
                collision_manager.object_grid.grid[self.y][self.x] = self

    def draw(self, surface):
        # Draw the sprite
        self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition)
        # Draw the attack
        self.weapon.draw(surface) 
        # self.rewards.draw(surface)
        
    def update(self, collision_manager, grid):
        self.move(collision_manager, grid)
        self.weapon.update() 
        self.hit_target(collision_manager)
        self.regenerate_health()

    @property
    def collision_block(self):
        return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

    def hit_target(self, collision_manager):
        """
        Perform an attack if the player is pressing space and the weapon is ready.
        Detects enemy NPCs in range and applies damage.
        """
        if not self.moving["space"] or self.weapon.active:
            return
        
        self.weapon.attack(self)

        if not self.weapon.attack_rect: 
            return
        
        self.weapon.attack(self)

        if not self.weapon.attack_rect:
            return

        targets = self._get_enemies_in_attack_range(collision_manager)
        self._apply_damage_to_enemies(targets, collision_manager)
        object_hit, object_type = collision_manager.get_object_hit(self.weapon.attack_rect)
        print("The object being hit is :" + str(object_hit))
        if object_type == 'T':
            mined = object_hit.mine(1)
            self.wood += mined

    def _get_enemies_in_attack_range(self, collision_manager):
        """Return a list of enemy NPCs hit by the attack."""
        npcs_hit = collision_manager.rectangle_collision(rect=self.weapon.attack_rect)
        return [npc for npc in npcs_hit if npc.clan != self.clan]
    
    def _apply_damage_to_enemies(self, enemies, collision_manager):
        """Deal damage to all hit enemies."""
        for npc in enemies:
            print(f"{npc.id} is being attacked by player")
            npc.take_damage(self.weapon.damage, collision_manager.npcs, self)

    def take_damage(self, damage, npc_list, attacker):
      """Called when the player is hit"""
      self.health -= damage
      print(f"Player took {damage} damage! Health: {self.health}")
      if self.health <= 0:
          print(f"Player {self.id} has died!")
          print("Game over")

    def spawn(self, collision_manager, grid):
        xPosition = random.randint(0, grid.grid_width - 1)
        yPosition = random.randint(0, grid.grid_height - 1 )
        while(collision_manager.grid_colliding_circle(self, xPosition, yPosition, grid)):
            xPosition = random.randint(0, grid.grid_width - 1)
            yPosition = random.randint(0, grid.grid_height - 1 )

        self.x, self.y = xPosition, yPosition
        self.xPosition, self.yPosition = grid.grid_to_pixel(xPosition, yPosition)