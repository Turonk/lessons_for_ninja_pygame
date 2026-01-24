"""
Простая игра на Pygame: Движение при удержании клавиши + прыжок
"""

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра: Спрайт игрока — движение при удержании")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Настройки игрока
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1
GROUND_Y = SCREEN_HEIGHT - 100  # Уровень земли

# --- Загрузка или создание спрайта ---
def load_player_sprite():
    try:
        sprite = pygame.image.load("assets/player.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (PLAYER_SIZE, PLAYER_SIZE))
    except (FileNotFoundError, pygame.error):
        print("Файл 'assets/player.png' не найден. Используется заглушка.")
        sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(sprite, (0, 100, 255), (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=10)
        pygame.draw.rect(sprite, (255, 255, 255), (10, 10, 30, 30), border_radius=5)  # Глазик
    return sprite

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False
        self.sprite = load_player_sprite()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= PLAYER_SPEED
        elif direction == "right":
            self.x += PLAYER_SPEED

        # Ограничение по краям экрана
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def jump(self):
        if not self.is_jumping:  # Прыгаем только если на земле
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Проверка на землю
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.is_jumping = False

        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.sprite, (self.x, self.y))


# Создаём игрока
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)

# Основной цикл игры
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Рисуем землю
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Прыжок — срабатывает при нажатии (один раз)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # --- Движение при удержании клавиш ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move("left")
    if keys[pygame.K_RIGHT]:
        player.move("right")

    # --- Физика и отрисовка ---
    player.apply_gravity()
    player.draw(screen)

    # Обновление экрана
    pygame.display.flip()

# Выход
pygame.quit()
sys.exit()
