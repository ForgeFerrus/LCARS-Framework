# ТЕСТ БАЗОВОЇ ФУНКЦІОНАЛЬНОСТІ ЯДРА LCARS
# Опис: Перевірка чи може ядро ініціалізуватися без помилок
# Автор: Devin AI
# Дата: 2026-05-01

import sys
from pathlib import Path

project_root = Path(__file__).parent
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

# TEST 3: Import AI engine
print("\n[3/5] Testing AI engine import...")
try:
    from lcars.modules.ai_engine import Engine
    print("   [OK] AI engine imported successfully")
except Exception as e:
    print(f"   [FAIL] Error importing AI engine: {e}")
    sys.exit(1)

# TEST 4: Create QApplication
print("\n[4/5] Testing QApplication creation...")
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print("   [OK] QApplication created successfully")
except Exception as e:
    print(f"   [FAIL] Error creating QApplication: {e}")
    sys.exit(1)

# TEST 5: Create basic components
print("\n[5/5] Testing basic components import...")
try:
    from lcars.base.component import Graphic, LCARSLabel
    print("   [OK] Components imported successfully")
except Exception as e:
    print(f"   [FAIL] Error importing components: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("ALL CORE TESTS PASSED SUCCESSFULLY!")
print("LCARS CORE IS READY")
print("=" * 50)