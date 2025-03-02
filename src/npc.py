from characters import *

class NPC(Characters):
  def __init__(self, surface):
    self.xPosition = random.randint(RADIUS_SIZE, WIDTH - RADIUS_SIZE)
    self.yPosition = random.randint(RADIUS_SIZE, HEIGHT - RADIUS_SIZE)
    sprite = Sprites.Circle(surface, RED, self.xPosition, self.yPosition)
    super().__init__(sprite, "npc", "red")
    self.state = IdleState(self)
    self.speed = 1
    self.vision = 200 # How far they can see
    self.dx = 0
    self.dy = 0
  
  def draw(self, surface):
    self.sprite = Sprites.Circle(surface, RED, self.xPosition, self.yPosition)

  def update(self, player, collision_manager):
    self.state.move(player, collision_manager)  # Delegate behavior to the current state
  
  def set_state(self, state):
     self.state = state

  @property
  def collision_block(self):
    return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)


