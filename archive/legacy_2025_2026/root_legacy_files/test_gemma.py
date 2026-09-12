# LCARS TITANIUM v44.20
# ◤ AI TEST RUNNER — Тестування інтеграції Gemma AI
# ОПИС: Цей тестовий скрипт перевіряє коректність інтеграції AI провайдера (Gemma) в LCARS Titanium.
# ПРОТОКОЛ: No-Q (Жодних прямих імпортів PyQt), Zero-Except (Без виключень при відсутності компонентів).
# ФУНКЦІЇ: Ініціалізація системи, отримання AI провайдера, відправка тестового запиту та вивід відповіді.
# ─────────────────────────────────────────────────────────────────────────────
import sys

# Додаємо шлях до проекту
sys.path.append(".")
from lcars.base.type import LCARS, 
from lcars.system.software import QuickBoot

def TestAiIntegration():
    print("◤ INITIALIZING LCARS TITANIUM BOOT SEQUENCE ◢")
    # 1. Запуск системи (ініціалізує AI Engine автоматично)
    Loader = QuickBoot()
    
    # 2. Отримуємо доступ до ШІ через міст
    Ai = LCARS.Bridge.GetAI()  # Повертає об'єкт AI провайдера (Gemma/Mistral/тощо)
    if not Ai:
        print("ERROR: AI Engine not registered in LCARS Bridge!")
        return

    print(f"AI Service: ONLINE (Authority: {Ai.Authority})")
    
    # 3. Тестовий запит до Gemma
    Task = "Generate LCARS Dashboard layout for Engineering Suite"
    print(f"\nSENDING TASK: {Task}")
    
    Response = Ai.ProcessTask(Task)
    
    print(f"\nGEMMA RESPONSE:\n{'-'*40}\n{Response}\n{'-'*40}")
    print("\n◤ INTEGRATION TEST COMPLETED SUCCESSFULLY ◢")

if __name__ == "__main__":
    TestAiIntegration()
