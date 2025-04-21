from characters import *
from weapons import *


class NPC(Characters):
  def __init__(self, surface, clan):
    self.xPosition = random.randint(RADIUS_SIZE, WIDTH - RADIUS_SIZE)
    self.yPosition = random.randint(RADIUS_SIZE, HEIGHT - RADIUS_SIZE)
    self.clan = clan
    if self.clan == "RED":
      self.color = RED
    elif self.clan == "BLUE":
      self.color = BLUE
    sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition)
    super().__init__(sprite, "npc")
    self.state = IdleState(self)
    self.speed = 1
    self.vision = 200 # How far they can see
    self.dx = 0
    self.dy = 0
    self.attack_speed = 5
    self.weapon = NoWeapon(self)
    self.player = False 
    self.target = [] # It will contain only one target but I made a list just in case
    
  def draw(self, surface):
    self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition)
    # Draw the health bar
    self.healthbar = Sprites.Rectangle(surface, LIGHT_GREEN, self.xPosition - 20, self.yPosition + 30, self.health // 2, 10, 0)



  def update(self, characters, collision_manager):
    if self.health > 0:
      self.state.move(characters, collision_manager)  # Delegate behavior to the current state
    if self.is_in_state(CloseState):
      self.weapon.update() 
      self.attack_target(collision_manager)
    
  
  def set_state(self, state):
     self.state = state

  @property
  def collision_block(self):
    return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

  def take_damage(self, damage, npc_list):
      """Called when the NPC is hit"""
      self.health -= damage
      print(f"NPC {self.id} took {damage} damage! Health: {self.health}")
      if self.health <= 0 and self in npc_list:
          print(f"NPC {self.id} has died!")
          npc_list.remove(self)  # Remove from the game

  def attack_target(self, collision_manager):
    if not self.weapon.active and self.is_in_state(CloseState):
      print("attack enemy")
      self.weapon.attack(self)
      target = self.target[0]
      target.take_damage(self.weapon.damage, collision_manager.npcs)  # Make NPC take damage!

  def is_in_state(self, state_class):
    return isinstance(self.state, state_class)
  
