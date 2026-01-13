"""
Модуль для проверки заданий по тестам.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
from code_executor import CodeExecutor


class TestChecker:
    """
    Класс для проверки выполнения заданий.
    """
    
    def __init__(self):
        self.executor = CodeExecutor()
    
    def check_exercise(self, code, exercise_config):
        """
        Проверяет выполнение задания по конфигурации.
        
        Args:
            code: Код пользователя
            exercise_config: Конфигурация задания (dict)
        
        Returns:
            dict: Результаты проверки
        """
        results = {
            'passed': True,
            'tests': [],
            'message': '',
            'hint': exercise_config.get('hint', '')
        }
        
        tests = exercise_config.get('tests', [])
        
        for i, test in enumerate(tests):
            test_result = self._run_test(code, test)
            results['tests'].append(test_result)
            
            if not test_result['passed']:
                results['passed'] = False
        
        # Формируем итоговое сообщение
        passed_count = sum(1 for t in results['tests'] if t['passed'])
        total_count = len(results['tests'])
        
        if results['passed']:
            results['message'] = f'🎉 Отлично! Все {total_count} тестов пройдено!'
        else:
            results['message'] = f'Пройдено {passed_count} из {total_count} тестов. Попробуй ещё раз!'
        
        return results
    
    def _run_test(self, code, test_config):
        """
        Выполняет один тест.
        
        Args:
            code: Код пользователя
            test_config: Конфигурация теста
        
        Returns:
            dict: Результат теста
        """
        test_type = test_config.get('type')
        
        if test_type == 'output':
            # Проверка вывода
            expected = test_config.get('expected', '')
            return self.executor.check_output(code, expected)
        
        elif test_type == 'variable':
            # Проверка переменной
            var_name = test_config.get('variable')
            expected_value = test_config.get('expected')
            return self.executor.check_variable(code, var_name, expected_value)
        
        elif test_type == 'contains':
            # Проверка, что вывод содержит строку
            result = self.executor.execute(code)
            if not result['success']:
                return {
                    'passed': False,
                    'message': f'Ошибка: {result["error"]}',
                    'actual': None
                }
            
            expected = test_config.get('expected', '')
            passed = expected in result['output']
            
            return {
                'passed': passed,
                'message': f'✅ Строка "{expected}" найдена!' if passed else f'❌ Строка "{expected}" не найдена в выводе',
                'actual': result['output']
            }
        
        elif test_type == 'no_error':
            # Проверка, что код выполняется без ошибок
            result = self.executor.execute(code)
            passed = result['success']
            
            return {
                'passed': passed,
                'message': '✅ Код выполнен без ошибок!' if passed else f'❌ Ошибка: {result.get("error", "Неизвестная ошибка")}',
                'actual': None
            }
        
        else:
            return {
                'passed': False,
                'message': f'Неизвестный тип теста: {test_type}',
                'actual': None
            }

