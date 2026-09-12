# ◤ LCARS STARSHIP BOARD COMPUTER // DIRECT LAUNCHER 🖖
# =============================================================================
# ДОСТУПНІ МОДЕЛІ ШТУЧНОГО ІНТЕЛЕКТУ ТА ПАРАМЕТРИ ЗАПУСКУ:
# 1. Локальна на ПК (за замовчуванням, офлайн):
#    py start.py
#    py start.py --model local
#    Ваги: C:\Users\Forge\MyProject\Models\HuggingFace\models--Qwen--Qwen2.5-0.5B-Instruct\...
#
# 2. Інші підтримувані бекенди через флаг --model:
#    py start.py --model groq       # Groq Cloud (Qwen 3.6 / Compound, потрібен GROQ_API_KEY)
#    py start.py --model mistral    # Mistral AI (Codestral / Large, потрібен MISTRAL_API_KEY)
#    py start.py --model astra      # Experiential Labs Astra GPT-6 (потрібен EXPERIENTIAL_API_KEY)
#    py start.py --model openrouter # OpenRouter Multi-Provider (потрібен OPENROUTER_API_KEY)
# =============================================================================

from lcars.base.type import LCARS
from lcars.core.computer import BoardComputer
from lcars.service.provider import AIProviderManager

def Main():
    # 1. Налаштування UTF-8 консолі через LCARS.System.Core
    LCARS.System.Core.stdout.reconfigure(encoding="utf-8")
    LCARS.System.Core.stdin.reconfigure(encoding="utf-8")

    # 2. Пряме підключення до моделі Google Gemma 3 1B IT (1.0 млрд параметрів)
    AiManager = AIProviderManager.GetInstance()
    AiManager.SwitchModel("local")
    ActiveBackend = AiManager.ActiveBackend
    if ActiveBackend:
        ActiveBackend.MaxTokens = 1500

    ModelName = "google/gemma-3-1b-it (1.0B Parameters, Instruction-Tuned)"
    ModelPath = r"C:\Users\Forge\MyProject\Models\HuggingFace\models--google--gemma-3-1b-it\snapshots\dcc83ea841ab6100d6b47a070329e1ba4cf78752"
    ActiveBackend.LOCAL_PATH = ModelPath

    print("=" * 76, flush=True)
    print("◤ LCARS STARSHIP BOARD COMPUTER // NEURAL CORE ONLINE", flush=True)
    print(f"  TARGET MODEL : {ModelName}", flush=True)
    print(f"  ENGINE TYPE  : Direct CPU Offline Inference (Transformers + PyTorch)", flush=True)
    print(f"  WEIGHTS PATH : {ModelPath}", flush=True)
    print(f"  WEIGHTS SIZE : 1.94 GB", flush=True)
    print("=" * 76, flush=True)

    # 3. Ініціалізація Живого Ядра Бортового Комп'ютера
    Computer = BoardComputer.GetInstance()
    System = Computer.InitializeSystem()

    if not System:
        print("◤ LCARS FAULT: SYSTEM BOOT FAILED", flush=True)
        return

    print(f"◤ STARSHIP: {Computer.ShipRegistry} ({Computer.ShipClass}) // ODN CONDUITS NOMINAL", flush=True)

    # 4. Створення графічного застосунку та розгортання повної черги завантаження LCARS (Boot -> Login -> Desktop)
    AppInstance = LCARS.Application.instance() if hasattr(LCARS.Application, "instance") else None
    if AppInstance is None and hasattr(LCARS, "Application"):
        AppInstance = LCARS.Application([])

    print(f">> [ODN] DEPLOYING LCARS PROGRESSIVE STAGED BOOT INITIALIZATION SEQUENCE", flush=True)
    BootScreen = Computer.LaunchInterface("BOOT", Show=True)

    # 5. Фонове підвантаження локальної моделі ШІ (щоб не блокувати розгортання інтерфейсу)
    Threading = LCARS.System.Threading
    def WarmupNeuralCore():
        if ActiveBackend and hasattr(ActiveBackend, "EnsureLoaded"):
            ActiveBackend.EnsureLoaded()
            print(f">> [ODN] NEURAL CORE RESIDENT ONLINE & SYNCHRONIZED", flush=True)

    if Threading is not None:
        WarmupThread = Threading.Thread(target=WarmupNeuralCore, daemon=True)
        WarmupThread.start()

    # 6. Головний цикл графічних подій LCARS
    if AppInstance is not None:
        ExecMethod = getattr(AppInstance, "exec", None)
        if callable(ExecMethod):
            ExecMethod()

    print("◤ LCARS: DISCONNECTING BOARD COMPUTER. LIVE LONG AND PROSPER 🖖", flush=True)

if __name__ == "__main__":
    Main()