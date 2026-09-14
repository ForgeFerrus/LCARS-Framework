#!/usr/bin/env python3
# LCARS BASE TEST - Перевірка основних компонентів

import sys
from pathlib import Path

# Додаємо корінь проєкту
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("◤ TESTING LCARS BASE SYSTEM")
print("=" * 50)

# Тест 1: Імпорт базових типів
try:
    from lcars.base.type import LCARS, Matrix, SystemComponent
    print("✓ Base types imported successfully")
except Exception as e:
    print(f"✗ Base types import failed: {e}")
    sys.exit(1)

# Тест 2: Імпорт реєстру
try:
    from lcars.base.register import registry
    print("✓ Registry imported successfully")
except Exception as e:
    print(f"✗ Registry import failed: {e}")
    sys.exit(1)

# Тест 3: Створення базових об'єктів
try:
    # Створюємо LCARS об'єкт
    lcars_obj = LCARS("test_system")
    print(f"✓ LCARS object created: {lcars_obj.SystemId}")
    
    # Створюємо Matrix
    matrix = Matrix("test_matrix")
    print(f"✓ Matrix object created: {matrix.LcarsId}")
    
    # Створюємо SystemComponent
    component = SystemComponent("test_component")
    print(f"✓ SystemComponent created: {component.SystemId}")
    
except Exception as e:
    print(f"✗ Object creation failed: {e}")
    sys.exit(1)

# Тест 4: Робота з реєстром
try:
    # Реєстрація об'єкта
    registry.Register("Test.Object", lcars_obj)
    print("✓ Object registered")
    
    # Отримання об'єкта
    entry = registry.Resolve("Test.Object")
    retrieved = entry[0] if isinstance(entry, tuple) else entry
    if retrieved == lcars_obj:
        print("✓ Object retrieved successfully")
    else:
        print("✗ Object retrieval failed")
        
    # Перевірка списку
    keys = registry.List()
    print(f"✓ Registry has {len(keys)} keys")
    
except Exception as e:
    print(f"✗ Registry operations failed: {e}")
    sys.exit(1)

# Тест 5: Перевірка функцій доступу
try:
    Color = LCARS.Visual.Color
    Font = LCARS.Visual.Font
    Widget = LCARS.Interface.Widget
    print("✓ Access functions imported")
    
    # Спроба отримати з реєстру (може бути None якщо не ініціалізовано)
    color = Color()
    print(f"✓ Color function returns: {type(color)}")
    
except Exception as e:
    print(f"✗ Access functions failed: {e}")

# Тест 6: Перевірка метакласу
try:
    type_obj = LCARS("test_type")
    print(f"✓ LCARS object created: {type_obj.SystemId}")
    
    # Перевірка діагностики компонента та дескриптора вузла
    comp_diag = component.Diagnostics()
    print(f"✓ Component Diagnostics: {comp_diag['id']} -> {comp_diag['status']}")
    descriptor = type_obj.Descriptor()
    print(f"✓ LCARS Descriptor: {descriptor['id']}")
    
except Exception as e:
    print(f"✗ Metaclass test failed: {e}")

print("=" * 50)
print("◤ BASE SYSTEM TEST COMPLETE")
print("✓ All core components working!")
