import pygame 
from pygame.locals import *
from characters import *

def main():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    surface.fill(WHITE)
    clock = pygame.time.Clock()
    pygame.display.set_caption(TITLE)

    player = Player(surface, "Josh")
    enemy = Enemies(surface)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

main()