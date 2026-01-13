"""
LCARS 25th Century Framework - CONSTRUCTOR v3.0
Authentic Picard-era "Computer Core" Engine
"""
import sys
import os
import json
import random
import psutil
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QTextEdit, QComboBox, QLineEdit, QInputDialog, QColorDialog, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QTransform, QFont, QPainterPath

# --- 1. SYSTEM INTEGRATION ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lcars_path = os.path.join(current_dir, 'lcars', 'themes')
    if lcars_path not in sys.path:
        sys.path.insert(0, lcars_path)
    
    from lcars_palette import get_palette_by_name, get_random_button_color
    from primitives import get_universal_primitives
except ImportError:
    def get_palette_by_name(n): return {"button_colors": ["#37A6D1", "#9EA5BA", "#FF9F1C", "#E7442A", "#6D748C"], "background": "#000000"}
    def get_universal_primitives(): return {}

# --- 2. AUTHENTIC LCARS ELEMENTS ---

class LcarsElbow(QWidget):
    """Iconic LCARS L-bend (Elbow) connector"""
    def __init__(self, parent=None, color="#37A6D1", direction="top-left", size=(100, 40)):
        super().__init__(parent)
        self.color = color
        self.direction = direction
        self.setFixedSize(QSize(*size))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        w, h = self.width(), self.height()
        thickness = h // 2
        path = QPainterPath()
        
        if self.direction == "top-left":
            path.moveTo(w, 0)
            path.lineTo(thickness, 0)
            path.arcTo(0, 0, thickness*2, thickness*2, 90, 90)
            path.lineTo(0, h)
            path.lineTo(thickness, h)
            path.lineTo(thickness, thickness)
            path.arcTo(thickness, thickness, 2, 2, 180, -90) # Tiny inner curve
            path.lineTo(w, thickness)
        elif self.direction == "top-right":
            path.moveTo(0, 0)
            path.lineTo(w - thickness, 0)
            path.arcTo(w - thickness*2, 0, thickness*2, thickness*2, 90, -90)
            path.lineTo(w, h)
            path.lineTo(w - thickness, h)
            path.lineTo(w - thickness, thickness)
            path.lineTo(0, thickness)
            
        p.drawPath(path)

# --- 3. SYSTEM EDITOR ---

class LCARSCodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("LCARS ANALYTICS EDITOR")
        self.resize(1100, 800)
        self.setStyleSheet("""
            QWidget { background-color: #000000; color: #9EA5BA; font-family: 'Swis721 BT'; }
            QTextEdit { border: none; background: #050505; color: #FFFFFF; font-family: 'Courier New'; font-size: 14px; padding: 20px; border-radius: 20px; }
            QPushButton { background-color: #37A6D1; color: black; font-weight: bold; border-radius: 17px; padding: 12px; border: none; }
            QPushButton:hover { background-color: #FFFFFF; }
        """)
        l = QVBoxLayout(self)
        self.hdr = QLabel("◢ SYSTEM_DATA_STREAM")
        self.hdr.setStyleSheet("font-size: 20px; color: #FF9F1C; font-weight: bold;")
        l.addWidget(self.hdr)
        self.edit = QTextEdit()
        l.addWidget(self.edit)
        
        row = QHBoxLayout()
        save = QPushButton("INJECT CODE")
        save.clicked.connect(self.save)
        row.addWidget(save)
        close = QPushButton("TERMINATE")
        close.clicked.connect(self.close)
        row.addWidget(close)
        l.addLayout(row)
        
        self.cb = None
        self.path = None

    def open_logic(self, code, cb):
        self.path = None
        self.cb = cb
        self.edit.setPlainText(code)
        self.hdr.setText("◢ EDITING WIDGET LOGIC")
        self.show()

    def open_file(self, path):
        self.path = path
        self.cb = None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.edit.setPlainText(f.read())
            self.hdr.setText(f"◢ CORE FILE: {os.path.basename(path)}")
            self.show()
        except Exception: pass

    def save(self):
        if self.cb: self.cb(self.edit.toPlainText())
        elif self.path:
            with open(self.path, 'w', encoding='utf-8') as f: f.write(self.edit.toPlainText())
        self.close()

