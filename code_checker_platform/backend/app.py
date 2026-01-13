"""
Flask API для проверки Python кода.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from test_checker import TestChecker
import json
import os

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с фронтенда

checker = TestChecker()

# Загружаем задания
EXERCISES_DIR = os.path.join(os.path.dirname(__file__), '..', 'exercises')
exercises_cache = {}


def load_exercise(lesson, exercise_num):
    """Загружает конфигурацию задания из файла."""
    cache_key = f"{lesson}_{exercise_num}"
    
    if cache_key in exercises_cache:
        return exercises_cache[cache_key]
    
    exercise_file = os.path.join(EXERCISES_DIR, lesson, f"exercise_{exercise_num}.json")
    
    if not os.path.exists(exercise_file):
        return None
    
    with open(exercise_file, 'r', encoding='utf-8') as f:
        exercise_data = json.load(f)
    
    exercises_cache[cache_key] = exercise_data
    return exercise_data


@app.route('/api/check', methods=['POST'])
def check_code():
    """
    Проверяет код пользователя.
    
    Body:
        {
            "code": "код пользователя",
            "lesson": "lesson_03a",
            "exercise": 6
        }
    """
    try:
        data = request.json
        code = data.get('code', '')
        lesson = data.get('lesson', '')
        exercise_num = data.get('exercise', 0)
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Код не предоставлен'
            }), 400
        
        # Загружаем конфигурацию задания
        exercise_config = load_exercise(lesson, exercise_num)
        
        if not exercise_config:
            return jsonify({
                'success': False,
                'error': f'Задание {lesson}/exercise_{exercise_num} не найдено'
            }), 404
        
        # Проверяем код
        result = checker.check_exercise(code, exercise_config)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exercise/<lesson>/<int:exercise_num>', methods=['GET'])
def get_exercise(lesson, exercise_num):
    """Получает информацию о задании."""
    exercise_config = load_exercise(lesson, exercise_num)
    
    if not exercise_config:
        return jsonify({
            'success': False,
            'error': 'Задание не найдено'
        }), 404
    
    # Возвращаем только описание задания (без тестов)
    return jsonify({
        'success': True,
        'exercise': {
            'title': exercise_config.get('title', ''),
            'description': exercise_config.get('description', ''),
            'hint': exercise_config.get('hint', ''),
            'example': exercise_config.get('example', '')
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API."""
    return jsonify({
        'status': 'ok',
        'message': 'API работает'
    })


if __name__ == '__main__':
    # Создаём директорию для заданий, если её нет
    os.makedirs(EXERCISES_DIR, exist_ok=True)
    
    print("Starting code checker server...")
    print("API available at http://localhost:5000")
    print("Exercises loaded from:", EXERCISES_DIR)
    
    app.run(debug=True, port=5000)

