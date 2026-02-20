# Шаг 4: Визуал — фон, земля, спрайты врагов

## Что мы делаем на этом шаге

Всё загружается из файлов через `AssetLoader`. Нет файла — заглушка:
1. **Небо** — `assets/sky.png` (заглушка: заливка голубым цветом)
2. **Земля** — `assets/ground.png` (заглушка: заливка коричневым цветом)
3. **Враги** — `assets/enemy.png` (заглушка: серый прямоугольник с глазиком)

Подход единый: положил картинку в `assets/` — перезапустил — работает.

---

## Изменение 1: Новый метод `load_background()` в AssetLoader

### Зачем

У нас уже есть `load_image()` — он загружает спрайты персонажей. Но для фонов
его заглушка (серый прямоугольник с глазиком) не подходит. Для неба нужна
голубая заливка, для земли — коричневая.

### Пошаговые изменения

#### Шаг А: Добавляем цвета-заглушки в константы

В блок `# ===== КОНСТАНТЫ ЦВЕТА =====` добавляем:

```python
SKY_BLUE = (135, 200, 235)       # Цвет неба (заглушка, если нет sky.png)
GROUND_COLOR = (100, 70, 40)     # Цвет земли (заглушка, если нет ground.png)
```

#### Шаг Б: Добавляем метод `load_background()` в класс `AssetLoader`

После метода `load_image()` добавляем:

```python
    def load_background(self, path, width, height, fallback_color):
        """Загружает фоновое изображение или создаёт заливку цветом."""
        try:
            image = pygame.image.load(path).convert()
            return pygame.transform.scale(image, (width, height))
        except (FileNotFoundError, pygame.error):
            print(f"Файл не найден: {path}. Используем заливку цветом.")
            surface = pygame.Surface((width, height))
            surface.fill(fallback_color)
            return surface
```

Отличия от `load_image()`:
- `.convert()` вместо `.convert_alpha()` — фонам не нужна прозрачность
- Заглушка — просто заливка цветом `fallback_color`, а не прямоугольник с глазиком
- Принимает `fallback_color` — каждый фон может иметь свой цвет заглушки

#### Шаг В: Загружаем фоны в `load_all()`

В конец метода `load_all()` добавляем:

```python
        # Фоны: небо и земля
        ground_height = SCREEN_HEIGHT - GROUND_Y
        self.sprites["sky"] = self.load_background("assets/sky.png", SCREEN_WIDTH, SCREEN_HEIGHT, SKY_BLUE)
        self.sprites["ground"] = self.load_background("assets/ground.png", SCREEN_WIDTH, ground_height, GROUND_COLOR)
```

Небо — размером во весь экран. Земля — полоса высотой 100 пикселей (от `GROUND_Y` до низа).

### Что объяснить ученикам

> **Два метода загрузки — зачем?**
>
> `load_image()` — для персонажей. Заглушка с глазиком, прозрачный фон.
> `load_background()` — для фонов. Заглушка — заливка цветом, без прозрачности.
>
> Можно было бы всё сделать одним методом, но тогда он стал бы сложным
> и запутанным. Лучше два простых метода, чем один сложный.

---

## Изменение 2: Отрисовка фона в игровом цикле

### Пошаговые изменения

#### Шаг А: Достаём фоны из AssetLoader при инициализации

После создания `asset_loader` добавляем:

```python
enemy_sprite = asset_loader.get("enemy")
sky_surface = asset_loader.get("sky")
ground_surface = asset_loader.get("ground")
```

#### Шаг Б: Меняем отрисовку в игровом цикле

Было:
```python
    screen.fill(WHITE)
    pygame.draw.line(screen, RED, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
```

Стало:
```python
    screen.blit(sky_surface, (0, 0))               # Небо
    screen.blit(ground_surface, (0, GROUND_Y))     # Земля
```

Красная линия больше не нужна — вместо неё полноценная поверхность земли.

---

## Изменение 3: Спрайты врагов

