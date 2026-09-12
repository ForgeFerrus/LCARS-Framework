"""
Простий запускач Python-файлів
"""
import os
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QListWidget, QLabel, 
                           QFileDialog, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QDir

class FileRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Runner")
        self.setGeometry(100, 100, 1000, 700)
        
        # Основний віджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Головний лейаут
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Створюємо спліттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Ліва панель - список файлів
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Кнопка вибору папки
        self.btn_open = QPushButton("Відкрити папку")
        self.btn_open.clicked.connect(self.open_folder)
        left_layout.addWidget(self.btn_open)
        
        # Список файлів
        self.file_list = QListWidget()
        self.file_list.doubleClicked.connect(self.run_selected_file)
        left_layout.addWidget(self.file_list)
        
        # Права панель - вміст файлу
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Заголовок
        self.file_title = QLabel("Виберіть файл для перегляду")
        right_layout.addWidget(self.file_title)
        
        # Вміст файлу
        self.file_content = QTextEdit()
        self.file_content.setReadOnly(True)
        self.file_content.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #ccc;
            }
        """)
        right_layout.addWidget(self.file_content)
        
        # Кнопка запуску
        self.btn_run = QPushButton("Запустити файл (F5)")
        self.btn_run.clicked.connect(self.run_selected_file)
        right_layout.addWidget(self.btn_run)
        
        # Додаємо панелі до спліттера
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        # Додаємо спліттер до головного лейаута
        layout.addWidget(splitter)
        
        # Змінні
        self.current_dir = os.getcwd()
        self.current_file = None
        
        # Завантажуємо файли поточної папки
        self.load_files(self.current_dir)
    
    def open_folder(self):
        """Відкриття папки з файлами"""
        folder = QFileDialog.getExistingDirectory(self, "Виберіть папку з проектом")
        if folder:
            self.current_dir = folder
            self.load_files(folder)
    
    def load_files(self, folder):
        """Завантаження списку Python-файлів"""
        self.file_list.clear()
        self.file_title.setText(f"Папка: {folder}")
        
        # Додаємо всі Python-файли у списку
        for file in sorted(os.listdir(folder)):
            if file.endswith('.py'):
                self.file_list.addItem(file)
        
        # Вибираємо перший файл
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)
            self.show_file_content(self.file_list.currentItem().text())
    
    def show_file_content(self, filename):
        """Відображення вмісту файлу"""
        file_path = os.path.join(self.current_dir, filename)
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_content.setPlainText(content)
                self.file_title.setText(f"Файл: {filename}")
        except Exception as e:
            self.file_content.setPlainText(f"Помилка читання файлу:\n{str(e)}")
    
    def run_selected_file(self):
        """Запуск вибраного файлу"""
        if not self.file_list.currentItem():
            return
            
        filename = self.file_list.currentItem().text()
        file_path = os.path.join(self.current_dir, filename)
        
        try:
            # Очищаємо консоль
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/Mac
                os.system('clear')
                
            print(f"Запуск файлу: {filename}")
            print("=" * 80)
            
            # Запускаємо файл
            subprocess.run([sys.executable, file_path], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Помилка при виконанні файлу: {e}")
        except Exception as e:
            print(f"Невідома помилка: {e}")
        
        print("\n" + "=" * 80)
        input("Натисніть Enter для продовження...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Встановлюємо шрифт
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    window = FileRunner()
    window.show()
    sys.exit(app.exec())