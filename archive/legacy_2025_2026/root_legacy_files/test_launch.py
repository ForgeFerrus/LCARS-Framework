#!/usr/bin/env python3
"""
Тестовий запуск LCARS Framework
Мінімальне вікно для перевірки роботи типів
"""

import sys
from lcars.base.type import LCARS, LCARSMatrix, SystemComponent

class TestWindow(LCARSMatrix):
    """Тестове вікно LCARS"""
    
    def __init__(self):
        super().__init__(Id="test_window")
        self.SystemId = "test_window"
        self.Active = True
        
    def Initialize(self) -> bool:
        # Налаштування вікна
        self.SetTitle("LCARS Test Window")
        self.Resize(800, 600)
        self.Move(100, 100)
        return True

def main():
    print("◤ LCARS FRAMEWORK v1.0.0-GOLD ◢")
    print("Запуск тестового вікна...")
    
    # Створення додатка
    App = LCARS.CreateApp(sys.argv)
    if not App:
        print("ПОМИЛКА: Не вдалося створити QApplication")
        return 1
    
    print(f"✓ QApplication створено: {App}")
    
    # Створення вікна
    Window = TestWindow()
    Window.Initialize()
    Window.Show()
    
    print("✓ Вікно показано")
    print("Запуск циклу подій... (Ctrl+C для виходу)")
    
    # Запуск
    return App.exec()

if __name__ == "__main__":
    sys.exit(main())
