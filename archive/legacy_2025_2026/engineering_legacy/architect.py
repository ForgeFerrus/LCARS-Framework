# Isolinear Architect - середовище розробки LCARS.
# Інтегрована IDE для створення переглядів, модулів та тем LCARS для різних епох.

# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QFrame,
    QComboBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style, get_theme, LCARSEra
# Titanium Bridge Migration: import subprocess, sys
from lcars.engineering.editor import VisualEditor

class ArchitectCanvas(QFrame):
    # Інтегрована область малювання.

    selectionChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = getattr(parent, "theme", get_theme(LCARSEra.LCARS_25TH))
        bg = self.theme.get("bg", "#000000")
        border = self.theme.get("border", "#111")
        self.setStyleSheet(f"background-color: {bg}; border: 1px solid {border};")
        self.setMouseTracking(True)
        self.nodes = []
        self.selected_node = None
        self.background_image = None

        # Професійна підкладка для маніпуляцій (VisualEditor)
        self.edit_mode = VisualEditor(self)
        self.edit_mode.enabled = True
        self.edit_mode.set_elements(self.nodes)

    def set_background(self, pixmap):
        # Встановлення фонового зображення (креслення).
        self.background_image = pixmap
        self.update()

    def mousePressEvent(self, a0):
        # Реалізація функції "Click-to-Add" (Додати за кліком)
        if not a0:
            return
            
        parent = self.parentWidget()
        if parent and hasattr(parent, "active_tool") and getattr(parent, "active_tool", None):
            self._create_node_at(getattr(parent, "active_tool"), a0.position().toPoint())
            return

        # Логіка зняття виділення
        if hasattr(self, "selected_node") and self.selected_node:
            getattr(self.selected_node, "update_style")(False)
            self.selected_node = None
        super().mousePressEvent(a0)

    def _create_node_at(self, ntype, pos):
        # Доступ до батьківського Architect для використання його фабрики створення
        parent = self.parentWidget()
        if parent and hasattr(parent, "create_widget_at"):
            getattr(parent, "create_widget_at")(ntype, pos)

    def paintEvent(self, a0):
        from PyQt6.QtGui import QPainter, QPen

        qp = QPainter(self)

        # Професійна підкладка для креслення (Blueprint Substrate)
        if self.background_image:
            qp.drawPixmap(self.rect(), self.background_image)

        grid_color = QColor(30, 30, 30)
        if hasattr(self, "theme"):
            # Використовуємо трохи світлішу версію фону для сітки
            grid_color = QColor(self.theme.get("border", "#222"))
            
        qp.setPen(QPen(grid_color, 1))
        # Нейронна сітка (Neural Grid)
        for x in range(0, self.width(), 50):
            qp.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 50):
            qp.drawLine(0, y, self.width(), y)
        qp.end()

# Універсальний вузол для розгортання різних типів елементів (кнопки, панелі, зображення тощо).
class ArchitectNode(QFrame):

    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.resize(inner_widget.size())

        self._dragging = False
        self._drag_start = QPoint()
        self.update_style(False)
    # Професійна логіка виділення та перетягування вузлів
    def update_style(self, selected: bool):
        theme = getattr(self.parentWidget(), "theme", {})
        accent = theme.get("accent", "#FF9900")
        border = theme.get("border", "#444")
        
        color = accent if selected else border
        self.setStyleSheet(f"border: 2px solid {color}; background-color: transparent;")
    
    def mousePressEvent(self, a0):
        if not a0:
            return
        if a0.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = a0.position().toPoint()
            canvas = self.parentWidget()
            if canvas and hasattr(canvas, "selectionChanged"):
                # Зняття виділення з попереднього вузла
                if hasattr(canvas, "selected_node") and getattr(canvas, "selected_node", None):
                    getattr(getattr(canvas, "selected_node"), "update_style")(False)

                setattr(canvas, "selected_node", self)
                self.update_style(True)
                getattr(canvas, "selectionChanged").emit(self)
            self.raise_()

    def mouseMoveEvent(self, a0):
        if self._dragging and a0:
            delta = a0.position().toPoint() - self._drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, a0):
        self._dragging = False

    def export_node_data(self):
        # Базова логіка експорту параметрів вузла (буде викликатись конструктором)
        return {
            "geom": [self.x(), self.y(), self.width(), self.height()],
            "type": self.inner.__class__.__name__
        }

