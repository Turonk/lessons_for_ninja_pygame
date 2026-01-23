import pygame

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

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = 5
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

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.speed = 2
        self.direction = "right"
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        if self.direction == "right":
            self.x += self.speed
            if self.x >= SCREEN_WIDTH - self.width:
                self.direction = "left"
        else:
            self.x -= self.speed
            if self.x <= 0:
                self.direction = "right"

        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

def check_collision(rect1, rect2):
    """Проверяет столкновение между двумя прямоугольниками"""
    return rect1.colliderect(rect2)

def main():
    player = Player(100, SCREEN_HEIGHT - PLAYER_SIZE - 50)
    enemy = Enemy(0, SCREEN_HEIGHT - ENEMY_SIZE - 50)

    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        clock.tick(60)
        screen.fill(WHITE)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Перезапуск игры
                    game_over = False
                    player.x = 100
                    player.y = SCREEN_HEIGHT - PLAYER_SIZE - 50
                    enemy.x = 0
                    enemy.y = SCREEN_HEIGHT - ENEMY_SIZE - 50
                    enemy.direction = "right"
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Управление игроком (только если игра не окончена)
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")

            # Движение врага
            enemy.move()

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
