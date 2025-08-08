import random
import pygame

# --- Configuration
WIDTH, HEIGHT = 800, 600
PLAYER_RADIUS = 30
ENEMY_RADIUS = 20
ENEMY_COUNT = 10
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# --- Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple 2D Agar.io-like Game")
clock = pygame.time.Clock()

# --- Player
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

# --- Enemies
enemies = []
for _ in range(ENEMY_COUNT):
    pos = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    # Assign each enemy a random direction
    direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
    enemies.append({"pos": pos, "dir": direction})

def move_player(keys, pos):
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        pos.y -= PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        pos.y += PLAYER_SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        pos.x -= PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        pos.x += PLAYER_SPEED
    # Keep player within screen bounds
    pos.x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, pos.x))
    pos.y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, pos.y))

def move_enemies(enemy_list):
    for enemy in enemy_list:
        enemy["pos"] += enemy["dir"] * ENEMY_SPEED
        # Bounce off edges of screen
        if enemy["pos"].x < ENEMY_RADIUS or enemy["pos"].x > WIDTH - ENEMY_RADIUS:
            enemy["dir"].x *= -1
        if enemy["pos"].y < ENEMY_RADIUS or enemy["pos"].y > HEIGHT - ENEMY_RADIUS:
            enemy["dir"].y *= -1

def check_collisions():
    """Remove enemies if the player collides with them."""
    global enemies
    remaining_enemies = []
    for enemy in enemies:
        dist = player_pos.distance_to(enemy["pos"])
        if dist > PLAYER_RADIUS + ENEMY_RADIUS:
            remaining_enemies.append(enemy)
        # If collided, enemy is removed
    enemies = remaining_enemies

# --- Game Loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    move_player(keys, player_pos)
    move_enemies(enemies)
    check_collisions()

    # Draw green background
    screen.fill((34, 139, 34))
    # Draw player (blue)
    pygame.draw.circle(screen, (0, 0, 255), player_pos, PLAYER_RADIUS)
    # Draw enemies (red)
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy["pos"], ENEMY_RADIUS)

    pygame.display.flip()

pygame.quit()
