import pygame
import sys

# Настраиваем окно
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Урок 1: окно и земля")

# Цвета и земля
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 100

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    # События: только выход
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Рисуем землю
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

    pygame.display.flip()

pygame.quit()
sys.exit()

