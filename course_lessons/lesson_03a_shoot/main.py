import pygame
import sys

# ============================================
# УРОК 3A: ВЫСТРЕЛ В СТОРОНУ МЫШКИ
# ============================================
# В этом уроке мы научимся:
# 1. Получать позицию мышки на экране
# 2. Вычислять направление от игрока к мышке
# 3. Создавать снаряд, который летит в сторону мышки
# ============================================

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 3A: Выстрел в сторону мышки")

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
PROJECTILE_SPEED = 10  # Скорость полёта снаряда


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
        """
        Возвращает координаты центра игрока.
        Это нужно, чтобы снаряд вылетал из центра игрока, а не из угла.
        """
        return self.x + self.width // 2, self.y + self.height // 2


class Projectile:
    """
    Класс снаряда - это то, что мы будем "выстреливать" в сторону мышки.
    """
    def __init__(self, x, y, target_pos):
        """
        Создаём новый снаряд.
        
        Параметры:
        - x, y: начальная позиция снаряда (откуда он вылетает)
        - target_pos: позиция цели (куда он должен лететь) - это позиция мышки!
        """
        # Создаём прямоугольник для снаряда (12x12 пикселей)
        self.rect = pygame.Rect(x, y, 12, 12)
        
        # ============================================
        # ШАГ 1: Вычисляем направление полёта
        # ============================================
        # Чтобы снаряд летел в сторону мышки, нужно:
        # 1. Найти разницу между позицией мышки и позицией игрока
        # 2. Это даст нам вектор направления (направление + расстояние)
        
        # Создаём вектор направления от игрока к мышке
        # Vector2 - это специальный класс Pygame для работы с векторами
        direction = pygame.math.Vector2(
            target_pos[0] - x,  # Разница по X (горизонталь)
            target_pos[1] - y   # Разница по Y (вертикаль)
        )
        
        # ============================================
        # ШАГ 2: Нормализуем вектор (делаем его единичной длины)
        # ============================================
        # normalize() делает вектор длиной 1, но сохраняет направление
        # Зачем? Чтобы все снаряды летели с одинаковой скоростью,
        # независимо от того, далеко мышка или близко!
        
        if direction.length() > 0:
            # Если расстояние больше нуля (мышка не на игроке)
            direction = direction.normalize()
            # Умножаем на скорость, чтобы получить вектор скорости
            self.velocity = direction * PROJECTILE_SPEED
        else:
            # Если мышка прямо на игроке, снаряд не двигается
            self.velocity = pygame.math.Vector2(0, 0)
        
        # Флаг активности: True = снаряд летит, False = снаряд удалён
        self.active = True

    def update(self):
        """
        Обновляем позицию снаряда каждый кадр.
        """
        # Если снаряд неактивен, ничего не делаем
        if not self.active:
            return
        
        # ============================================
        # ШАГ 3: Двигаем снаряд
        # ============================================
        # Каждый кадр мы добавляем скорость к позиции снаряда
        # velocity.x - скорость по горизонтали
        # velocity.y - скорость по вертикали
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        # ============================================
        # ШАГ 4: Проверяем, не улетел ли снаряд за экран
        # ============================================
        # Если снаряд ушёл за границы экрана или упал в землю,
        # делаем его неактивным (он исчезнет)
        
        # Проверяем все стороны экрана
        if (self.rect.bottom < 0 or           # Улетел вверх
            self.rect.top > SCREEN_HEIGHT or   # Улетел вниз
            self.rect.right < 0 or             # Улетел влево
            self.rect.left > SCREEN_WIDTH):    # Улетел вправо
            self.active = False
        
        # Проверяем, не упал ли в землю
        if self.rect.bottom >= GROUND_Y:
            self.active = False

    def draw(self, surface):
        """
        Рисуем снаряд на экране.
        """
        if self.active:
            # Рисуем маленький серый квадратик
            pygame.draw.rect(surface, (60, 60, 60), self.rect)


# ============================================
# СОЗДАНИЕ ИГРОВЫХ ОБЪЕКТОВ
# ============================================
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)
projectiles = []  # Список всех снарядов на экране
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
        
        # Прыжок по пробелу
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()
        
        # ============================================
        # СОЗДАНИЕ СНАРЯДА ПРИ КЛИКЕ МЫШКОЙ
        # ============================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # button == 1 означает левую кнопку мышки
            
            # Получаем позицию центра игрока
            px, py = player.center
            
            # Получаем позицию мышки на экране
            mouse_pos = pygame.mouse.get_pos()
            # mouse_pos - это кортеж (x, y) с координатами мышки
            
            # Создаём новый снаряд, который полетит в сторону мышки
            projectile = Projectile(px, py, mouse_pos)
            
            # Добавляем снаряд в список всех снарядов
            projectiles.append(projectile)

    # ============================================
    # УПРАВЛЕНИЕ ИГРОКОМ
    # ============================================
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_horizontal("left")
    if keys[pygame.K_RIGHT]:
        player.move_horizontal("right")

    # Применяем гравитацию к игроку
    player.apply_gravity()

    # ============================================
    # ОБНОВЛЕНИЕ СНАРЯДОВ
    # ============================================
    for projectile in projectiles:
        # Обновляем позицию каждого снаряда
        projectile.update()
        # Рисуем снаряд на экране
        projectile.draw(screen)
    
    # Удаляем неактивные снаряды из списка (чтобы не накапливались)
    projectiles = [p for p in projectiles if p.active]

    # ============================================
    # ОТРИСОВКА
    # ============================================
    # Рисуем землю
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
    
    # Рисуем игрока
    player.draw(screen)

    # Обновляем экран
    pygame.display.flip()

# Выход из игры
pygame.quit()
sys.exit()

