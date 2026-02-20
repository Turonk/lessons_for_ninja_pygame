import pygame
import random
from enemy import Enemy, ENEMY_HEIGHT, ENEMY_WIDTH, SPAWN_DELAY

DEBUG = False

# Константы экрана
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Основная игра")

# Константы игрока
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1

# Константы цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

# Константы снаряда
PROJECTILE_SPEED = 10
MAX_COUNT_PROJECTILES = 3
PICUP_DISTANCE = 40


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
            pygame.draw.circle(image, (255, 255, 255), (15, 15), 5)
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
        self.jump_count = 0
        self.max_jumps = 2
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
            self.jump_count = 0

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

    @property
    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2


class Projectile:
    def __init__(self, x, y, target_pos):
        self.rect = pygame.Rect(x, y, 12, 12)

        direction = pygame.math.Vector2(target_pos[0] - x,
                                        target_pos[1] - y)

        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * PROJECTILE_SPEED
        else:
            self.velocity = 0

        self.active = True
        self.stuck = False
        self.hit_surface = False

        self.gravity = 0.6

    def update(self):
        if self.stuck or not self.active:
            return

        # Обычный полёт
        if not self.hit_surface:
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # когда снаряд ударяется о стену
            # левая стена
            if self.rect.left <= 0:
                self.velocity.x = self.velocity.x * -0.4
                self.hit_surface = True
            # правая стена
            if self.rect.right >= SCREEN_WIDTH:
                self.velocity.x = self.velocity.x * -0.4
                self.hit_surface = True
            # потолок
            if self.rect.top <= 0:
                self.velocity.y = self.velocity.y * -0.4
                self.hit_surface = True
            # пол
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True
                self.velocity.y = 0

        # Падение после рикошета
        if self.hit_surface and not self.stuck:
            self.velocity.y += self.gravity
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            if abs(self.velocity.x) < 0.1:
                self.velocity.x = self.velocity.x * 0.92
            else:
                self.velocity.x = 0

            # проверка приземления
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True
                self.velocity.y = 0

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, RED, self.rect)

    def is_close_to_player(self, player_rect):
        if not self.stuck:
            return False

        picup_zone = player_rect.inflate(PICUP_DISTANCE, PICUP_DISTANCE)
        return self.rect.colliderect(picup_zone)

    def reset(self):
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = 0


asset_loader = AssetLoader()
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE, assets=asset_loader)

enemies = []
spawn_timer = 0
projectiles = []

clock = pygame.time.Clock()
running = True
game_over = False


def check_collisions(rect1, rect2):
    return rect1.colliderect(rect2)


while running:
    clock.tick(60)
    screen.fill(WHITE)
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

    # БЛОК ЭВЕНТОВ (СОБЫТИЙ)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.jump()
            elif event.key == pygame.K_r and game_over:
                game_over = False
                player.x = 100
                player.y = GROUND_Y - PLAYER_SIZE
                player.vel_y = 0
                player.is_jumping = False
                enemies.clear()
                projectiles.clear()
                spawn_timer = 0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            active_count = len([p for p in projectiles if p.active])

            if active_count < MAX_COUNT_PROJECTILES:
                px, py = player.center
                mouse_pos = pygame.mouse.get_pos()
                projectile = Projectile(px, py, mouse_pos)
                projectiles.append(projectile)

    # Проверка нажатия клавиш управления
    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")

    # Обновление игрока
    if not game_over:
        player.apply_gravity()
        player.update_animation()

    player_rect = player.rect

    # Управление снарядами
    for projectile in projectiles:
        projectile.update()
        projectile.draw(screen)
        if projectile.is_close_to_player(player_rect):
            projectile.reset()

    projectiles = [p for p in projectiles if p.active]

    # Спавн врагов
    spawn_timer += 1
    if spawn_timer >= SPAWN_DELAY:
        spawn_timer = 0
        side = random.choice(["left", "right"])

        if side == "left":
            en_x = -ENEMY_WIDTH
        else:
            en_x = SCREEN_WIDTH + ENEMY_WIDTH

        en_y = GROUND_Y - ENEMY_HEIGHT

        new_enemy = Enemy(en_x, en_y)
        enemies.append(new_enemy)

    # Обновление врагов
    for enemy in enemies[:]:
        enemy.position_update(player.x)
        enemy.draw(screen)

        if check_collisions(player.rect, enemy.rect) and not DEBUG:
            game_over = True

        for projectile in projectiles:
            if check_collisions(projectile.rect, enemy.rect):
                projectile.reset()
                enemies.remove(enemy)
                break

        if enemy in enemies and enemy.is_off_screen():
            enemies.remove(enemy)

    player.draw(screen)

    # Экран Game Over
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 74)
        game_over_text = font.render("ИГРА ОКОНЧЕНА!", True, WHITE)

        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Нажми R для рестарта", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    active_count = len([p for p in projectiles if p.active])
    font = pygame.font.Font(None, 36)
    count_text = font.render(f"Снарядов: {active_count}", True, (0, 0, 255))
    screen.blit(count_text, (10, 10))

    pygame.display.flip()
