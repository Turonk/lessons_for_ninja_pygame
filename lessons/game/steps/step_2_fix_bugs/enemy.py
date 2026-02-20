import pygame

# Ширина экрана — нужна для определения направления врага при спавне
# и для проверки, ушёл ли враг за пределы экрана
SCREEN_WIDTH = 800

# Константы врага
ENEMY_HEIGHT = 50
ENEMY_WIDTH = 50
ENEMY_SPEED = 1
SPAWN_DELAY = 180  # 180 тиков / 60 fps = 3 секунды


class Enemy:
    """Враг, который появляется с краёв экрана и идёт к игроку."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Определяем начальное направление по стороне спавна:
        # если появился справа — идём влево (-1), иначе вправо (1)
        if x >= SCREEN_WIDTH // 2:
            self.direction = -1
        else:
            self.direction = 1

    def position_update(self, player_x):
        """Двигает врага в сторону игрока каждый кадр."""
        if self.rect.x < player_x:
            self.direction = 1   # игрок правее — идём вправо
        else:
            self.direction = -1  # игрок левее — идём влево

        self.x += self.direction * ENEMY_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        """Рисует врага как синий прямоугольник."""
        pygame.draw.rect(surface, (0, 0, 255), self.rect)

    def is_off_screen(self):
        """Проверяет, ушёл ли враг далеко за пределы экрана (можно удалить)."""
        return self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50
