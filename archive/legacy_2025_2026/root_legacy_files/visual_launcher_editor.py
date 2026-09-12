#!/usr/bin/env python3
"""Візуальний редактор позицій кнопок для LCARS лаунчера

Дозволяє вручну розставити кнопки на зображенні і зберегти позиції
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                            QWidget, QPushButton, QHBoxLayout, QTextEdit)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint

# Імпортуємо LCARS компоненти
from lcars.themes.eras.pcars22_components import PCARS22MiniButton, PCARS22Button
from lcars.themes.eras.PCARSPanel import PCARS22Screen

class DraggableLCARSButton:
    """Клас для перетягуваних кнопок LCARS"""
    def __init__(self, button_type, label, parent_widget, x=100, y=100):
        self.button_type = button_type
        self.label = label
        self.parent_widget = parent_widget
        self.dragging = False
        self.offset = QPoint()
        
        # Створюємо відповідний тип кнопки
        if button_type == "mini":
            self.widget = PCARS22MiniButton(label=label, size=70, color_index=0, parent=parent_widget)
            self.widget.setFixedSize(90, 70)
        elif button_type == "era":
            self.widget = PCARS22Button(number=label, label=label, width=260, height=70, border=0, parent=parent_widget)
            self.widget.setFixedSize(120, 80)
        elif button_type == "screen":
            self.widget = PCARS22Screen(parent=parent_widget)
            self.widget.setFixedSize(600, 350)
        else:  # label
            self.widget = QLabel(label, parent=parent_widget)
            self.widget.setStyleSheet("color: #FFCC33; font-size: 24px; font-weight: bold; background: transparent;")
            self.widget.setFixedSize(200, 40)
        
        self.widget.move(x, y)
        self.widget.show()
        
        # Підключаємо події миші
        self.widget.mousePressEvent = self.mouse_press_event
        self.widget.mouseMoveEvent = self.mouse_move_event
        self.widget.mouseReleaseEvent = self.mouse_release_event
    
    def mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
    
    def mouse_move_event(self, event):
        if self.dragging:
            new_pos = event.position().toPoint() - self.offset
            self.widget.move(self.widget.pos() + new_pos)
            self.offset = event.position().toPoint()
    
    def mouse_release_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            pos = self.widget.pos()
            print(f"{self.label}: ({pos.x()}, {pos.y()})")
    
    def get_position(self):
        pos = self.widget.pos()
        return (pos.x(), pos.y(), self.widget.width(), self.widget.height())

class VisualLauncherEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = [
            "C:\\Users\\Forge\\MyProject\\LCARS-Framework\\resources\\PCARS_22.png",
            "C:\\Users\\Forge\\MyProject\\LCARS-Framework\\resources\\COMS2.png"
        ]
        self.current_image_index = 0
        self.draggable_buttons = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Visual Editor - Розставте кнопки вручну")
        self.showFullScreen()
        
        # Створюємо головний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Фонове зображення
        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        
        # Панель керування
        control_panel = QWidget(central_widget)
        control_panel.setGeometry(10, 10, 300, 400)
        control_panel.setStyleSheet("background: rgba(0,0,0,0.8); border: 2px solid #FFCC33;")
        
        layout = QVBoxLayout(control_panel)
        
        # Інструкція
        instruction = QLabel("Перетягуйте кнопки на потрібні місця")
        instruction.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
        layout.addWidget(instruction)
        
        # Кнопки для додавання елементів
        add_faction_btn = QPushButton("Додати кнопки фракцій")
        add_faction_btn.clicked.connect(self.add_faction_buttons)
        layout.addWidget(add_faction_btn)
        
        add_side_btn = QPushButton("Додати DATE/MOD/BACK")
        add_side_btn.clicked.connect(self.add_side_buttons)
        layout.addWidget(add_side_btn)
        
        add_era_btn = QPushButton("Додати кнопки епох")
        add_era_btn.clicked.connect(self.add_era_buttons)
        layout.addWidget(add_era_btn)
        
        add_activate_btn = QPushButton("Додати ACTIVATE")
        add_activate_btn.clicked.connect(self.add_activate_button)
        layout.addWidget(add_activate_btn)
        
        add_title_btn = QPushButton("Додати заголовок")
        add_title_btn.clicked.connect(self.add_title)
        layout.addWidget(add_title_btn)
        
        add_screen_btn = QPushButton("Додати центральний екран")
        add_screen_btn.clicked.connect(self.add_info_screen)
        layout.addWidget(add_screen_btn)
        
        # Кнопка збереження
        save_btn = QPushButton("Зберегти позиції")
        save_btn.setStyleSheet("background: #00AA00; color: white; font-size: 16px;")
        save_btn.clicked.connect(self.save_positions)
        layout.addWidget(save_btn)
        
        # Кнопка очищення
        clear_btn = QPushButton("Очистити все")
        clear_btn.setStyleSheet("background: #AA0000; color: white;")
        clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(clear_btn)
        
        # Поле для відображення позицій
        self.positions_text = QTextEdit()
        self.positions_text.setMaximumHeight(150)
        self.positions_text.setStyleSheet("background: black; color: white; font-family: monospace;")
        layout.addWidget(self.positions_text)
        
        # Завантажуємо зображення
        self.update_image()
        
        # Таймер для зміни зображень
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_image)
        self.timer.start(5000)  # Кожні 5 секунд
    
    def add_faction_buttons(self):
        """Додає кнопки фракцій"""
        labels = ["FED", "KLI", "ROM", "CAR"]
        start_x = 50
        start_y = 200
        
        for i, label in enumerate(labels):
            button = DraggableLCARSButton("mini", label, self.image_label, 
                                        start_x, start_y + i * 100)
            button.widget.setStyleSheet("")  # Очищуємо стилі щоб було видно
            self.draggable_buttons.append(button)
        
        self.update_positions_display()
    
    def add_side_buttons(self):
        """Додає кнопки DATE/MOD/BACK"""
        labels = ["DATE", "MOD", "BACK"]
        start_x = 400
        start_y = 50
        
        for i, label in enumerate(labels):
            button = DraggableLCARSButton("mini", label, self.image_label,
                                        start_x + i * 100, start_y)
            self.draggable_buttons.append(button)
        
        self.update_positions_display()
    
    def add_era_buttons(self):
        """Додає кнопки епох"""
        labels = ["22-TH", "23-RD", "23-ST", "24-TH", "25-TH", "29-TH"]
        
        # Ліві кнопки
        for i, label in enumerate(labels[:3]):
            button = DraggableLCARSButton("era", label, self.image_label,
                                        50, 150 + i * 100)
            self.draggable_buttons.append(button)
        
        # Праві кнопки
        for i, label in enumerate(labels[3:]):
            button = DraggableLCARSButton("era", label, self.image_label,
                                        self.width() - 200, 150 + i * 100)
            self.draggable_buttons.append(button)
        
        self.update_positions_display()
    
    def add_activate_button(self):
        """Додає кнопку ACTIVATE"""
        button = DraggableLCARSButton("era", "ACTIVATE", self.image_label,
                                    self.width()//2 - 110, self.height() - 150)
        self.draggable_buttons.append(button)
        self.update_positions_display()
    
    def add_title(self):
        """Додає заголовок"""
        button = DraggableLCARSButton("label", "SELECT FACTION", self.image_label,
                                    self.width()//2 - 100, 100)
        self.draggable_buttons.append(button)
        self.update_positions_display()
    
    def add_info_screen(self):
        """Додає центральний екран"""
        button = DraggableLCARSButton("screen", "", self.image_label,
                                    self.width()//2 - 300, self.height()//2 - 175)
        self.draggable_buttons.append(button)
        self.update_positions_display()
    
    def clear_all(self):
        """Очищує всі кнопки"""
        for button in self.draggable_buttons:
            button.widget.deleteLater()
        self.draggable_buttons.clear()
        self.positions_text.clear()
    
    def update_positions_display(self):
        """Оновлює відображення позицій"""
        positions = {}
        for button in self.draggable_buttons:
            if button.label not in positions:
                positions[button.label] = []
            positions[button.label].append(button.get_position())
        
        text = "Поточні позиції:\\n"
        for label, pos_list in positions.items():
            for pos in pos_list:
                text += f"{label}: {pos}\\n"
        
        self.positions_text.setText(text)
    
    def save_positions(self):
        """Зберігає позиції у файл"""
        positions = {}
        for button in self.draggable_buttons:
            if button.button_type == "mini" and button.label in ["FED", "KLI", "ROM", "CAR"]:
                if "faction_buttons" not in positions:
                    positions["faction_buttons"] = []
                positions["faction_buttons"].append(button.get_position())
            elif button.button_type == "mini" and button.label in ["DATE", "MOD", "BACK"]:
                if "side_buttons" not in positions:
                    positions["side_buttons"] = []
                positions["side_buttons"].append(button.get_position())
            elif button.button_type == "era" and button.label != "ACTIVATE":
                if "era_buttons" not in positions:
                    positions["era_buttons"] = []
                positions["era_buttons"].append(button.get_position())
            elif button.label == "ACTIVATE":
                positions["activate_button"] = button.get_position()
            elif button.button_type == "label":
                positions["title"] = button.get_position()
            elif button.button_type == "screen":
                positions["info_screen"] = button.get_position()
        
        # Зберігаємо у JSON файл
        with open('launcher_positions_manual.json', 'w', encoding='utf-8') as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)
        
        print("Позиції збережено у launcher_positions_manual.json")
        
        # Генеруємо код для лаунчера
        code = self.generate_launcher_code(positions)
        with open('launcher_positions_manual.py', 'w', encoding='utf-8') as f:
            f.write(code)
        
        print("Код збережено у launcher_positions_manual.py")
    
    def generate_launcher_code(self, positions):
        """Генерує код для лаунчера"""
        code = "# Ручні позиції для лаунчера\\n\\n"
        
        if "faction_buttons" in positions:
            code += f"faction_positions = {positions['faction_buttons']}\\n"
        
        if "side_buttons" in positions:
            code += f"side_positions = {positions['side_buttons']}\\n"
        
        if "era_buttons" in positions:
            code += f"era_positions = {positions['era_buttons']}\\n"
        
        if "activate_button" in positions:
            code += f"activate_position = {positions['activate_button']}\\n"
        
        if "title" in positions:
            code += f"title_position = {positions['title']}\\n"
        
        if "info_screen" in positions:
            code += f"info_screen_position = {positions['info_screen']}\\n"
        
        return code
    
    def change_image(self):
        """Змінює фонове зображення"""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_image()
    
    def update_image(self):
        """Оновлює фонове зображення"""
        image_path = self.images[self.current_image_index]
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            print(f"Показано зображення: {os.path.basename(image_path)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VisualLauncherEditor()
    editor.show()
    sys.exit(app.exec())
