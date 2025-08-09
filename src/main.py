import random
import pygame

# --- Configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# World is much larger than the visible screen
MAP_WIDTH, MAP_HEIGHT = 2400, 1800
PLAYER_RADIUS = 30
ENEMY_RADIUS = 20
ENEMY_COUNT = 10
PLAYER_SPEED = 5
ENEMY_SPEED = 2
PLAYER_MAX_HEALTH = 100
ENEMY_MAX_HEALTH = 30
COLLISION_DAMAGE = 1
PLAYER_REGEN_DELAY = 20  # frames required to regain 1 health when stationary
WALL_COLOR = (139, 69, 19)
ATTACK_RANGE = 20  # additional distance from the player to hit enemies
ATTACK_DAMAGE = 15
PLAYER_COLOR = (0, 0, 255)
PLAYER_ATTACK_COLOR = (0, 155, 155)
PLAYER_ATTACK_RADIUS_BOOST = 5

# simple static walls represented as pygame.Rect objects
WALLS = [
    pygame.Rect(150, 100, 50, 400),
    pygame.Rect(400, 200, 250, 50),
]

# --- Setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple 2D Agar.io-like Game")
clock = pygame.time.Clock()

# --- Player
player_pos = pygame.Vector2(MAP_WIDTH // 2, MAP_HEIGHT // 2)
player_health = PLAYER_MAX_HEALTH
player_regen_counter = 0

# --- Enemies
enemies = []
for _ in range(ENEMY_COUNT):
    pos = pygame.Vector2(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT))
    enemies.append({"pos": pos, "health": ENEMY_MAX_HEALTH})


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


def resolve_circle_rect_collision(circle_pos, radius, rect):
    """Push a circle out of a rectangle if they overlap."""
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    distance_vec = pygame.Vector2(circle_pos.x - closest_x, circle_pos.y - closest_y)
    distance = distance_vec.length()
    if distance < radius:
        if distance == 0:
            left = circle_pos.x - rect.left
            right = rect.right - circle_pos.x
            top = circle_pos.y - rect.top
            bottom = rect.bottom - circle_pos.y
            min_dist = min(left, right, top, bottom)
            if min_dist == left:
                circle_pos.x = rect.left - radius
            elif min_dist == right:
                circle_pos.x = rect.right + radius
            elif min_dist == top:
                circle_pos.y = rect.top - radius
            else:
                circle_pos.y = rect.bottom + radius
        else:
            circle_pos += distance_vec.normalize() * (radius - distance)

def move_player(keys, pos):
    moved = False
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        pos.y -= PLAYER_SPEED
        moved = True
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        pos.y += PLAYER_SPEED
        moved = True
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        pos.x -= PLAYER_SPEED
        moved = True
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        pos.x += PLAYER_SPEED
        moved = True
    # Keep player within map bounds
    pos.x = max(PLAYER_RADIUS, min(MAP_WIDTH - PLAYER_RADIUS, pos.x))
    pos.y = max(PLAYER_RADIUS, min(MAP_HEIGHT - PLAYER_RADIUS, pos.y))
    for wall in WALLS:
        resolve_circle_rect_collision(pos, PLAYER_RADIUS, wall)
    # Resolve collisions with enemies
    for enemy in enemies:
        resolve_circle_collision(pos, PLAYER_RADIUS, enemy["pos"], ENEMY_RADIUS)
        # Ensure the player stays within bounds after resolution
        pos.x = max(PLAYER_RADIUS, min(MAP_WIDTH - PLAYER_RADIUS, pos.x))
        pos.y = max(PLAYER_RADIUS, min(MAP_HEIGHT - PLAYER_RADIUS, pos.y))
        for wall in WALLS:
            resolve_circle_rect_collision(pos, PLAYER_RADIUS, wall)
    return moved

