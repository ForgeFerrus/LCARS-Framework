# Тест Bridge системи для AI провайдерів
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

print("Testing Bridge system for AI providers...")

try:
    from lcars.service.bridge import Bridge
    print("✅ Bridge module imported")
    
    bridge = Bridge()
    print("✅ Bridge instance created")
    
    # Перевіримо чи може Bridge завантажувати системні модулі
    path_module = bridge.Load("System.Path")
    if path_module:
        print("✅ System.Path loaded via Bridge")
    else:
        print("❌ System.Path NOT loaded via Bridge")
    
    # Перевіримо AI провайдер через Bridge
    ai_provider = bridge.Load("AI.Provider")
    if ai_provider:
        print("✅ AI.Provider loaded via Bridge")
    else:
        print("❌ AI.Provider NOT loaded via Bridge")
        
    # Перевіримо конкретні AI бекенди
    groq = bridge.Load("AI.Provider.Groq")
    mistral = bridge.Load("AI.Provider.Mistral")
    
    print(f"Groq via Bridge: {'✅' if groq else '❌'}")
    print(f"Mistral via Bridge: {'✅' if mistral else '❌'}")
    
except Exception as e:
    print(f"❌ Bridge system error: {e}")
    import traceback
    traceback.print_exc()