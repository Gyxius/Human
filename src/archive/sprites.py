import pygame 
from settings import *

class Sprites:
  # Define a method that draws a circle on the canvas.
  @staticmethod
  def Circle(surface, color, posx, posy, radius = RADIUS_SIZE):
    pygame.draw.circle(surface, (0, 0, 0), (posx, posy), radius + 1 ) # Radius + Border thickness
    pygame.draw.circle(surface, color, (posx, posy), width = 0, radius = radius) 
  
  @staticmethod
  def Rectangle(surface, color, posx, posy, rect_width = RADIUS_SIZE * 2, rect_height = RADIUS_SIZE * 2, width = 1):
    rect = pygame.Rect(posx, posy, rect_width, rect_height)
    pygame.draw.rect(surface, color, rect, width=width)
    return rect