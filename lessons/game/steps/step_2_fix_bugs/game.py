import pygame
import random
from enemy import Enemy, ENEMY_HEIGHT, ENEMY_WIDTH, SPAWN_DELAY

DEBUG = False

# ===== КОНСТАНТЫ ЭКРАНА =====
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Основная игра")

# ===== КОНСТАНТЫ ИГРОКА =====
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1

# ===== КОНСТАНТЫ ЦВЕТА =====
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100  # Линия земли на 100 пикселей от низа

# ===== КОНСТАНТЫ СНАРЯДА =====
PROJECTILE_SPEED = 10
MAX_COUNT_PROJECTILES = 3
PICKUP_DISTANCE = 40  # Расстояние подбора снаряда (было PICUP — опечатка)


# =============================================================================
# КЛАСС: Загрузчик ресурсов
# =============================================================================
class AssetLoader:
    """Загружает спрайты из файлов. Если файл не найден — создаёт заглушку."""

    def __init__(self):
        self.sprites = {}
        self.load_all()

    def load_image(self, path, width, height):
        """Загружает изображение или возвращает заглушку."""
        try:
            image = pygame.image.load(path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            print(f"Файл не найден: {path}. Создаём заглушку.")
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(image, (100, 100, 100), (5, 5, width - 10, height - 10), border_radius=8)
            pygame.draw.circle(image, (255, 255, 255), (15, 15), 5)
        return pygame.transform.scale(image, (width, height))

    def load_all(self):
        """Загружаем все спрайты для игры."""
        self.sprites["player_idle"] = self.load_image("assets/idle.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_walk"] = self.load_image("assets/walk.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["player_jump"] = self.load_image("assets/jump.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites["projectile"] = self.load_image("assets/projectile.png", 24, 24)

    def get(self, name):
        """Возвращает спрайт по имени."""
        return self.sprites.get(name, None)


# =============================================================================
# КЛАСС: Игрок
# =============================================================================
class Player:
    """Игрок — ниндзя-кот. Умеет бегать, прыгать (двойной прыжок) и стрелять."""

    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0            # Вертикальная скорость (для прыжка и гравитации)
        self.is_jumping = False
        self.jump_count = 0       # Сколько раз прыгнул (макс 2 — двойной прыжок)
        self.max_jumps = 2
        self.direction = "right"  # Куда смотрит (для отражения спрайта)
        self.assets = assets

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        """Двигает игрока влево или вправо, не даёт выйти за экран."""
        if direction == "left":
            self.x -= PLAYER_SPEED
            self.direction = "left"
        elif direction == "right":
            self.x += PLAYER_SPEED
            self.direction = "right"

        # Ограничение по краям экрана
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        self.rect.x = self.x

    def jump(self):
        """Прыжок. Можно прыгнуть дважды (двойной прыжок)."""
        if self.jump_count < self.max_jumps:
            self.vel_y = -JUMP_HEIGHT  # Отрицательная скорость = вверх
            self.is_jumping = True
            self.jump_count += 1

    def apply_gravity(self):
        """Применяет гравитацию. Каждый кадр скорость тянет вниз."""
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Приземление на землю
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.is_jumping = False
            self.jump_count = 0  # Сброс прыжков при касании земли

        self.rect.y = self.y

    def update_animation(self):
        """Выбирает нужный спрайт в зависимости от состояния игрока."""
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]

        # Приоритет: прыжок > бег > стоять
        if self.is_jumping:
            self.current_sprite = self.assets.get("player_jump")
        elif moving:
            self.current_sprite = self.assets.get("player_walk")
        else:
            self.current_sprite = self.assets.get("player_idle")

        # Отражаем спрайт, если смотрим влево
        if self.direction == "left":
            self.flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
        else:
            self.flipped_sprite = self.current_sprite

    def draw(self, surface):
        """Рисует игрока на экране."""
        surface.blit(self.flipped_sprite, (self.x, self.y))

    @property
    def center(self):
        """Возвращает координаты центра игрока (для запуска снаряда)."""
        return self.x + self.width // 2, self.y + self.height // 2


# =============================================================================
# КЛАСС: Снаряд
# =============================================================================
class Projectile:
    """Снаряд, летящий к курсору мыши. Рикошетит от стен и падает."""

    def __init__(self, x, y, target_pos):
        self.rect = pygame.Rect(x, y, 12, 12)

        # Вычисляем направление от игрока к курсору мыши
        direction = pygame.math.Vector2(target_pos[0] - x,
                                        target_pos[1] - y)

        # Нормализуем вектор (делаем длину = 1) и умножаем на скорость
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * PROJECTILE_SPEED
        else:
            # FIX: было self.velocity = 0 (число)
            # Нужен Vector2, иначе вызов self.velocity.x упадёт с ошибкой
            self.velocity = pygame.math.Vector2(0, 0)

        self.active = True        # Снаряд существует (не подобран)
        self.stuck = False         # Снаряд застрял в земле
        self.hit_surface = False   # Снаряд ударился о стену/потолок

        self.gravity = 0.6  # Гравитация после рикошета (слабее чем у игрока)

    def update(self):
        """Обновляет позицию снаряда каждый кадр."""
        if self.stuck or not self.active:
            return

        # === Фаза 1: Обычный полёт (до первого столкновения) ===
        if not self.hit_surface:
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # Рикошет от левой стены
            if self.rect.left <= 0:
                self.velocity.x *= -0.4  # Отскок с потерей энергии (40%)
                self.hit_surface = True

            # Рикошет от правой стены
            if self.rect.right >= SCREEN_WIDTH:
                self.velocity.x *= -0.4
                self.hit_surface = True

            # Рикошет от потолка
            if self.rect.top <= 0:
                self.velocity.y *= -0.4
                self.hit_surface = True

            # Попадание в пол — застревает
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True
                self.velocity.y = 0

        # === Фаза 2: Падение после рикошета (гравитация + трение) ===
        if self.hit_surface and not self.stuck:
            self.velocity.y += self.gravity  # Гравитация тянет вниз
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # FIX: логика трения была перевёрнута!
            # Было: если скорость МАЛЕНЬКАЯ — замедлять, если БОЛЬШАЯ — обнулять
            # Стало: если скорость ещё заметная — замедлять, если крошечная — обнулять
            if abs(self.velocity.x) > 0.1:
                self.velocity.x *= 0.92  # Плавное замедление (трение)
            else:
                self.velocity.x = 0      # Полная остановка

            # Приземление на пол
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True
                self.velocity.y = 0

    def draw(self, surface):
        """Рисует снаряд как красный квадрат."""
        if self.active:
            pygame.draw.rect(surface, RED, self.rect)

    def is_close_to_player(self, player_rect):
        """Проверяет, может ли игрок подобрать застрявший снаряд."""
        if not self.stuck:
            return False

        # Увеличиваем зону подбора вокруг игрока
        pickup_zone = player_rect.inflate(PICKUP_DISTANCE, PICKUP_DISTANCE)
        return self.rect.colliderect(pickup_zone)

    def reset(self):
        """Деактивирует снаряд (подобран или попал во врага)."""
        self.active = False
        self.stuck = False
        self.hit_surface = False
        # FIX: было self.velocity = 0 (число)
        # Нужен Vector2, чтобы не сломать .x и .y при повторном использовании
        self.velocity = pygame.math.Vector2(0, 0)


# =============================================================================
# ИНИЦИАЛИЗАЦИЯ ИГРЫ
# =============================================================================
asset_loader = AssetLoader()
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE, assets=asset_loader)

