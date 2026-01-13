from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .services import CodeExecutionService
from .models import CodeExecution


@login_required
@require_POST
def execute_code(request):
    """
    API endpoint для выполнения кода.
    """
    code = request.POST.get('code', '')
    if not code.strip():
        return JsonResponse({
            'success': False,
            'error': 'Код не может быть пустым'
        }, status=400)

    # Выполняем код
    service = CodeExecutionService()
    result = service.execute_code(code)

    # Сохраняем результат в базу данных
    execution = CodeExecution.objects.create(
        user=request.user,
        code=code,
        results=result,
        status='completed' if result['success'] else 'failed',
        score=100 if result['success'] else 0,  # Простая оценка
        execution_time=0.0  # Пока не измеряем время
    )

    return JsonResponse({
        'success': result['success'],
        'output': result.get('output', ''),
        'error': result.get('error', ''),
        'variables': result.get('variables', {}),
        'execution_id': execution.id
    })


class ExecutionHistoryView(ListView):
    """История выполнения кода"""
    model = CodeExecution
    template_name = 'code_execution/history.html'
    context_object_name = 'executions'
    paginate_by = 20

    def get_queryset(self):
        return CodeExecution.objects.filter(user=self.request.user).order_by('-created_at')