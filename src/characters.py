from Sprites import *
from states import *
from settings import *
import random


class Characters:
  def __init__(self, sprite, name = "npc", color = "red"):
    # Basic Player Attributes
    self.id = 0
    self.color = color
    self.name = name
    self.sprite = sprite
    self.health = 100
    self.status = "Villager"  # Villager, Chief, Slave, Outcast
    self.profession = "Unemployed"

        # Clan and Reputation
    self.clan = "None"
    self.clan_points = 0
    self.reputation = {
        "dangerous": 0,
        "loved": 0,
        "feared": 0
    }

    # Economy and Assets
    self.money = 100
    self.inventory = []
    self.house = None
    self.land = []
    self.animals = []

  def draw():
     pass

  # Economic Actions
  def gather_wood(self):
      self.inventory.append("wood")
      print(f"{self.name} gathered wood!")

  def mine_ore(self):
      self.inventory.append("ore")
      print(f"{self.name} mined ore!")

  def raise_animal(self, animal):
      self.animals.append(animal)
      print(f"{self.name} raised a {animal}.")

  def buy_item(self, item, price):
      if self.money >= price:
          self.money -= price
          self.inventory.append(item)
          print(f"{self.name} bought {item} for {price} gold.")
      else:
          print(f"{self.name} cannot afford {item}.")

  def sell_item(self, item, price):
      if item in self.inventory:
          self.inventory.remove(item)
          self.money += price
          print(f"{self.name} sold {item} for {price} gold.")
      else:
          print(f"{self.name} does not have {item}.")

  def open_shop(self):
      if self.house:
          print(f"{self.name} opened a shop in their house.")
      else:
          print(f"{self.name} has no house to open a shop.")

  # Political/Clan System
  def join_clan(self, clan_name):
      self.clan = clan_name
      print(f"{self.name} joined the {clan_name} clan!")

  def follow_chief(self):
      self.clan_points += 5
      print(f"{self.name} gains 5 clan points by following the chief.")

  def betray_clan(self):
      self.clan_points -= 10
      print(f"{self.name} betrays the {self.clan} clan and loses 10 points.")

  def check_clan_status(self):
      if self.clan_points < -50:
          print(f"{self.name} is EXPELLED from {self.clan}!")
          self.status = "Outcast"
      elif self.clan_points >= 100:
          print(f"{self.name} is now an ELDER in the {self.clan} clan!")

  # Land and Housing
  def build_house(self):
      if self.house is None:
          self.house = "Small House"
          print(f"{self.name} built a house!")
      else:
          print(f"{self.name} already has a house.")

  def buy_land(self, land_name):
      self.land.append(land_name)
      print(f"{self.name} bought land: {land_name}.")

  def collides_with_anything(new_x, new_y, width, height, player, npcs, obstacles):
    # Check obstacles (houses, etc.)
    for obj in obstacles:
        if (new_x < obj["x"] + obj["width"] and
            new_x + width > obj["x"] and
            new_y < obj["y"] + obj["height"] and
            new_y + height > obj["y"]):
            return True

    # Check NPCs
    for npc in npcs:
        if (new_x < npc.xPosition + RADIUS_SIZE and
            new_x + width > npc.xPosition and
            new_y < npc.yPosition + RADIUS_SIZE and
            new_y + height > npc.yPosition):
            return True

    # Check player (if enemies are moving)
    if player:
        if (new_x < player.xPosition + RADIUS_SIZE and
            new_x + width > player.xPosition and
            new_y < player.yPosition + RADIUS_SIZE and
            new_y + height > player.yPosition):
            return True

    return False  


class Player(Characters):
  def __init__(self, surface, name):
    
    self.xPosition = WIDTH//2
    self.yPosition = HEIGHT//2
    self.speed = 2
    self.moving = {"up": False, "down": False, "left": False, "right": False}
    sprite = Sprites.Circle(surface, BLUE, self.xPosition, self.yPosition)
    super().__init__(sprite, name, "blue")

  def moveUp(self):
    self.yPosition -= self.speed

  def moveDown(self):
    self.yPosition += self.speed
  
  def moveLeft(self):
    self.xPosition -= self.speed
  
  def moveRight(self):
    self.xPosition += self.speed

  def draw(self, surface):
    self.sprite = Sprites.Circle(surface, BLUE, self.xPosition, self.yPosition)

  def update(self, surface):
    # Move player based on held keys
    if self.moving["up"]:
        self.moveUp()
    if self.moving["down"]:
        self.moveDown()
    if self.moving["left"]:
        self.moveLeft()
    if self.moving["right"]:
        self.moveRight()
  

class NPC(Characters):
  def __init__(self, surface):
    self.xPosition = random.randint(0, WIDTH)
    self.yPosition = random.randint(0, HEIGHT)
    sprite = Sprites.Circle(surface, RED, self.xPosition, self.yPosition)
    super().__init__(sprite, "npc", "red")
    self.state = IdleState(self)
    self.speed = 1
    self.vision = 100 # How far they can see
  
  def draw(self, surface):
    self.sprite = Sprites.Circle(surface, RED, self.xPosition, self.yPosition)

  def update(self, player):
    self.state.move(player)  # Delegate behavior to the current state
  
  def set_state(self, state):
     self.state = state


