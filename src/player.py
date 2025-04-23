from characters import *
from weapons import *
from settings import *


class Player(Characters):
    def __init__(self, surface, name):
        
        self.xPosition = WIDTH//2
        self.yPosition = HEIGHT//2
        self.speed = 2
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

    def regenerate_health(self):
        # Decrease the health timer
        if self.health_timer > 0:
            self.health_timer -= 1
        else:
            # Regenerate health when timer hits 0
            if self.health < 100:
                self.health += self.regeneration_time
            self.health_timer = 100  # Reset timer

    def move(self, collision_manager):
        self.dx = self.dy = 0  # reset every frame

        if self.moving["up"]:
            self.dy = -self.speed
        if self.moving["down"]:
            self.dy = self.speed
        if self.moving["left"]:
            self.dx = -self.speed
        if self.moving["right"]:
            self.dx = self.speed

        # Use the delta values directly for collision check
        if not collision_manager.is_colliding_circle(self, self.dx, self.dy):
            self.xPosition += self.dx
            self.yPosition += self.dy


    def draw(self, surface):
        # Draw the sprite
        self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition)
        # Draw the attack
        self.weapon.draw(surface) 
        # Draw the health bar
        # self.healthbar = Sprites.Rectangle(surface, LIGHT_GREEN, self.xPosition - 20, self.yPosition + 30, self.health // 2, 10, 0)
        self.healthbar.draw(surface)

    def update(self, collision_manager):
        # Move player based on held keys
        self.move(collision_manager)
        self.weapon.update() 
        self.attack_target(collision_manager)
        self.regenerate_health()

    @property
    def collision_block(self):
        return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

    def attack_target(self, collision_manager):
        # Check who is around
        if self.moving["space"] and not self.weapon.active:
            self.weapon.attack(self)
            if self.weapon.attack_rect: 
                npcs_attacked = collision_manager.rectangle_collision(rect = self.weapon.attack_rect)   # Check if the attack (Rectangle Square collides with an enemy)
                enemies_attacked = [npc for npc in npcs_attacked if npc.clan != self.clan]
                for npc in enemies_attacked:
                    print(f"{npc.id} is being attacked by player")
                    npc.take_damage(self.weapon.damage, collision_manager.npcs, self)  # Make NPC take damage!

    def take_damage(self, damage, npc_list, attacker):
      """Called when the player is hit"""
      self.health -= damage
      print(f"Player took {damage} damage! Health: {self.health}")
      if self.health <= 0:
          print(f"Player {self.id} has died!")
          print("Game over")