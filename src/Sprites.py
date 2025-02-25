import pygame 

class Sprites:
  # Define a method that draws a circle on the canvas.
  @staticmethod
  def Circle(surface, color, posx, posy, radius):
    return pygame.draw.circle(surface, color, (posx, posy), radius) 
