import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Демонстрация столкновения")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Размеры объектов
PLAYER_SIZE = 50
ENEMY_SIZE = 50

# Константы для прыжков
JUMP_HEIGHT = 15
GRAVITY = 1
GROUND_Y = SCREEN_HEIGHT - 50

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = 5
        self.vel_y = 0
        self.is_jumping = False
        self.jump_count = 0  # Счетчик прыжков
        self.max_jumps = 2   # Максимальное количество прыжков
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed

        # Ограничение движения в пределах экрана
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        self.rect.x = self.x

    def jump(self):
        if self.jump_count < self.max_jumps:
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True
            self.jump_count += 1

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.is_jumping = False
            self.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении

        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.speed = 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move_towards_player(self, player_x):
        """Двигает врага в направлении игрока по оси X"""
        if self.x < player_x:
            # Игрок справа, двигаемся вправо
            self.x += self.speed
        elif self.x > player_x:
            # Игрок слева, двигаемся влево
            self.x -= self.speed

        # Ограничение движения в пределах экрана
        if self.x < -self.width:
            self.x = -self.width
        if self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH

        self.rect.x = self.x

    def is_off_screen(self):
        """Проверяет, ушел ли враг за пределы экрана"""
        return self.x < -self.width or self.x > SCREEN_WIDTH

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

def check_collision(rect1, rect2):
    """Проверяет столкновение между двумя прямоугольниками"""
    return rect1.colliderect(rect2)

def spawn_enemy():
    """Создает нового врага за пределами экрана"""
    side = random.choice(["left", "right"])
    if side == "left":
        x = -ENEMY_SIZE
    else:
        x = SCREEN_WIDTH
    y = SCREEN_HEIGHT - ENEMY_SIZE - 50
    return Enemy(x, y)

def main():
    player = Player(100, GROUND_Y - PLAYER_SIZE)
    enemy = spawn_enemy()

    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        clock.tick(60)
        screen.fill(WHITE)

        # Рисуем землю
        pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.jump()
                elif event.key == pygame.K_r and game_over:
                    # Перезапуск игры
                    game_over = False
                    player.x = 100
                    player.y = GROUND_Y - PLAYER_SIZE
                    player.vel_y = 0
                    player.is_jumping = False
                    player.jump_count = 0
                    enemy = spawn_enemy()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Управление игроком (только если игра не окончена)
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")

            # Применяем гравитацию и прыжки
            player.apply_gravity()

            # Враг двигается к игроку
            enemy.move_towards_player(player.x)

            # Если враг ушел за пределы экрана, создаем нового
            if enemy.is_off_screen():
                enemy = spawn_enemy()

            # Проверка столкновения
            if check_collision(player.rect, enemy.rect):
                game_over = True

        # Рисование объектов
        player.draw(screen)
        enemy.draw(screen)

        # Экран окончания игры
        if game_over:
            # Полупрозрачный фон
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # Сообщение об окончании
            font = pygame.font.Font(None, 48)
            text = font.render("СТОЛКНОВЕНИЕ! Игра окончена!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

            # Подсказка
            small_font = pygame.font.Font(None, 24)
            hint = small_font.render("Нажмите R для перезапуска", True, WHITE)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(hint, hint_rect)

        pygame.display.flip()

if __name__ == "__main__":
    main()
