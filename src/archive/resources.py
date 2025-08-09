import random
from sprites import *

class Resources:
    next_id = 0
    def __init__(self, resource_type, quantity, color):
        self.resource_type = resource_type  # e.g., "wood", "stone"
        self.quantity = quantity  # total amount available to gather
        self.x = 0
        self.y = 0
        self.xPosition = 0
        self.yPosition = 0
        self.color = color
        self.id = resource_type + str(Resources.next_id)

    def mine(self, amount):
        if self.quantity <= 0:
            print(f"The {self.resource_type} resource is depleted.")
            return 0

        gathered = min(amount, self.quantity)
        self.quantity -= gathered
        print(f"You gathered {gathered} {self.resource_type}. Remaining: {self.quantity}")
        return gathered

    def is_depleted(self):
        return self.quantity <= 0 
    
    def spawn(self, collision_manager, grid):
        x = random.randint(0, grid.grid_width - 1)
        y = random.randint(0, grid.grid_height - 1 )
        while(collision_manager.grid_colliding_circle(self, x, y, grid)):
            x = random.randint(0, grid.grid_width - 1)
            y = random.randint(0, grid.grid_height - 1 )
        self.x, self.y = x, y
        self.xPosition, self.yPosition = grid.grid_to_pixel(x, y)
        collision_manager.grid.grid[self.y][self.x] = 'T'
        collision_manager.object_grid.grid[self.y][self.x] = self
    
    def draw(self, surface):
        self.sprite = Sprites.Circle(surface, self.color, self.xPosition, self.yPosition)

    def update(self, collision_manager):
        if self.is_depleted():
            collision_manager.grid.grid[self.y][self.x] = ' '
            collision_manager.object_grid.grid[self.y][self.x] = None


if __name__ == '__main__':
    # Example usage
    tree = Resources("wood", 10)
    rock = Resources("stone", 20)

    tree.mine(3)  # You gathered 3 wood.
    tree.mine(4)  # You gathered 4 wood.
    tree.mine(5)  # You gathered 3 wood. (only 3 left)
    print(tree.is_depleted())  # True or False