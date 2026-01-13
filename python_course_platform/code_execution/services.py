"""
Сервис для безопасного выполнения Python кода.
"""
import sys
import io
import traceback
import time
from contextlib import redirect_stdout, redirect_stderr
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.PrintCollector import PrintCollector


class CodeExecutionService:
    """
    Сервис для безопасного выполнения Python кода и проверки заданий.
    """

    def __init__(self, timeout=5.0):
        self.timeout = timeout

    def execute_and_test(self, code, test_cases):
        """
        Выполняет код и проверяет его на соответствие тестам.

        Args:
            code: Строка с Python кодом
            test_cases: QuerySet или список объектов TestCase

        Returns:
            dict: Результаты выполнения и проверки
        """
        start_time = time.time()

        try:
            # Выполняем код
            execution_result = self.execute_code(code)
            execution_time = time.time() - start_time

            if not execution_result['success']:
                return {
                    'success': False,
                    'error': execution_result['error'],
                    'score': 0,
                    'execution_time': execution_time,
                    'tests': []
                }

            # Проверяем тесты
            test_results = []
            passed_tests = 0

            for test_case in test_cases:
                test_result = self.check_test_case(execution_result, test_case)
                test_results.append({
                    'id': test_case.id,
                    'type': test_case.test_type,
                    'description': test_case.description,
                    'passed': test_result['passed'],
                    'message': test_result['message']
                })
                if test_result['passed']:
                    passed_tests += 1

            score = int((passed_tests / len(test_cases)) * 100) if test_cases else 0

            return {
                'success': True,
                'output': execution_result['output'],
                'variables': execution_result['variables'],
                'score': score,
                'execution_time': execution_time,
                'tests': test_results,
                'passed_count': passed_tests,
                'total_count': len(test_cases)
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': f'Ошибка выполнения: {str(e)}',
                'score': 0,
                'execution_time': execution_time,
                'tests': []
            }

    def execute_code(self, code, context=None):
        """
        Безопасно выполняет Python код.

        Args:
            code: Строка с Python кодом
            context: Словарь с начальными переменными

        Returns:
            dict: Результат выполнения
        """
        # Перехватываем вывод
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Начальный контекст
        if context is None:
            context = {}

        # Создаём безопасное окружение с необходимыми "стражами"
        restricted_globals = safe_globals.copy()
        restricted_globals['__builtins__'] = {
            name: func for name, func in safe_builtins.items()
            if name in [
                'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict',
                'tuple', 'set', 'range', 'enumerate', 'zip', 'max', 'min', 'sum',
                'abs', 'round', 'sorted', 'reversed', 'type', 'isinstance',
                'hasattr', 'getattr', 'setattr', 'delattr', 'dir', 'vars',
                'all', 'any', 'map', 'filter', 'iter', 'next'
            ]
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
        if context:
            restricted_globals.update(context)

        try:
            # Компилируем код с ограничениями
            compile_result = compile_restricted(code, '<string>', 'exec')

            # Проверяем наличие ошибок компиляции
            if hasattr(compile_result, 'errors') and compile_result.errors:
                errors = compile_result.errors
                if isinstance(errors, list):
                    error_msg = '\n'.join(str(e) for e in errors)
                else:
                    error_msg = str(errors)
                return {
                    'success': False,
                    'output': '',
                    'error': f'Ошибка компиляции: {error_msg}',
                    'variables': {}
                }

            # Получаем code object для выполнения
            if hasattr(compile_result, 'code'):
                code_to_execute = compile_result.code
            else:
                code_to_execute = compile_result

            # Выполняем код
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code_to_execute, restricted_globals)

            # Получаем вывод из PrintCollector
            print_output = ''
            if '_print' in restricted_globals:
                try:
                    print_output = restricted_globals['_print']()
                except:
                    print_output = str(restricted_globals.get('_print', ''))

            # Получаем переменные из контекста
            variables = {
                key: self._safe_repr(value)
                for key, value in restricted_globals.items()
                if not key.startswith('_') and key not in ['__builtins__', '_print']
            }

            # Объединяем вывод
            stdout_output = stdout_capture.getvalue()
            if print_output:
                output = print_output + stdout_output
            else:
                output = stdout_output

            error = stderr_capture.getvalue() if stderr_capture.getvalue() else None

            return {
                'success': True,
                'output': output,
                'error': error,
                'variables': variables
            }

        except Exception as e:
            return {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': str(e),
                'variables': {}
            }

    def check_test_case(self, execution_result, test_case):
        """
        Проверяет один тестовый случай.

        Args:
            execution_result: Результат выполнения кода
            test_case: Объект TestCase

        Returns:
            dict: Результат проверки теста
        """
        if not execution_result['success']:
            return {
                'passed': False,
                'message': f'Код не выполнился: {execution_result["error"]}'
            }

        test_type = test_case.test_type
        expected_value = test_case.expected_value

        if test_type == 'variable':
            # Проверка переменной
            var_name = test_case.variable_name
            if var_name not in execution_result['variables']:
                return {
                    'passed': False,
                    'message': f'Переменная "{var_name}" не найдена'
                }

            actual_value = execution_result['variables'][var_name]
            passed = self._compare_values(actual_value, expected_value)

            return {
                'passed': passed,
                'message': f'✅ Переменная {var_name} верна!' if passed
                         else f'❌ Ожидалось: {expected_value}, получено: {actual_value}'
            }

        elif test_type == 'output':
            # Проверка вывода
            actual_output = execution_result['output'].strip()
            expected_output = str(expected_value).strip()
            passed = actual_output == expected_output

            return {
                'passed': passed,
                'message': '✅ Вывод верный!' if passed
                         else f'❌ Ожидалось: "{expected_output}", получено: "{actual_output}"'
            }

        elif test_type == 'contains':
            # Проверка, что вывод содержит текст
            expected_text = str(expected_value)
            passed = expected_text in execution_result['output']

            return {
                'passed': passed,
                'message': f'✅ Найден текст: "{expected_text}"' if passed
                         else f'❌ Текст "{expected_text}" не найден в выводе'
            }

        elif test_type == 'no_error':
            # Проверка, что код выполнился без ошибок
            passed = execution_result['success'] and not execution_result.get('error')

            return {
                'passed': passed,
                'message': '✅ Код выполнен без ошибок!' if passed
                         else f'❌ Ошибка выполнения: {execution_result.get("error", "Неизвестная ошибка")}'
            }

        else:
            return {
                'passed': False,
                'message': f'Неизвестный тип теста: {test_type}'
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
