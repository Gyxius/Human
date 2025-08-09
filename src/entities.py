import random
import pygame
import config
from collisions import resolve_circle_collision, resolve_circle_rect_collision

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(config.MAP_WIDTH // 2, config.MAP_HEIGHT // 2)
        self.health = config.PLAYER_MAX_HEALTH
        self.regen_counter = 0

    def move(self, keys, enemies):
        moved = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.pos.y -= config.PLAYER_SPEED
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.pos.y += config.PLAYER_SPEED
            moved = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.pos.x -= config.PLAYER_SPEED
            moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.pos.x += config.PLAYER_SPEED
            moved = True
        self.pos.x = max(config.PLAYER_RADIUS, min(config.MAP_WIDTH - config.PLAYER_RADIUS, self.pos.x))
        self.pos.y = max(config.PLAYER_RADIUS, min(config.MAP_HEIGHT - config.PLAYER_RADIUS, self.pos.y))
        for wall in config.WALLS:
            resolve_circle_rect_collision(self.pos, config.PLAYER_RADIUS, wall)
        for enemy in enemies:
            resolve_circle_collision(self.pos, config.PLAYER_RADIUS, enemy.pos, config.ENEMY_RADIUS)
            self.pos.x = max(config.PLAYER_RADIUS, min(config.MAP_WIDTH - config.PLAYER_RADIUS, self.pos.x))
            self.pos.y = max(config.PLAYER_RADIUS, min(config.MAP_HEIGHT - config.PLAYER_RADIUS, self.pos.y))
            for wall in config.WALLS:
                resolve_circle_rect_collision(self.pos, config.PLAYER_RADIUS, wall)
        return moved

    def reset_regen_counter(self):
        self.regen_counter = 0

    def regenerate(self):
        if self.health < config.PLAYER_MAX_HEALTH:
            self.regen_counter += 1
            if self.regen_counter >= config.PLAYER_REGEN_DELAY:
                self.health = min(self.health + 1, config.PLAYER_MAX_HEALTH)
                self.regen_counter = 0

class Enemy:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, config.MAP_WIDTH), random.randint(0, config.MAP_HEIGHT))
        self.health = config.ENEMY_MAX_HEALTH

    def move(self, player_pos):
        direction = player_pos - self.pos
        if direction.length() != 0:
            direction = direction.normalize()
            self.pos += direction * config.ENEMY_SPEED
        self.pos.x = max(config.ENEMY_RADIUS, min(config.MAP_WIDTH - config.ENEMY_RADIUS, self.pos.x))
        self.pos.y = max(config.ENEMY_RADIUS, min(config.MAP_HEIGHT - config.ENEMY_RADIUS, self.pos.y))
        for wall in config.WALLS:
            resolve_circle_rect_collision(self.pos, config.ENEMY_RADIUS, wall)
