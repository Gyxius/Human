from characters import *
from weapons import *
from reward import *

class NPC(Characters):
  def __init__(self, surface, clan, radius = RADIUS_SIZE, speed = 300, vision = 200, damage = 10):
    self.xPosition = 0
    self.yPosition = 0
    self.x = 0
    self.y = 0
    self.radius = radius
    self.clan = clan
    if self.clan == "RED":
      self.color = RED
      self.grid_character = 'R'
    elif self.clan == "BLUE":
      self.color = BLUE
      self.grid_character = 'B'
    sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition, self.radius)
    super().__init__(sprite, "npc")
    self.state = IdleState(self)
    
    self.movement_speed = speed
    self.last_move_time = pygame.time.get_ticks()
    self.damage = damage
    self.vision = vision # How far they can see
    self.dx = 0
    self.dy = 0
    self.attack_speed = 5
    self.weapon = NoWeapon(self)
    self.player = False 
    self.target = [] # It will contain only one target but I made a list just in case
    self.wood = 0
    self.attack_reward = 0
    self.rewards = Reward()

  def movement_control(func):
      def wrapper(self, *args, **kwargs):
          if getattr(self, 'play_mode', True):
              current_time = pygame.time.get_ticks()
              if current_time - self.last_move_time >= self.movement_speed:
                  func(self, *args, **kwargs)
                  self.last_move_time = current_time
          else:
              func(self, *args, **kwargs)
      return wrapper
  
  def spawn(self, collision_manager, grid):
    xPosition = random.randint(0, grid.grid_width - 1)
    yPosition = random.randint(0, grid.grid_height - 1 )
    while(collision_manager.grid_colliding_circle(self, xPosition, yPosition, grid)):
      xPosition = random.randint(0, grid.grid_width - 1)
      yPosition = random.randint(0, grid.grid_height - 1 )

    self.x, self.y = xPosition, yPosition
    self.xPosition, self.yPosition = grid.grid_to_pixel(xPosition, yPosition)
    
  def draw(self, surface):
    if self.alive:
      self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition, self.radius)
      self.healthbar.draw(surface)
      self.rewards.draw(self.xPosition, self.yPosition, surface) 

  @movement_control
  def move(self, characters, collision_manager):
     self.state.move(characters, collision_manager)  # Delegate behavior to the current state
  
  def update(self, characters, collision_manager):
    if self.alive:
      if self.target and not self.target[0].alive:
        print(f"NPC {self.id} target is dead. Switching to IdleState.")
        self.target = []
        self.set_state(IdleState(self))
      self.move(characters, collision_manager) 
      if self.is_in_state(CloseState):
        self.weapon.update() 
        self.hit_target(collision_manager)

  def set_state(self, state):
     self.state = state

  @property
  def collision_block(self):
    return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

  def take_damage(self, damage, npc_list, attacker):
      """Called when the NPC is hit
        if health is too low the rewards is super negative
      
      
      """
      if attacker.clan == self.clan:
         return
      self.health -= damage
      if (self.target and self.target[0]):
        self.target[0] = attacker
        print(f"NPC {self.id} took {damage} damage! Health: {self.health}")
        self.rewards.reward(-5 - 0.5*(100 - self.health), "Getting attacked")
        if self.health <= 0:
            self.alive = False
            print(f"NPC {self.id} has died!")
            if self in npc_list:
                npc_list.remove(self)
            # Cleanup targets for others
            for npc in npc_list:
                if npc.target and npc.target[0] == self:
                    npc.target = []
                    npc.set_state(IdleState(npc))

  def hit_target(self, collision_manager):
    if self.target and not self.target[0].alive:
        print(f"NPC {self.id} target died during attack. Switching to IdleState.")
        self.target = []
        self.set_state(IdleState(self))
        return
  
    if self.weapon.active or not self.is_in_state(CloseState):
       return
    
    print("attack enemy")
    self.weapon.attack(self)
    target = self.target[0]
    target.take_damage(self.weapon.damage, collision_manager.npcs, self)  # Make NPC take damage!
    self.rewards.reward(10 + 0.5*(100 - self.health), "attacked target")

  def is_in_state(self, state_class):
    return isinstance(self.state, state_class)
  
  def act(self, *args, **kwargs):
      return 0, False  # Dummy reward, done