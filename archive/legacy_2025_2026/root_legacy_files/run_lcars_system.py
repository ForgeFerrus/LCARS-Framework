#!/usr/bin/env python3
"""
Запуск LCARS системи зі згенерованих компонентів
Демонстрація повноцінного інтерфейсу
"""

import sys
import os
from pathlib import Path

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QQuickWidget
    from PyQt6.QtCore import QUrl, QTimer
    from PyQt6.QtQml import QQmlApplicationEngine
except ImportError:
    print("❌ PyQt6 не встановлено. Встановіть: pip install PyQt6")
    sys.exit(1)

class LcarsSystemWindow(QMainWindow):
    """Головне вікно LCARS системи"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 LCARS System - Generated Components")
        self.setGeometry(100, 100, 1200, 800)
        
        # Створюємо QML віджет
        self.qml_widget = QQuickWidget()
        self.setCentralWidget(self.qml_widget)
        
        # Завантажуємо QML файл
        qml_path = Path(__file__).parent / "lcars_system_demo.qml"
        self.qml_widget.setSource(QUrl.fromLocalFile(str(qml_path)))
        
        # Перевіряємо чи завантажився QML
        if not self.qml_widget.rootObject():
            print("❌ Помилка завантаження QML файлу")
            sys.exit(1)
        
        print("✅ LCARS система завантажена успішно!")
        self.setup_status_timer()
    
    def setup_status_timer(self):
        """Налаштування таймера для оновлення статусу"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Оновлення кожну секунду
    
    def update_status(self):
        """Оновлення статусу системи"""
        # Тут можна додати логіку оновлення статусу
        pass

def show_system_info():
    """Показує інформацію про систему"""
    print("🚀 LCARS SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    # Перевіряємо наявність згенерованих компонентів
    generated_dir = Path(__file__).parent / "lcars" / "qml" / "generated"
    
    if generated_dir.exists():
        qml_files = list(generated_dir.glob("*.qml"))
        print(f"📁 Знайдено {len(qml_files)} згенерованих компонентів:")
        
        # Групуємо за типами
        klingon_files = [f for f in qml_files if 'klingon' in f.name.lower()]
        romulan_files = [f for f in qml_files if 'romulan' in f.name.lower()]
        cardassian_files = [f for f in qml_files if 'cardassian' in f.name.lower()]
        panel_files = [f for f in qml_files if 'panel' in f.name.lower()]
        
        print(f"   🔺 Клінгонські: {len(klingon_files)}")
        print(f"   🔻 Ромуланські: {len(romulan_files)}")
        print(f"   🔶 Кардасіанські: {len(cardassian_files)}")
        print(f"   📋 Панелі: {len(panel_files)}")
    else:
        print("❌ Папка згенерованих компонентів не знайдена")
        print("💡 Запустіть: python demo_component_factory.py")
    
    print("\n🎯 Система містить:")
    print("   ✅ Головний дисплей з радаром")
    print("   ✅ Тактичні панелі")
    print("   ✅ Системні індикатори")
    print("   ✅ Комунікаційну панель")
    print("   ✅ Статусні монітори")
    print("   ✅ Контрольні панелі")
    
    print("\n🔧 Компоненти згенеровані через Component Factory:")
    print("   📋 Автоматична генерація QML коду")
    print("   🎨 Динамічні кольори фракцій")
    print("   ✨ Анімації та ефекти")
    print("   🔄 Інтерактивні елементи")

def main():
    """Головна функція"""
    show_system_info()
    
    print("\n🚀 Запуск LCARS системи...")
    print("💡 Для виходу закрийте вікно")
    
    app = QApplication(sys.argv)
    
    # Налаштування стилю
    app.setStyle('Fusion')
    
    # Створення головного вікна
    window = LcarsSystemWindow()
    window.show()
    
    # Запуск додатку
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
