# Шаг 3: Доработка снарядов и лимит врагов

## Что мы делаем на этом шаге

Две геймплейные доработки:
1. Снаряд, лежащий на земле, **не убивает** врага — только летящий наносит урон
2. На экране одновременно может быть **максимум 5 врагов**

Для первой доработки мы используем штуку из Python, которая называется `@property`.
Ниже — полный урок на 20 минут.

---

## Урок: `@property` в Python (20 минут)

### Часть 1: Проблема (3 минуты)

Давайте представим, что мы делаем персонажа для игры.
У него есть здоровье — `hp`. Мы хотим знать, жив ли он.

```python
class Hero:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.is_alive = True    # жив? да!
```

Вроде бы всё нормально. Но вот что произойдёт в игре:

```python
hero = Hero("Котик")
hero.hp = 0              # здоровье кончилось...
print(hero.is_alive)     # True ?!?!
```

`hp` стало `0`, но `is_alive` по-прежнему `True`. Почему?

Потому что `is_alive` — это **обычная переменная**. Она была установлена один
раз в `__init__` и больше никогда не менялась. Она не знает, что `hp` изменился.
Переменная не следит за другими переменными — она просто хранит то, что в неё
положили.

Чтобы это работало правильно, нам пришлось бы **каждый раз вручную** обновлять
`is_alive`:

```python
hero.hp -= 30
if hero.hp <= 0:
    hero.is_alive = False   # не забудь обновить!

hero.hp -= 50
if hero.hp <= 0:
    hero.is_alive = False   # и тут не забудь!

hero.hp -= 20
if hero.hp <= 0:
    hero.is_alive = False   # и тут тоже!
```

Это утомительно и легко забыть. Один раз забудешь — и герой с нулевым здоровьем
будет считаться живым. Баг!

**Нужен способ, чтобы `is_alive` вычислялся автоматически.**

---

### Часть 2: Решение — метод (2 минуты)

Первая идея — сделать метод:

```python
class Hero:
    def __init__(self, name):
        self.name = name
        self.hp = 100

    def is_alive(self):
        return self.hp > 0
```

Теперь `is_alive()` каждый раз считает заново:

```python
hero = Hero("Котик")
print(hero.is_alive())   # True  (hp = 100 > 0)

hero.hp = 0
print(hero.is_alive())   # False (hp = 0, не > 0)
```

Работает! Но есть неудобство: нужны **скобки** `()`.

Сравни:
- `hero.hp` — без скобок (это переменная)
- `hero.name` — без скобок (это переменная)
- `hero.is_alive()` — со скобками (это метод)

Выглядит непоследовательно. `is_alive` — это характеристика героя, такая же
как `hp` или `name`. Хотелось бы писать `hero.is_alive` без скобок.

---

### Часть 3: `@property` — метод, который притворяется переменной (3 минуты)

Вот тут и помогает `@property`:

```python
class Hero:
    def __init__(self, name):
        self.name = name
        self.hp = 100

    @property
    def is_alive(self):
        return self.hp > 0
```

Что изменилось? Только одна строка: добавили `@property` перед `def`.

Теперь:

```python
hero = Hero("Котик")
print(hero.is_alive)    # True   — без скобок!

hero.hp = 0
print(hero.is_alive)    # False  — обновилось автоматически!
```

**Что делает `@property`:**
- Снаружи `is_alive` выглядит как обычная переменная — без скобок
- Внутри это метод — он вычисляет результат каждый раз, когда к нему обращаются

Это как **умная переменная**: ты спрашиваешь у неё значение, а она не просто
вспоминает, что было записано, а **вычисляет ответ прямо сейчас**.

#### Аналогия

Представь два способа узнать температуру на улице:

**Обычная переменная** — это записка на холодильнике: «Утром было +15°».
Ты записал утром и весь день смотришь на одну и ту же записку.
Даже если на улице уже +25°, записка покажет +15°.

**Property** — это термометр за окном.
Каждый раз, когда ты смотришь на него, он показывает **текущую** температуру.
Тебе не нужно ничего обновлять — он делает это сам.

`@property` превращает переменную из «записки» в «термометр».

---

### Часть 4: Пример — телефон (3 минуты)

Давайте сделаем класс телефона. У него есть заряд батареи,
и мы хотим знать его статус:

