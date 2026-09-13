# LCARS TITANIUM v44.20
# ◤ AI TEST RUNNER — Тестування інтеграції Gemma AI
# ОПИС: Мінімальний тест Gemma провайдера без зайвих залежностей
# ПРОТОКОЛ: No-Q (Жодних прямих імпортів PyQt), No-OS (LCARS.Directive замість OS)
# ─────────────────────────────────────────────────────────────────────────────
import sys

sys.path.append(".")
from lcars.service.gemma import GetGemmaProvider, GemmaProvider

def TestAiIntegration():
    print("=" * 60)
    print("◤ LCARS TITANIUM GEMMA AI INTEGRATION TEST ◢")
    print("=" * 60)
    
    # Імпорт та створення провайдера
    print("\n[1] Creating GemmaProvider instance...")
    Provider = GetGemmaProvider("gemma4-9b")
    print(f"   Model: {Provider.ModelKey}")
    print(f"   Path: {Provider.ModelPath}")
    
    # Перевірка кожної залежності окремо
    print("\n[2] Checking dependencies:")
    import importlib.util
    
    Deps = {
        "transformers": importlib.util.find_spec("transformers") is not None,
        "kagglehub": importlib.util.find_spec("kagglehub") is not None,
        "torch": importlib.util.find_spec("torch") is not None,
    }
    
    for DepName, IsFound in Deps.items():
        StatusIcon = "✓" if IsFound else "✗"
        print(f"   {StatusIcon} {DepName}: {'FOUND' if IsFound else 'NOT FOUND'}")
    
    # Перевірка загальної доступності
    print("\n[3] Checking provider availability...")
    IsAvailable = Provider.CheckAvailable()
    print(f"   Available: {IsAvailable}")
    
    if not IsAvailable:
        print("\n[!] Cannot proceed - missing dependencies")
        print("[!] Install with: pip install transformers kagglehub torch")
        print("\n◤ TEST FAILED - DEPENDENCIES MISSING ◢")
        return
    
    # Спроба завантаження моделі
    print("\n[4] Loading model (this may take a while)...")
    Loaded = Provider.LoadModel()
    print(f"   Model loaded: {Loaded}")
    
    if not Loaded:
        print(f"   Error: {Provider.LastError}")
        print("\n◤ TEST FAILED - MODEL LOAD ERROR ◢")
        return
    
    # Тестовий запит
    print("\n[5] Sending test prompt...")
    Task = "Generate LCARS Dashboard layout for Engineering Suite"
    print(f"   Prompt: {Task}")
    
    Response = Provider.Generate(Task)
    
    print(f"\n[6] Response received:")
    print("─" * 60)
    print(Response[:500] + "..." if len(Response) > 500 else Response)
    print("─" * 60)
    
    print("\n◤ INTEGRATION TEST COMPLETED SUCCESSFULLY ◢")

if __name__ == "__main__":
    TestAiIntegration()
