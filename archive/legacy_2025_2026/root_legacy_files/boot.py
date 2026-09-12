"""
LCARS Boot - просто передача в консоль на екран
"""

import sys
from pathlib import Path

# Додаємо шлях
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    # Створюємо QApplication для показу консолі на екран
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
    from PyQt6.QtCore import Qt
    
    app = QApplication(sys.argv)
    
    # Створюємо вікно консолі
    console = QMainWindow()
    console.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    console.showFullScreen()
    console.setStyleSheet("background-color: #000000;")
    
    central = QWidget()
    console.setCentralWidget(central)
    layout = QVBoxLayout(central)
    
    # Заголовок
    header = QLabel("LCARS BOOT v0.1.0-alpha")
    header.setStyleSheet("""
        QLabel {
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        }
    """)
    layout.addWidget(header)
    
    # Консольний вивід
    console_output = QTextEdit()
    console_output.setStyleSheet("""
        QTextEdit {
            background-color: #000000;
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border: 1px solid #00FF00;
        }
    """)
    console_output.setReadOnly(True)
    layout.addWidget(console_output)
    
    # Кнопка продовження
    continue_btn = QPushButton("Continue")
    continue_btn.setStyleSheet("""
        QPushButton {
            background-color: #00FF00;
            color: #000000;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
        }
    """)
    layout.addWidget(continue_btn)
    
    console.show()
    
    # Функція виводу в консоль
    def print_to_console(text):
        console_output.append(text)
        app.processEvents()
    
    # Показуємо повідомлення тільки на екрані
    print_to_console("Starting LCARS Framework...")
    print_to_console("Checking components...")
    
    # Перевіряємо файли системи без імпортів
    try:
        from pathlib import Path
        
        # Перевіряємо існування файлів
        files_to_check = [
            ("lcars/base/default.py", "LCARS Base"),
            ("lcars/ui/screen/loading.py", "Loading Screen"),
            ("lcars/ui/screen/login.py", "Login Screen"),
            ("lcars/ui/desktop.py", "Desktop"),
            ("lcars/base/version.py", "Version System")
        ]
        
        for file_path, description in files_to_check:
            if Path(file_path).exists():
                print_to_console(f"[OK] {description}: OK")
            else:
                print_to_console(f"[ERROR] {description}: NOT FOUND")
        
        print_to_console("\n[SUCCESS] System check completed")
        print_to_console("Click Continue to start LCARS...")
        
    except Exception as e:
        print_to_console(f"[ERROR] System check failed: {e}")
        print_to_console("[INFO] Falling back to emergency mode...")
        
        # Показуємо помилку і не вилітаємо
        def emergency_boot():
            console.close()
            print("[EMERGENCY MODE] System failure detected")
            print("[EMERGENCY MODE] Starting minimal LCARS...")
            
            try:
                from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
                from PyQt6.QtCore import Qt
                
                app = QApplication(sys.argv)
                emergency = QMainWindow()
                emergency.setWindowFlag(Qt.WindowType.FramelessWindowHint)
                emergency.showFullScreen()
                emergency.setStyleSheet("background-color: #FF0000;")
                
                central = QWidget()
                emergency.setCentralWidget(central)
                layout = QVBoxLayout(central)
                
                error_label = QLabel("EMERGENCY MODE\nSystem failure detected")
                error_label.setStyleSheet("""
                    QLabel {
                        color: #FFFFFF;
                        font-family: 'Courier New', monospace;
                        font-size: 24px;
                        font-weight: bold;
                        padding: 20px;
                    }
                """)
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(error_label)
                
                shutdown_btn = QPushButton("Shutdown")
                shutdown_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF;
                        color: #FF0000;
                        font-family: 'Courier New', monospace;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                    }
                """)
                shutdown_btn.clicked.connect(app.quit)
                layout.addWidget(shutdown_btn)
                
                emergency.show()
                return app.exec()
                
            except Exception as emergency_e:
                print(f"[CRITICAL] Emergency mode failed: {emergency_e}")
                return 1
        
        # Замінюємо кнопку на emergency
        continue_btn.setText("Emergency Mode")
        continue_btn.clicked.connect(emergency_boot)
    
    # Функція для продовження
    def continue_boot():
        console.close()
        
        # Імпортуємо тільки коли потрібно
        from lcars.ui.screen.loading import LCARSLoading
        from lcars.ui.screen.login import LCARSLogin
        from lcars.ui.desktop import LCARSDesktop
        
        # Створюємо завантаження
        loading = LCARSLoading()
        loading.show()
        
        # Створюємо логін
        try:
            login = LCARSLogin()
            login.show()
        except:
            desktop = LCARSDesktop()
            desktop.show()
    
    continue_btn.clicked.connect(continue_boot)
    
    return app.exec()

if __name__ == "__main__":
    main()
