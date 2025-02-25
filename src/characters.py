from Sprites import *
from settings import *


class Characters:
  def __init__(self, sprite, name = "npc", color = "red"):
    self.id = 0
    self.color = color
    self.name = name
    self.xPosition = 200
    self.yPosition = 75
    self.sprite = sprite
    self.speed = 10

  def draw():
     pass

class Player(Characters):
  def __init__(self, surface, name):
    sprite = Sprites.Circle(surface, BLUE, WIDTH//2, HEIGHT//2, 40)
    super().__init__(sprite, name, "blue")

  def moveUp(self):
    self.yPosition -= self.speed

  def moveDown(self):
    self.yPosition += self.speed
  
  def moveLeft(self):
    self.xPosition -= self.speed
  
  def moveRight(self):
    self.xPosition += self.speed
  


class Enemies(Characters):
  def __init__(self, surface):
    sprite = Sprites.Circle(surface, RED, WIDTH//3, HEIGHT//3, 40)
    super().__init__(sprite, "npc", "red")
  
  def move():
    pass