enemies = []       # Список активных врагов
spawn_timer = 0    # Таймер спавна врагов
projectiles = []   # Список активных снарядов

clock = pygame.time.Clock()
running = True
game_over = False


def check_collisions(rect1, rect2):
    """Проверяет столкновение двух прямоугольников."""
    return rect1.colliderect(rect2)


# =============================================================================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# =============================================================================
while running:
    clock.tick(60)  # 60 кадров в секунду
    screen.fill(WHITE)
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Пробел — прыжок
            if event.key == pygame.K_SPACE and not game_over:
                player.jump()
            # R — рестарт после Game Over
            elif event.key == pygame.K_r and game_over:
                game_over = False
                player.x = 100
                player.y = GROUND_Y - PLAYER_SIZE
                player.vel_y = 0
                player.is_jumping = False
                enemies.clear()
                projectiles.clear()
                spawn_timer = 0

        # Левая кнопка мыши — выстрел
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            active_count = len([p for p in projectiles if p.active])

            if active_count < MAX_COUNT_PROJECTILES:
                px, py = player.center
                mouse_pos = pygame.mouse.get_pos()
                projectile = Projectile(px, py, mouse_pos)
                projectiles.append(projectile)

    # --- Управление движением (зажатые клавиши) ---
    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")

    # --- Обновление игрока ---
    if not game_over:
        player.apply_gravity()
        player.update_animation()

    player_rect = player.rect

    # --- Обновление снарядов ---
    for projectile in projectiles:
        projectile.update()
        projectile.draw(screen)
        # Подбор застрявшего снаряда при приближении
        if projectile.is_close_to_player(player_rect):
            projectile.reset()

    # Убираем неактивные снаряды из списка
    projectiles = [p for p in projectiles if p.active]

    # --- Спавн врагов ---
    spawn_timer += 1
    if spawn_timer >= SPAWN_DELAY:
        spawn_timer = 0
        side = random.choice(["left", "right"])

        if side == "left":
            en_x = -ENEMY_WIDTH        # Появляется за левым краем
        else:
            en_x = SCREEN_WIDTH + ENEMY_WIDTH  # Появляется за правым краем

        en_y = GROUND_Y - ENEMY_HEIGHT  # На уровне земли

        new_enemy = Enemy(en_x, en_y)
        enemies.append(new_enemy)

    # --- Обновление врагов ---
    for enemy in enemies[:]:  # [:] — копия списка, чтобы безопасно удалять
        enemy.position_update(player.x)
        enemy.draw(screen)

        # Столкновение игрок-враг
        if check_collisions(player.rect, enemy.rect) and not DEBUG:
            game_over = True

        # Столкновение снаряд-враг
        for projectile in projectiles:
            if check_collisions(projectile.rect, enemy.rect):
                projectile.reset()
                enemies.remove(enemy)
                break  # Враг уже удалён — выходим из цикла снарядов

        # Удаляем врага, если ушёл далеко за экран
        if enemy in enemies and enemy.is_off_screen():
            enemies.remove(enemy)

    player.draw(screen)

    # --- Экран Game Over ---
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Полупрозрачный чёрный фон
        screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 74)
        game_over_text = font.render("ИГРА ОКОНЧЕНА!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Нажми R для рестарта", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    # --- HUD: счётчик снарядов ---
    active_count = len([p for p in projectiles if p.active])
    font = pygame.font.Font(None, 36)
    count_text = font.render(f"Снарядов: {active_count}", True, (0, 0, 255))
    screen.blit(count_text, (10, 10))

    pygame.display.flip()
