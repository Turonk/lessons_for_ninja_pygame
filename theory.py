"""
Урок по ООП (Объектно-Оrientированное Программирование) на Python

Содержание:
1. Создание классов
2. Атрибуты и методы
3. Наследование
4. Инкапсуляция
5. Полиморфизм
6. Практические задания
"""

# 1. Создание классов
# Класс — это шаблон для создания объектов.
# Пример: создадим класс `Car`

class Car:
    # Конструктор класса (специальный метод __init__)
    def __init__(self, brand, model, year):
        self.brand = brand    # атрибут экземпляра
        self.model = model
        self.year = year

    # Метод экземпляра
    def start_engine(self):
        print(f"{self.brand} {self.model} завел двигатель.")

    def get_info(self):
        return f"{self.year} {self.brand} {self.model}"


# Пример использования
my_car = Car("Toyota", "Camry", 2020)
my_car.start_engine()
print(my_car.get_info())


# 2. Атрибуты и методы
# Атрибуты бывают:
# - экземпляра (уникальны для каждого объекта)
# - класса (общие для всех экземпляров)

class Dog:
    species = "Canis lupus"  # атрибут класса

    def __init__(self, name, age):
        self.name = name      # атрибут экземпляра
        self.age = age

    def bark(self):  # метод экземпляра
        print(f"{self.name} лает: Гав!")

    @classmethod
    def get_species(cls):
        return cls.species

    @staticmethod
    def info():
        print("Собаки — лучшие друзья человека!")


# Примеры
dog1 = Dog("Шарик", 5)
dog2 = Dog("Бобик", 3)

print(dog1.name, dog2.name)
print(Dog.get_species())  # вызов метода класса
Dog.info()                # вызов статического метода


# 3. Наследование
# Позволяет одному классу (потомку) наследовать атрибуты и методы другого (родителя)

class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Метод должен быть переопределён в подклассе")


class Cat(Animal):
    def speak(self):
        return f"{self.name} говорит: Мяу!"


class Dog(Animal):
    def speak(self):
        return f"{self.name} говорит: Гав!"


# Пример
cat = Cat("Мурка")
dog = Dog("Тузик")
print(cat.speak())
print(dog.speak())


# 4. Инкапсуляция
# Скрытие внутренних данных объекта. В Python:
# _ — защищённый (для разработчиков, не запрещает доступ)
# __ — приватный (усиленная защита имени)

class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance  # приватный атрибут

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            print(f"Пополнено: {amount}")

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            print(f"Снято: {amount}")
        else:
            print("Недостаточно средств")

    def get_balance(self):
        return self.__balance


# Пример
acc = BankAccount("Иван", 1000)
acc.deposit(500)
acc.withdraw(200)
print(f"Баланс: {acc.get_balance()}")
# print(acc.__balance)  # Ошибка! Атрибут приватный


# 5. Полиморфизм
# Один интерфейс — разные реализации

def animal_sound(animal):
    print(animal.speak())

# Работает с любым объектом, у которого есть метод speak()
animal_sound(cat)
animal_sound(dog)


# 6. Практические задания

"""
Задача 1:
Создайте класс `Rectangle` с атрибутами `width` и `height`.
Добавьте метод `area()`, возвращающий площадь.

Задача 2:
Создайте класс `Person` с атрибутами `name` и `age`.
Переопределите метод `__str__`, чтобы он возвращал строку вида "Имя: ..., Возраст: ...".

Задача 3:
Создайте класс `Student`, унаследованный от `Person`.
Добавьте атрибут `student_id` и метод `enroll(course)`.

Задача 4:
В классе `Student` сделайте атрибут `grades` приватным.
Добавьте методы `add_grade(оценка)` и `get_average_grade()`.

Задача 5:
Создайте функцию `introduce(person)`, которая вызывает метод `introduce()` у любого объекта.
Создайте два класса: `Teacher` и `Student`, реализующие этот метод по-разному.
"""


# --- Решения заданий (можно раскомментировать для проверки) ---

# Задача 1
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


# Задача 2
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Имя: {self.name}, Возраст: {self.age}"


# Задача 3
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
        self.__grades = []

    def enroll(self, course):
        print(f"{self.name} записан на курс: {course}")

    # Задача 4
    def add_grade(self, grade):
        if 1 <= grade <= 10:
            self.__grades.append(grade)
        else:
            print("Оценка должна быть от 1 до 10")

    def get_average_grade(self):
        if self.__grades:
            return sum(self.__grades) / len(self.__grades)
        return 0


# Задача 5
class Teacher(Person):
    def introduce(self):
        return f"Меня зовут {self.name}, я преподаватель."

    def __str__(self):
        return super().__str__()


class Student(Person):
    def introduce(self):
        return f"Привет, я {self.name}, студент."

    def __str__(self):
        return super().__str__()


def introduce(person):
    print(person.introduce())


# Пример использования
if __name__ == "__main__":
    # Проверка задач
    rect = Rectangle(5, 10)
    print("Площадь прямоугольника:", rect.area())

    p = Person("Анна", 25)
    print(p)

    s = Student("Петя", 20, "S123")
    s.enroll("Python")
    s.add_grade(8)
    s.add_grade(9)
    print("Средний балл:", s.get_average_grade())

    t = Teacher("Мария", 40)
    introduce(t)
    introduce(s)
