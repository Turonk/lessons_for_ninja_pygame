from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages


class LoginView(LoginView):
    """Вход в систему"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class LogoutView(LogoutView):
    """Выход из системы"""
    next_page = '/api/accounts/login/'


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['user'] = user

        if user.is_student():
            context['class_info'] = user.student_class
            context['progress_count'] = user.progress.count()
        elif user.is_admin():
            context['managed_classes'] = user.managed_classes.all()
            context['total_students'] = sum(cls.students.count() for cls in user.managed_classes.all())

        return context