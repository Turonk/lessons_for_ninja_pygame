// Инициализация редактора кода
let editor;

document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        lineNumbers: true,
        mode: 'python',
        theme: 'monokai',
        indentUnit: 4,
        indentWithTabs: false,
        lineWrapping: true
    });
    
    // Загружаем первое задание по умолчанию
    loadExercise();
});

// Загрузка задания
async function loadExercise() {
    const lesson = document.getElementById('lesson-select').value;
    const exerciseNum = document.getElementById('exercise-select').value;
    
    try {
        const response = await fetch(`http://localhost:5000/api/exercise/${lesson}/${exerciseNum}`);
        const data = await response.json();
        
        if (data.success) {
            const exercise = data.exercise;
            document.getElementById('exercise-title').textContent = exercise.title;
            document.getElementById('exercise-description').textContent = exercise.description;
            document.getElementById('exercise-hint').textContent = exercise.hint;
            document.getElementById('exercise-example').textContent = exercise.example || 'Пример не предоставлен';
            
            // Очищаем результаты
            document.getElementById('results-content').innerHTML = '';
        } else {
            alert('Ошибка загрузки задания: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка подключения к серверу. Убедись, что backend запущен на http://localhost:5000');
        console.error(error);
    }
}

// Проверка кода
async function runCode() {
    const code = editor.getValue();
    const lesson = document.getElementById('lesson-select').value;
    const exerciseNum = parseInt(document.getElementById('exercise-select').value);
    
    if (!code.trim()) {
        alert('Введи код для проверки!');
        return;
    }
    
    const resultsDiv = document.getElementById('results-content');
    resultsDiv.innerHTML = '<div class="loading">⏳ Проверяю код...</div>';
    
    try {
        const response = await fetch('http://localhost:5000/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                lesson: lesson,
                exercise: exerciseNum
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.result);
        } else {
            resultsDiv.innerHTML = `<div class="test-result failed">
                <div class="test-message">❌ Ошибка: ${data.error}</div>
            </div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="test-result failed">
            <div class="test-message">❌ Ошибка подключения к серверу. Убедись, что backend запущен.</div>
        </div>`;
        console.error(error);
    }
}

// Отображение результатов
function displayResults(result) {
    const resultsDiv = document.getElementById('results-content');
    let html = '';
    
    // Отображаем результаты каждого теста
    result.tests.forEach((test, index) => {
        const className = test.passed ? 'passed' : 'failed';
        html += `
            <div class="test-result ${className}">
                <div class="test-description">Тест ${index + 1}: ${test.description || 'Проверка'}</div>
                <div class="test-message">${test.message}</div>
            </div>
        `;
    });
    
    // Итоговое сообщение
    const summaryClass = result.passed ? 'success' : 'failure';
    html += `
        <div class="summary ${summaryClass}">
            ${result.message}
        </div>
    `;
    
    // Подсказка, если не все тесты пройдены
    if (!result.passed && result.hint) {
        html += `
            <div class="hint" style="margin-top: 15px;">
                ${result.hint}
            </div>
        `;
    }
    
    resultsDiv.innerHTML = html;
}

