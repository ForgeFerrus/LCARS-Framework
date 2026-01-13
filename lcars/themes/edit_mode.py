import json
import copy
import math
from PyQt6.QtWidgets import (QWidget, QMenu, QColorDialog, QInputDialog, QPushButton,
                             QFileDialog, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QRect, QPoint, QEvent
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor

class EditMode(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.enabled = False
        self.elements = []  # Посилання на список елементів
        self.selected = None
        self.selected_index = None
        
        # Стан маніпуляцій
        self._drag_mode = None  # 'move', 'resize_tl', 'resize_tr', 'resize_bl', 'resize_br', 'rotate'
        self._drag_offset = QPoint()
        self.grid_size = 5      # Магнітна сітка для ідеального LCARS
        self.clipboard = None   # Буфер обміну для копіювання
        
        # Вузли ресайзу (кути і сторони)
        self.handle_size = 8
        self.rotate_handle_size = 10
        
        # Групування
        self.selected_group = []  # Список вибраних елементів
        self.group_mode = False   # Режим групування

        # Встановлюємо event filter на батьківське вікно
        self.parent.installEventFilter(self)

    def set_elements(self, elements_list):
        self.elements = elements_list

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

        if event.type() == QEvent.Type.MouseButtonPress:
            return self.handle_mouse_press(event)
        
        elif event.type() == QEvent.Type.MouseMove:
            return self.handle_mouse_move(event)
        
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_mode = None
            self.parent.unsetCursor()
            return True

        return False

    def handle_mouse_press(self, event):
        try:
            pos = event.pos()
            
            # Якщо це подія від віджета, конвертуємо координати до canvas
            if hasattr(event, 'widget') and event.widget() != self.parent:
                # Конвертуємо локальні координати віджета до глобальних координат canvas
                widget_pos = event.widget().mapTo(self.parent, event.pos())
                pos = widget_pos

            # Права кнопка миші - Контекстне меню
            if event.button() == Qt.MouseButton.RightButton:
                self.show_context_menu(pos)
                return True

            # Shift+клік - вибір групи
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                return self.handle_group_selection(pos)

            # Шукаємо об'єкт (з кінця списку, щоб вибрати верхній)
            for i in range(len(self.elements) - 1, -1, -1):
                el = self.elements[i]
                rect = el['widget'].geometry()
                
                # Спочатку перевіряємо вузли (якщо є)
                if hasattr(el['widget'], 'resize_handles'):
                    for j, handle in enumerate(el['widget'].resize_handles):
                        handle_rect = handle.geometry()
                        if handle_rect.contains(pos):
                            self.selected = el
                            self.selected_index = i
                            # Встановлюємо режим drag
                            if j < 4:  # Перші 4 - resize вузли
                                modes = ['resize_tl', 'resize_tr', 'resize_bl', 'resize_br']
                                self._drag_mode = modes[j]
                            else:  # Останній - rotate
                                self._drag_mode = 'rotate'
                            self.set_resize_cursor(self._drag_mode)
                            self.highlight_selected()
                            return True

                # Потім перевіряємо сам елемент
                if rect.contains(pos):
                    self.selected = el
                    self.selected_index = i
                    self._drag_mode = 'move'
                    self._drag_offset = pos - rect.topLeft()
                    self.highlight_selected()
                    # Оновлюємо властивості в конструкторі
                    if hasattr(self.parent, 'parent_constructor') and hasattr(self.parent.parent_constructor, 'update_properties'):
                        self.parent.parent_constructor.update_properties()
                    return True

            self.selected = None
            self.selected_index = None
            self.clear_highlight()
            return False
        except Exception as e:
            print(f"Помилка в handle_mouse_press: {e}")
            return False

    def get_resize_handles(self, rect):
        """Повертає прямокутники для всіх вузлів зміни розміру"""
        h = self.handle_size
        return {
            'resize_tl': QRect(rect.left() - h//2, rect.top() - h//2, h, h),  # верхній лівий
            'resize_tr': QRect(rect.right() - h//2, rect.top() - h//2, h, h),  # верхній правий
            'resize_bl': QRect(rect.left() - h//2, rect.bottom() - h//2, h, h), # нижній лівий
            'resize_br': QRect(rect.right() - h//2, rect.bottom() - h//2, h, h), # нижній правий
        }

    def set_resize_cursor(self, handle_name):
        """Встановлює курсор для відповідного вузла"""
        cursors = {
            'resize_tl': Qt.CursorShape.SizeFDiagCursor,
            'resize_tr': Qt.CursorShape.SizeBDiagCursor,
            'resize_bl': Qt.CursorShape.SizeBDiagCursor,
            'resize_br': Qt.CursorShape.SizeFDiagCursor,
        }
        self.parent.setCursor(QCursor(cursors.get(handle_name, Qt.CursorShape.ArrowCursor)))

    def handle_group_selection(self, pos):
        """Обробка вибору групи елементів"""
        for i in range(len(self.elements) - 1, -1, -1):
            el = self.elements[i]
            rect = el['widget'].geometry()
            
            if rect.contains(pos):
                if el in self.selected_group:
                    self.selected_group.remove(el)
                else:
                    self.selected_group.append(el)
                
                self.highlight_selected()
                return True
        
        return False

    def highlight_selected(self):
        """Підсвічує вибраний елемент і додає візуальні вузли"""
        # Очищуємо попереднє підсвічування
        self.clear_highlight()
        
        if self.selected:
            widget = self.selected['widget']
            # Додаємо рамку для вибраного елемента
            current_style = widget.styleSheet()
            widget.setStyleSheet(current_style + "; border: 2px solid #00ff00;")
            
            # Додаємо візуальні вузли для зміни розміру
            self.add_resize_handles(widget)
        
        # Підсвічуємо групу
        for el in self.selected_group:
            widget = el['widget']
            widget.setStyleSheet(widget.styleSheet() + "; border: 2px solid #ff9900;")

    def add_resize_handles(self, widget):
        """Додає візуальні вузли для зміни розміру"""
        rect = widget.geometry()
        parent = widget.parent()
        
        # Створюємо вузли
        handles = []
        positions = [
            (rect.left() - 4, rect.top() - 4, 'resize_tl'),      # верхній лівий
            (rect.right() - 4, rect.top() - 4, 'resize_tr'),     # верхній правий  
            (rect.left() - 4, rect.bottom() - 4, 'resize_bl'),   # нижній лівий
            (rect.right() - 4, rect.bottom() - 4, 'resize_br'),  # нижній правий
            (rect.center().x() - 5, rect.top() - 15, 'rotate')    # обертання
        ]
        
        for pos in positions:
            handle = QPushButton(parent)
            handle.setGeometry(pos[0], pos[1], 8, 8)
            handle.setStyleSheet("background-color: #00ff00; border: 1px solid white;")
            handle.show()
            # Зберігаємо тип вузла
            handle.handle_type = pos[2]
            handles.append(handle)
        
        # Зберігаємо вузли для очищення
        widget.resize_handles = handles

    def clear_highlight(self):
        """Очищує підсвічування і вузли"""
        for el in self.elements:
            widget = el['widget']
            # Прибираємо рамки
            style = widget.styleSheet()
            style = style.replace("; border: 2px solid #00ff00;", "")
            style = style.replace("; border: 2px solid #ff9900;", "")
            widget.setStyleSheet(style)
            
            # Прибираємо вузли
            if hasattr(widget, 'resize_handles'):
                for handle in widget.resize_handles:
                    handle.deleteLater()
                delattr(widget, 'resize_handles')

    def handle_mouse_move(self, event):
        pos = event.pos()
        
        # Якщо це подія від віджета, конвертуємо координати до canvas
        if hasattr(event, 'widget') and event.widget() != self.parent:
            widget_pos = event.widget().mapTo(self.parent, event.pos())
            pos = widget_pos
        
        if not self.selected or not self._drag_mode:
            return False

        el = self.selected
        rect = el['widget'].geometry()
        
        if self._drag_mode == 'move':
            new_pos = pos - self._drag_offset
            # Магнітна сітка
            nx = (new_pos.x() // self.grid_size) * self.grid_size
            ny = (new_pos.y() // self.grid_size) * self.grid_size
            el['geom'][0], el['geom'][1] = nx, ny

        elif self._drag_mode == 'rotate':
            # Обертання навколо центру
            center = rect.center()
            angle = math.degrees(math.atan2(pos.y() - center.y(), pos.x() - center.x()))
            # Зберігаємо кут в даних елемента
            el['rotation'] = angle
            
        elif 'resize' in self._drag_mode:
            # Зміна розміру з відповідного кута
            if self._drag_mode == 'resize_tl':  # верхній лівий
                nw = ((rect.right() - pos.x()) // self.grid_size) * self.grid_size
                nh = ((rect.bottom() - pos.y()) // self.grid_size) * self.grid_size
                el['geom'][0] = rect.right() - max(20, nw)
                el['geom'][1] = rect.bottom() - max(20, nh)
                el['geom'][2] = max(20, nw)
                el['geom'][3] = max(20, nh)
                
            elif self._drag_mode == 'resize_tr':  # верхній правий
                nw = ((pos.x() - rect.left()) // self.grid_size) * self.grid_size
                nh = ((rect.bottom() - pos.y()) // self.grid_size) * self.grid_size
                el['geom'][2] = max(20, nw)
                el['geom'][1] = rect.bottom() - max(20, nh)
                
            elif self._drag_mode == 'resize_bl':  # нижній лівий
                nw = ((rect.right() - pos.x()) // self.grid_size) * self.grid_size
                nh = ((pos.y() - rect.top()) // self.grid_size) * self.grid_size
                el['geom'][0] = rect.right() - max(20, nw)
                el['geom'][2] = max(20, nw)
                el['geom'][3] = max(20, nh)
                
            elif self._drag_mode == 'resize_br':  # нижній правий
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
        
        # Групування
        if len(self.selected_group) > 1:
            act_group = menu.addAction("🔗 Згрупувати")
            act_ungroup = menu.addAction("🔓 Розгрупувати")
        else:
            act_group = menu.addAction("🔗 Додати до групи")
            act_ungroup = menu.addAction("🔓 Очистити групу")
        
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
            # Створюємо просту копію без віджета
            self.clipboard = {
                'type': self.selected['type'],
                'geom': self.selected['geom'].copy(),
                'color': self.selected['color'],
                'text': self.selected.get('text', ''),
                'logic': self.selected.get('logic', '')
            }

        elif action == act_group:
            if self.selected not in self.selected_group:
                self.selected_group.append(self.selected)
            self.highlight_selected()
            
        elif action == act_ungroup:
            self.selected_group.clear()
            self.highlight_selected()

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
        if hasattr(self.parent, 'add_element_from_data'):
            self.parent.add_element_from_data(new_el)

    def handle_mouse_release(self, event):
        """Обробка відпускання кнопки миші"""
        try:
            if self._drag_mode:
                self._drag_mode = None
                if hasattr(self.parent, 'unsetCursor'):
                    self.parent.unsetCursor()
            return True
        except Exception as e:
            print(f"Помилка в handle_mouse_release: {e}")
            return False

    def update_element_geometry(self, el):
        el['widget'].setGeometry(*el['geom'])
        # Оновлюємо візуальні вузли якщо елемент виділений
        if self.selected == el:
            self.clear_highlight()
            self.highlight_selected()