# --- 4. ENGINE CLASSES ---

class DraggableWidget(QWidget):
    def __init__(self, parent=None, constructor=None, primitive=None, p_type="Block"):
        super().__init__(parent)
        self.constructor = constructor
        self.primitive = primitive
        self.p_type = p_type
        self.color = constructor.palette['button_colors'][0]
        self.selected = False
        self.dragging = False
        self.drag_start = QPoint()
        self.logic = ""
        
        if self.primitive:
            self.primitive.setParent(self)
            self.primitive.setAttribute(Qt.WidgetAttribute.WA_TransparentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(160, 110)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.selected:
            p.setBrush(QColor(255, 255, 255, 50))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(self.rect(), 22, 22)
            
        if not self.primitive:
            p.setBrush(QColor(self.color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(self.rect().adjusted(5,5,-5,-5), 18, 18)
            p.setPen(QColor(0,0,0))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.p_type.upper())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.constructor.select_widget(self)
            self.raise_()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.drag_start))
            self.constructor.update_telemetry()

    def mouseReleaseEvent(self, event): self.dragging = False

class LCARSAIAgent(QThread):
    def process(self, q):
        q = q.lower()
        if "створ" in q or "add" in q:
            t = "Button"
            if "панел" in q: t = "Panel"
            elif "круг" in q or "circle" in q: t = "Circle"
            return f"BUILDING_{t.upper()}... [ACTION: SPAWN type='{t}']"
        elif "clear" in q or "очист" in q: return "WIPING_WORKSPACE... [ACTION: CLEAR]"
        elif "color" in q or "колір" in q: return "RECYCLING_COLORS... [ACTION: COLOR]"
        return "COMPUTER_STANDBY. WAITING_INPUT."

