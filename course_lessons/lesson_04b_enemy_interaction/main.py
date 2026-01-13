import pygame
import sys
import random

# ============================================
# УРОК 4B: ВЗАИМОДЕЙСТВИЕ С ВРАГАМИ
# ============================================
# В этом уроке мы научимся:
# 1. Стрелять по врагам и уничтожать их
# 2. Обрабатывать столкновение игрока с врагом
# 3. Отнимать жизни при столкновении
# 4. Завершать игру при потере всех жизней
# ============================================

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 4B: Взаимодействие с врагами")

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

# Снаряды
PROJECTILE_SPEED = 10
MAX_PROJECTILES = 3
PICKUP_DISTANCE = 40

# Враги
ENEMY_SIZE = 40
ENEMY_SPEED = 2
SPAWN_DELAY = 180


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False
        # ============================================
        # ДОБАВЛЯЕМ СИСТЕМУ ЖИЗНЕЙ
        # ============================================
        self.lives = 3  # Начальное количество жизней

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

    @property
    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2


class Projectile:
    def __init__(self, x, y, target_pos):
        self.rect = pygame.Rect(x, y, 12, 12)
        direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * PROJECTILE_SPEED
        else:
            self.velocity = pygame.math.Vector2(0, 0)
        self.active = True
        self.stuck = False
        self.hit_surface = False
        self.gravity = 0.6

    def update(self, enemies):
        """
        Обновляет позицию снаряда и проверяет попадание во врагов.
        
        Параметры:
        - enemies: список всех врагов на экране
        """
        if self.stuck or not self.active:
            return

        if not self.hit_surface:
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # ============================================
            # ПРОВЕРКА ПОПАДАНИЯ СНАРЯДА ВО ВРАГА
            # ============================================
            # Проходим по всем врагам и проверяем столкновение
            for enemy in enemies[:]:  # Используем копию списка для безопасного удаления
                # Проверяем, пересекается ли снаряд с врагом
                if self.rect.colliderect(enemy.rect):
                    # ============================================
                    # УНИЧТОЖЕНИЕ ВРАГА
                    # ============================================
                    # Удаляем врага из списка (снаряд попал в него!)
                    enemies.remove(enemy)
                    
                    # ============================================
                    # РИКОШЕТ ПОСЛЕ ПОПАДАНИЯ
                    # ============================================
                    # После попадания снаряд отскакивает и начинает падать
                    # Определяем, в какую сторону отскакивать
                    if abs(self.velocity.x) > abs(self.velocity.y):
                        # Если скорость по X больше, отскакиваем по горизонтали
                        self.velocity.x *= -0.4
                    else:
                        # Если скорость по Y больше, отскакиваем по вертикали
                        self.velocity.y *= -0.4
                    
                    # Помечаем, что снаряд ударился (теперь будет падать)
                    self.hit_surface = True
                    break  # Важно: выходим из цикла после первого попадания

            # Рикошет от стен (как в уроке 3B)
            if self.rect.left <= 0:
                self.velocity.x *= -0.4
                self.hit_surface = True
            if self.rect.right >= SCREEN_WIDTH:
                self.velocity.x *= -0.4
                self.hit_surface = True
            if self.rect.top <= 0:
                self.velocity.y *= -0.4
                self.hit_surface = True
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True

        # Падение после рикошета (как в уроке 3B)
        if self.hit_surface and not self.stuck:
            self.velocity.y += self.gravity
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y
            if abs(self.velocity.x) > 0.1:
                self.velocity.x *= 0.92
            else:
                self.velocity.x = 0
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.stuck = True
                self.velocity = pygame.math.Vector2(0, 0)

    def draw(self, surface):
        if self.active:
            color = (100, 100, 100) if self.stuck else (60, 60, 60)
            pygame.draw.rect(surface, color, self.rect)

    def is_close_to_player(self, player_rect):
        if not self.stuck:
            return False
        pickup_zone = player_rect.inflate(PICKUP_DISTANCE, PICKUP_DISTANCE)
        return self.rect.colliderect(pickup_zone)

    def reset(self):
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = pygame.math.Vector2(0, 0)


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.direction = -1 if x > SCREEN_WIDTH // 2 else 1

    def update(self, player_x):
        if self.rect.x < player_x:
            self.direction = 1
        else:
            self.direction = -1
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.bottom < GROUND_Y:
            self.rect.bottom = GROUND_Y

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 0, 0), self.rect)

    def is_off_screen(self):
        return self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50