def move_enemies(enemy_list, player_pos):
    for i, enemy in enumerate(enemy_list):
        # Move towards the player
        direction = player_pos - enemy["pos"]
        if direction.length() != 0:
            direction = direction.normalize()
            enemy["pos"] += direction * ENEMY_SPEED
        # Keep enemy within map bounds
        enemy["pos"].x = max(ENEMY_RADIUS, min(MAP_WIDTH - ENEMY_RADIUS, enemy["pos"].x))
        enemy["pos"].y = max(ENEMY_RADIUS, min(MAP_HEIGHT - ENEMY_RADIUS, enemy["pos"].y))
        for wall in WALLS:
            resolve_circle_rect_collision(enemy["pos"], ENEMY_RADIUS, wall)

        # Resolve collisions with the player
        resolve_circle_collision(enemy["pos"], ENEMY_RADIUS, player_pos, PLAYER_RADIUS)
        for wall in WALLS:
            resolve_circle_rect_collision(enemy["pos"], ENEMY_RADIUS, wall)

        # Resolve collisions with other enemies processed so far
        for j in range(i):
            other = enemy_list[j]
            resolve_circle_collision(enemy["pos"], ENEMY_RADIUS, other["pos"], ENEMY_RADIUS)
            for wall in WALLS:
                resolve_circle_rect_collision(enemy["pos"], ENEMY_RADIUS, wall)

        # Keep enemy within bounds after resolution
        enemy["pos"].x = max(ENEMY_RADIUS, min(MAP_WIDTH - ENEMY_RADIUS, enemy["pos"].x))
        enemy["pos"].y = max(ENEMY_RADIUS, min(MAP_HEIGHT - ENEMY_RADIUS, enemy["pos"].y))
        for wall in WALLS:
            resolve_circle_rect_collision(enemy["pos"], ENEMY_RADIUS, wall)

def check_collisions(attacking: bool):
    """Handle damage when the player collides with enemies or attacks them."""
    global enemies, player_health
    remaining_enemies = []
    for enemy in enemies:
        dist = player_pos.distance_to(enemy["pos"])
        if dist <= PLAYER_RADIUS + ENEMY_RADIUS:
            player_health -= COLLISION_DAMAGE
            enemy["health"] -= COLLISION_DAMAGE
        if attacking and dist <= PLAYER_RADIUS + ENEMY_RADIUS + ATTACK_RANGE:
            enemy["health"] -= ATTACK_DAMAGE
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
    attacking = keys[pygame.K_SPACE]
    moved = move_player(keys, player_pos)
    move_enemies(enemies, player_pos)
    check_collisions(attacking)
    if moved:
        player_regen_counter = 0
    elif player_health < PLAYER_MAX_HEALTH:
        player_regen_counter += 1
        if player_regen_counter >= PLAYER_REGEN_DELAY:
            player_health = min(player_health + 1, PLAYER_MAX_HEALTH)
            player_regen_counter = 0
    if player_health <= 0:
        running = False

    # Determine camera offset to keep player centered
    camera_offset = pygame.Vector2(
        max(0, min(player_pos.x - SCREEN_WIDTH / 2, MAP_WIDTH - SCREEN_WIDTH)),
        max(0, min(player_pos.y - SCREEN_HEIGHT / 2, MAP_HEIGHT - SCREEN_HEIGHT)),
    )

    # Draw green background
    screen.fill((34, 139, 34))
    # Draw walls adjusted for camera
    for wall in WALLS:
        pygame.draw.rect(screen, WALL_COLOR, wall.move(-camera_offset))
    # Draw player
    player_draw_radius = PLAYER_RADIUS + (PLAYER_ATTACK_RADIUS_BOOST if attacking else 0)
    player_color = PLAYER_ATTACK_COLOR if attacking else PLAYER_COLOR
    pygame.draw.circle(screen, player_color, player_pos - camera_offset, player_draw_radius)
    # Draw enemies (red)
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), enemy["pos"] - camera_offset, ENEMY_RADIUS)

    # Draw player health
    font = pygame.font.SysFont(None, 24)
    hp_text = font.render(f"HP: {player_health}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 10))

    pygame.display.flip()

pygame.quit()
