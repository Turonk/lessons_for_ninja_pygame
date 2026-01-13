import pygame
import sys

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 2: движение и прыжок")

# Цвета и земля
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

# Игрок
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
GRAVITY = 1


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

        # Держим игрока в окне
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def jump(self):
        if not self.is_jumping:
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Приземляемся на землю
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.is_jumping = False

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 150, 255), (self.x, self.y, self.width, self.height))


player = Player(x=100, y=GROUND_Y - PLAYER_SIZE)
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_horizontal("left")
    if keys[pygame.K_RIGHT]:
        player.move_horizontal("right")

    player.apply_gravity()

    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

