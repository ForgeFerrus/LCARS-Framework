"""Запуск QML UI через PySide6.

Цей модуль відповідає за старт графічного інтерфейсу, підключення
Python->QML bridge і завантаження `QML/main.qml` з кореневого каталогу проекту.

Використання:
    python tools/main_qml.py

Примітка:
    Запуск відкриває GUI; для швидкої перевірки синтаксису можна
    виконати `python -m py_compile tools/main_qml.py`.
"""

# Titanium Bridge Migration: import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot
# Titanium Bridge Migration: from pathlib import Path
import argparse


# Міст між QML і Python: тут визначаються слоти, які викликає інтерфейс
class Bridge(QObject):
    """Bridge (міст) для викликів з QML до Python.

    Методи помічені як `@Slot` щоб QML міг їх викликати.
    """

    @Slot()
    def exit_system(self):
        """Закриває програму (виклик з QML)."""
        sys.exit(0)

    @Slot(str)
    def button_clicked(self, button_name):
        """Обробка натискання кнопок з інтерфейсу.

        Поточна реалізація просто лог-фрагменту; сюди можна додати
        маршрутизацію подій або виклики бізнес-логіки програми.
        """
        print(f"Button clicked: {button_name}")


def _qml_file_path() -> Path:
    """Повертає шлях до `main.qml`.

    Перевіряє кілька кандидатів у порядку пріоритету і повертає перший існуючий.
    """
    base = Path(__file__).resolve().parent
    candidates = [
        # стандартний шлях у корені проекту
        base.parent / 'QML' / 'main.qml',
        # запасні варіанти у `tools/qml`
        base / 'qml' / 'generated' / 'MainPanel.qml',
        base / 'qml' / 'KlingonButton.qml',
        # ще один варіант у lcars/qml
        base.parent / 'lcars' / 'qml' / 'generated' / 'WeaponsKlingon.qml',
    ]

    for p in candidates:
        if p.exists():
            print(f"Using QML file: {p}")
            return p
    raise FileNotFoundError(f"No candidate QML file found. Tried: {candidates}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--test-load', action='store_true', help='Only test loading the QML file and exit')
    args, remaining = parser.parse_known_args()

    # Створюємо Qt-додаток
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    bridge = Bridge()

    # Передаємо об'єкт bridge у QML, щоб викликати функції Python з інтерфейсу
    engine.rootContext().setContextProperty("con", bridge)

    # Завантажуємо QML (підтримка запасних шляхів через _qml_file_path)
    qml_path = _qml_file_path()
    engine.load(str(qml_path))

    # Якщо запущено у тестовому режимі — лише перевіряємо, чи завантажився компонент
    if args.test_load:
        if engine.rootObjects():
            print('QML loaded successfully:', qml_path)
            sys.exit(0)
        else:
            print('Failed to load QML:', qml_path)
            sys.exit(1)

    # Якщо кореневі об'єкти не завантажилися — виходимо з помилкою
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
