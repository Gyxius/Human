import random
import pygame

def resolve_circle_collision(pos1, radius1, pos2, radius2):
    """Push two circles apart if they overlap."""
    delta = pos2 - pos1
    distance = delta.length()
    if distance == 0:
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
