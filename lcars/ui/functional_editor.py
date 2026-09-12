"""
Функціональний LCARS редактор - простий керування елементами
"""

# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget, 
                           QTableWidget, QTableWidgetItem, QTextEdit, 
                           QColorDialog, QFontDialog, QSpinBox, QComboBox,
                           QGroupBox, QFormLayout, QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Кольори для епох
ERA_COLORS = {
    "22nd": {"bg": "#1E3A8A", "text": "#E0E0FF", "border": "#4C4C7A"},
    "23rd": {"bg": "#FF0000", "text": "#FFFFFF", "border": "#D3A200"},
    "24th": {"bg": "#FFCC66", "text": "#000000", "border": "#664466"}
}

class LCARSElement(QWidget):
    """Базовий елемент LCARS"""
    
    def __init__(self, element_type="button", text="BUTTON", era="22nd", parent=None):
        super().__init__(parent)
        self.element_type = element_type
        self.text = text
        self.era = era
        self.bg_color = ERA_COLORS[era]["bg"]
        self.text_color = ERA_COLORS[era]["text"]
        self.border_color = ERA_COLORS[era]["border"]
        self.border_radius = 5
        self.font_size = 12
        self.setup_ui()
        
    def setup_ui(self):
        self.apply_style()
        
    def apply_style(self):
        if self.element_type == "button":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.bg_color};
                    color: {self.text_color};
                    border: 2px solid {self.border_color};
                    border-radius: {self.border_radius}px;
                    padding: 8px 16px;
                    font-size: {self.font_size}px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
                QPushButton:pressed {{
                    opacity: 0.6;
                }}
            """)
        elif self.element_type == "label":
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.bg_color};
                    color: {self.text_color};
                    border: 1px solid {self.border_color};
                    border-radius: {self.border_radius}px;
                    padding: 5px;
                    font-size: {self.font_size}px;
                    font-weight: bold;
                }}
            """)
        elif self.element_type == "panel":
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.bg_color};
                    border: 2px solid {self.border_color};
                    border-radius: {self.border_radius}px;
                }}
            """)
    
    def update_style(self):
        self.apply_style()
        self.update()

class FunctionalLCARSEditor(QMainWindow):
    """Функціональний редактор LCARS"""
    
    element_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FUNCTIONAL LCARS EDITOR")
        self.setGeometry(100, 100, 1400, 800)
        
        self.elements = []
        self.selected_element = None
        self.setup_ui()
        
    def setup_ui(self):
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Ліва панель - керування
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Заголовок
        header = QLabel("LCARS EDITOR")
        header.setStyleSheet("""
            QLabel {
                color: #FFE600;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                padding: 10px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(header)
        
        # Створення елементів
        create_group = QGroupBox("Create Elements")
        create_layout = QVBoxLayout(create_group)
        
        # Вибір епохи
        era_layout = QHBoxLayout()
        era_layout.addWidget(QLabel("Era:"))
        self.era_combo = QComboBox()
        self.era_combo.addItems(["22nd", "23rd", "24th"])
        self.era_combo.currentTextChanged.connect(self.on_era_changed)
        era_layout.addWidget(self.era_combo)
        create_layout.addLayout(era_layout)
        
        # Кнопки створення
        self.create_button_btn = QPushButton("Create Button")
        self.create_button_btn.clicked.connect(lambda: self.create_element("button"))
        create_layout.addWidget(self.create_button_btn)
        
        self.create_label_btn = QPushButton("Create Label")
        self.create_label_btn.clicked.connect(lambda: self.create_element("label"))
        create_layout.addWidget(self.create_label_btn)
        
        self.create_panel_btn = QPushButton("Create Panel")
        self.create_panel_btn.clicked.connect(lambda: self.create_element("panel"))
        create_layout.addWidget(self.create_panel_btn)
        
        left_layout.addWidget(create_group)
        
        # Редагування елементів
        edit_group = QGroupBox("Edit Selected Element")
        edit_layout = QFormLayout(edit_group)
        
        # Текст
        self.text_edit = QLineEdit()
        self.text_edit.textChanged.connect(self.update_element_text)
        edit_layout.addRow("Text:", self.text_edit)
        
        # Фоновий колір
        self.bg_color_btn = QPushButton("Background Color")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        edit_layout.addRow("BG Color:", self.bg_color_btn)
        
        # Колір тексту
        self.text_color_btn = QPushButton("Text Color")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        edit_layout.addRow("Text Color:", self.text_color_btn)
        
        # Розмір шрифту
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        edit_layout.addRow("Font Size:", self.font_size_spin)
        
        # Радіус рамки
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 50)
        self.border_radius_spin.setValue(5)
        self.border_radius_spin.valueChanged.connect(self.update_border_radius)
        edit_layout.addRow("Border Radius:", self.border_radius_spin)
        
        # Видалення
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setStyleSheet("background-color: #CC3333; color: white;")
        edit_layout.addRow(self.delete_btn)
        
        left_layout.addWidget(edit_group)
        
        # Список елементів
        list_group = QGroupBox("Elements List")
        list_layout = QVBoxLayout(list_group)
        
        self.elements_list = QListWidget()
        self.elements_list.itemSelectionChanged.connect(self.on_element_selected)
        list_layout.addWidget(self.elements_list)
        
        left_layout.addWidget(list_group)
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        
        # Права панель - робоча область
        self.work_area = QWidget()
        self.work_area.setStyleSheet("background-color: #000000;")
        self.work_layout = QVBoxLayout(self.work_area)
        self.work_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок робочої області
        work_header = QLabel("WORK AREA - Click elements to select")
        work_header.setStyleSheet("""
            QLabel {
                color: #FFE600;
                font-size: 14px;
                background: transparent;
                padding: 10px;
            }
        """)
        work_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.work_layout.addWidget(work_header)
        
        # Контейнер для елементів
        self.elements_container = QWidget()
        self.elements_container.setStyleSheet("background-color: #111111;")
        self.elements_layout = QVBoxLayout(self.elements_container)
        self.work_layout.addWidget(self.elements_container, 1)
        
        main_layout.addWidget(self.work_area, 1)
        
        # Спочатку вимикаємо редагування
        self.set_editing_enabled(False)
        
    def create_element(self, element_type):
        """Створити новий елемент"""
        era = self.era_combo.currentText()
        element = LCARSElement(element_type, f"{element_type.upper()}", era, self.elements_container)
        
        # Додаємо можливість вибору
        element.mousePressEvent = lambda e: self.select_element(element)
        
        self.elements.append(element)
        self.elements_layout.addWidget(element)
        
        # Додаємо в список
        list_item = f"{element_type.upper()} - {element.text} ({era})"
        self.elements_list.addItem(list_item)
        
        # Автоматично вибираємо створений елемент
        self.select_element(element)
        
    def select_element(self, element):
        """Вибрати елемент для редагування"""
        self.selected_element = element
        
        # Оновлюємо список
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if item.text().startswith(element.element_type.upper()):
                self.elements_list.setCurrentItem(item)
                break
        
        # Вмикаємо редагування
        self.set_editing_enabled(True)
        
        # Оновлюємо значення в полях
        self.text_edit.setText(element.text)
        self.font_size_spin.setValue(element.font_size)
        self.border_radius_spin.setValue(element.border_radius)
        
    def set_editing_enabled(self, enabled):
        """Ввімкнути/вимкнути редагування"""
        self.text_edit.setEnabled(enabled)
        self.bg_color_btn.setEnabled(enabled)
        self.text_color_btn.setEnabled(enabled)
        self.font_size_spin.setEnabled(enabled)
        self.border_radius_spin.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
        
    def on_element_selected(self):
        """Обробка вибору елемента зі списку"""
        current_item = self.elements_list.currentItem()
        if current_item:
            # Знаходимо відповідний елемент
            for element in self.elements:
                if current_item.text().startswith(element.element_type.upper()):
                    self.select_element(element)
                    break
                    
    def on_era_changed(self, era):
        """Обробка зміни епохи"""
        # Оновлюємо кольори для нових елементів
        pass
        
    def update_element_text(self):
        """Оновити текст елемента"""
        if self.selected_element:
            self.selected_element.text = self.text_edit.text()
            if hasattr(self.selected_element, 'setText'):
                self.selected_element.setText(self.text_edit.text())
            self.selected_element.update_style()
            
            # Оновлюємо список
            self.update_elements_list()
            
    def update_elements_list(self):
        """Оновити список елементів"""
        self.elements_list.clear()
        for element in self.elements:
            list_item = f"{element.element_type.upper()} - {element.text} ({element.era})"
            self.elements_list.addItem(list_item)
            
    def choose_bg_color(self):
        """Вибрати фоновий колір"""
        if self.selected_element:
            color = QColorDialog.getColor(QColor(self.selected_element.bg_color), self)
            if color.isValid():
                self.selected_element.bg_color = color.name()
                self.selected_element.update_style()
                
    def choose_text_color(self):
        """Вибрати колір тексту"""
        if self.selected_element:
            color = QColorDialog.getColor(QColor(self.selected_element.text_color), self)
            if color.isValid():
                self.selected_element.text_color = color.name()
                self.selected_element.update_style()
                
    def update_font_size(self, size):
        """Оновити розмір шрифту"""
        if self.selected_element:
            self.selected_element.font_size = size
            self.selected_element.update_style()
            
    def update_border_radius(self, radius):
        """Оновити радіус рамки"""
        if self.selected_element:
            self.selected_element.border_radius = radius
            self.selected_element.update_style()
            
    def delete_selected(self):
        """Видалити вибраний елемент"""
        if self.selected_element:
            # Видаляємо з контейнера
            self.elements_layout.removeWidget(self.selected_element)
            self.selected_element.setParent(None)
            self.selected_element.deleteLater()
            
            # Видаляємо зі списку
            self.elements.remove(self.selected_element)
            self.selected_element = None
            
            # Оновлюємо список
            self.update_elements_list()
            
            # Вимикаємо редагування
            self.set_editing_enabled(False)

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо шрифт
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = FunctionalLCARSEditor()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
