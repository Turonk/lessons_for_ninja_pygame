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
SPAWN_DELAY = 180 # Спавн задержка между появлением противника
# 180 тиков поделить на fps = 3 секунды.
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if x >= SCREEN_WIDTH //2:
            self.direction = -1
        else:
            self.direction = 1
        

    #def move(self, direction):
    #    if direction == "left":
    #        self.x -= ENEMY_SPEED
    #    elif direction == "right":
    #        self.x += ENEMY_SPEED
        
    #    if self.x < 0:
    #        self.x = 0
    #    if self.x > SCREEN_WIDTH - self.width:
    #        self.x = SCREEN_WIDTH - self.width
    
    def position_update(self, player_x):
        if self.rect.x < player_x:
            self.direction = 1
        else:
            self.direction = -1
        
        self.x += self.direction * ENEMY_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

    def is_off_screen(self):
        return self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50

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