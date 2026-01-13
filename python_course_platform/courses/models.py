from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Class(models.Model):
    """Класс учеников"""
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название класса')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_classes',
        verbose_name=_('Создан администратором')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Класс')
        verbose_name_plural = _('Классы')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_students_count(self):
        return self.students.count()
    get_students_count.short_description = _('Количество учеников')


class Topic(models.Model):
    """Тема курса (Переменные, Циклы, Классы и т.д.)"""
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название темы')
    )
    description = models.TextField(
        verbose_name=_('Описание темы')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок сортировки')
    )
    theory_content = models.TextField(
        blank=True,
        verbose_name=_('Теоретический материал')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Тема')
        verbose_name_plural = _('Темы')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_tasks_count(self):
        return self.tasks.count()
    get_tasks_count.short_description = _('Количество заданий')


class Task(models.Model):
    """Задание для практики"""
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('Тема')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название задания')
    )
    description = models.TextField(
        verbose_name=_('Описание задания')
    )
    hint = models.TextField(
        blank=True,
        verbose_name=_('Подсказка')
    )
    example_code = models.TextField(
        blank=True,
        verbose_name=_('Пример кода')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок в теме')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Задание')
        verbose_name_plural = _('Задания')
        ordering = ['topic', 'order', 'title']

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class TestCase(models.Model):
    """Тестовый случай для проверки задания"""

    class TestType(models.TextChoices):
        VARIABLE = 'variable', _('Проверка переменной')
        OUTPUT = 'output', _('Проверка вывода')
        CONTAINS = 'contains', _('Содержит текст')
        NO_ERROR = 'no_error', _('Без ошибок')

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name=_('Задание')
    )
    test_type = models.CharField(
        max_length=20,
        choices=TestType.choices,
        verbose_name=_('Тип теста')
    )
    variable_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Имя переменной')
    )
    expected_value = models.JSONField(
        verbose_name=_('Ожидаемое значение')
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_('Описание теста')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Тестовый случай')
        verbose_name_plural = _('Тестовые случаи')
        ordering = ['task', 'order']

    def __str__(self):
        return f"{self.task.title} - {self.description}"


class ClassTopicAccess(models.Model):
    """Доступ класса к теме"""
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        verbose_name=_('Класс')
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        verbose_name=_('Тема')
    )
    is_accessible = models.BooleanField(
        default=False,
        verbose_name=_('Доступ открыт')
    )
    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата открытия')
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Открыт администратором')
    )

    class Meta:
        verbose_name = _('Доступ к теме')
        verbose_name_plural = _('Доступ к темам')
        unique_together = ['class_obj', 'topic']

    def __str__(self):
        return f"{self.class_obj.name} - {self.topic.title}"


class StudentProgress(models.Model):
    """Прогресс ученика по заданиям"""

    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Не начато')
        IN_PROGRESS = 'in_progress', _('В процессе')
        COMPLETED = 'completed', _('Завершено')
        FAILED = 'failed', _('Не пройдено')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name=_('Ученик')
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name=_('Задание')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
        verbose_name=_('Статус')
    )
    attempts_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество попыток')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    best_score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Лучший результат (%)')
    )

    class Meta:
        verbose_name = _('Прогресс ученика')
        verbose_name_plural = _('Прогресс учеников')
        unique_together = ['student', 'task']

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"

    def update_progress(self, score):
        """Обновить прогресс после выполнения задания"""
        self.attempts_count += 1

        if score == 100:
            self.status = self.Status.COMPLETED
            if not self.completed_at:
                self.completed_at = models.timezone.now()
        elif score > 0:
            self.status = self.Status.IN_PROGRESS
        else:
            self.status = self.Status.FAILED

        if score > self.best_score:
            self.best_score = score

        self.save()


class CodeSubmission(models.Model):
    """Отправка кода учеником"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Ученик')
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name=_('Задание')
    )
    code = models.TextField(
        verbose_name=_('Код')
    )
    test_results = models.JSONField(
        default=dict,
        verbose_name=_('Результаты тестов')
    )
    score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Оценка (%)')
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Время отправки')
    )

    class Meta:
        verbose_name = _('Отправка кода')
        verbose_name_plural = _('Отправки кода')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.task.title} ({self.score}%)"