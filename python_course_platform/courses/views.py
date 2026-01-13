from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Class, Topic, Task, StudentProgress, ClassTopicAccess
from .forms import ClassForm, StudentForm, TopicForm, TaskForm, TestCaseForm, TopicAccessForm
from code_execution.services import CodeExecutionService

User = get_user_model()


class HomeView(TemplateView):
    """Главная страница платформы"""
    template_name = 'courses/home.html'

    def dispatch(self, request, *args, **kwargs):
        # Если пользователь не авторизован, перенаправляем на login
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('accounts:login') + '?next=/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_student():
            # Для учеников - доступные темы
            available_topics = Topic.objects.filter(
                classtopicaccess__class_obj=user.student_class,
                classtopicaccess__is_accessible=True,
                is_active=True
            ).distinct()

            # Получаем прогресс ученика
            student_progress = StudentProgress.objects.filter(
                student=user
            ).select_related('task', 'task__topic')

            # Создаем словарь прогресса по темам
            progress_by_topic = {}
            for progress in student_progress:
                topic_id = progress.task.topic_id
                if topic_id not in progress_by_topic:
                    progress_by_topic[topic_id] = {
                        'completed': 0,
                        'total': 0
                    }
                progress_by_topic[topic_id]['total'] += 1
                if progress.status == 'completed':
                    progress_by_topic[topic_id]['completed'] += 1

            # Добавляем информацию о прогрессе к каждой теме
            for topic in available_topics:
                topic.progress_info = progress_by_topic.get(topic.id, {'completed': 0, 'total': 0})

            context['available_topics'] = available_topics
            context['student_progress'] = student_progress
        elif user.is_teacher():
            # Для преподавателей - управляемые классы
            context['managed_classes'] = user.managed_classes.all()
            context['all_topics'] = Topic.objects.filter(is_active=True)

        return context


