import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра про нинзя кота")

WHITE = (255, 255, 255)
BLUE = (0, 0 ,255)
RED = (255, 0 , 0)

ENEMY_HEIGHT = 50
ENEMY_WIDTH = 50
ENEMY_SPEED = 1 # Нужно добавить в первую очередь

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.speed = ENEMY_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed

        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def position_update(self):
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

def main():
    enemy = Enemy(x=0, y=SCREEN_HEIGHT - ENEMY_HEIGHT - 100)

    clock = pygame.time.Clock()
    enemy_direction = "right"
    running = True

    while running:

        clock.tick(60)
        screen.fill(WHITE)

        pygame.draw.line(screen, RED, (0, SCREEN_HEIGHT-100), (SCREEN_WIDTH, SCREEN_HEIGHT -100), 3)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if enemy.x >= SCREEN_WIDTH - ENEMY_WIDTH:
            enemy_direction = "left"
        elif enemy.x <= 0:
            enemy_direction = "right"
        
        enemy.move(enemy_direction)

        enemy.position_update()
        enemy.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()