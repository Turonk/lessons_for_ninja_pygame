import pygame
import sys

# ============================================
# УРОК 3B: ФИЗИКА СНАРЯДОВ (РИКОШЕТ И ПОДБОР)
# ============================================
# В этом уроке мы научимся:
# 1. Делать так, чтобы снаряд отскакивал от стен
# 2. Добавлять гравитацию к снаряду после рикошета
# 3. Ограничивать количество снарядов (максимум 3)
# 4. Подбирать застрявшие снаряды, подойдя к ним близко
# ============================================

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 3B: Рикошет и подбор снарядов")

# Цвета и земля
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

# Игрок
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1

# Снаряды
PROJECTILE_SPEED = 10
MAX_PROJECTILES = 3  # Максимальное количество снарядов на экране
PICKUP_DISTANCE = 40  # Расстояние, на котором можно подобрать снаряд


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False

    def move_horizontal(self, direction):
        if direction == "left":
            self.x -= PLAYER_SPEED
        elif direction == "right":
            self.x += PLAYER_SPEED
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

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

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 150, 255), (self.x, self.y, self.width, self.height))

    @property
    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    @property
    def rect(self):
        """Возвращает прямоугольник игрока для проверки столкновений"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Projectile:
    """
    Улучшенный класс снаряда с рикошетом и гравитацией.
    """
    def __init__(self, x, y, target_pos):
        # Создаём прямоугольник для снаряда
        self.rect = pygame.Rect(x, y, 12, 12)
        
        # Вычисляем направление полёта (как в уроке 3A)
        direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * PROJECTILE_SPEED
        else:
            self.velocity = pygame.math.Vector2(0, 0)
        
        # Флаги состояния снаряда
        self.active = True  # Активен ли снаряд
        self.stuck = False  # Застрял ли снаряд в земле
        self.hit_surface = False  # Ударился ли о стену/потолок
        
        # Гравитация для снаряда (применяется после рикошета)
        self.gravity = 0.6

    def update(self):
        """
        Обновляем позицию снаряда с учётом рикошета и гравитации.
        """
        # Если снаряд застрял или неактивен, ничего не делаем
        if self.stuck or not self.active:
            return

        # ============================================
        # ЭТАП 1: ОБЫЧНЫЙ ПОЛЁТ (до первого удара)
        # ============================================
        if not self.hit_surface:
            # Двигаем снаряд в направлении скорости
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # ============================================
            # ПРОВЕРКА РИКОШЕТА ОТ СТЕН
            # ============================================
            # Когда снаряд ударяется о стену, мы меняем направление скорости
            
            # Левая стена
            if self.rect.left <= 0:
                # Отскакиваем вправо (меняем знак скорости по X)
                self.velocity.x *= -0.4  # -0.4 означает, что скорость уменьшается
                self.hit_surface = True  # Теперь снаряд будет падать
            
            # Правая стена
            if self.rect.right >= SCREEN_WIDTH:
                # Отскакиваем влево
                self.velocity.x *= -0.4
                self.hit_surface = True
            
            # Потолок
            if self.rect.top <= 0:
                # Отскакиваем вниз (меняем знак скорости по Y)
                self.velocity.y *= -0.4
                self.hit_surface = True

            # ============================================
            # ПРОВЕРКА ПОПАДАНИЯ В ЗЕМЛЮ
            # ============================================
            if self.rect.bottom >= GROUND_Y:
                # Ставим снаряд точно на землю
                self.rect.bottom = GROUND_Y
                # Помечаем как застрявший
                self.stuck = True
                # Останавливаем движение
                self.velocity = pygame.math.Vector2(0, 0)

        # ============================================
        # ЭТАП 2: ПАДЕНИЕ ПОСЛЕ РИКОШЕТА
        # ============================================
        if self.hit_surface and not self.stuck:
            # Применяем гравитацию (снаряд падает вниз)
            self.velocity.y += self.gravity
            
            # Двигаем снаряд
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # ============================================
            # ЗАТУХАНИЕ ГОРИЗОНТАЛЬНОЙ СКОРОСТИ
            # ============================================
            # После рикошета скорость постепенно уменьшается
            # Это создаёт эффект "трения"
            if abs(self.velocity.x) > 0.1:
                # Умножаем скорость на 0.92 (немного уменьшаем)
                self.velocity.x *= 0.92
            else:
                # Если скорость очень маленькая, останавливаем полностью
                self.velocity.x = 0

            # ============================================
            # ПРОВЕРКА ПРИЗЕМЛЕНИЯ
            # ============================================
            if self.rect.bottom >= GROUND_Y:
                # Ставим снаряд на землю
                self.rect.bottom = GROUND_Y
                # Помечаем как застрявший
                self.stuck = True
                # Останавливаем движение
                self.velocity = pygame.math.Vector2(0, 0)

    def draw(self, surface):
        """Рисуем снаряд на экране"""
        if self.active:
            # Если застрял, рисуем другим цветом (чтобы было видно, что можно подобрать)
            color = (100, 100, 100) if self.stuck else (60, 60, 60)
            pygame.draw.rect(surface, color, self.rect)

    def is_close_to_player(self, player_rect):
        """
        Проверяет, находится ли снаряд достаточно близко к игроку для подбора.
        
        Параметры:
        - player_rect: прямоугольник игрока
        
        Возвращает:
        - True, если снаряд застрял и игрок рядом
        - False в остальных случаях
        """
        if not self.stuck:
            return False
        
        # Увеличиваем прямоугольник игрока на PICKUP_DISTANCE со всех сторон
        # Это создаёт "зону подбора" вокруг игрока
        pickup_zone = player_rect.inflate(PICKUP_DISTANCE, PICKUP_DISTANCE)
        
        # Проверяем, пересекается ли снаряд с зоной подбора
        return self.rect.colliderect(pickup_zone)

    def reset(self):
        """
        Сбрасывает снаряд (делает его неактивным).
        Вызывается, когда игрок подбирает снаряд.
        """
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = pygame.math.Vector2(0, 0)


# ============================================
# СОЗДАНИЕ ИГРОВЫХ ОБЪЕКТОВ
# ============================================
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)
projectiles = []  # Список всех снарядов
clock = pygame.time.Clock()
running = True

# ============================================
# ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
# ============================================
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # ============================================
    # ОБРАБОТКА СОБЫТИЙ
    # ============================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()
        
        # ============================================
        # СОЗДАНИЕ СНАРЯДА С ОГРАНИЧЕНИЕМ
        # ============================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Подсчитываем количество активных снарядов
            active_count = len([p for p in projectiles if p.active])
            
            # ============================================
            # ПРОВЕРКА ЛИМИТА СНАРЯДОВ
            # ============================================
            # Если активных снарядов меньше максимума, создаём новый
            if active_count < MAX_PROJECTILES:
                px, py = player.center
                mouse_pos = pygame.mouse.get_pos()
                projectile = Projectile(px, py, mouse_pos)
                projectiles.append(projectile)
            # Если лимит достигнут, новый снаряд не создаётся
            # Игрок должен подобрать старые снаряды!

    # ============================================
    # УПРАВЛЕНИЕ ИГРОКОМ
    # ============================================
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_horizontal("left")
    if keys[pygame.K_RIGHT]:
        player.move_horizontal("right")

    player.apply_gravity()

    # ============================================
    # ОБНОВЛЕНИЕ СНАРЯДОВ
    # ============================================
    player_rect = player.rect  # Получаем прямоугольник игрока для проверки подбора
    
    for projectile in projectiles:
        # Обновляем физику снаряда
        projectile.update()
        # Рисуем снаряд
        projectile.draw(screen)
        
        # ============================================
        # ПОДБОР СНАРЯДОВ
        # ============================================
        # Проверяем, может ли игрок подобрать этот снаряд
        if projectile.is_close_to_player(player_rect):
            # Сбрасываем снаряд (делаем его неактивным)
            projectile.reset()
            # Теперь игрок может выстрелить новый снаряд!

    # Удаляем неактивные снаряды из списка
    projectiles = [p for p in projectiles if p.active]

    # ============================================
    # ОТРИСОВКА
    # ============================================
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
    player.draw(screen)
    
    # Показываем количество активных снарядов
    active_count = len([p for p in projectiles if p.active])
    font = pygame.font.SysFont("Arial", 24)
    text = font.render(f"Снаряды: {active_count}/{MAX_PROJECTILES}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()

# Выход из игры
pygame.quit()
sys.exit()

