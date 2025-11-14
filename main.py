"""
Простая игра на Pygame: Движение и прыжок персонажа
"""

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра: Перемещение и прыжок")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Настройки игрока
PLAYER_SIZE = 50
PLAYER_COLOR = BLUE
PLAYER_SPEED = 15
JUMP_HEIGHT = 20  # "сила" прыжка
GRAVITY = 1

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0        # вертикальная скорость
        self.is_jumping = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= PLAYER_SPEED
        elif direction == "right":
            self.x += PLAYER_SPEED

        # Ограничиваем движение по краям экрана
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def jump(self):
        if not self.is_jumping:  # Прыгаем только если не в прыжке
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Проверка на землю (нижняя линия)
        if self.y >= SCREEN_HEIGHT - self.height - 100:  # Горизонтальная линия "земли"
            self.y = SCREEN_HEIGHT - self.height - 100
            self.vel_y = 0
            self.is_jumping = False

        # Обновляем положение прямоугольника
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)


# Создаём игрока на "земле"
ground_y = SCREEN_HEIGHT - 100
player = Player(x=100, y=SCREEN_HEIGHT - PLAYER_SIZE - 100)

# Основной игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)  # 60 FPS
    screen.fill(WHITE)

    # Рисуем землю (горизонтальную линию)
    pygame.draw.line(screen, RED, (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 3)

    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #if event.type == pygame.KEYDOWN:
        if pygame.key.get_pressed()[pygame.K_a]:
            player.move("left")
        if pygame.key.get_pressed()[pygame.K_d]:
            player.move("right")
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            player.jump()

    # Гравитация и прыжок
    player.apply_gravity()

    # Отрисовка
    player.draw(screen)

    # Обновление экрана
    pygame.display.flip()

# Выход из игры
pygame.quit()
sys.exit()
