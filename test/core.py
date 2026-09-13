# ТЕСТ БАЗОВОЇ ФУНКЦІОНАЛЬНОСТІ ЯДРА LCARS
# Опис: Перевірка чи може ядро ініціалізуватися без помилок
# Автор: Devin AI
# Дата: 2026-05-01

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("TESTING LCARS CORE")
print("=" * 50)

# TEST 1: Import basic types
print("\n[1/5] Testing basic types import...")
try:
    from lcars.base.type import LCARS, Matrix, Directive, Primitives, Type, ODN
    print("   [OK] Basic types imported successfully")
except Exception as e:
    print(f"   [FAIL] Error importing basic types: {e}")
    sys.exit(1)

# TEST 2: Import registry
print("\n[2/5] Testing registry import...")
try:
    from lcars.base.register import registry
    print("   [OK] Registry imported successfully")
except Exception as e:
    print(f"   [FAIL] Error importing registry: {e}")
    sys.exit(1)

# TEST 3: Import Bridge
print("\n[3/5] Testing Bridge import...")
try:
    from lcars.service.bridge import Bridge
    bridge = Bridge.GetInstance()
    print("   [OK] Bridge imported and initialized successfully")
except Exception as e:
    print(f"   [FAIL] Error importing Bridge: {e}")
    sys.exit(1)

# TEST 4: Create Application
print("\n[4/5] Testing Application creation...")
try:
    AppClass = LCARS.Application
    app = AppClass.instance() or AppClass(sys.argv)
    print("   [OK] Application created successfully")
except Exception as e:
    print(f"   [FAIL] Error creating Application: {e}")
    sys.exit(1)

# TEST 5: Create basic components
print("\n[5/5] Testing basic components import...")
try:
    from lcars.base.graphic import Graphic
    from lcars.base.component import Component, LCARSLabel
    print("   [OK] Components imported successfully")
except Exception as e:
    print(f"   [FAIL] Error importing components: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("ALL CORE TESTS PASSED SUCCESSFULLY!")
print("LCARS CORE IS READY")
print("=" * 50)