from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CodeExecution(models.Model):
    """Результат выполнения кода"""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает')
        RUNNING = 'running', _('Выполняется')
        COMPLETED = 'completed', _('Завершено')
        FAILED = 'failed', _('Ошибка')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    code = models.TextField(
        verbose_name=_('Код для выполнения')
    )
    test_cases = models.JSONField(
        default=list,
        verbose_name=_('Тестовые случаи')
    )
    results = models.JSONField(
        default=dict,
        verbose_name=_('Результаты выполнения')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Статус')
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Оценка (%)')
    )
    execution_time = models.FloatField(
        default=0.0,
        verbose_name=_('Время выполнения (сек)')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Время создания')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время завершения')
    )

    class Meta:
        verbose_name = _('Выполнение кода')
        verbose_name_plural = _('Выполнения кода')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.score}%)"