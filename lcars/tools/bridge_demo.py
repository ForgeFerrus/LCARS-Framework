"""Console demo that simulates QML calling the Python `Bridge`.

This script does NOT require PySide6 — it shows how QML would call
`con.button_clicked(...)` and `con.exit_system()` by invoking the
corresponding Python methods (slots).

Запуск:
    python tools/bridge_demo.py
"""

import time


class Bridge:
    """Імітація мосту (Bridge) між QML і Python.

    Методи відповідають слотам, які в реальному додатку оголошені
    як `@Slot()` і доступні з QML через `engine.rootContext().setContextProperty("con", bridge)`.
    """

    def exit_system(self):
        # У реальному додатку тут викликається sys.exit(0)
        print("[Bridge] exit_system() called -> (would exit application)")

    def button_clicked(self, button_name: str):
        print(f"[Bridge] button_clicked: {button_name}")
        # Тут могла б бути маршрутизація подій у бізнес-логіку


def simulate_user_interaction(bridge: Bridge):
    """Імітує послідовність подій від інтерфейсу (QML)."""
    buttons = ["WEAPONS", "ENGINE", "MAIN_PANEL", "SHUTDOWN"]
    for b in buttons:
        print(f"[QML] Simulating click on '{b}'")
        bridge.button_clicked(b)
        time.sleep(0.2)

    # Імітуємо виклик завершення системи
    print("[QML] Simulating system exit")
    bridge.exit_system()


if __name__ == "__main__":
    bridge = Bridge()
    simulate_user_interaction(bridge)