class ClassListView(LoginRequiredMixin, ListView):
    """Список классов"""
    model = Class
    template_name = 'courses/class_list.html'
    context_object_name = 'classes'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Class.objects.all()
        elif user.is_teacher():
            return user.managed_classes.all()
        else:
            # Ученик видит только свой класс
            return Class.objects.filter(students=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем количество доступных тем для каждого класса
        for class_obj in context['classes']:
            class_obj.available_topics_count = class_obj.classtopicaccess_set.filter(is_accessible=True).count()

        return context


class ClassCreateView(LoginRequiredMixin, CreateView):
    """Создание нового класса"""
    model = Class
    form_class = ClassForm
    template_name = 'courses/class_form.html'
    success_url = reverse_lazy('courses:class_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Класс "{form.instance.name}" успешно создан!')
        return super().form_valid(form)


class ClassUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование класса"""
    model = Class
    form_class = ClassForm
    template_name = 'courses/class_form.html'

    def get_success_url(self):
        return reverse_lazy('courses:class_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Класс "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)


class ClassDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о классе"""
    model = Class
    template_name = 'courses/class_detail.html'
    context_object_name = 'class_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        class_obj = self.object

        # Доступные темы для класса
        available_topics = Topic.objects.filter(
            classtopicaccess__class_obj=class_obj,
            classtopicaccess__is_accessible=True,
            is_active=True
        ).distinct()

        # Добавляем количество активных задач для каждой темы
        for topic in available_topics:
            topic.active_tasks_count = topic.tasks.filter(is_active=True).count()

        context['available_topics'] = available_topics

        # Общее количество доступных задач для класса
        context['total_available_tasks'] = sum(
            topic.active_tasks_count for topic in available_topics
        )

        # Все активные темы (для администраторов)
        if user.is_admin():
            all_topics = Topic.objects.filter(is_active=True)
            # Добавляем количество активных задач для каждой темы
            for topic in all_topics:
                topic.active_tasks_count = topic.tasks.filter(is_active=True).count()
            context['all_topics'] = all_topics

        # Студенты класса
        context['students'] = class_obj.students.all()

        # Прогресс студентов (только для администраторов)
        if user.is_admin():
            # Получаем прогресс всех студентов
            students_progress = StudentProgress.objects.filter(
                student__in=context['students']
            ).select_related('student', 'task')

            # Добавляем прогресс к каждому студенту как атрибут
            for student in context['students']:
                student.completed_tasks = [
                    progress for progress in students_progress
                    if progress.student == student
                ]

        return context


class ClassDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление класса (без удаления учеников)"""
    model = Class
    template_name = 'courses/class_confirm_delete.html'
    success_url = reverse_lazy('courses:class_list')
    context_object_name = 'class_obj'

    def get_queryset(self):
        # Администратор может удалять только свои классы
        return Class.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        # При удалении класса ученики остаются, но теряют связь с классом
        class_obj = self.get_object()
        # Получаем учеников этого класса перед удалением
        students = list(class_obj.students.all())

        # Удаляем класс
        response = super().delete(request, *args, **kwargs)

        # Для каждого ученика очищаем связь с классом
        for student in students:
            student.student_class = None
            student.save()

        messages.success(request, f'Класс "{class_obj.name}" удален. Ученики сохранены, но больше не привязаны к классу.')
        return response


class StudentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового ученика"""
    model = User
    form_class = StudentForm
    template_name = 'courses/student_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(created_by=self.request.user)
        return context

    def form_valid(self, form):
        # Получаем класс из POST данных
        class_id = self.request.POST.get('student_class')
        if class_id:
            try:
                student_class = Class.objects.get(pk=class_id, created_by=self.request.user)
                form.instance.student_class = student_class
            except Class.DoesNotExist:
                messages.error(self.request, 'Выбранный класс не существует или у вас нет прав на него.')
                return self.form_invalid(form)

        user = form.save()
        messages.success(self.request, f'Ученик "{user.get_full_name()}" успешно создан!')
        return redirect('courses:class_detail', pk=student_class.pk)


class ClassStudentManageView(LoginRequiredMixin, DetailView):
    """Управление учениками класса (добавление/удаление существующих учеников)"""
    model = Class
    template_name = 'courses/class_student_manage.html'
    context_object_name = 'class_obj'

    def get_queryset(self):
        return Class.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_obj = self.object

        # Текущие ученики класса
        context['current_students'] = class_obj.students.all()

        # Доступные ученики (не привязанные к классам или созданные этим администратором)
        context['available_students'] = User.objects.filter(
            role='student'
        ).exclude(
            student_class__isnull=False
        ).exclude(
            pk__in=context['current_students'].values_list('pk', flat=True)
        )

        return context


def add_student_to_class(request, class_pk, student_pk):
    """AJAX представление для добавления ученика в класс"""
    if not request.user.is_admin():
        return JsonResponse({'success': False, 'error': 'Недостаточно прав'})

    try:
        class_obj = Class.objects.get(pk=class_pk, created_by=request.user)
        student = User.objects.get(pk=student_pk, role='student')

        if student.student_class:
            return JsonResponse({'success': False, 'error': 'Ученик уже в другом классе'})

        student.student_class = class_obj
        student.save()

        return JsonResponse({
            'success': True,
            'student': {
                'id': student.pk,
                'name': student.get_full_name() or student.username,
                'email': student.email
            }
        })

    except (Class.DoesNotExist, User.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Класс или ученик не найден'})


def remove_student_from_class(request, class_pk, student_pk):
    """AJAX представление для удаления ученика из класса"""
    if not request.user.is_admin():
        return JsonResponse({'success': False, 'error': 'Недостаточно прав'})

    try:
        class_obj = Class.objects.get(pk=class_pk, created_by=request.user)
        student = User.objects.get(pk=student_pk, student_class=class_obj)

        student.student_class = None
        student.save()

        return JsonResponse({'success': True})

    except (Class.DoesNotExist, User.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Класс или ученик не найден'})


class TopicListView(LoginRequiredMixin, ListView):
    """Список тем"""
    model = Topic
    template_name = 'courses/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Topic.objects.filter(is_active=True)
        elif user.is_student():
            # Ученик видит только доступные темы
            return Topic.objects.filter(
                classtopicaccess__class_obj=user.student_class,
                classtopicaccess__is_accessible=True,
                is_active=True
            ).distinct()
        else:
            return Topic.objects.none()


class TopicDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о теме"""
    model = Topic
    template_name = 'courses/topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        topic = self.object

        # Задания темы
        context['tasks'] = topic.tasks.filter(is_active=True)

        # Прогресс ученика по заданиям
        if user.is_student():
            context['progress'] = {
                progress.task_id: progress
                for progress in StudentProgress.objects.filter(
                    student=user,
                    task__in=context['tasks']
                )
            }

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о задании"""
    model = Task
    template_name = 'courses/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        task = self.object

        # Проверяем доступ к заданию
        if user.is_student():
            has_access = ClassTopicAccess.objects.filter(
                class_obj=user.student_class,
                topic=task.topic,
                is_accessible=True
            ).exists()

            if not has_access:
                messages.error(self.request, 'У вас нет доступа к этому заданию.')
                return redirect('courses:home')

        # Прогресс ученика
        if user.is_student():
            context['progress'], created = StudentProgress.objects.get_or_create(
                student=user,
                task=task,
                defaults={'status': 'not_started'}
            )

        # Тестовые случаи (только для администраторов)
        if user.is_admin():
            context['test_cases'] = task.test_cases.all()

        return context


class ProgressView(LoginRequiredMixin, TemplateView):
    """Прогресс ученика"""
    template_name = 'courses/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_student():
            context['progress'] = StudentProgress.objects.filter(
                student=user
            ).select_related('task', 'task__topic')
        elif user.is_admin():
            # Администратор видит прогресс всех учеников
            context['all_progress'] = StudentProgress.objects.all().select_related(
                'student', 'task', 'task__topic'
            )

        return context


@login_required
def submit_code(request, task_id):
    """AJAX endpoint для отправки кода"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    task = get_object_or_404(Task, pk=task_id)
    code = request.POST.get('code', '')

    if not code.strip():
        return JsonResponse({'error': 'Код не может быть пустым'}, status=400)

    # Выполняем код и проверяем тесты
    execution_service = CodeExecutionService()
    result = execution_service.execute_and_test(code, task.test_cases.all())

    # Сохраняем результат выполнения
    from code_execution.models import CodeExecution
    execution = CodeExecution.objects.create(
        user=request.user,
        code=code,
        test_cases=[tc.id for tc in task.test_cases.all()],
        results=result,
        status='completed' if result.get('success') else 'failed',
        score=result.get('score', 0),
        execution_time=result.get('execution_time', 0)
    )

    # Обновляем прогресс ученика
    if request.user.is_student():
        progress, created = StudentProgress.objects.get_or_create(
            student=request.user,
            task=task
        )
        progress.update_progress(result.get('score', 0))

    return JsonResponse(result)


@login_required
def save_topic_access(request, class_id):
    """AJAX endpoint для сохранения доступа к темам класса"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    class_obj = get_object_or_404(Class, pk=class_id)
    selected_topics = request.POST.getlist('topics', [])

    # Получаем все активные темы
    all_topics = Topic.objects.filter(is_active=True)

    # Обновляем доступ для каждой темы
    for topic in all_topics:
        is_accessible = str(topic.pk) in selected_topics

        access, created = ClassTopicAccess.objects.get_or_create(
            class_obj=class_obj,
            topic=topic,
            defaults={'opened_by': request.user}
        )

        if access.is_accessible != is_accessible:
            access.is_accessible = is_accessible
            if access.is_accessible and not access.opened_at:
                access.opened_at = timezone.now()
                access.opened_by = request.user
            access.save()

    return JsonResponse({'success': True})


def toggle_topic_access(request, class_id, topic_id):
    """AJAX endpoint для изменения доступа к теме"""
    if not request.user.is_admin():
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)

    class_obj = get_object_or_404(Class, pk=class_id)
    topic = get_object_or_404(Topic, pk=topic_id)

    access, created = ClassTopicAccess.objects.get_or_create(
        class_obj=class_obj,
        topic=topic,
        defaults={'opened_by': request.user}
    )

    access.is_accessible = not access.is_accessible
    if access.is_accessible and not access.opened_at:
        access.opened_at = timezone.now()
        access.opened_by = request.user
    access.save()

    return JsonResponse({
        'is_accessible': access.is_accessible,
        'opened_at': access.opened_at.isoformat() if access.opened_at else None
    })