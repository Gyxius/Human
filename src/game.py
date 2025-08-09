import pygame
import config
from collisions import resolve_circle_collision, resolve_circle_rect_collision
from entities import Player, Enemy

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Simple 2D Agar.io-like Game")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.enemies = [Enemy() for _ in range(config.ENEMY_COUNT)]

    def move_enemies(self):
        for i, enemy in enumerate(self.enemies):
            enemy.move(self.player.pos)
            resolve_circle_collision(enemy.pos, config.ENEMY_RADIUS, self.player.pos, config.PLAYER_RADIUS)
            for j in range(i):
                other = self.enemies[j]
                resolve_circle_collision(enemy.pos, config.ENEMY_RADIUS, other.pos, config.ENEMY_RADIUS)
            enemy.pos.x = max(config.ENEMY_RADIUS, min(config.MAP_WIDTH - config.ENEMY_RADIUS, enemy.pos.x))
            enemy.pos.y = max(config.ENEMY_RADIUS, min(config.MAP_HEIGHT - config.ENEMY_RADIUS, enemy.pos.y))
            for wall in config.WALLS:
                resolve_circle_rect_collision(enemy.pos, config.ENEMY_RADIUS, wall)

    def check_collisions(self, attacking: bool):
        remaining = []
        for enemy in self.enemies:
            dist = self.player.pos.distance_to(enemy.pos)
            if dist <= config.PLAYER_RADIUS + config.ENEMY_RADIUS:
                self.player.health -= config.COLLISION_DAMAGE
                enemy.health -= config.COLLISION_DAMAGE
            if attacking and dist <= config.PLAYER_RADIUS + config.ENEMY_RADIUS + config.ATTACK_RANGE:
                enemy.health -= config.ATTACK_DAMAGE
            if enemy.health > 0:
                remaining.append(enemy)
        self.enemies = remaining

    def draw(self, attacking: bool):
        camera_offset = pygame.Vector2(
            max(0, min(self.player.pos.x - config.SCREEN_WIDTH / 2, config.MAP_WIDTH - config.SCREEN_WIDTH)),
            max(0, min(self.player.pos.y - config.SCREEN_HEIGHT / 2, config.MAP_HEIGHT - config.SCREEN_HEIGHT)),
        )
        self.screen.fill((34, 139, 34))
        for wall in config.WALLS:
            pygame.draw.rect(self.screen, config.WALL_COLOR, wall.move(-camera_offset))
        player_draw_radius = config.PLAYER_RADIUS + (
            config.PLAYER_ATTACK_RADIUS_BOOST if attacking else 0
        )
        player_color = config.PLAYER_ATTACK_COLOR if attacking else config.PLAYER_COLOR
        pygame.draw.circle(self.screen, player_color, self.player.pos - camera_offset, player_draw_radius)
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, (255, 0, 0), enemy.pos - camera_offset, config.ENEMY_RADIUS)
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f"HP: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(hp_text, (10, 10))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            attacking = keys[pygame.K_SPACE]
            moved = self.player.move(keys, self.enemies)
            self.move_enemies()
            self.check_collisions(attacking)
            if moved:
                self.player.reset_regen_counter()
            else:
                self.player.regenerate()
            if self.player.health <= 0:
                running = False
            self.draw(attacking)
        pygame.quit()
