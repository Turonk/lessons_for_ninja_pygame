import pygame

SCREEN_WIDTH = 800

ENEMY_HEIGHT = 50
ENEMY_WIDTH = 50
ENEMY_SPEED = 1
SPAWN_DELAY = 180  # 180 тиков / 60 fps = 3 секунды


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if x >= SCREEN_WIDTH // 2:
            self.direction = -1
        else:
            self.direction = 1

    def position_update(self, player_x):
        if self.rect.x < player_x:
            self.direction = 1
        else:
            self.direction = -1

        self.x += self.direction * ENEMY_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 255), self.rect)

    def is_off_screen(self):
        return self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50
