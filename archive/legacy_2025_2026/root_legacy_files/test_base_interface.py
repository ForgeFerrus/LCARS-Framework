import sys
from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path('.').absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PyQt6.QtWidgets import QApplication
    from lcars.ui.base_interface import BaseLCARSInterface
    
    print("Starting Base LCARS Interface...")
    app = QApplication([])
    
    # Create base interface
    window = BaseLCARSInterface(project_root)
    window.show()
    print("Base interface window shown!")
    
    app.exec()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