```python
class Phone:
    def __init__(self, model, battery=100):
        self.model = model
        self.battery = battery    # заряд в процентах (0-100)

    @property
    def status(self):
        """Текстовый статус батареи — вычисляется по текущему заряду."""
        if self.battery > 50:
            return "Заряжен"
        elif self.battery > 20:
            return "Средний заряд"
        elif self.battery > 0:
            return "Мало заряда!"
        else:
            return "Разряжен"

    @property
    def is_dead(self):
        """Телефон полностью разряжен?"""
        return self.battery <= 0
```

Тестируем:

```python
phone = Phone("iPhone", 75)
print(phone.model)      # "iPhone"      — обычная переменная
print(phone.battery)    # 75            — обычная переменная
print(phone.status)     # "Заряжен"     — property!
print(phone.is_dead)    # False         — property!
```

Всё читается одинаково — без скобок. Но `status` и `is_dead` вычисляются
каждый раз заново.

```python
phone.battery = 10
print(phone.status)     # "Мало заряда!"  — обновилось!

phone.battery = 0
print(phone.status)     # "Разряжен"      — обновилось!
print(phone.is_dead)    # True             — обновилось!
```

Мы **ни разу** не писали `phone.status = "..."` — property сам вычислил
правильный текст по текущему заряду.

**Запомни правило:** если значение зависит от других переменных — это property.
Если значение задаётся один раз — это обычная переменная.

| Что | Тип | Почему |
|-----|-----|--------|
| `model` | переменная | Модель не меняется от заряда |
| `battery` | переменная | Задаётся и меняется напрямую |
| `status` | property | Зависит от `battery` |
| `is_dead` | property | Зависит от `battery` |

---

### Часть 5: Property может использовать другой property (2 минуты)

Property — это обычное значение снаружи. Значит, один property может
использовать другой:

```python
class Player:
    def __init__(self):
        self.hp = 100
        self.energy = 50

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def can_fight(self):
        # Используем is_alive (другой property) как обычную переменную!
        return self.is_alive and self.energy > 10
```

```python
player = Player()
print(player.can_fight)   # True  (жив и энергия > 10)

player.energy = 5
print(player.can_fight)   # False (энергии мало)

player.hp = 0
print(player.can_fight)   # False (мёртв)
```

`can_fight` вызывает `is_alive`, а `is_alive` проверяет `hp`.
Цепочка вычислений, и всё работает автоматически.

---

### Часть 6: Как мы используем это в игре (2 минуты)

В нашей игре есть снаряд (`Projectile`). У него три состояния:
- **Летит** — активен и двигается
- **Лежит** — застрял в земле, можно подобрать
- **Исчез** — деактивирован после подбора или попадания

Мы хотим знать: может ли снаряд нанести урон врагу?

Ответ: только если он **активен** (`active`) и **не лежит** (`not stuck`).

```python
class Projectile:
    def __init__(self, ...):
        self.active = True
        self.stuck = False
        ...

    @property
    def can_damage(self):
        """Может ли снаряд нанести урон?
        Только активный летящий снаряд наносит урон.
        Застрявший в земле — безопасный, его можно только подобрать."""
        return self.active and not self.stuck
```

В игровом цикле мы проверяем столкновение снаряда с врагом:

```python
# Только летящий снаряд убивает врага
if projectile.can_damage and check_collisions(projectile.rect, enemy.rect):
    projectile.reset()
    enemies.remove(enemy)
```

Без property пришлось бы писать условие прямо здесь:
```python
if projectile.active and not projectile.stuck and check_collisions(...):
```

Это длинно и непонятно. А `projectile.can_damage` — сразу ясно, что проверяем.

---

### Часть 7: Шпаргалка (1 минута)

```
ОБЫЧНАЯ ПЕРЕМЕННАЯ          @property
──────────────────          ─────────
self.name = "Котик"         @property
                            def is_alive(self):
                                return self.hp > 0

Хранит значение             Вычисляет значение
Записал — и оно там         Каждый раз считает заново
Нужно обновлять вручную     Обновляется автоматически
hero.name                   hero.is_alive
```

**Когда использовать property:**
- Значение **зависит** от других переменных
- Значение может **устареть**, если забыть обновить
- Значение можно **вычислить** из того, что уже есть

**Когда использовать обычную переменную:**
- Значение **задаётся напрямую** (имя, размер, скорость)
- Значение **не зависит** от других переменных

