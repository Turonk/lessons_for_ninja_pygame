from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),

    # Классы
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/edit/', views.ClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/delete/', views.ClassDeleteView.as_view(), name='class_delete'),
    path('classes/<int:pk>/students/', views.ClassStudentManageView.as_view(), name='class_student_manage'),

    # Ученики
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),

    # Темы
    path('topics/', views.TopicListView.as_view(), name='topic_list'),
    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),

    # Задания
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),

    # Прогресс
    path('progress/', views.ProgressView.as_view(), name='progress'),

    # API endpoints для AJAX
    path('api/tasks/<int:task_id>/submit/', views.submit_code, name='submit_code'),
    path('api/classes/<int:class_id>/topics/access/', views.save_topic_access, name='save_topic_access'),
    path('api/classes/<int:class_id>/topics/<int:topic_id>/access/', views.toggle_topic_access, name='toggle_topic_access'),

    # AJAX endpoints для управления учениками
    path('classes/<int:class_pk>/students/<int:student_pk>/add/', views.add_student_to_class, name='add_student_to_class'),
    path('classes/<int:class_pk>/students/<int:student_pk>/remove/', views.remove_student_from_class, name='remove_student_from_class'),
]
