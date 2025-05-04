import pygame
from settings import *

class Grid:
    def __init__(self, windows_height, windows_width, block_size):
        self.windows_height = windows_height
        self.windows_width = windows_width
        self.block_size = block_size
        self.grid_width = self.windows_width // self.block_size
        self.grid_height = self.windows_height // self.block_size
        self._set_grid()

    def _set_grid(self):
        self.grid = []
        for _ in range(self.grid_height):
            row = []
            for _ in range(self.grid_width):
                row.append(' ')
            self.grid.append(row)
            
    def clear(self):
        self._set_grid()

    def draw_grid(self, surface):
        for x in range(0, self.windows_width , self.block_size):
            for y in range(0, self.windows_height, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(surface, WHITE, rect, 1)

    def print_grid(self):
        """ print to the consol the content of the grid"""
        print("\nGrid Content:")
        for row in self.grid:
            print(' |'.join(row))
        print("\n")
    
    def grid_to_pixel(self, positionx, positiony, center = True):
        """Convert grid position to pixel coordinates. Centered by default."""
        pixel_x = positionx * self.block_size
        pixel_y = positiony * self.block_size
        if center:
            pixel_x += self.block_size // 2
            pixel_y += self.block_size // 2
        return pixel_x, pixel_y
    
    def pixel_to_grid(self, pixelx, pixely):
        """ You give a grid position x and y and it tells you where to put it pixel wise"""
        gridx = pixelx // self.block_size
        gridy = pixely // self.block_size 
        return gridx, gridy
    
    def empty_grid(self, characters):
        """ update the grid with the pos of each character"""
        for character in characters:
            self.grid[character.y][character.x] = ' '

    def update_grid(self, characters):
        """ update the grid with the pos of each character"""
        for character in characters:
            self.grid[character.y][character.x] = 'C'


if __name__ == '__main__':
    grid = Grid(HEIGHT, WIDTH, BLOCK_SIZE)
    ## Should return the top left 
    print(grid.grid_to_pixel(0,0)) 
    ## Should return the bottom right
    print(grid.grid_to_pixel(grid.grid_width - 1 - 1, grid.grid_height - 1 - 1)) 