### Пошаговые изменения

#### Шаг А: В `load_all()` — загрузка спрайта врага

Добавляем строку (уже через существующий `load_image()`):

```python
        self.sprites["enemy"] = self.load_image("assets/enemy.png", ENEMY_WIDTH, ENEMY_HEIGHT)
```

#### Шаг Б: `Enemy.__init__` принимает спрайт

Было:
```python
def __init__(self, x, y):
```

Стало:
```python
def __init__(self, x, y, sprite=None):
    ...
    self.sprite = sprite
```

#### Шаг В: `Enemy.draw()` — спрайт с отражением

Было:
```python
def draw(self, surface):
    pygame.draw.rect(surface, (0, 0, 255), self.rect)
```

Стало:
```python
def draw(self, surface):
    if self.sprite:
        if self.direction == -1:
            flipped = pygame.transform.flip(self.sprite, True, False)
            surface.blit(flipped, (self.x, self.y))
        else:
            surface.blit(self.sprite, (self.x, self.y))
    else:
        pygame.draw.rect(surface, (0, 0, 255), self.rect)
```

Если спрайт есть — рисуем с отражением. Если нет — квадрат как раньше.

#### Шаг Г: При спавне — передаём спрайт

Было:
```python
new_enemy = Enemy(en_x, en_y)
```

Стало:
```python
new_enemy = Enemy(en_x, en_y, sprite=enemy_sprite)
```

### Что объяснить ученикам

> **Как добавить свои картинки?**
>
> 1. Нарисуй или найди картинки (PNG лучше всего)
> 2. Сохрани в папку `assets/`:
>    - `sky.png` — фон неба (800 x 600 пикселей)
>    - `ground.png` — полоса земли (800 x 100 пикселей)
>    - `enemy.png` — враг (50 x 50 пикселей)
> 3. Перезапусти игру — `AssetLoader` подхватит файлы автоматически!
>
> Пока файлов нет — игра работает с заглушками.

---

## Изменение 4: Цвет текста HUD

Фон теперь голубой — синий текст плохо видно. Меняем на чёрный `BLACK`:

```python
count_text = font.render(f"Снарядов: {active_count}", True, BLACK)
enemy_text = font.render(f"Врагов: {len(enemies)} / {MAX_ENEMIES}", True, BLACK)
```

---

## Итог изменений

| Файл | Что изменилось |
|------|---------------|
| `game.py` | `AssetLoader.load_background()` — новый метод для фонов |
| `game.py` | `load_all()` загружает `sky`, `ground`, `enemy` |
| `game.py` | Фон: `blit(sky)` + `blit(ground)` вместо `fill(WHITE)` + линия |
| `game.py` | `SKY_BLUE`, `GROUND_COLOR` — цвета-заглушки |
| `game.py` | HUD: цвет текста `BLACK` |
| `enemy.py` | `Enemy.__init__` принимает `sprite=None` |
| `enemy.py` | `Enemy.draw()` — спрайт с отражением или квадрат как fallback |

---

## Файлы в этом шаге

```
step_4_visuals/
├── enemy.py     — поддержка спрайтов в классе Enemy
├── game.py      — загрузка фонов и спрайтов через AssetLoader
└── changes.md   — этот файл
```

## Как добавить свои картинки

Положи файлы в папку `assets/`:

| Файл | Размер | Описание |
|------|--------|----------|
| `sky.png` | 800 x 600 | Фон неба (весь экран) |
| `ground.png` | 800 x 100 | Полоса земли |
| `enemy.png` | 50 x 50 | Спрайт врага |
| `idle.png` | 50 x 50 | Игрок стоит |
| `walk.png` | 50 x 50 | Игрок бежит |
| `jump.png` | 50 x 50 | Игрок прыгает |
| `projectile.png` | 24 x 24 | Снаряд |

## Следующий шаг

**Шаг 5** — Система жизней: 3 HP, отбрасывание при ударе, отображение на экране.
