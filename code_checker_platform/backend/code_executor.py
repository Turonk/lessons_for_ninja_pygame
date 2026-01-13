"""
Безопасное выполнение Python кода для проверки заданий.
"""
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.PrintCollector import PrintCollector


class CodeExecutor:
    """
    Класс для безопасного выполнения Python кода.
    Ограничивает доступ к опасным операциям.
    """
    
    # Разрешённые встроенные функции
    ALLOWED_BUILTINS = {
        'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 
        'tuple', 'set', 'range', 'enumerate', 'zip', 'max', 'min', 'sum',
        'abs', 'round', 'sorted', 'reversed', 'type', 'isinstance',
        'hasattr', 'getattr', 'setattr', 'delattr', 'dir', 'vars',
        'all', 'any', 'map', 'filter', 'iter', 'next'
    }
    
    def __init__(self, timeout=5):
        """
        Инициализация исполнителя кода.
        
        Args:
            timeout: Максимальное время выполнения в секундах
        """
        self.timeout = timeout
        self.safe_builtins = {
            name: func for name, func in safe_builtins.items()
            if name in self.ALLOWED_BUILTINS
        }
    
    def execute(self, code, context=None):
        """
        Безопасно выполняет Python код.
        
        Args:
            code: Строка с Python кодом
            context: Словарь с начальными переменными (опционально)
        
        Returns:
            dict: {
                'success': bool,
                'output': str,
                'error': str или None,
                'variables': dict,
                'traceback': str или None
            }
        """
        # Перехватываем вывод
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Начальный контекст
        if context is None:
            context = {}
        
        # Создаём безопасное окружение
        # RestrictedPython требует _print_ для работы функции print
        # и других "стражей" (_getattr_, _setattr_ и т.д.)
        
        # Создаём безопасное окружение с необходимыми "стражами"
        restricted_globals = safe_globals.copy()
        restricted_globals['__builtins__'] = {
            name: func for name, func in safe_builtins.items()
            if name in self.ALLOWED_BUILTINS
        }
        restricted_globals['_print_'] = PrintCollector

        # Добавляем базовые стражи для работы с атрибутами и элементами
        # Эти функции обеспечивают безопасный доступ к объектам
        def safe_getattr(obj, name):
            if isinstance(obj, (list, tuple, dict, str, int, float, bool)):
                try:
                    return getattr(obj, name)
                except AttributeError:
                    raise AttributeError(f"'{type(obj).__name__}' object has no attribute '{name}'")
            else:
                raise AttributeError(f"Access to attribute '{name}' not allowed")

        def safe_setattr(obj, name, value):
            if isinstance(obj, list):
                if name in ['append', 'extend', 'insert', 'remove', 'pop', 'clear', 'sort', 'reverse']:
                    setattr(obj, name, value)
                else:
                    raise AttributeError(f"Setting attribute '{name}' not allowed")
            else:
                raise AttributeError(f"Setting attribute '{name}' not allowed")

        def safe_getitem(obj, key):
            if isinstance(obj, (list, tuple, dict)):
                return obj[key]
            elif isinstance(obj, str):
                if isinstance(key, int):
                    return obj[key]
                else:
                    raise TypeError("String indices must be integers")
            else:
                raise TypeError("Object is not subscriptable")

        def safe_setitem(obj, key, value):
            if isinstance(obj, list):
                obj[key] = value
            elif isinstance(obj, dict):
                obj[key] = value
            else:
                raise TypeError("Object does not support item assignment")

        restricted_globals['_getattr_'] = safe_getattr
        restricted_globals['_setattr_'] = safe_setattr
        restricted_globals['_getitem_'] = safe_getitem
        restricted_globals['_setitem_'] = safe_setitem

        # Добавляем пользовательский контекст
        if context is not None:
            restricted_globals.update(context)
        
        try:
            # Компилируем код с ограничениями
            compile_result = compile_restricted(code, '<string>', 'exec')
            
            # Проверяем, что компиляция прошла успешно
            if compile_result is None:
                return {
                    'success': False,
                    'output': '',
                    'error': 'Ошибка компиляции: компилятор вернул None',
                    'variables': {},
                    'traceback': None
                }
            
            # Проверяем наличие ошибок компиляции
            # В RestrictedPython результат может быть CompileResult или code object
            if hasattr(compile_result, 'errors'):
                errors = compile_result.errors
                if errors:
                    # errors может быть списком или строкой
                    if isinstance(errors, list):
                        error_msg = '\n'.join(str(e) for e in errors)
                    else:
                        error_msg = str(errors)
                    return {
                        'success': False,
                        'output': '',
                        'error': f'Ошибка компиляции: {error_msg}',
                        'variables': {},
                        'traceback': None
                    }
            
            # Получаем code object для выполнения
            # Если это CompileResult, используем атрибут code, иначе сам объект
            if hasattr(compile_result, 'code'):
                code_to_execute = compile_result.code
                # Проверяем, что code не None
                if code_to_execute is None:
                    return {
                        'success': False,
                        'output': '',
                        'error': 'Ошибка компиляции: не удалось получить code object',
                        'variables': {},
                        'traceback': None
                    }
            else:
                code_to_execute = compile_result
            
            # Выполняем код
            # RestrictedPython автоматически создаст функцию _print в restricted_globals
            # которая будет собирать весь вывод print
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code_to_execute, restricted_globals)
            
            # Получаем вывод из PrintCollector
            # RestrictedPython создаёт функцию _print после выполнения кода
            print_output = ''
            if '_print' in restricted_globals:
                # Вызываем функцию _print() чтобы получить собранный вывод
                try:
                    print_output = restricted_globals['_print']()
                except:
                    # Если _print не функция, просто получаем строковое представление
                    print_output = str(restricted_globals.get('_print', ''))
            
            # Получаем переменные из контекста
            variables = {
                key: self._safe_repr(value) 
                for key, value in restricted_globals.items()
                if not key.startswith('_') and key not in ['__builtins__', '_print']
            }
            
            # Объединяем вывод из stdout и PrintCollector
            stdout_output = stdout_capture.getvalue()
            if print_output:
                # PrintCollector возвращает строку с выводом
                output = print_output + stdout_output
            else:
                output = stdout_output
            
            error = stderr_capture.getvalue() if stderr_capture.getvalue() else None
            
            return {
                'success': True,
                'output': output,
                'error': error,
                'variables': variables,
                'traceback': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': str(e),
                'variables': {},
                'traceback': traceback.format_exc()
            }
    
    def _safe_repr(self, obj):
        """
        Безопасное представление объекта для вывода.
        """
        try:
            if isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [self._safe_repr(item) for item in obj]
            elif isinstance(obj, dict):
                return {str(k): self._safe_repr(v) for k, v in obj.items()}
            else:
                return str(type(obj).__name__)
        except:
            return '<не удалось представить>'
    
    def check_variable(self, code, variable_name, expected_value):
        """
        Проверяет, что переменная имеет ожидаемое значение.
        
        Args:
            code: Код для выполнения
            variable_name: Имя переменной для проверки
            expected_value: Ожидаемое значение
        
        Returns:
            dict: Результат проверки
        """
        result = self.execute(code)
        
        if not result['success']:
            return {
                'passed': False,
                'message': f'Ошибка выполнения: {result["error"]}',
                'actual': None
            }
        
        if variable_name not in result['variables']:
            return {
                'passed': False,
                'message': f'Переменная "{variable_name}" не найдена',
                'actual': None
            }
        
        actual_value = result['variables'][variable_name]
        passed = self._compare_values(actual_value, expected_value)
        
        return {
            'passed': passed,
            'message': '✅ Правильно!' if passed else f'❌ Ожидалось: {expected_value}, получено: {actual_value}',
            'actual': actual_value
        }
    
    def check_output(self, code, expected_output):
        """
        Проверяет, что вывод кода соответствует ожидаемому.
        
        Args:
            code: Код для выполнения
            expected_output: Ожидаемый вывод (строка)
        
        Returns:
            dict: Результат проверки
        """
        result = self.execute(code)
        
        if not result['success']:
            return {
                'passed': False,
                'message': f'Ошибка выполнения: {result["error"]}',
                'actual': None
            }
        
        actual_output = result['output'].strip()
        expected_output = expected_output.strip()
        
        passed = actual_output == expected_output
        
        return {
            'passed': passed,
            'message': '✅ Правильно!' if passed else f'❌ Ожидалось:\n{expected_output}\n\nПолучено:\n{actual_output}',
            'actual': actual_output
        }
    
    def _compare_values(self, actual, expected):
        """
        Сравнивает два значения с учётом типов.
        """
        # Простое сравнение
        if actual == expected:
            return True
        
        # Для списков сравниваем содержимое
        if isinstance(actual, list) and isinstance(expected, list):
            if len(actual) != len(expected):
                return False
            return all(self._compare_values(a, e) for a, e in zip(actual, expected))
        
        # Для словарей сравниваем ключи и значения
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            return all(self._compare_values(actual[k], expected[k]) for k in expected.keys())
        
        return False