# ============================================
# СОЗДАНИЕ ИГРОВЫХ ОБЪЕКТОВ
# ============================================
player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)
projectiles = []
enemies = []
spawn_timer = 0
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 28)

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
        
        # Стрельба (как в уроке 3A)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            active_count = len([p for p in projectiles if p.active])
            if active_count < MAX_PROJECTILES:
                px, py = player.center
                projectile = Projectile(px, py, pygame.mouse.get_pos())
                projectiles.append(projectile)

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
    player_rect = player.rect
    
    for projectile in projectiles:
        # Передаём список врагов в метод update
        # Теперь снаряд может проверять попадание во врагов
        projectile.update(enemies)
        projectile.draw(screen)
        
        # Подбор снарядов (как в уроке 3B)
        if projectile.is_close_to_player(player_rect):
            projectile.reset()

    projectiles = [p for p in projectiles if p.active]

    # ============================================
    # СПАВН ВРАГОВ (как в уроке 4A)
    # ============================================
    spawn_timer += 1
    if spawn_timer >= SPAWN_DELAY:
        spawn_timer = 0
        side = random.choice(["left", "right"])
        x = -ENEMY_SIZE if side == "left" else SCREEN_WIDTH + ENEMY_SIZE
        y = GROUND_Y - ENEMY_SIZE
        enemies.append(Enemy(x, y))

    # ============================================
    # ОБНОВЛЕНИЕ ВРАГОВ И ПРОВЕРКА СТОЛКНОВЕНИЙ
    # ============================================
    for enemy in enemies[:]:  # Используем копию списка для безопасного удаления
        enemy.update(player.x)
        enemy.draw(screen)

        # ============================================
        # СТОЛКНОВЕНИЕ ИГРОКА С ВРАГОМ
        # ============================================
        # Проверяем, пересекается ли прямоугольник врага с прямоугольником игрока
        if enemy.rect.colliderect(player.rect):
            # ============================================
            # ОТТАЛКИВАНИЕ ИГРОКА
            # ============================================
            # Когда враг касается игрока, отталкиваем игрока назад
            # Это создаёт эффект "удара"
            knockback = 50  # На сколько пикселей отталкиваем
            # Отталкиваем в противоположную сторону от направления движения
            if player.x < enemy.rect.x:
                # Если игрок слева от врага, отталкиваем влево
                player.x -= knockback
            else:
                # Если игрок справа от врага, отталкиваем вправо
                player.x += knockback
            
            # Убеждаемся, что игрок не вышел за границы экрана
            player.x = max(0, min(player.x, SCREEN_WIDTH - player.width))

            # ============================================
            # ПОТЕРЯ ЖИЗНИ
            # ============================================
            # Отнимаем одну жизнь у игрока
            player.lives -= 1
            
            # Удаляем врага после столкновения
            enemies.remove(enemy)

            # ============================================
            # ПРОВЕРКА КОНЦА ИГРЫ
            # ============================================
            # Если у игрока не осталось жизней, игра заканчивается
            if player.lives <= 0:
                print("Игра окончена! У вас закончились жизни.")
                running = False

        # Удаление врагов, ушедших за экран (как в уроке 4A)
        if enemy in enemies and enemy.is_off_screen():
            enemies.remove(enemy)

    # ============================================
    # ОТРИСОВКА
    # ============================================
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
    player.draw(screen)
    
    # ============================================
    # ОТОБРАЖЕНИЕ ЖИЗНЕЙ
    # ============================================
    # Показываем количество оставшихся жизней
    lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
    screen.blit(lives_text, (10, 10))

    pygame.display.flip()

# Выход из игры
pygame.quit()
sys.exit()

