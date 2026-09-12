#!/usr/bin/env python3
"""
Запуск TCARS 29th Century
"""

import sys
from pathlib import Path

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt6.QtWidgets import QApplication
    from lcars.ui.TCARS_29th import TCARS29thCentury
    print("✅ TCARS 29th Century завантажено")
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)

    # Створюємо TCARS вікно
    tcars = TCARS29thCentury()

    # Налаштовуємо інтерфейс
    tcars.setup_interface()

    tcars.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
