import pygame 
from settings import *

class Sprites:
  # Define a method that draws a circle on the canvas.
  @staticmethod
  def Circle(surface, color, posx, posy):
    pygame.draw.circle(surface, (0, 0, 0), (posx, posy), RADIUS_SIZE + 1 ) # Radius + Border thickness
    pygame.draw.circle(surface, color, (posx, posy), width = 0, radius = RADIUS_SIZE) 
  
  @staticmethod
  def Rectangle(surface, color, posx, posy):
    pygame.draw.rect(surface, color, rect=(posx, posy, RADIUS_SIZE * 2, RADIUS_SIZE * 2), width=1)
