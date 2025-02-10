import pygame
from pygame.locals import *
from settings import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(WHITE)
    clock = pygame.time.Clock()
    pygame.display.set_caption(TITLE)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

main()