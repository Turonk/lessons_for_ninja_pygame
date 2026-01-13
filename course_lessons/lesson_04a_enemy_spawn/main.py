import pygame
import sys
import random

# ============================================
# УРОК 4A: ВРАГИ - ХОДЬБА И СПАВН ПО ТАЙМЕРУ
# ============================================
# В этом уроке мы научимся:
# 1. Создавать класс врага
# 2. Заставлять врага двигаться к игроку
# 3. Использовать таймер для появления новых врагов
# 4. Удалять врагов, которые ушли за экран
# ============================================

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 4A: Враги - ходьба и спавн")

# Цвета и земля
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

# Игрок
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1

# Враги
ENEMY_SIZE = 40
ENEMY_SPEED = 2  # Скорость движения врага
SPAWN_DELAY = 180  # Задержка между появлением врагов (в кадрах)
# 180 кадров = 3 секунды (при 60 кадрах в секунду)


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
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Enemy:
    """
    Класс врага - противник, который будет преследовать игрока.
    """
    def __init__(self, x, y):
        """
        Создаём нового врага.
        
        Параметры:
        - x, y: начальная позиция врага
        """
        # Создаём прямоугольник для врага
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        # ============================================
        # ОПРЕДЕЛЕНИЕ НАПРАВЛЕНИЯ ДВИЖЕНИЯ
        # ============================================
        # Направление: 1 = вправо, -1 = влево
        # Определяем, с какой стороны экрана появился враг
        if x > SCREEN_WIDTH // 2:
            # Если враг справа от центра, идёт влево
            self.direction = -1
        else:
            # Если враг слева от центра, идёт вправо
            self.direction = 1

    def update(self, player_x):
        """
        Обновляет позицию врага каждый кадр.
        
        Параметры:
        - player_x: X-координата игрока (чтобы враг двигался к нему)
        """
        # ============================================
        # ИЗМЕНЕНИЕ НАПРАВЛЕНИЯ В ЗАВИСИМОСТИ ОТ ПОЗИЦИИ ИГРОКА
        # ============================================
        # Если игрок справа от врага, враг идёт вправо
        if self.rect.x < player_x:
            self.direction = 1  # Вправо
        else:
            # Если игрок слева от врага, враг идёт влево
            self.direction = -1  # Влево

        # ============================================
        # ДВИЖЕНИЕ ВРАГА
        # ============================================
        # Двигаем врага в выбранном направлении
        # Умножаем скорость на направление (1 или -1)
        self.rect.x += ENEMY_SPEED * self.direction
        
        # ============================================
        # УСТАНОВКА ВРАГА НА ЗЕМЛЮ
        # ============================================
        # Враг всегда должен стоять на земле
        if self.rect.bottom < GROUND_Y:
            self.rect.bottom = GROUND_Y

    def draw(self, surface):
        """
        Рисует врага на экране.
        """
        # Рисуем красный квадрат - это наш враг
        pygame.draw.rect(surface, (200, 0, 0), self.rect)

    def is_off_screen(self):
        """
        Проверяет, ушёл ли враг за границы экрана.
        
        Возвращает:
        - True, если враг ушёл за экран
        - False, если враг ещё на экране
        """
        # Проверяем, ушёл ли враг далеко влево или вправо
        # Добавляем небольшой запас (50 пикселей), чтобы враг удалялся,
        # когда полностью скрылся за экраном
        return self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50


# ============================================
# СОЗДАНИЕ ИГРОВЫХ ОБЪЕКТОВ
# ============================================
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)
enemies = []  # Список всех врагов на экране
spawn_timer = 0  # Таймер для отсчёта времени до следующего спавна
clock = pygame.time.Clock()
running = True

# ============================================
# ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
# ============================================
while running:
    clock.tick(60)  # 60 кадров в секунду
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
    # УПРАВЛЕНИЕ ИГРОКОМ
    # ============================================
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_horizontal("left")
    if keys[pygame.K_RIGHT]:
        player.move_horizontal("right")

    player.apply_gravity()

    # ============================================
    # СПАВН НОВЫХ ВРАГОВ ПО ТАЙМЕРУ
    # ============================================
    # Увеличиваем таймер на 1 каждый кадр
    spawn_timer += 1
    
    # Проверяем, прошло ли достаточно времени для спавна
    if spawn_timer >= SPAWN_DELAY:
        # Сбрасываем таймер
        spawn_timer = 0
        
        # ============================================
        # ВЫБОР СТОРОНЫ ПОЯВЛЕНИЯ
        # ============================================
        # Случайно выбираем, с какой стороны появится враг
        side = random.choice(["left", "right"])
        
        # ============================================
        # ВЫЧИСЛЕНИЕ ПОЗИЦИИ ВРАГА
        # ============================================
        if side == "left":
            # Враг появляется слева за экраном
            x = -ENEMY_SIZE
        else:
            # Враг появляется справа за экраном
            x = SCREEN_WIDTH + ENEMY_SIZE
        
        # Y-координата всегда на земле
        y = GROUND_Y - ENEMY_SIZE
        
        # ============================================
        # СОЗДАНИЕ НОВОГО ВРАГА
        # ============================================
        # Создаём нового врага и добавляем в список
        new_enemy = Enemy(x, y)
        enemies.append(new_enemy)

    # ============================================
    # ОБНОВЛЕНИЕ ВРАГОВ
    # ============================================
    for enemy in enemies[:]:  # Используем копию списка для безопасного удаления
        # Обновляем позицию врага (передаём X-координату игрока)
        enemy.update(player.x)
        # Рисуем врага
        enemy.draw(screen)
        
        # ============================================
        # УДАЛЕНИЕ ВРАГОВ, УШЕДШИХ ЗА ЭКРАН
        # ============================================
        # Проверяем, не ушёл ли враг за границы экрана
        if enemy.is_off_screen():
            # Удаляем врага из списка
            enemies.remove(enemy)
            # Это нужно, чтобы список врагов не разрастался бесконечно

    # ============================================
    # ОТРИСОВКА
    # ============================================
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
    player.draw(screen)
    
    # Показываем количество врагов на экране
    font = pygame.font.SysFont("Arial", 24)
    text = font.render(f"Врагов: {len(enemies)}", True, BLACK)
    screen.blit(text, (10, 10))

    pygame.display.flip()

# Выход из игры
pygame.quit()
sys.exit()

