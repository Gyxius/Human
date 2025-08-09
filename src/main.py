import random
import pygame

# --- Configuration
WIDTH, HEIGHT = 800, 600
PLAYER_RADIUS = 30
ENEMY_RADIUS = 20
ENEMY_COUNT = 10
PLAYER_SPEED = 5
ENEMY_SPEED = 2
PLAYER_MAX_HEALTH = 100
ENEMY_MAX_HEALTH = 30
COLLISION_DAMAGE = 1
WALL_COLOR = (139, 69, 19)

# simple static walls represented as pygame.Rect objects
WALLS = [
    pygame.Rect(150, 100, 50, 400),
    pygame.Rect(400, 200, 250, 50),
]

# --- Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple 2D Agar.io-like Game")
clock = pygame.time.Clock()

# --- Player
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_health = PLAYER_MAX_HEALTH

# --- Enemies
enemies = []
for _ in range(ENEMY_COUNT):
    pos = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    enemies.append({"pos": pos, "health": ENEMY_MAX_HEALTH})


def circle_rect_collision(circle_pos, radius, rect):
    """Return True if a circle collides with a rectangle."""
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    distance = pygame.Vector2(closest_x - circle_pos.x, closest_y - circle_pos.y)
    return distance.length() < radius


def resolve_circle_collision(pos1, radius1, pos2, radius2):
    """Push two circles apart if they overlap."""
    delta = pos2 - pos1
    distance = delta.length()
    if distance == 0:
        # Avoid division by zero by giving a tiny random direction
        delta = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        distance = delta.length()
    if distance < radius1 + radius2:
        overlap = radius1 + radius2 - distance
        direction = delta.normalize()
        pos1 -= direction * overlap / 2
        pos2 += direction * overlap / 2

def move_player(keys, pos):
    prev_pos = pos.copy()
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
    for wall in WALLS:
        if circle_rect_collision(pos, PLAYER_RADIUS, wall):
            pos.update(prev_pos)
            break
    # Resolve collisions with enemies
    for enemy in enemies:
        resolve_circle_collision(pos, PLAYER_RADIUS, enemy["pos"], ENEMY_RADIUS)
        # Ensure the player stays within bounds after resolution
        pos.x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, pos.x))
        pos.y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, pos.y))
        # Avoid pushing into walls
        for wall in WALLS:
            if circle_rect_collision(pos, PLAYER_RADIUS, wall):
                pos.update(prev_pos)
                resolve_circle_collision(pos, PLAYER_RADIUS, enemy["pos"], ENEMY_RADIUS)
                break

def move_enemies(enemy_list, player_pos):
    for i, enemy in enumerate(enemy_list):
        prev_pos = enemy["pos"].copy()
        # Move towards the player
        direction = player_pos - enemy["pos"]
        if direction.length() != 0:
            direction = direction.normalize()
            enemy["pos"] += direction * ENEMY_SPEED
        # Keep enemy within screen bounds
        enemy["pos"].x = max(ENEMY_RADIUS, min(WIDTH - ENEMY_RADIUS, enemy["pos"].x))
        enemy["pos"].y = max(ENEMY_RADIUS, min(HEIGHT - ENEMY_RADIUS, enemy["pos"].y))
        for wall in WALLS:
            if circle_rect_collision(enemy["pos"], ENEMY_RADIUS, wall):
                enemy["pos"].update(prev_pos)
                break

        # Resolve collisions with the player
        resolve_circle_collision(enemy["pos"], ENEMY_RADIUS, player_pos, PLAYER_RADIUS)

        # Resolve collisions with other enemies processed so far
        for j in range(i):
            other = enemy_list[j]
            resolve_circle_collision(enemy["pos"], ENEMY_RADIUS, other["pos"], ENEMY_RADIUS)

        # Keep enemy within bounds after resolution
        enemy["pos"].x = max(ENEMY_RADIUS, min(WIDTH - ENEMY_RADIUS, enemy["pos"].x))
        enemy["pos"].y = max(ENEMY_RADIUS, min(HEIGHT - ENEMY_RADIUS, enemy["pos"].y))

def check_collisions():
    """Handle damage when the player collides with enemies."""
    global enemies, player_health
    remaining_enemies = []
    for enemy in enemies:
        dist = player_pos.distance_to(enemy["pos"])
        if dist <= PLAYER_RADIUS + ENEMY_RADIUS:
            player_health -= COLLISION_DAMAGE
            enemy["health"] -= COLLISION_DAMAGE
        if enemy["health"] > 0:
            remaining_enemies.append(enemy)
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
    move_enemies(enemies, player_pos)
    check_collisions()
    if player_health <= 0:
        running = False

    # Draw green background
    screen.fill((34, 139, 34))
    # Draw walls
    for wall in WALLS:
        pygame.draw.rect(screen, WALL_COLOR, wall)
    # Draw player (blue)
    pygame.draw.circle(screen, (0, 0, 255), player_pos, PLAYER_RADIUS)
    # Draw enemies (red)
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy["pos"], ENEMY_RADIUS)

    # Draw player health
    font = pygame.font.SysFont(None, 24)
    hp_text = font.render(f"HP: {player_health}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 10))

    pygame.display.flip()

pygame.quit()
