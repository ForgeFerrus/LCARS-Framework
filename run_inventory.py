# LCARS NEURAL CONSOLE
# Постійний живий консольний інтерфейс до локального Neural Core.

from lcars.base.type import LCARS
from lcars.service.provider import AIProviderManager


# Налаштовує кодування системної консолі.
def ConfigureEncoding():
    try:
        LCARS.System.Core.stdout.reconfigure(encoding="utf-8")
        LCARS.System.Core.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Запускає постійний локальний Neural Core.
def Main():
    ConfigureEncoding()

    ModelPath = (
        r"C:\Users\Forge\MyProject\Models\HuggingFace"
        r"\models--google--gemma-3-1b-it"
        r"\snapshots\dcc83ea841ab6100d6b47a070329e1ba4cf78752"
    )

    print()
    print("════════════════════════════════════════════════════════════")
    print("                 LCARS NEURAL CORE")
    print("════════════════════════════════════════════════════════════")
    print("MODE    : LOCAL")
    print("MODEL   : Google Gemma 3 1B IT")
    print("RUNTIME : Transformers / CPU")
    print("STATUS  : INITIALIZING")
    print("════════════════════════════════════════════════════════════")
    print()

    # Отримуємо єдиний менеджер AI-провайдерів.
    AiManager = AIProviderManager.GetInstance()

    if not AiManager.SwitchModel("local"):
        print("LCARS: ERROR — LOCAL NEURAL CORE NOT AVAILABLE")
        return

    ActiveBackend = AiManager.ActiveBackend

    if ActiveBackend is None:
        print("LCARS: ERROR — NO ACTIVE NEURAL BACKEND")
        return

    # Підміняємо локальний шлях на Gemma.
    ActiveBackend.LOCAL_PATH = ModelPath

    # Обмежуємо довжину відповіді для швидшого інтерактивного режиму.
    ActiveBackend.MaxTokens = 256

    print(">> [ODN] Establishing Neural Core link...")
    print(">> [NEURAL CORE] Loading Gemma into host RAM...")
    print()

    # Завантаження виконується ОДИН раз.
    if not ActiveBackend.EnsureLoaded():
        print()
        print("LCARS: ERROR — GEMMA FAILED TO LOAD")
        return

    print()
    print("════════════════════════════════════════════════════════════")
    print("STATUS  : NEURAL CORE ONLINE")
    print("MODEL   : GEMMA 3 1B IT")
    print("MEMORY  : RESIDENT")
    print("LINK    : ODN")
    print("════════════════════════════════════════════════════════════")
    print()
    print("LCARS: Neural Core готове.")
    print("LCARS: Введіть повідомлення.")
    print("LCARS: /clear — очистити контекст")
    print("LCARS: /status — стан Neural Core")
    print("LCARS: /exit — завершити роботу")
    print()

    # Постійний контекст поточного сеансу.
    Messages = [
        {
            "role": "system",
            "content": (
                "Ти є локальним нейронним ядром бортового комп'ютера LCARS. "
                "Відповідай мовою користувача. "
                "Будь коротким, точним і природним. "
                "Не вигадуй фактів про систему, яких не знаєш."
            )
        }
    ]

    while True:
        try:
            UserText = input("LCARS> ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("LCARS: Neural Core disconnecting...")
            break

        UserText = UserText.strip()

        if not UserText:
            continue

        if UserText.lower() == "/exit":
            print()
            print("LCARS: Neural Core disconnecting...")
            break

        if UserText.lower() == "/clear":
            Messages = [
                {
                    "role": "system",
                    "content": (
                        "Ти є локальним нейронним ядром бортового комп'ютера LCARS. "
                        "Відповідай мовою користувача. "
                        "Будь коротким, точним і природним. "
                        "Не вигадуй фактів про систему, яких не знаєш."
                    )
                }
            ]

            print("LCARS: Conversation context cleared.")
            print()
            continue

        if UserText.lower() == "/status":
            try:
                Info = ActiveBackend.GetInfo()
            except Exception:
                Info = {}

            print()
            print("┌─ NEURAL CORE STATUS")
            print(f"│ Backend : {Info.get('name', 'localllm')}")
            print("│ Model   : Google Gemma 3 1B IT")
            print("│ Runtime : transformers-cpu")
            print("│ Loaded  : YES")
            print(f"│ Context : {len(Messages) - 1} messages")
            print("└────────────────────")
            print()
            continue

        Messages.append(
            {
                "role": "user",
                "content": UserText
            }
        )

        print()
        print(">> [ODN] Transmitting to Neural Core...")
        print()

        try:
            Response = ActiveBackend.Chat(Messages)

            if not Response:
                Response = "[Neural Core returned an empty response]"

            Messages.append(
                {
                    "role": "assistant",
                    "content": Response
                }
            )

            # Поточний LocalLLM уже друкує відповідь через TextStreamer.
            # Тому тут навмисно НЕ робимо print(Response),
            # щоб відповідь не дублювалася.

        except Exception as Error:
            print()
            print(f"LCARS: NEURAL CORE ERROR — {Error}")

            # Невдалий запит не повинен залишатися в історії.
            if Messages and Messages[-1].get("role") == "user":
                Messages.pop()

        print()


if __name__ == "__main__":
    Main()