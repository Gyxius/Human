from characters import *

class Player(Characters):
    def __init__(self, surface, name):
        
        self.xPosition = WIDTH//2
        self.yPosition = HEIGHT//2
        self.speed = 2
        self.moving = {"up": False, "down": False, "left": False, "right": False, "space": False}
        sprite = Sprites.Circle(surface, BLUE, self.xPosition, self.yPosition)
        super().__init__(sprite, name, "blue")
        self.dx = 0
        self.dy = 0

    def move(self, collision_manager):
        self.dx = self.dy = 0  # reset every frame

        if self.moving["up"]:
            self.dy = -self.speed
        if self.moving["down"]:
            self.dy = self.speed
        if self.moving["left"]:
            self.dx = -self.speed
        if self.moving["right"]:
            self.dx = self.speed

        # Use the delta values directly for collision check
        if not collision_manager.is_colliding_circle(self, self.dx, self.dy):
            self.xPosition += self.dx
            self.yPosition += self.dy


    def draw(self, surface):
        self.sprite = Sprites.Circle(surface, BLUE, self.xPosition, self.yPosition)
        self.draw_rectangle(surface)


    def update(self, collision_manager):
        # Move player based on held keys
        self.move(collision_manager)

    @property
    def collision_block(self):
        return pygame.Rect(self.xPosition - RADIUS_SIZE, self.yPosition - RADIUS_SIZE, self.width, self.height)

    def draw_rectangle(self, surface):
        if self.moving["space"] and self.moving["right"] and self.moving["up"]:
            # Top-right
            Sprites.Rectangle(surface, WHITE, self.xPosition + RADIUS_SIZE, self.yPosition - 3 * RADIUS_SIZE)

        elif self.moving["space"] and self.moving["right"] and self.moving["down"]:
            # Bottom-right
            Sprites.Rectangle(surface, WHITE, self.xPosition + RADIUS_SIZE, self.yPosition + RADIUS_SIZE)

        elif self.moving["space"] and self.moving["left"] and self.moving["up"]:
            # Top-left
            Sprites.Rectangle(surface, WHITE, self.xPosition - 3 * RADIUS_SIZE, self.yPosition - 3 * RADIUS_SIZE)

        elif self.moving["space"] and self.moving["left"] and self.moving["down"]:
            # Bottom-left
            Sprites.Rectangle(surface, WHITE, self.xPosition - 3 * RADIUS_SIZE, self.yPosition + RADIUS_SIZE)

        elif self.moving["space"] and self.moving["right"]:
            Sprites.Rectangle(surface, WHITE, self.xPosition + RADIUS_SIZE, self.yPosition - RADIUS_SIZE)

        elif self.moving["space"] and self.moving["left"]:
            Sprites.Rectangle(surface, WHITE, self.xPosition - 3 * RADIUS_SIZE, self.yPosition - RADIUS_SIZE)

        elif self.moving["space"] and self.moving["up"]:
            Sprites.Rectangle(surface, WHITE, self.xPosition - RADIUS_SIZE, self.yPosition - 3 * RADIUS_SIZE)

        elif self.moving["space"] and self.moving["down"]:
            Sprites.Rectangle(surface, WHITE, self.xPosition - RADIUS_SIZE, self.yPosition + RADIUS_SIZE)


