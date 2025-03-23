from sprites import *
from states import *
from settings import *
import random


class Characters:
  next_id = 0
  def __init__(self, sprite, name = "npc"):
    # Basic Player Attributes
    Characters.next_id += 1
    self.id = Characters.next_id
    self.name = name
    self.sprite = sprite
    self.health = 100
    self.status = "Villager"  # Villager, Chief, Slave, Outcast
    self.profession = "Unemployed"
    self.width = 2 * RADIUS_SIZE
    self.height = 2 * RADIUS_SIZE
    self.damage = 10

        # Reputation
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