# --- 5. MAIN CONSTRUCTOR v3 ---

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.palette = get_palette_by_name("25th")
        self.prims = get_universal_primitives()
        self.elements = []
        self.sel = None
        self.edit_mode = True
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet(f"background: #000000; color: {self.palette['button_colors'][1]}; font-family: 'Swis721 BT';")

        self.root = QWidget()
        self.setCentralWidget(self.root)
        
        self.setup_ui()
        self.ed = LCARSCodeEditor()
        self.ai = LCARSAIAgent()
        
        self.t = QTimer()
        self.t.timeout.connect(self.sync)
        self.t.start(30)

    def setup_ui(self):
        # Top Bar (Header)
        self.top = QFrame(self.root)
        self.top.setFixedHeight(70)
        self.top.setStyleSheet(f"background: #0F1620; border-bottom: 3px solid {self.palette['button_colors'][0]};")
        tl = QHBoxLayout(self.top)
        
        self.hdr_elbow = LcarsElbow(self.top, self.palette['button_colors'][0], "top-left", (120, 40))
        tl.addWidget(self.hdr_elbow)
        
        self.title = QLabel("◢ LCARS COMP_CORE ACCESS // MISSION_CONTROL")
        self.title.setStyleSheet(f"color: {self.palette['button_colors'][0]}; font-weight: bold; font-size: 18px; padding-left: 20px;")
        tl.addWidget(self.title)
        tl.addStretch()
        
        # Right Toggle Bars (Authentic 25th style vertical pilar)
        self.r_tab = QFrame(self.root)
        self.r_tab.setFixedWidth(60)
        self.r_tab.setStyleSheet("background: #0A0E1A;")
        rv = QVBoxLayout(self.r_tab)
        rv.setContentsMargins(5, 10, 5, 10)
        
        for n, c, clr in [("AI", self.tog_ai, self.palette['button_colors'][0]), 
                          ("SYS", self.tog_sys, self.palette['button_colors'][2]),
                          ("EDIT", self.tog_edit, self.palette['button_colors'][1]),
                          ("✕", self.close, self.palette['button_colors'][3])]:
            b = QPushButton(n)
            b.setFixedSize(50, 60)
            b.setStyleSheet(f"background: {clr}; color: black; font-weight: bold; border-radius: 15px; border: none; font-size: 11px;")
            b.clicked.connect(c)
            rv.addWidget(b)
        rv.addStretch()

        # Sliding AI Panel
        self.ai_p = QFrame(self.root)
        self.ai_p.setFixedWidth(320)
        self.ai_p.setStyleSheet("background: rgba(15, 22, 32, 0.95); border-radius: 20px;")
        av = QVBoxLayout(self.ai_p)
        av.addWidget(LcarsElbow(self.ai_p, self.palette['button_colors'][0], "top-left", (150, 30)))
        av.addWidget(QLabel("◤ ON-BOARD ANALYTICS"))
        self.ai_out = QTextEdit()
        self.ai_out.setReadOnly(True)
        self.ai_out.setStyleSheet("background: #050505; color: #9EA5BA; border: none; border-radius: 15px; padding: 10px;")
        av.addWidget(self.ai_out)
        self.ai_in = QLineEdit()
        self.ai_in.setPlaceholderText("Direct core request...")
        self.ai_in.setStyleSheet("background: #2F3749; color: #37A6D1; border: none; border-radius: 12px; padding: 10px;")
        self.ai_in.returnPressed.connect(self.exec_ai)
        av.addWidget(self.ai_in)
        self.ai_p.hide()

        # Sliding Systems Panel
        self.sys_p = QFrame(self.root)
        self.sys_p.setFixedWidth(320)
        self.sys_p.setStyleSheet("background: rgba(15, 22, 32, 0.95); border-radius: 20px;")
        sv = QVBoxLayout(self.sys_p)
        sv.addWidget(LcarsElbow(self.sys_p, self.palette['button_colors'][2], "top-right", (150, 30)))
        sv.addWidget(QLabel("◢ SYSTEM INSTRUMENTATION"))
        self.tel = QLabel("TELEMETRY: STANDBY")
        self.tel.setStyleSheet("background: #0A0E1A; color: #6D748C; padding: 12px; border-radius: 15px; font-size: 10px;")
        sv.addWidget(self.tel)
        
        # Spawner Grid
        grid = QGridLayout()
        grid.setSpacing(5)
        for i, (n, t) in enumerate([("PANEL", "Panel"), ("BUTTON", "Button"), ("RECT", "Rect"), ("CIRC", "Circle"), ("SQR", "Square")]):
            b = self.btn(n, lambda checked, x=t: self.spawn(x), self.palette['button_colors'][i % 5])
            grid.addWidget(b, i//2, i%2)
        sv.addLayout(grid)
        
        # Tools
        sv.addWidget(self.btn("DUPLICATE", self.dup, self.palette['button_colors'][1]))
        sv.addWidget(self.btn("EDIT LOGIC", self.ed_log, self.palette['button_colors'][0]))
        sv.addWidget(self.btn("FILE ACCESS", self.ed_file, self.palette['button_colors'][4]))
        sv.addWidget(self.btn("SAVE LAYOUT", self.save, self.palette['button_colors'][2]))
        sv.addWidget(self.btn("LOAD LAYOUT", self.load, self.palette['button_colors'][0]))
        sv.addWidget(self.btn("DELETE", self.delete, "#E7442A"))
        sv.addStretch()
        self.sys_p.hide()

        self.canvas = QFrame(self.root)
        self.canvas.setStyleSheet("background: transparent;")

    def btn(self, text, cb, clr):
        b = QPushButton(text)
        b.setFixedHeight(35)
        b.setStyleSheet(f"background: {clr}; color: black; font-weight: bold; border-radius: 17px; border: none; font-size: 10px;")
        b.clicked.connect(cb)
        return b

    def sync(self):
        w, h = self.width(), self.height()
        self.top.setGeometry(0, 0, w, 70)
        self.r_tab.setGeometry(w-60, 70, 60, h-70)
        
        cv_x, cv_w = 0, w - 60
        if self.ai_p.isVisible():
            self.ai_p.setGeometry(10, 80, 320, h - 100)
            cv_x = 340; cv_w -= 340
        if self.sys_p.isVisible():
            self.sys_p.setGeometry(w - 390, 80, 320, h - 100)
            cv_w -= 330
            
        self.canvas.setGeometry(cv_x, 80, cv_w, h - 100)

    def tog_ai(self): self.ai_p.setVisible(not self.ai_p.isVisible())
    def tog_sys(self): self.sys_p.setVisible(not self.sys_p.isVisible())
    def tog_edit(self):
        self.edit_mode = not self.edit_mode
        clr = self.palette['button_colors'][1] if self.edit_mode else self.palette['button_colors'][0]
        self.top.setStyleSheet(f"background: #0F1620; border-bottom: 3px solid {clr};")
        self.hdr_elbow.color = clr; self.hdr_elbow.update()

    def spawn(self, t):
        p = self.prims[t]() if t in self.prims else None
        w = DraggableWidget(self.canvas, self, p, t)
        w.move(random.randint(100, 400), random.randint(100, 400))
        w.show(); self.elements.append(w)
        self.select_widget(w)

    def select_widget(self, w):
        for el in self.elements: el.selected = False
        self.sel = w; w.selected = True; w.update(); self.update_telemetry()

    def update_telemetry(self):
        if self.sel: self.tel.setText(f"OBJECT: {self.sel.p_type}\nX, Y: {self.sel.x()},{self.sel.y()}\nDIM: {self.sel.width()}x{self.sel.height()}")
        else: self.tel.setText("TELEMETRY: STANDBY")

    def exec_ai(self):
        cmd = self.ai_in.text()
        if not cmd: return
        self.ai_in.clear()
        self.ai_out.append(f"> {cmd}")
        res = self.ai.process(cmd)
        self.ai_out.append(f"COMP: {res}")
        if "[ACTION:" in res:
            if "SPAWN" in res:
                import re; m = re.search(r"type=['\"](.*?)['\"]", res)
                self.spawn(m.group(1) if m else "Button")
            elif "CLEAR" in res: self.clear_all()
            elif "COLOR" in res: self.cycle_color()

    def dup(self):
        if self.sel: self.spawn(self.sel.p_type)

    def ed_log(self):
        if self.sel: 
            def cb(c): self.sel.logic = c
            self.ed.open_logic(self.sel.logic, cb)

    def ed_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Core File", "", "All (*.*)")
        if f: self.ed.open_file(f)

    def save(self):
        data = [{'t': e.p_type, 'x': e.x(), 'y': e.y(), 'w': e.width(), 'h': e.height(), 'c': e.color, 'l': e.logic} for e in self.elements]
        with open("lcars_layout.json", 'w') as f: json.dump(data, f)

    def load(self):
        try:
            with open("lcars_layout.json", 'r') as f: data = json.load(f)
            self.clear_all()
            for d in data:
                self.spawn(d['t'])
                e = self.elements[-1]; e.move(d['x'], d['y']); e.resize(d['w'], d['h']); e.color = d['c']; e.logic = d['l']
        except: pass

    def delete(self):
        if self.sel: self.elements.remove(self.sel); self.sel.deleteLater(); self.sel = None; self.update_telemetry()

    def clear_all(self):
        for e in self.elements: e.deleteLater()
        self.elements.clear(); self.sel = None; self.update_telemetry()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    sys.exit(app.exec())
