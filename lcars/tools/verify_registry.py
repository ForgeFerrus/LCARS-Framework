# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Коректні шляхи через pathlib
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from lcars.system.initialization import initialize_system
from lcars.base.types import Directive, Chassis, Visual, Lore, Primitives

def verify_registry():
    print("--- INITIATING REGISTRY VERIFICATION ---")
    
    app = QApplication.instance() or QApplication(["verify"])
    
    from lcars.base.register import register_standard, registry
    register_standard()
    print(f"Technical.Widget: {registry.get('Technical.Widget')}")
    
    # Ініціалізація без перехоплення помилок за Titanium Standard
    initialize_system()
    
    categories = {
    }
    for name in registry.ComponentNames():
        print(f"{name}: {registry.get(name)}")
        
    print("--- REGISTRY VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_registry()


