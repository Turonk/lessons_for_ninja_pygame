"""
Простая игра на Pygame: Анимации + отдельный класс для загрузки ресурсов
+ метательное оружие, отскок от стен, подбор, спрайты
"""

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра: Загрузчик ресурсов")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Настройки
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1
GROUND_Y = SCREEN_HEIGHT - 100


# ===== Класс: Загрузчик ресурсов =====
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
        self.sprites["player_idle"] = self.load_image("assets/idle.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_walk"] = self.load_image("assets/walk.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_jump"] = self.load_image("assets/jump.png", PLAYER_SIZE, PLAYER_SIZE)
        # Обнови размер под 24x24
        self.sprites["projectile"] = self.load_image("assets/projectile.png", 24, 24)

    def get(self, name):
        """Возвращает спрайт по имени"""
        return self.sprites.get(name, None)


# ===== Класс: Игрок =====
class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False
        self.direction = "right"
        self.assets = assets  # Получаем загрузчик
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

        # Поворот спрайта
        if self.direction == "left":
            self.flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
        else:
            self.flipped_sprite = self.current_sprite

    def draw(self, surface):
        surface.blit(self.flipped_sprite, (self.x, self.y))


# ===== Класс: Снаряд =====
# ===== Класс: Снаряд — корректные отскоки от всех стен =====
class Projectile:
    def __init__(self, x, y, target_pos, assets, speed=10):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.assets = assets
        self.active = True
        self.stuck = False

        # Направление полёта
        direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        self.hit_surface = False  # Ударился о стену/потолок
        self.gravity = 0.6        # Включится после удара

    def update(self, ground_y):
        if self.stuck or not self.active:
            return

        # === Полёт до удара: без гравитации ===
        if not self.hit_surface:
            # Предикат движения — где будет снаряд на следующем кадре
            next_x = self.rect.x + self.velocity.x
            next_y = self.rect.y + self.velocity.y

            # Проверяем коллизии ДО перемещения
            if next_x <= 0 or next_x + self.rect.width >= SCREEN_WIDTH:
                # Удар о левую или правую стену
                self.velocity.x = -self.velocity.x * 0.3  # Слабый отскок
                self.hit_surface = True

            if next_y <= 0:
                # Удар о потолок
                self.velocity.y = abs(self.velocity.y) * 0.3  # Небольшой импульс вниз
                self.hit_surface = True

            # Обновляем позицию
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # Дополнительная фиксация — не дать уйти за границы
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            # Попадание в землю — сразу застреваем
            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.stuck = True

        # === После удара: падение ===
        if self.hit_surface and not self.stuck:
            self.velocity.y += self.gravity
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # Затухание горизонтальной скорости
            if abs(self.velocity.x) > 0.1:
                self.velocity.x *= 0.92
            else:
                self.velocity.x = 0

            # Падение на землю
            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.stuck = True
                self.velocity = pygame.math.Vector2(0, 0)

    def draw(self, surface):
        if not self.active:
            return
        sprite = self.assets.get("projectile")
        if sprite:
            draw_x = self.rect.x - (sprite.get_width() // 2 - self.rect.width // 2)
            draw_y = self.rect.y - (sprite.get_height() // 2 - self.rect.height // 2)
            surface.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.circle(surface, (50, 50, 50), self.rect.center, 12)

    def is_close_to_player(self, player_rect, threshold=40):
        return self.stuck and self.rect.colliderect(player_rect.inflate(threshold, threshold))

    def reset(self):
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = pygame.math.Vector2(0, 0)


# ===== Инициализация =====
asset_loader = AssetLoader()
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE, assets=asset_loader)

# Снаряды
projectiles = []
max_projectiles = 3

# ===== Основной цикл =====
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)
    screen.fill(WHITE)

    # Рисуем землю
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # ЛКМ
                active_count = len([p for p in projectiles if p.active])
                if active_count < max_projectiles:
                    pos = player.x + PLAYER_SIZE // 2, player.y + PLAYER_SIZE // 2
                    projectile = Projectile(pos[0], pos[1], pygame.mouse.get_pos(), asset_loader)
                    projectiles.append(projectile)

    # Управление
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move("left")
    if keys[pygame.K_RIGHT]:
        player.move("right")

    # Логика
    player.apply_gravity()
    player.update_animation()

    # Обновление снарядов
    mouse_buttons = pygame.mouse.get_pressed()
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

    for projectile in projectiles:
        projectile.update(GROUND_Y)
        projectile.draw(screen)

        # Автоподбор при касании (без клика!)
        if projectile.stuck and projectile.is_close_to_player(player_rect):
            projectile.reset()  # Подобрали!

    # Отрисовка игрока
    player.draw(screen)

    pygame.display.flip()

# Выход
pygame.quit()
sys.exit()