class IsolinearArchitect:
    # Головний інженерний рушій (Controller).
    # Не має власного інтерфейсу. Надає API для програм (наприклад, programs/constructor.py)
    # або штучного інтелекту (Majel) для програмної генерації та експорту інтерфейсів LCARS.
    
    def __init__(self, canvas=None):
        # Прив'язка до полотна, на якому відбуваються фізичні маніпуляції
        self.canvas = canvas

    def set_canvas(self, canvas):
        # Встановлює робоче полотно.
        self.canvas = canvas

    def spawn_element(self, widget_type: str, pos: QPoint, label: str = "NEW_NODE"):
        # Програмне створення вузла. Викликається конструктором або голосом (ШІ).
        if not self.canvas:
            print("◤ ARCHITECT-ERROR: Canvas not bound to IsolinearArchitect.")
            return
            
        theme = getattr(self.canvas, "theme", {})
        accent = theme.get("accent", "var(--accent)")
        secondary = theme.get("secondary", "var(--secondary)")
        border = theme.get("border", "var(--border)")
        text = theme.get("text", "var(--text)")

        # Генерація сирого віджета залежно від типу
        if "BUTTON" in widget_type:
            inner = LCARSButton(label, accent)
            inner.resize(140, 40)
        elif "ELBOW" in widget_type:
            inner = LCARSElbow("top-left", color=secondary)
            inner.resize(100, 100)
        elif "PANEL" in widget_type:
            inner = QFrame()
            inner.setStyleSheet(f"background-color: {border}; border: 2px solid {secondary};")
            inner.resize(200, 150)
        else:
            inner = QLabel(label)
            inner.setStyleSheet(f"color: {text}; font-family: 'Courier New';")
            inner.resize(100, 30)

        # Обгортка в інженерний вузол
        node = ArchitectNode(inner, self.canvas)
        node.move(pos)
        node.show()

        # Реєстрація вузла в системі
        node_data = {
            "widget": node,
            "geom": [pos.x(), pos.y(), inner.width(), inner.height()],
            "type": widget_type,
            "id": f"node_{len(self.canvas.nodes)}"
        }
        self.canvas.nodes.append(node_data)
        
        print(f"◤ ARCHITECT: Deployed {widget_type} at {pos.x()}:{pos.y()}")
        return node

    def serialize_state(self):
        # Пакує всі створені на полотні елементи у формат JSON для збереження.
        if not self.canvas:
            return {}
            
        data = {"nodes": []}
        for node_meta in self.canvas.nodes:
            widget = node_meta["widget"]
            data["nodes"].append({
                "id": node_meta.get("id"),
                "type": node_meta.get("type"),
                "geom": [widget.x(), widget.y(), widget.width(), widget.height()]
            })
        return data

    def export_to_python_code(self, class_name: str = "GeneratedView") -> str:
        # Головна інженерна функція: трансляція зібраних блоків у робочий Python-код LCARS.
        code = f"from PyQt6.QtWidgets import QWidget, QLabel, QFrame\n"
        code += f"from lcars.ui.base.widgets import LCARSButton, LCARSElbow\n\n"
        code += f"class {class_name}(QWidget):\n"
        code += f"    def __init__(self, parent=None):\n"
        code += f"        super().__init__(parent)\n"
        code += f"        self.resize(800, 600)\n"
        code += f"        self.theme = getattr(self, 'theme', {{}})\n"
        
        if not self.canvas or not self.canvas.nodes:
            code += "        # Полотно порожнє\n"
            return code

        for idx, node_meta in enumerate(self.canvas.nodes):
            geom = node_meta["geom"]
            ntype = node_meta["type"]
            nid = node_meta.get("id", f"item_{idx}")
            
            if "BUTTON" in ntype:
                code += f"        self.{nid} = LCARSButton('NODE', self.theme.get('accent', 'var(--accent)'), self)\n"
            elif "ELBOW" in ntype:
                code += f"        self.{nid} = LCARSElbow('top-left', parent=self, color=self.theme.get('secondary', 'var(--secondary)'))\n"
            else:
                code += f"        self.{nid} = QFrame(self)\n"
                
            code += f"        self.{nid}.setGeometry({geom[0]}, {geom[1]}, {geom[2]}, {geom[3]})\n"

        return code


