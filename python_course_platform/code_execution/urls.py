from django.urls import path
from . import views

app_name = 'code_execution'

urlpatterns = [
    path('execute/', views.execute_code, name='execute_code'),
    path('history/', views.ExecutionHistoryView.as_view(), name='execution_history'),
]
