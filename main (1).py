import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Игра про нинзя кота")

WHITE = (255, 255, 255)
BLUE = (0, 0 ,255)
RED = (255, 0 , 0)

PLAYER_SIZE = 50
PLAYER_COLOR = BLUE
PLAYER_SPEED = 15
JUMP_HEIGHT = 20
GRAVITY = 1
GROUND_Y = SCREEN_HEIGHT - 100

class AssetLoader:
    def __init__(self):
        self.sprites = {}
        self.load_all()

    def load_image(self, path, width, height):
        try:
            image = pygame.image.load(path).convert_alpha()
        except(FileNotFoundError, pygame.error):
            print(f'Картинка не найдена по пути {path}')
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(image, (100, 100, 100), (5, 5, width-10, height-10))
        return pygame.transform.scale(image, (width, height))
    
    def load_all(self):
        self.sprites['player_idle'] = self.load_image("assets/idle.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites['player_walk'] = self.load_image("assets/walk.png", PLAYER_SIZE, PLAYER_SIZE)
        self.sprites['player_jump'] = self.load_image("assets/jump.png", PLAYER_SIZE, PLAYER_SIZE)

    def get(self, name):
        return self.sprites.get(name, None)

class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_y = 0
        self.is_jumping = False
        self.direction = 'right'
        self.assets = assets
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def move(self, deriction):
        if deriction == "right":
            self.x += PLAYER_SPEED
            self.direction = "right"
        elif deriction == "left":
            self.x -= PLAYER_SPEED
            self.direction = "left"

        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - PLAYER_SIZE:
            self.x = SCREEN_WIDTH - PLAYER_SIZE

    def jump(self):
        if not self.is_jumping:
            self.vel_y = -JUMP_HEIGHT
            self.is_jumping = True

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= SCREEN_HEIGHT - self.height - 100:
            self.y = SCREEN_HEIGHT - self.height - 100
            self.vel_y = 0
            self.is_jumping = False

        self.rect.topleft = (self.x, self.y)
    
    def update_animation(self):
        keys = pygame.key.get_pressed()
        moving =keys[pygame.K_a] or keys[pygame.K_d]

        if self.is_jumping:
            self.current_sprite = self.assets.get("player_jump")
        elif moving:
            self.current_sprite = self.assets.get("player_walk")
        else:
            self.current_sprite = self.assets.get("player_idle")

        if self.direction == 'left':
            self.flipped_sprite = pygame.transform.flip(self.current_sprite, True, False)
        else:
            self.flipped_sprite = self.current_sprite
    
    def draw(self, surface):
        # pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
        surface.blit(self.flipped_sprite, (self.x, self.y))


class Projectile:
    def __init__(self, x, y, target_pos, assets, speed=10):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.assets = assets
        self.active = True
        self.stuck = False

        direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        self.hit_surface = False
        self.gravity = 0.6

    def update(self, ground_y, enemies):
        if self.stuck or not self.active:
            return
        
        if not self.hit_surface:
            self.rect.x = self.velocity.x
            self.rect.y = self.velocity.y

            # Отскок от левой стены
            if self.rect.left <= 0:
                self.velocity.x = self.velocity.x * -0.4
                self.hit_surface = True
            # Отскок от правой стены
            if self.rect.right <= SCREEN_WIDTH:
                self.velocity.x = self.velocity.x * -0.4
                self.hit_surface = True

            if self.rect.top <= 0:
                self.velocity.y = self.velocity.y * -0.4
                self.hit_surface = True

            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.stuck = True
        
        if self.hit_surface and not self.stuck:
            self.velocity.y += self.gravity
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            if abs(self.velocity.x) > 0.1:
                self.velocity.x *= 0.92
            
            else:
                self.velocity.x = 0

            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.stuck = True
                self.velocity = pygame.math.Vector2(0, 0)


    def draw(self, surface):
        if not self.active:
            return
        sprite = self.assets.get("arrow")
        if sprite:
            pass
        else:
            pygame.draw.circle(surface, (0,0,0), self.rect.center, 12)

    def is_close_to_player(self, player_rect, threshold=40):
        return self.stuck and self.rect.colliderect(player.rect.inflate(threshold, threshold))
    
    def reset(self):
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = pygame.math.Vector2(0, 0)
    


assets_load = AssetLoader() 
player = Player(x = 100, y = SCREEN_HEIGHT - PLAYER_SIZE -100, assets=assets_load)
ground_y = SCREEN_HEIGHT - 100

projectiles = []
max_projectiles = 3
clock = pygame.time.Clock()
running = True

while running:

    clock.tick(60)
    screen.fill(WHITE)

    pygame.draw.line(screen, RED, (0, SCREEN_HEIGHT-100), (SCREEN_WIDTH, SCREEN_HEIGHT -100), 3)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            player.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                active_count = len([p for p in projectiles if p.active])
                if active_count < max_projectiles:
                    pos = player.x + PLAYER_SIZE // 2, player.y + PLAYER_SIZE // 2
                    projectile = Projectile(pos[0], pos[1], pygame.mouse.get_pos(), assets_load)
                    projectiles.append(projectile)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
            player.move('left')     
    if keys[pygame.K_d]:
            player.move('right')

    
    
    player.apply_gravity()
    player.update_animation()

    player.rect = pygame. Rect(player.x, player.y, player.width, player.height)

    for projectile in projectiles:
        projectile.update(GROUND_Y, enemies=None)
        projectile.draw

        if projectile.stuck and projectile.is_close_to_player(player.rect):
            projectile.reset()

    player.draw(screen)

    pygame.display.flip()