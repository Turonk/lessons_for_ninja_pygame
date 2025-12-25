
# 🎓 Урок 4: Как добавить метательное оружие (сюрикен) в Pygame — пошагово

> 💡 Этот урок покажет, как **постепенно добавить снаряд** в игру на Pygame:  
от простого квадрата — до реалистичного сюрикена, который летит в сторону курсора, отскакивает от стен и подбирается обратно.

---

## 🎯 Цель урока
К концу урока у тебя будет:
- Снаряд, который летит в сторону курсора.
- Отскакивает от стен и потолка.
- Падает на землю и застревает.
- Подбирается игроком.
- Ограничение — максимум 3 снаряда.

---

## 🧰 Что нужно знать
- Основы Python и Pygame.
- Работа с `pygame.Rect`, `pygame.math.Vector2`.
- Обработка событий и цикл обновления.

---

## 🚶‍♂️ Шаг 1: Создаём класс `Projectile`

Создаём минимальный класс снаряда — просто квадрат.

```python
class Projectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)  # 24x24 пикселя
        self.active = True  # Активен

    def update(self):
        # Пока ничего не делаем
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Чёрный квадрат
```
## ✅ Добавь этот класс после класса Player.

🧩 Использование в игре
В секции инициализации:

```python
projectiles = []  # Список снарядов
```
Бросок снаряда (временно — по клавише F):

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_f]:
    pos_x = player.x + 25
    pos_y = player.y + 25
    projectiles.append(Projectile(pos_x, pos_y))
```
В основном цикле:

```python
# Обновление и отрисовка
for projectile in projectiles[:]:
    projectile.update()
    projectile.draw(screen)
    if not projectile.active:
        projectiles.remove(projectile)
```

## 🚶‍♂️ Шаг 2: Снаряд летит в сторону взгляда (влево/вправо)
Теперь снаряд будет лететь в направлении, куда смотрит игрок.

## 🔄 Обнови __init__:
```python
def __init__(self, x, y, direction, speed=8):
    self.rect = pygame.Rect(x, y, 24, 24)
    self.speed = speed
    self.direction = direction  # "left" или "right"
    self.active = True
```

## 🔄 Обнови update():
```python
def update(self):
    if not self.active:
        return
    if self.direction == "right":
        self.rect.x += self.speed
    else:
        self.rect.x -= self.speed

    # Удаляем, если улетел за экран
    if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
        self.active = False
```

## 🔄 Обнови бросок:
```python
if keys[pygame.K_f]:
    direction = player.direction
    pos_x = player.x + 25
    pos_y = player.y + 25
    projectile = Projectile(pos_x, pos_y, direction)
    projectiles.append(projectile)
```
## ✅ Теперь снаряд летит влево или вправо.

## 🚶‍♂️ Шаг 3: Полёт в сторону курсора мыши
Сделаем, чтобы снаряд летел в направлении мыши.

## 🔄 Обнови __init__:
```python
def __init__(self, x, y, target_pos, speed=10):
    self.rect = pygame.Rect(x, y, 24, 24)
    self.speed = speed
    self.active = True

    # Вектор направления
    direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
    if direction.length() > 0:
        self.velocity = direction.normalize() * speed
    else:
        self.velocity = pygame.math.Vector2(0, 0)
```

## 🔄 Обнови update():
```python
def update(self):
    if not self.active:
        return

    self.rect.x += self.velocity.x
    self.rect.y += self.velocity.y

    # Удаляем при выходе за экран
    if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
        self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
        self.active = False
```
## 🔄 Замени управление — бросок по ЛКМ:
```python
for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Левая кнопка мыши
            pos_x = player.x + 25
            pos_y = player.y + 25
            projectile = Projectile(pos_x, pos_y, pygame.mouse.get_pos())
            projectiles.append(projectile)
```
### ✅ Снаряд теперь летит точно в сторону курсора.

## 🚶‍♂️ Шаг 4: Отскок от стен, падение и подбор
Сделаем поведение реалистичнее: снаряд отскакивает, падает, застревает, подбирается.

### 🔄 Полная версия Projectile
```python
class Projectile:
    def __init__(self, x, y, target_pos, speed=10):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.active = True
        self.stuck = False

        direction = pygame.math.Vector2(target_pos[0] - x, target_pos[1] - y)
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        self.hit_surface = False  # Ударился о стену/потолок
        self.gravity = 0.6

    def update(self, ground_y):
        if self.stuck or not self.active:
            return

        # Полёт до удара
        if not self.hit_surface:
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y

            # Отскок от стен
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.velocity.x *= -0.3
                self.hit_surface = True

            if self.rect.top <= 0:
                self.velocity.y *= -0.3
                self.hit_surface = True

            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.stuck = True

        # После удара — падение
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
        if self.active:
            pygame.draw.rect(surface, (0, 0, 0), self.rect)

    def is_close_to_player(self, player_rect, threshold=40):
        return self.stuck and self.rect.colliderect(player_rect.inflate(threshold, threshold))

    def reset(self):
        self.active = False
        self.stuck = False
        self.hit_surface = False
        self.velocity = pygame.math.Vector2(0, 0)
```

### 🔄 В основном цикле — подбор:
```python
player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

for projectile in projectiles:
    projectile.update(GROUND_Y)
    projectile.draw(screen)

    if projectile.stuck and projectile.is_close_to_player(player_rect):
        projectile.reset()  # Подобрали!
```

### ✅ Теперь снаряд:

- Отскакивает от стен.
- Падает при ударе.
- Застревает в земле.
- Подбирается.
## 🚶‍♂️ Шаг 5: Ограничение — только 3 снаряда
Добавим лимит: нельзя бросить больше 3 снарядов.

## 🔄 В событии клика:
```python
if event.button == 1:
    active_count = len([p for p in projectiles if p.active])
    if active_count < 3:
        pos_x = player.x + 25
        pos_y = player.y + 25
        projectile = Projectile(pos_x, pos_y, pygame.mouse.get_pos())
        projectiles.append(projectile)
```
### ✅ Теперь игрок должен подобрать снаряды, чтобы бросить снова.