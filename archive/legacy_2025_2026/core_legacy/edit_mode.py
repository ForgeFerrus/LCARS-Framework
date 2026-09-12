"""
LCARS Framework - Edit Mode Module
"""

# Titanium Bridge Migration: import json
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSlider, QDialog, QColorDialog, QFileDialog,
                            QLineEdit, QSpinBox, QMenu)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen

class EditMode(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.enabled = False
        self.elements = []
        self.selected = None
        self._drag = None
        self._drag_offset = None
        
        # Для зміни розміру
        self.resize_handles = []
        self._resize_handle = None
        self._resize_start_pos = None
        self._original_geom = None
        self.selected_widget = None
        
        # Встановлюємо event filter
        self.parent.installEventFilter(self)
        
        # Створюємо UI
        self.create_edit_ui()
    
    def create_edit_ui(self):
        """Створення інтерфейсу режиму редагування"""
        
        # Кнопка MOD
        self.edit_btn = QPushButton("MOD", self.parent)
        self.edit_btn.setGeometry(10, 10, 120, 32)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                color: #FFF;
                border: 2px solid #666;
                border-radius: 6px;
                font-weight: bold;
                padding: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        
        # Toolbar
        self.toolbar = QWidget(self.parent)
        self.toolbar.setGeometry(10, 50, 150, 400)
        self.toolbar.setStyleSheet("""
            QWidget {
                background: #222;
                border: 2px solid #444;
                border-radius: 8px;
            }
        """)
        self.toolbar.hide()
        
        toolbar_layout = QVBoxLayout(self.toolbar)
        
        # Кнопки компонентів
        self.palette_buttons = {}
        component_descriptions = {
            'panel': 'ПАНЕЛЬ',
            'button': 'КНОПКА',
            'mini': 'МІНІ-КНОПКА',
            'text': 'ТЕКСТ',
            'image': 'ЗОБРАЖЕННЯ',
            'rect': 'ПРЯМОКУТНИК',
            'square': 'КВАДРАТ',
            'circle': 'КОЛО',
            'triangle': 'ТРИКУТНИК',
        }
        
        for idx, key in enumerate(self.component_palette):
            description = component_descriptions.get(key, key.upper())
            
            btn = QPushButton(description, self.toolbar)
            btn.setGeometry(10, 10 + idx * 35, 130, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: #3399FF;
                    color: #FFF;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background: #55AAFF;
                }
                QPushButton:pressed {
                    background: #0066CC;
                    transform: scale(0.95);
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self.add_element(k))
            self.palette_buttons[key] = btn
            toolbar_layout.addWidget(btn)
        
        # Кнопки дій
        properties_btn = QPushButton("🔧 ВЛАСТИВОСТІ", self.toolbar)
        properties_btn.setStyleSheet("""
            QPushButton {
                background: #0066CC;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        properties_btn.clicked.connect(self.show_properties_dialog)
        toolbar_layout.addWidget(properties_btn)
        
        copy_btn = QPushButton("📋 КОПІЮВАТИ", self.toolbar)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: #FF9900;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        copy_btn.clicked.connect(self.copy_selected)
        toolbar_layout.addWidget(copy_btn)
        
        delete_btn = QPushButton("🗑️ ВИДАЛИТИ", self.toolbar)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #CC0000;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected)
        toolbar_layout.addWidget(delete_btn)
        
        # Кнопки збереження/завантаження
        save_btn = QPushButton("💾 ЗБЕРЕГТИ", self.toolbar)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #00AA00;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        save_btn.clicked.connect(self.save_layout)
        toolbar_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📁 ЗАВАНТАЖИТИ", self.toolbar)
        load_btn.setStyleSheet("""
            QPushButton {
                background: #AA6600;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        load_btn.clicked.connect(self.load_layout)
        toolbar_layout.addWidget(load_btn)
    
    def toggle_edit_mode(self):
        """Перемикач режиму редагування"""
        self.enabled = not self.enabled
        print(f"EditMode toggled: {self.enabled}")
        
        if self.enabled:
            # РЕЖИМ ВВІМКНЕНО - робимо кнопку зеленою і показуємо toolbar
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: #090;  # Яскраво-зелений
                    background: #090;
                    color: #FFF;
                    border: 2px solid #0F0;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 4px;
                }
            """)
            self.toolbar.show()
            print("✅ Toolbar показано")
        else:
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: #333;
                    color: #FFF;
                    border: 2px solid #666;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 4px;
                }
            """)
            self.toolbar.hide()
            self.clear_resize_handles()
            self.selected = None
            self.parent.update()
            print("✅ Toolbar сховано")
    
    def eventFilter(self, obj, event):
        """Обробка подій миші"""
        if not self.enabled:
            return False
        
        # Обробка кутів для зміни розміру
        if hasattr(self, 'resize_handles') and obj in self.resize_handles:
            if event.type() == Qt.MouseEventType.MouseButtonPress:
                self._resize_handle = obj
                self._resize_start_pos = event.pos()
                self._original_geom = self.selected_widget.geometry()
                print(f"✅ Resize handle {obj.handle_index} pressed")
                return True
            elif event.type() == Qt.MouseEventType.MouseMove and hasattr(self, '_resize_handle'):
                self.handle_resize(event)
                return True
            elif event.type() == Qt.MouseEventType.MouseButtonRelease and hasattr(self, '_resize_handle'):
                self._resize_handle = None
                print("✅ Resize handle released")
                return True
        
        # Обробка основних подій
        if event.type() == Qt.MouseEventType.MouseButtonPress:
            return self.mouse_press_event(event)
        elif event.type() == Qt.MouseEventType.MouseMove:
            return self.mouse_move_event(event)
        elif event.type() == Qt.MouseEventType.MouseButtonRelease:
            return self.mouse_release_event(event)
            
        return False
    
    def mouse_press_event(self, event):
        """Обробка натискання кнопки миші"""
        # Перевіряємо чи не натиснули на кут
        if hasattr(self, 'resize_handles'):
            for handle in self.resize_handles:
                if handle.geometry().contains(event.pos()):
                    return False
        
        # Шукаємо елемент під курсором
        px, py = event.pos().x(), event.pos().y()
        
        for actual_idx, el in enumerate(reversed(self.elements)):
            widget = el['widget']
            if not widget.isVisible():
                continue
                
            x, y, w, h = el['geom']
            
            # Check element body
            if x <= px <= x + w and y <= py <= y + h:
                self._drag = actual_idx
                self._drag_offset = (px - x, py - y)
                self.selected = actual_idx
                print(f"✅ Selected element {actual_idx}: {el['type']}")
                
                # Показуємо кути
                self.highlight_selected(widget)
                
                self.parent.update()
                return True
        
        # Якщо не натиснули на елемент - скидаємо виділення
        self.clear_resize_handles()
        self.selected = None
        return False
    
    def mouse_move_event(self, event):
        """Обробка руху миші"""
        if self._drag is not None:
            px, py = event.pos().x(), event.pos().y()
            
            # Update element position
            el = self.elements[self._drag]
            x, y, w, h = el['geom']
            new_x = px - self._drag_offset[0]
            new_y = py - self._drag_offset[1]
            el['geom'] = [new_x, new_y, w, h]
            
            self.update_layout()
            self.update_resize_handles()
            self.parent.update()
            return True
        
        return False
    
    def mouse_release_event(self, event):
        """Обробка відпускання кнопки миші"""
        self._drag = None
        return False
    
    def add_element(self, element_type):
        """Додати новий елемент"""
        if not self.enabled:
            return
            
        if element_type in self.component_palette:
            if True:
                widget = self.component_palette[element_type](parent=self.parent)
                
                w, h = widget.width(), widget.height()
                if w == 0 or h == 0:
                    w, h = 120, 40
                    widget.setFixedSize(w, h)
                
                cx, cy = self.parent.width() // 2, self.parent.height() // 2
                
                element = {
                    'type': element_type,
                    'widget': widget,
                    'geom': [cx - w//2, cy - h//2, w, h]
                }
                
                self.elements.append(element)
                self.selected = len(self.elements) - 1
                
                self.update_layout()
                self.parent.update()
                
                # Робимо елемент видимим
                widget.show()
                widget.raise_()
                
                # Додаємо контекстне меню
                widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                widget.customContextMenuRequested.connect(lambda pos: self.show_context_menu(widget, pos))
                
                print(f"✅ Element {element_type} added at ({cx - w//2}, {cy - h//2})")
                
            if False: # Removed except block
                print(f"❌ Error creating element: {e}")
                # Titanium Bridge Migration: import traceback
                traceback.print_exc()
    
    def highlight_selected(self, widget):
        """Показати кути для редагування"""
        self.clear_resize_handles()
        
        self.resize_handles = []
        geom = widget.geometry()
        handle_size = 10
        
        # Створюємо 8 кутів
        positions = [
            (geom.x() - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width()//2 - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() + geom.height()//2 - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() + geom.width()//2 - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() - handle_size//2, geom.y() + geom.height()//2 - handle_size//2),
        ]
        
        for i, (x, y) in enumerate(positions):
            handle = QLabel("", self.parent)
            handle.setGeometry(x, y, handle_size, handle_size)
            handle.setStyleSheet("""
                QLabel {
                    background: #3399FF;
                    border: 2px solid #FFF;
                    border-radius: 3px;
                }
                QLabel:hover {
                    background: #55AAFF;
                    border-color: #FFF;
                }
            """)
            
            cursors = [
                Qt.CursorShape.SizeFDiagCursor,
                Qt.CursorShape.SizeVerCursor,
                Qt.CursorShape.SizeBDiagCursor,
                Qt.CursorShape.SizeHorCursor,
                Qt.CursorShape.SizeFDiagCursor,
                Qt.CursorShape.SizeVerCursor,
                Qt.CursorShape.SizeBDiagCursor,
                Qt.CursorShape.SizeHorCursor,
            ]
            handle.setCursor(cursors[i])
            handle.handle_index = i
            handle.show()
            handle.raise_()
            self.resize_handles.append(handle)
        
        # Встановлюємо event filter для кутів
        for handle in self.resize_handles:
            handle.installEventFilter(self)
        
        self.selected_widget = widget
        print(f"✅ Created {len(self.resize_handles)} resize handles")
    
    def clear_resize_handles(self):
        """Прибрати всі кути"""
        if hasattr(self, 'resize_handles'):
            for handle in self.resize_handles:
                handle.deleteLater()
            self.resize_handles = []
    
    def show_context_menu(self, widget, pos):
        """Показати контекстне меню"""
        menu = QMenu(widget)
        menu.setStyleSheet("""
            QMenu {
                background: #222;
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                background: transparent;
                color: #FFF;
                padding: 4px 16px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background: #3399FF;
            }
        """)
        
        # Властивості
        properties_action = menu.addAction("🔧 Властивості")
        properties_action.triggered.connect(lambda: self.show_properties_dialog())
        
        # Зміна кольору
        color_action = menu.addAction("🎨 Змінити колір")
        color_action.triggered.connect(lambda: self.change_element_color(widget))
        
        # Масштабування
        scale_action = menu.addAction("📏 Масштабувати")
        scale_action.triggered.connect(lambda: self.scale_element(widget))
        
        # Обертання
        rotate_action = menu.addAction("🔄 Обернути")
        rotate_action.triggered.connect(lambda: self.rotate_element(widget))
        
        menu.addSeparator()
        
        # Копіювати
        copy_action = menu.addAction("📋 Копіювати")
        copy_action.triggered.connect(lambda: self.copy_selected())
        
        # Видалити
        delete_action = menu.addAction("🗑️ Видалити")
        delete_action.triggered.connect(lambda: self.delete_selected())
        
        menu.exec(widget.mapToGlobal(pos))
    
    def change_element_color(self, widget):
        """
        🎨 Відкрити редактор стилів LCARS з епохами
        Запускається через: правий клік на елемент → "🎨 Змінити колір"
        Підключається до існуючих палітр з lcars_palette.py
        """
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                                   QLabel, QTabWidget, QScrollArea, QWidget, QGridLayout)
        # Імпортуємо існуючі палітри
        from lcars.themes.lcars_palette import LCARSEra, get_era_palette
        
        dialog = QDialog(widget)
        dialog.setWindowTitle("LCARS Редактор стилів")
        dialog.setGeometry(200, 200, 800, 600)
        dialog.setStyleSheet("""
            QDialog {
                background: #000;
                color: #FFF;
                border: 3px solid #3399FF;
                border-radius: 12px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                color: #FFF;
                border: 2px solid #FFF;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px;
                margin: 2px;
                font-size: 11px;
            }
            QPushButton:hover {
                border: 2px solid #FFFF00;
                transform: scale(1.05);
            }
            QTabWidget::pane {
                border: 2px solid #3399FF;
                background: #111;
                border-radius: 8px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #333;
                color: #FFF;
                border: 2px solid #666;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3399FF;
                border: 2px solid #66CCFF;
            }
        """)
        
        main_layout = QHBoxLayout()
        
        # Ліва панель - функціональне меню
        left_panel = QWidget()
        left_panel.setMaximumWidth(200)
        left_layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🎨 LCARS Стилі")
        title.setStyleSheet("font-size: 16px; color: #3399FF; padding: 10px;")
        left_layout.addWidget(title)
        
        # Кнопки дій
        apply_btn = QPushButton("✅ Застосувати")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #00AA00;
                color: #FFF;
                border: 2px solid #00FF00;
                border-radius: 6px;
                font-weight: bold;
                padding: 12px;
                font-size: 12px;
            }
        """)
        
        reset_btn = QPushButton("🔄 Скинути")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #FF6600;
                color: #FFF;
                border: 2px solid #FFAA00;
                border-radius: 6px;
                font-weight: bold;
                padding: 12px;
                font-size: 12px;
            }
        """)
        
        cancel_btn = QPushButton("❌ Скасувати")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #CC0000;
                color: #FFF;
                border: 2px solid #FF0000;
                border-radius: 6px;
                font-weight: bold;
                padding: 12px;
                font-size: 12px;
            }
        """)
        
        # Зберігаємо оригінальний стиль
        if not hasattr(widget, '_original_style'):
            widget._original_style = widget.styleSheet()
        
        # Функції кнопок
        def apply_style():
            """Застосувати обраний стиль до елемента"""
            widget.setStyleSheet(widget._current_style if hasattr(widget, '_current_style') else widget._original_style)
            print("✅ Стиль застосовано")
            dialog.close()
        
        def reset_style():
            """Скинути до оригінального стилю"""
            widget.setStyleSheet(widget._original_style)
            print("🔄 Стиль скинуто")
            dialog.close()
        
        apply_btn.clicked.connect(apply_style)
        reset_btn.clicked.connect(reset_style)
        cancel_btn.clicked.connect(dialog.close)
        
        left_layout.addWidget(apply_btn)
        left_layout.addWidget(reset_btn)
        left_layout.addWidget(cancel_btn)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)
        
        # Права панель - палітри епох
        right_panel = QTabWidget()
        
        # Використовуємо існуючі палітри з lcars_palette.py
        # LCARSEra.COMS_22ND - 22nd century (Enterprise NX-01)
        # LCARSEra.PCARS_23RD - 23rd century (TOS era)
        # LCARSEra.PCARS_23ST - 23rd century (TMP era)
        # LCARSEra.LCARS_24TH - 24th century (TNG/DS9/VOY)
        # LCARSEra.LCARS_24ST - 24th century (Sovereign era)
        # LCARSEra.LCARS_25TH - 25th century (Picard era)
        # LCARSEra.TCARS_29TH - 29th century (Future era)
        
        era_names = {
            LCARSEra.COMS_22ND: "COMS 22nd Century",
            LCARSEra.PCARS_23RD: "PCARS 23rd Century (TOS)",
            LCARSEra.PCARS_23ST: "PCARS 23rd Century (TMP)",
            LCARSEra.LCARS_24TH: "LCARS 24th Century (TNG/DS9/VOY)",
            LCARSEra.LCARS_24ST: "LCARS 24th Century (Sovereign)",
            LCARSEra.LCARS_25TH: "LCARS 25th Century (Picard)",
            LCARSEra.TCARS_29TH: "TCARS 29th Century (Future)"
        }
        
        # Створюємо вкладки для кожної епохи з існуючих палітр
        for era, display_name in era_names.items():
            epoch_widget = QWidget()
            epoch_layout = QVBoxLayout()
            
            # Заголовок епохи
            epoch_title = QLabel(f"🚀 {display_name}")
            epoch_title.setStyleSheet("font-size: 14px; color: #3399FF; padding: 10px;")
            epoch_layout.addWidget(epoch_title)
            
            # Отримуємо палітру з lcars_palette.py
            palette = get_era_palette(era)
            
            # Створюємо секції кольорів з існуючої палітри
            # Кольори кнопок
            if 'button_colors' in palette:
                section_label = QLabel("Button Colors")
                section_label.setStyleSheet("font-size: 12px; color: #66CCFF; padding: 5px;")
                epoch_layout.addWidget(section_label)
                
                color_grid = QGridLayout()
                for i, color_hex in enumerate(palette['button_colors']):
                    row = i // 5
                    col = i % 5
                    
                    color_btn = QPushButton("")
                    color_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: {color_hex};
                            border: 2px solid #FFF;
                            border-radius: 8px;
                            min-width: 40px;
                            min-height: 40px;
                        }}
                        QPushButton:hover {{
                            border: 3px solid #FFFF00;
                            transform: scale(1.1);
                        }}
                    """)
                    
                    def apply_era_color(c=color_hex, era_name=display_name, section="button"):
                        """Застосувати колір з існуючої палітри епохи"""
                        new_style = widget._original_style
                        if 'background:' in new_style:
                            # Titanium Bridge Migration: import re
                            new_style = re.sub(r'background:\s*[^;]+;', f'background: {c};', new_style)
                        else:
                            new_style += f'background: {c};'
                        
                        widget._current_style = new_style
                        print(f"✅ Обрано колір {c} з {era_name} ({section})")
                    
                    color_btn.clicked.connect(apply_era_color)
                    color_grid.addWidget(color_btn, row, col)
                
                epoch_layout.addLayout(color_grid)
            
            # Alert кольори
            if 'alert_colors' in palette:
                section_label = QLabel("Alert Colors")
                section_label.setStyleSheet("font-size: 12px; color: #66CCFF; padding: 5px;")
                epoch_layout.addWidget(section_label)
                
                color_grid = QGridLayout()
                for i, color_hex in enumerate(palette['alert_colors']):
                    row = i // 5
                    col = i % 5
                    
                    color_btn = QPushButton("")
                    color_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: {color_hex};
                            border: 2px solid #FFF;
                            border-radius: 8px;
                            min-width: 40px;
                            min-height: 40px;
                        }}
                        QPushButton:hover {{
                            border: 3px solid #FFFF00;
                            transform: scale(1.1);
                        }}
                    """)
                    
                    def apply_alert_color(c=color_hex, era_name=display_name, section="alert"):
                        """Застосувати alert колір з існуючої палітри"""
                        new_style = widget._original_style
                        if 'background:' in new_style:
                            # Titanium Bridge Migration: import re
                            new_style = re.sub(r'background:\s*[^;]+;', f'background: {c};', new_style)
                        else:
                            new_style += f'background: {c};'
                        
                        widget._current_style = new_style
                        print(f"✅ Обрано alert колір {c} з {era_name} ({section})")
                    
                    color_btn.clicked.connect(apply_alert_color)
                    color_grid.addWidget(color_btn, row, col)
                
                epoch_layout.addLayout(color_grid)
            
            epoch_layout.addStretch()
            epoch_widget.setLayout(epoch_layout)
            right_panel.addTab(epoch_widget, display_name)
        
        main_layout.addWidget(right_panel)
        dialog.setLayout(main_layout)
        dialog.exec()
    
    def scale_element(self, widget):
        """Масштабувати елемент"""
        dialog = QDialog(widget)
        dialog.setWindowTitle("Масштабування")
        dialog.setGeometry(300, 300, 300, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: #222;
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel("Масштаб:")
        scale_slider = QSlider(Qt.Orientation.Horizontal)
        scale_slider.setRange(50, 200)
        scale_slider.setValue(100)
        scale_slider.valueChanged.connect(lambda v: label.setText(f"Масштаб: {v}%"))
        
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Застосувати")
        cancel_btn = QPushButton("Скасувати")
        
        def apply_scale():
            scale = scale_slider.value() / 100.0
            current_geom = widget.geometry()
            new_width = int(current_geom.width() * scale)
            new_height = int(current_geom.height() * scale)
            widget.setGeometry(current_geom.x(), current_geom.y(), new_width, new_height)
            print(f"✅ Масштаб змінено на {scale_slider.value()}%")
            dialog.close()
        
        apply_btn.clicked.connect(apply_scale)
        cancel_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(label)
        layout.addWidget(scale_slider)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def rotate_element(self, widget):
        """Обернути елемент"""
        dialog = QDialog(widget)
        dialog.setWindowTitle("Обертання")
        dialog.setGeometry(300, 300, 300, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: #222;
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel("Обертання:")
        rotate_slider = QSlider(Qt.Orientation.Horizontal)
        rotate_slider.setRange(0, 360)
        rotate_slider.setValue(0)
        rotate_slider.valueChanged.connect(lambda v: label.setText(f"Обертання: {v}°"))
        
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Застосувати")
        cancel_btn = QPushButton("Скасувати")
        
        def apply_rotation():
            angle = rotate_slider.value()
            if not hasattr(widget, '_original_style'):
                widget._original_style = widget.styleSheet()
            
            transform = f"transform: rotate({angle}deg);"
            new_style = widget._original_style + transform
            widget.setStyleSheet(new_style)
            print(f"✅ Обертання змінено на {angle}°")
            dialog.close()
        
        apply_btn.clicked.connect(apply_rotation)
        cancel_btn.clicked.connect(dialog.close())
        
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(label)
        layout.addWidget(rotate_slider)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def copy_selected(self):
        """Копіювати вибраний елемент"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        element_type = el['type']
        x, y, w, h = el['geom']
        
        widget = self.component_palette[element_type](parent=self.parent)
        new_element = {
            'type': element_type,
            'widget': widget,
            'geom': [x + 20, y + 20, w, h]
        }
        
        self.elements.append(new_element)
        self.selected = len(self.elements) - 1
        self.update_layout()
        self.parent.update()
    
    def delete_selected(self):
        """Видалити вибраний елемент"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        el['widget'].deleteLater()
        del self.elements[self.selected]
        self.selected = None
        self.parent.update()
    
    def show_properties_dialog(self):
        """Показати діалог властивостей"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Властивості - {el['type']}")
        dialog.setGeometry(300, 300, 350, 250)
        dialog.setStyleSheet("""
            QDialog {
                background: rgba(34, 34, 34, 0.95);
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QLineEdit, QSpinBox {
                background: #333;
                color: #FFF;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Позиції
        x_label = QLabel("X:")
        x_input = QLineEdit(str(el['geom'][0]))
        y_label = QLabel("Y:")
        y_input = QLineEdit(str(el['geom'][1]))
        w_label = QLabel("Ширина:")
        w_input = QLineEdit(str(el['geom'][2]))
        h_label = QLabel("Висота:")
        h_input = QLineEdit(str(el['geom'][3]))
        
        # Колір тексту
        color_label = QLabel("Колір тексту:")
        color_input = QLineEdit("#FFFFFF")
        
        # Кнопка застосування
        apply_btn = QPushButton("Застосувати")
        apply_btn.clicked.connect(lambda: self.apply_properties(el, x_input, y_input, w_input, h_input, color_input, dialog))
        
        for widget in [x_label, x_input, y_label, y_input, w_label, w_input, h_label, h_input, color_label, color_input, apply_btn]:
            layout.addWidget(widget)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_properties(self, element, x_input, y_input, w_input, h_input, color_input, dialog):
        """Застосувати зміни властивостей"""
        if True:
            x = int(x_input.text())
            y = int(y_input.text())
            w = int(w_input.text())
            h = int(h_input.text())
            
            element['geom'] = [x, y, w, h]
            element['widget'].setGeometry(x, y, w, h)
            
            if hasattr(element['widget'], 'setTextColor'):
                color = color_input.text()
                element['widget'].setStyleSheet(f"color: {color};")
            
            self.update_layout()
            self.parent.update()
            dialog.close()
            
        if False: # Removed except block
            print("❌ Помилка введення чисел")
    
    def save_layout(self):
        """Зберегти макет"""
        if not self.enabled:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save Layout", "", "JSON Files (*.json)"
        )
        
        if file_path:
            layout_data = []
            for el in self.elements:
                layout_data.append({
                    'type': el['type'],
                    'geom': el['geom']
                })
            
            with open(file_path, 'w') as f:
                json.dump(layout_data, f, indent=2)
            print(f"✅ Layout saved to {file_path}")
    
    def load_layout(self):
        """Завантажити макет"""
        if not self.enabled:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Load Layout", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if True:
                with open(file_path, 'r') as f:
                    layout_data = json.load(f)
                
                # Очищуємо існуючі елементи
                for el in self.elements:
                    el['widget'].deleteLater()
                self.elements.clear()
                self.selected = None
                
                # Завантажуємо нові елементи
                for item in layout_data:
                    if item['type'] in self.component_palette:
                        widget = self.component_palette[item['type']](parent=self.parent)
                        element = {
                            'type': item['type'],
                            'widget': widget,
                            'geom': item['geom']
                        }
                        self.elements.append(element)
                
                self.update_layout()
                self.parent.update()
                print(f"✅ Layout loaded from {file_path}")
                
            if False: # Removed except block
                print(f"❌ Error loading layout: {e}")
    
    def update_layout(self):
        """Оновити позиції всіх елементів"""
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])
    
    def handle_resize(self, event):
        """Обробка зміни розміру"""
        if not hasattr(self, '_resize_handle') or not hasattr(self, 'selected_widget'):
            return
            
        handle = self._resize_handle
        widget = self.selected_widget
        start_pos = self._resize_start_pos
        original_geom = self._original_geom
        
        handle_index = handle.handle_index
        dx = event.pos().x() - start_pos.x()
        dy = event.pos().y() - start_pos.y()
        
        new_x = original_geom.x()
        new_y = original_geom.y()
        new_w = original_geom.width()
        new_h = original_geom.height()
        
        if handle_index == 0:  # верхній лівий
            new_x = original_geom.x() + dx
            new_y = original_geom.y() + dy
            new_w = original_geom.width() - dx
            new_h = original_geom.height() - dy
        elif handle_index == 1:  # верхній центр
            new_y = original_geom.y() + dy
            new_h = original_geom.height() - dy
        elif handle_index == 2:  # верхній правий
            new_y = original_geom.y() + dy
            new_w = original_geom.width() + dx
            new_h = original_geom.height() - dy
        elif handle_index == 3:  # правий центр
            new_w = original_geom.width() + dx
        elif handle_index == 4:  # нижній правий
            new_w = original_geom.width() + dx
            new_h = original_geom.height() + dy
        elif handle_index == 5:  # нижній центр
            new_h = original_geom.height() + dy
        elif handle_index == 6:  # нижній лівий
            new_x = original_geom.x() + dx
            new_y = original_geom.y() + dy
            new_w = original_geom.width() - dx
            new_h = original_geom.height() + dy
        elif handle_index == 7:  # лівий центр
            new_x = original_geom.x() + dx
            new_w = original_geom.width() - dx
        
        if new_w < 20:
            new_w = 20
        if new_h < 20:
            new_h = 20
            
        widget.setGeometry(new_x, new_y, new_w, new_h)
        self.update_resize_handles()
        self.parent.update()
    
    def update_resize_handles(self):
        """Оновити позиції кутів"""
        if not hasattr(self, 'selected_widget') or not hasattr(self, 'resize_handles'):
            return
            
        geom = self.selected_widget.geometry()
        handle_size = 8
        
        positions = [
            (geom.x() - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width()//2 - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() + geom.height()//2 - handle_size//2),
            (geom.x() + geom.width() - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() + geom.width()//2 - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() - handle_size//2, geom.y() + geom.height() - handle_size//2),
            (geom.x() - handle_size//2, geom.y() + geom.height()//2 - handle_size//2),
        ]
        
        for handle, (x, y) in zip(self.resize_handles, positions):
            handle.move(x, y)
    
    def scale_element(self, widget):
        """Масштабувати елемент"""
        dialog = QDialog(widget)
        dialog.setWindowTitle("Масштабування")
        dialog.setGeometry(300, 300, 300, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: #222;
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                background: #333;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3399FF;
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel("Масштаб:")
        scale_slider = QSlider(Qt.Orientation.Horizontal)
        scale_slider.setRange(50, 200)
        scale_slider.setValue(100)
        scale_slider.valueChanged.connect(lambda v: label.setText(f"Масштаб: {v}%"))
        
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Застосувати")
        cancel_btn = QPushButton("Скасувати")
        
        def apply_scale():
            scale = scale_slider.value() / 100.0
            current_geom = widget.geometry()
            new_width = int(current_geom.width() * scale)
            new_height = int(current_geom.height() * scale)
            widget.setGeometry(current_geom.x(), current_geom.y(), new_width, new_height)
            print(f"✅ Масштаб змінено на {scale_slider.value()}%")
            dialog.close()
        
        apply_btn.clicked.connect(apply_scale)
        cancel_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(label)
        layout.addWidget(scale_slider)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def rotate_element(self, widget):
        """Обернути елемент"""
        dialog = QDialog(widget)
        dialog.setWindowTitle("Обертання")
        dialog.setGeometry(300, 300, 300, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: #222;
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                background: #333;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3399FF;
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel("Обертання:")
        rotate_slider = QSlider(Qt.Orientation.Horizontal)
        rotate_slider.setRange(0, 360)
        rotate_slider.setValue(0)
        rotate_slider.valueChanged.connect(lambda v: label.setText(f"Обертання: {v}°"))
        
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Застосувати")
        cancel_btn = QPushButton("Скасувати")
        
        def apply_rotation():
            angle = rotate_slider.value()
            if not hasattr(widget, '_original_style'):
                widget._original_style = widget.styleSheet()
            
            transform = f"transform: rotate({angle}deg);"
            new_style = widget._original_style + transform
            widget.setStyleSheet(new_style)
            print(f"✅ Обертання змінено на {angle}°")
            dialog.close()
        
        apply_btn.clicked.connect(apply_rotation)
        cancel_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(label)
        layout.addWidget(rotate_slider)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_properties_dialog(self):
        """Показати діалог властивостей"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Властивості - {el['type']}")
        dialog.setGeometry(300, 300, 350, 250)
        dialog.setStyleSheet("""
            QDialog {
                background: rgba(34, 34, 34, 0.95);
                color: #FFF;
                border: 2px solid #3399FF;
                border-radius: 8px;
            }
            QLabel {
                color: #FFF;
                font-weight: bold;
            }
            QLineEdit, QSpinBox {
                background: #333;
                color: #FFF;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton {
                background: #3399FF;
                color: #FFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #55AAFF;
            }
        """)
        
        layout = QVBoxLayout()
        
        x_label = QLabel("X:")
        x_input = QLineEdit(str(el['geom'][0]))
        y_label = QLabel("Y:")
        y_input = QLineEdit(str(el['geom'][1]))
        w_label = QLabel("Ширина:")
        w_input = QLineEdit(str(el['geom'][2]))
        h_label = QLabel("Висота:")
        h_input = QLineEdit(str(el['geom'][3]))
        
        color_label = QLabel("Колір тексту:")
        color_input = QLineEdit("#FFFFFF")
        
        apply_btn = QPushButton("Застосувати")
        apply_btn.clicked.connect(lambda: self.apply_properties(el, x_input, y_input, w_input, h_input, color_input, dialog))
        
        for widget in [x_label, x_input, y_label, y_input, w_label, w_input, h_label, h_input, color_label, color_input, apply_btn]:
            layout.addWidget(widget)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_properties(self, element, x_input, y_input, w_input, h_input, color_input, dialog):
        """Застосувати зміни властивостей"""
        if True:
            x = int(x_input.text())
            y = int(y_input.text())
            w = int(w_input.text())
            h = int(h_input.text())
            
            element['geom'] = [x, y, w, h]
            element['widget'].setGeometry(x, y, w, h)
            
            if hasattr(element['widget'], 'setTextColor'):
                color = color_input.text()
                element['widget'].setStyleSheet(f"color: {color};")
            
            self.update_layout()
            self.update_resize_handles()
            self.parent.update()
            dialog.close()
            
        if False: # Removed except block
            print("❌ Помилка введення чисел")
    
    def copy_selected(self):
        """Копіювати вибраний елемент"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        element_type = el['type']
        x, y, w, h = el['geom']
        
        widget = self.component_palette[element_type](parent=self.parent)
        new_element = {
            'type': element_type,
            'widget': widget,
            'geom': [x + 20, y + 20, w, h]
        }
        
        self.elements.append(new_element)
        self.selected = len(self.elements) - 1
        self.update_layout()
        self.parent.update()
        print(f"✅ Element {element_type} copied")
    
    def delete_selected(self):
        """Видалити вибраний елемент"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        el['widget'].deleteLater()
        del self.elements[self.selected]
        self.clear_resize_handles()
        self.selected = None
        self.parent.update()
        print("✅ Element deleted")
    
    def save_layout(self):
        """Зберегти layout в JSON"""
        if not self.enabled:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save Layout", "", "JSON Files (*.json)"
        )
        
        if file_path:
            layout_data = []
            for el in self.elements:
                layout_data.append({
                    'type': el['type'],
                    'geom': el['geom']
                })
            
            with open(file_path, 'w') as f:
                json.dump(layout_data, f, indent=2)
            print(f"✅ Layout saved to {file_path}")
    
    def load_layout(self):
        """Завантажити layout з JSON"""
        if not self.enabled:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Load Layout", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if True:
                with open(file_path, 'r') as f:
                    layout_data = json.load(f)
                
                # Clear existing elements
                for el in self.elements:
                    el['widget'].deleteLater()
                self.elements.clear()
                self.clear_resize_handles()
                self.selected = None
                
                # Load new elements
                for item in layout_data:
                    if item['type'] in self.component_palette:
                        widget = self.component_palette[item['type']](parent=self.parent)
                        element = {
                            'type': item['type'],
                            'widget': widget,
                            'geom': item['geom']
                        }
                        self.elements.append(element)
                
                self.update_layout()
                self.parent.update()
                print(f"✅ Layout loaded from {file_path}")
            if False: # Removed except block
                print(f"❌ Error loading layout: {e}")
    
    def update_layout(self):
        """Оновити позиції всіх елементів"""
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])
