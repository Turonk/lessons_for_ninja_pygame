from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя"""

    class Role(models.TextChoices):
        STUDENT = 'student', _('Ученик')
        TEACHER = 'teacher', _('Преподаватель')
        ADMIN = 'admin', _('Администратор')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Роль')
    )

    # Поля для учеников
    student_class = models.ForeignKey(
        'courses.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name=_('Класс')
    )

    # Поля для преподавателей/админов
    managed_classes = models.ManyToManyField(
        'courses.Class',
        related_name='administrators',
        blank=True,
        verbose_name=_('Управляемые классы')
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_teacher(self):
        return self.role in [self.Role.TEACHER, self.Role.ADMIN]

    def is_student(self):
        return self.role == self.Role.STUDENT