---

### Часть 8: Задания (4 минуты)

#### Задание 1: NinjaCat

Создай класс `NinjaCat` с тремя property:

```python
class NinjaCat:
    def __init__(self, name, hp, energy):
        self.name = name
        self.hp = hp           # здоровье (0-100)
        self.energy = energy   # энергия (0-100)

    @property
    def is_alive(self):
        # Верни True если hp больше 0
        pass

    @property
    def can_attack(self):
        # Верни True если жив И энергия больше 10
        # Подсказка: можно использовать self.is_alive
        pass

    @property
    def status(self):
        # Верни текст:
        # "Мёртв" — если hp <= 0
        # "Устал" — если энергия <= 10
        # "Готов к бою!" — в остальных случаях
        pass
```

**Проверь себя:**
```python
cat = NinjaCat("Шурик", 100, 50)
print(cat.is_alive)     # True
print(cat.can_attack)   # True
print(cat.status)       # "Готов к бою!"

cat.energy = 5
print(cat.can_attack)   # False
print(cat.status)       # "Устал"

cat.hp = 0
print(cat.is_alive)     # False
print(cat.status)       # "Мёртв"
```

<details>
<summary><b>Решение</b> (попробуй сам, потом смотри!)</summary>

```python
class NinjaCat:
    def __init__(self, name, hp, energy):
        self.name = name
        self.hp = hp
        self.energy = energy

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def can_attack(self):
        return self.is_alive and self.energy > 10

    @property
    def status(self):
        if self.hp <= 0:
            return "Мёртв"
        elif self.energy <= 10:
            return "Устал"
        else:
            return "Готов к бою!"
```

Обрати внимание: `can_attack` использует `self.is_alive` — один property
вызывает другой!

</details>

---

#### Задание 2 (бонусное): GameCharacter

Этот класс посложнее — для тех, кто справился быстро.

```python
class GameCharacter:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

    @property
    def power_level(self):
        # Верни сумму attack + defense
        # Если не жив — верни 0
        pass

    @property
    def rank(self):
        # "Мёртв" — если hp <= 0
        # "Новичок" — если power_level < 30
        # "Воин" — если power_level от 30 до 59
        # "Мастер" — если power_level 60 и больше
        pass

    @property
    def battle_cry(self):
        # Составь строку: "{name} [{rank}] — Сила: {power_level}"
        # Пример: "Котик [Воин] — Сила: 45"
        pass
```

**Проверь себя:**
```python
char = GameCharacter("Котик", 100, 25, 20)
print(char.power_level)   # 45
print(char.rank)           # "Воин"
print(char.battle_cry)     # "Котик [Воин] — Сила: 45"

char.attack = 40
print(char.rank)           # "Мастер"
print(char.battle_cry)     # "Котик [Мастер] — Сила: 60"

char.hp = 0
print(char.power_level)   # 0
print(char.rank)           # "Мёртв"
print(char.battle_cry)     # "Котик [Мёртв] — Сила: 0"
```

<details>
<summary><b>Решение</b></summary>

```python
class GameCharacter:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

    @property
    def power_level(self):
        if self.hp <= 0:
            return 0
        return self.attack + self.defense

    @property
    def rank(self):
        if self.hp <= 0:
            return "Мёртв"
        elif self.power_level < 30:
            return "Новичок"
        elif self.power_level < 60:
            return "Воин"
        else:
            return "Мастер"

    @property
    def battle_cry(self):
        return f"{self.name} [{self.rank}] — Сила: {self.power_level}"
```

Здесь все три property связаны:
- `rank` использует `power_level`
- `battle_cry` использует `rank` и `power_level`
- Измени `attack` — и все три обновятся автоматически!

</details>

---

## Изменение 1: Снаряд на земле не наносит урон

### Проблема

Раньше любой снаряд при пересечении с врагом убивал его — даже тот, который
застрял в полу и просто лежит. Враг наступал на лежащий снаряд и погибал.

### Пошаговые изменения в коде

#### Шаг А: Добавляем property `can_damage` в класс `Projectile`

Открываем `game.py`, находим класс `Projectile`. После `self.gravity = 0.6`
в `__init__` и **перед** методом `def update(self)` вставляем:

