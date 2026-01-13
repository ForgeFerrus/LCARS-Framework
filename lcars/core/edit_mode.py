import json
import copy
from PyQt6.QtWidgets import (QWidget, QMenu, QColorDialog, QInputDialog, 
                             QFileDialog, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor

class EditMode(QWidget):
    # Сигнал для оновлення властивостей у головному вікні
    element_selected = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.enabled = False
        self.elements = []  # Посилання на список елементів
        self.selected = None
        self.selected_index = None
        
        # Стан маніпуляцій
        self._drag_mode = None  # 'move', 'resize', 'rotate'
        self._drag_offset = QPoint()
        self.grid_size = 10     # Магнітна сітка для ідеального LCARS
        self.clipboard = None   # Буфер обміну для копіювання
        
        # Вузол ресайзу (правий нижній кут)
        self.handle_size = 12

        # Встановлюємо event filter на батьківське вікно
        self.parent.installEventFilter(self)

    def set_elements(self, elements_list):
        self.elements = elements_list

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

        if event.type() == event.Type.MouseButtonPress:
            return self.handle_mouse_press(event)
        
        elif event.type() == event.Type.MouseMove:
            return self.handle_mouse_move(event)
        
        elif event.type() == event.Type.MouseButtonRelease:
            self._drag_mode = None
            self.parent.unsetCursor()
            return True

        return False

    def handle_mouse_press(self, event):
        pos = event.pos()

        # Права кнопка миші - Контекстне меню
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(pos)
            return True

        # Шукаємо об'єкт (з кінця списку, щоб вибрати верхній)
        for i in range(len(self.elements) - 1, -1, -1):
            el = self.elements[i]
            rect = el['widget'].geometry()
            
            # Перевірка на вузол зміни розміру (Resize Handle)
            resize_rect = QRect(rect.right() - self.handle_size, 
                                rect.bottom() - self.handle_size, 
                                self.handle_size + 5, self.handle_size + 5)
            
            if resize_rect.contains(pos):
                self.selected = el
                self.selected_index = i
                self._drag_mode = 'resize'
                self.parent.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                return True

            # Перевірка на переміщення
            if rect.contains(pos):
                self.selected = el
                self.selected_index = i
                self._drag_mode = 'move'
                self._drag_offset = pos - rect.topLeft()
                self.element_selected.emit(el)
                return True

        self.selected = None
        self.selected_index = None
        return False

    def handle_mouse_move(self, event):
        if not self.selected or not self._drag_mode:
            return False

        pos = event.pos()
        el = self.selected
        
        if self._drag_mode == 'move':
            new_pos = pos - self._drag_offset
            # Магнітна сітка
            nx = (new_pos.x() // self.grid_size) * self.grid_size
            ny = (new_pos.y() // self.grid_size) * self.grid_size
            el['geom'][0], el['geom'][1] = nx, ny

        elif self._drag_mode == 'resize':
            rect = el['widget'].geometry()
            nw = ((pos.x() - rect.left()) // self.grid_size) * self.grid_size
            nh = ((pos.y() - rect.top()) // self.grid_size) * self.grid_size
            el['geom'][2] = max(20, nw)
            el['geom'][3] = max(20, nh)

        self.update_element_geometry(el)
        return True

    def show_context_menu(self, pos):
        # Якщо клікнули на пусте місце
        if not self.selected:
            menu = QMenu()
            act_paste = menu.addAction("📋 Вставити")
            act_paste.setEnabled(self.clipboard is not None)
            action = menu.exec(self.parent.mapToGlobal(pos))
            if action == act_paste: self.paste_element(pos)
            return

        # Меню для вибраного елемента
        menu = QMenu()
        menu.setStyleSheet("background-color: #111; color: #ff9900; border: 1px solid #ff9900;")
        
        act_color = menu.addAction("🎨 Колір")
        act_text = menu.addAction("✏️ Текст")
        act_logic = menu.addAction("⚡ Алгоритм (Python)")
        menu.addSeparator()
        act_copy = menu.addAction("📋 Копіювати")
        act_del = menu.addAction("🗑 Видалити")
        
        action = menu.exec(self.parent.mapToGlobal(pos))

        if action == act_color:
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected['widget'].setStyleSheet(f"background-color: {color.name()}; border-radius: 5px;")
                self.selected['color'] = color.name()
        
        elif action == act_text:
            text, ok = QInputDialog.getText(self.parent, "LCARS Text", "Введіть текст:", text=self.selected.get('text', ''))
            if ok:
                if hasattr(self.selected['widget'], 'setText'):
                    self.selected['widget'].setText(text)
                self.selected['text'] = text

        elif action == act_logic:
            # Тут ми підключаємо "мозок" системи
            code, ok = QInputDialog.getMultiLineText(self.parent, "Logic MOD", 
                "Доступні змінні: me (віджет), sys (api)\nНаприклад: me.hide() якщо sys.cpu > 80", 
                self.selected.get('logic', ''))
            if ok: self.selected['logic'] = code

        elif action == act_copy:
            self.clipboard = copy.deepcopy(self.selected)
            # Прибираємо віджет з копії, він створиться заново при вставці
            self.clipboard.pop('widget')

        elif action == act_del:
            self.delete_selected()

    def delete_selected(self):
        if self.selected:
            self.selected['widget'].deleteLater()
            self.elements.pop(self.selected_index)
            self.selected = None
            self.selected_index = None

    def paste_element(self, pos):
        if not self.clipboard: return
        new_el = copy.deepcopy(self.clipboard)
        new_el['geom'][0] = (pos.x() // self.grid_size) * self.grid_size
        new_el['geom'][1] = (pos.y() // self.grid_size) * self.grid_size
        
        # Тут треба викликати метод створення віджета з Constructor.py
        # Наприклад: self.parent.create_element_from_data(new_el)
        self.parent.add_element_from_data(new_el)

    def update_element_geometry(self, el):
        el['widget'].setGeometry(*el['geom'])