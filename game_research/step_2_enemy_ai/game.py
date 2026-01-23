import pygame
import random
from enemy import Enemy, ENEMY_HEIGHT, ENEMY_WIDTH

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Основная игра")

PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

class AssetLoader:
    def __init__(self):
        self.sprites = {}
        self.load_all()

    def load_image(self, path, width, height):
        """Загружает изображение или возвращает заглушку"""
        try:
            image = pygame.image.load(path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            print(f"Файл не найден: {path}. Создаём заглушку.")
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(image, (100, 100, 100), (5, 5, width - 10, height - 10), border_radius=8)
            pygame.draw.circle(image, (255, 255, 255), (15, 15), 5)  # Глазик
        return pygame.transform.scale(image, (width, height))

    def load_all(self):
        """Загружаем все спрайты для игры"""
        self.sprites["player_idle"] = self.load_image("assets/idle.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_walk"] = self.load_image("assets/walk.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_jump"] = self.load_image("assets/jump.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["projectile"] = self.load_image("assets/projectile.png", 24, 24)

    def get(self, name):
        """Возвращает спрайт по имени"""
        return self.sprites.get(name, None)
    

class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False
        self.direction = "right"
        self.assets = assets
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= PLAYER_SPEED
            self.direction = "left"
        elif direction == "right":
            self.x += PLAYER_SPEED
            self.direction = "right"

        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        self.rect.x = self.x

    def jump(self):
        if not self.is_jumping:
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.is_jumping = False

        self.rect.y = self.y

    def update_animation(self):
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]

        if self.is_jumping:
            self.current_sprite = self.assets.get("player_jump")
        elif moving:
            self.current_sprite = self.assets.get("player_walk")
        else:
            self.current_sprite = self.assets.get("player_idle")

        if self.direction == "left":
            self.flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
        else:
            self.flipped_sprite = self.current_sprite

    def draw(self, surface):
        surface.blit(self.flipped_sprite, (self.x, self.y))


asset_loader = AssetLoader()
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE, assets=asset_loader)

# Функция для создания нового врага за пределами экрана
def spawn_enemy():
    # Случайно выбираем сторону спавна (слева или справа)
    side = random.choice(["left", "right"])
    if side == "left":
        x = -ENEMY_WIDTH  # За левым краем экрана
    else:
        x = SCREEN_WIDTH  # За правым краем экрана

    y = GROUND_Y - ENEMY_HEIGHT  # На уровне земли
    return Enemy(x, y)

enemy = spawn_enemy()

clock = pygame.time.Clock()
running = True
game_over = False

def check_collision(rect1, rect2):
    """Проверяет столкновение между двумя прямоугольниками"""
    return rect1.colliderect(rect2)

while running:
    clock.tick(60)
    screen.fill(WHITE)
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

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
                enemy = spawn_enemy()
            elif event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move("left")
    if keys[pygame.K_RIGHT]:
        player.move("right")

    # Обновляем игрока только если игра не окончена
    if not game_over:
        player.apply_gravity()
        player.update_animation()

        # Враг двигается к игроку по оси X
        enemy.move_towards_player(player.x)
        enemy.position_update()

        # Если враг ушел за пределы экрана, создаем нового
        if enemy.is_off_screen():
            enemy = spawn_enemy()

        # Проверяем столкновение между игроком и врагом
        if check_collision(player.rect, enemy.rect):
            game_over = True

    # Рисуем спрайты
    player.draw(screen)
    enemy.draw(screen)

    # Если игра окончена, показываем сообщение
    if game_over:
        # Создаем полупрозрачный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Черный с прозрачностью 180
        screen.blit(overlay, (0, 0))

        # Настраиваем шрифт для сообщения
        font = pygame.font.Font(None, 74)  # Размер шрифта 74
        game_over_text = font.render("ИГРА ОКОНЧЕНА!", True, WHITE)

        # Центрируем текст
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

        # Добавляем подсказку для перезапуска
        small_font = pygame.font.Font(None, 36)
        restart_text = small_font.render("Нажмите R для перезапуска или ESC для выхода", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()