```python
    @property
    def can_damage(self):
        """Может ли снаряд нанести урон?
        Только если он активен и НЕ лежит на земле.
        Снаряд застрявший в полу — это просто предмет для подбора.
        """
        return self.active and not self.stuck
```

Это property, которое каждый раз вычисляет ответ: снаряд опасен, только если
он `active` (существует) и `not stuck` (не лежит на земле).

#### Шаг Б: Меняем проверку столкновений в игровом цикле

Находим блок `# Столкновение снаряд-враг` внутри цикла `for enemy in enemies[:]`.

Было:
```python
        for projectile in projectiles:
            if check_collisions(projectile.rect, enemy.rect):
                projectile.reset()
                enemies.remove(enemy)
                break
```

Добавляем `projectile.can_damage and` перед `check_collisions`:
```python
        # Столкновение снаряд-враг (только летящие снаряды наносят урон!)
        for projectile in projectiles:
            if projectile.can_damage and check_collisions(projectile.rect, enemy.rect):
                projectile.reset()
                enemies.remove(enemy)
                break
```

Теперь лежащий снаряд (`can_damage = False`) пропускается, и враг проходит мимо.

#### Шаг В: Меняем отрисовку снаряда — визуальная разница

Находим метод `draw` класса `Projectile`.

Было (все снаряды одного цвета):
```python
    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, RED, self.rect)
```

Стало (летящий яркий, лежащий тёмный):
```python
    def draw(self, surface):
        """Рисует снаряд. Застрявший — тёмный, летящий — красный."""
        if not self.active:
            return

        if self.stuck:
            # Застрявший снаряд — приглушённый цвет
            pygame.draw.rect(surface, (150, 50, 50), self.rect)
        else:
            # Летящий снаряд — яркий красный
            pygame.draw.rect(surface, RED, self.rect)
```

Зачем: игрок визуально видит — яркий = опасный, тёмный = просто подбери.

---

## Изменение 2: Максимум 5 врагов на экране

### Пошаговые изменения в коде

#### Шаг А: Добавляем константу в `enemy.py`

Открываем `enemy.py`, находим строку `SPAWN_DELAY = 180`. Под ней добавляем:

```python
MAX_ENEMIES = 5     # Максимум врагов на экране одновременно
```

#### Шаг Б: Импортируем константу в `game.py`

Находим строку импорта:
```python
from enemy import Enemy, ENEMY_HEIGHT, ENEMY_WIDTH, SPAWN_DELAY
```

Добавляем `MAX_ENEMIES`:
```python
from enemy import Enemy, ENEMY_HEIGHT, ENEMY_WIDTH, SPAWN_DELAY, MAX_ENEMIES
```

#### Шаг В: Добавляем проверку при спавне

Находим блок спавна врагов:
```python
    if spawn_timer >= SPAWN_DELAY:
```

Добавляем второе условие:
```python
    if spawn_timer >= SPAWN_DELAY and len(enemies) < MAX_ENEMIES:
```

Теперь если врагов уже 5 — новый не появится, пока кого-то не убьют
или он не уйдёт за экран.

#### Шаг Г: Добавляем счётчик врагов на HUD

Находим блок `# --- HUD ---`. После строки `screen.blit(count_text, (10, 10))`
добавляем:

```python
    enemy_text = font.render(f"Врагов: {len(enemies)} / {MAX_ENEMIES}", True, (0, 0, 255))
    screen.blit(enemy_text, (10, 40))
```

Теперь игрок видит: `Врагов: 3 / 5` — сколько есть и сколько максимум.

---

## Итог изменений

| Файл | Что изменилось |
|------|---------------|
| `enemy.py` | Константа `MAX_ENEMIES = 5` |
| `game.py` | Property `Projectile.can_damage` |
| `game.py` | `Projectile.draw()` — разный цвет для летящих и лежащих снарядов |
| `game.py` | Спавн проверяет `len(enemies) < MAX_ENEMIES` |
| `game.py` | HUD: счётчик врагов |

---

## Файлы в этом шаге

```
step_3_projectile_and_enemies/
├── enemy.py     — добавлена константа MAX_ENEMIES
├── game.py      — can_damage, визуал снарядов, лимит врагов, HUD
└── changes.md   — этот файл (урок + описание изменений)
```

## Следующий шаг

**Шаг 4** — Система жизней: 3 HP, отбрасывание при ударе, отображение на экране.
