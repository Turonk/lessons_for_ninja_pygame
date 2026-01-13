"""
Тестовый скрипт для проверки работы RestrictedPython.
"""
from RestrictedPython import compile_restricted

# Тест 1: Простой код без ошибок
print("=== Тест 1: Простой код ===")
code1 = "age = 12\nname = 'Игрок'\nprint(f'Имя: {name}')"
result1 = compile_restricted(code1, '<string>', 'exec')
print(f"Тип результата: {type(result1)}")
print(f"Есть атрибут 'errors': {hasattr(result1, 'errors')}")
print(f"Есть атрибут 'code': {hasattr(result1, 'code')}")

if hasattr(result1, 'errors'):
    print(f"Errors: {result1.errors}")
if hasattr(result1, 'code'):
    print(f"Code type: {type(result1.code)}")

# Тест 2: Код с ошибкой
print("\n=== Тест 2: Код с ошибкой ===")
code2 = "age = 12\nprint(undefined_variable)"  # NameError при выполнении, но не при компиляции
result2 = compile_restricted(code2, '<string>', 'exec')
print(f"Тип результата: {type(result2)}")
print(f"Есть атрибут 'errors': {hasattr(result2, 'errors')}")
print(f"Есть атрибут 'code': {hasattr(result2, 'code')}")

if hasattr(result2, 'errors'):
    print(f"Errors: {result2.errors}")
if hasattr(result2, 'code'):
    print(f"Code type: {type(result2.code)}")

# Тест 3: Код с синтаксической ошибкой
print("\n=== Тест 3: Синтаксическая ошибка ===")
code3 = "age = 12\nprint("  # Незакрытая скобка
try:
    result3 = compile_restricted(code3, '<string>', 'exec')
    print(f"Тип результата: {type(result3)}")
    print(f"Есть атрибут 'errors': {hasattr(result3, 'errors')}")
    if hasattr(result3, 'errors'):
        print(f"Errors: {result3.errors}")
except Exception as e:
    print(f"Исключение при компиляции: {type(e).__name__}: {e}")

# Тест 4: Попытка выполнения
print("\n=== Тест 4: Выполнение кода ===")
if hasattr(result1, 'code'):
    code_to_exec = result1.code
else:
    code_to_exec = result1

print(f"Тип code_to_exec: {type(code_to_exec)}")

try:
    exec(code_to_exec, {})
    print("✅ Код выполнен успешно!")
except Exception as e:
    print(f"❌ Ошибка выполнения: {type(e).__name__}: {e}")

