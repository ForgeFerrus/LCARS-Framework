"""
LCARS Framework - Enhanced Constructor with LCARSToolkit-inspired components
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QToolBar, QDockWidget, 
                            QListWidget, QListWidgetItem, QLabel, QDialog, 
                            QLineEdit, QComboBox, QSpinBox, QColorDialog)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QFont, QLinearGradient

# Додаємо шлях до проекту
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# Імпорт компонентів
from lcars.themes.eras.primitives import Rect, Square, Circle, Triangle, Trapezoid, Line, LCARSButton, TextLabel

# Enums для LCARS компонентів
class Corner:
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_RIGHT = 2
    BOTTOM_LEFT = 3

class Direction:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Illumination:
    ON = 0
    OFF = 1
    FLASHING = 2

class LCARSStump(QWidget):
    """Декоративний елемент LCARS - аналог Stump з LCARSToolkit"""
    
    def __init__(self, corner=Corner.TOP_LEFT, parent=None):
        super().__init__(parent)
        self.corner = corner
        self.illumination = Illumination.ON
        self.is_lit = True
        self.fill_color = QColor("#FF9900")  # LCARS orange
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.flash_tick)
        self.flash_timer.start(500)  # Flash every 500ms
        self.setFixedSize(40, 40)
        
    def flash_tick(self):
        """Анімація мерехтіння"""
        if self.illumination == Illumination.FLASHING:
            self.is_lit = not self.is_lit
        elif self.illumination == Illumination.ON:
            self.is_lit = True
        else:
            self.is_lit = False
        self.update()
        
    def set_illumination(self, illumination):
        """Встановити режим ілюмінації"""
        self.illumination = illumination
        self.update()
        
    def paintEvent(self, event):
        """Малювання декоративного елемента"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Вибір кольору залежно від стану
        if self.is_lit:
            color = self.fill_color
        else:
            color = QColor("#333333")  # Dark when off
            
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Малювання залежно від кута
        if self.corner == Corner.TOP_LEFT:
            painter.drawPie(0, 0, 80, 80, 0, 90 * 16)
        elif self.corner == Corner.TOP_RIGHT:
            painter.drawPie(-40, 0, 80, 80, 90 * 16, 90 * 16)
        elif self.corner == Corner.BOTTOM_RIGHT:
            painter.drawPie(-40, -40, 80, 80, 180 * 16, 90 * 16)
        elif self.corner == Corner.BOTTOM_LEFT:
            painter.drawPie(0, -40, 80, 80, 270 * 16, 90 * 16)

class LCARSEnhancedButton(QPushButton):
    """Покращена LCARS кнопка з ілюмінацією"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.illumination = Illumination.ON
        self.is_lit = True
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.flash_tick)
        self.flash_timer.start(500)
        self.base_color = QColor("#FF9900")
        self.setup_style()
        
    def flash_tick(self):
        """Анімація мерехтіння"""
        if self.illumination == Illumination.FLASHING:
            self.is_lit = not self.is_lit
        elif self.illumination == Illumination.ON:
            self.is_lit = True
        else:
            self.is_lit = False
        self.setup_style()
        
    def set_illumination(self, illumination):
        """Встановити режим ілюмінації"""
        self.illumination = illumination
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю кнопки"""
        if self.is_lit:
            bg_color = self.base_color.name()
            text_color = "#000000"
        else:
            bg_color = "#333333"
            text_color = "#666666"
            
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg_color};
                color: {text_color};
                border: 2px solid #666;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {self.base_color.lighter(120).name()};
                border-color: #FFF;
            }}
            QPushButton:pressed {{
                background: #FFFFFF;
                color: #000000;
            }}
        """)

class LCARSElbo(QWidget):
    """Кутовий елемент LCARS - аналог Elbo з LCARSToolkit"""
    
    def __init__(self, corner=Corner.TOP_LEFT, size=60, parent=None):
        super().__init__(parent)
        self.corner = corner
        self.size = size
        self.fill_color = QColor("#FF9900")
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        """Малювання кутового елемента"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(self.fill_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Малювання L-подібної форми
        if self.corner == Corner.TOP_LEFT:
            painter.drawRect(0, 0, self.size, self.size//3)
            painter.drawRect(0, 0, self.size//3, self.size)
        elif self.corner == Corner.TOP_RIGHT:
            painter.drawRect(0, 0, self.size, self.size//3)
            painter.drawRect(self.size*2//3, 0, self.size//3, self.size)
        elif self.corner == Corner.BOTTOM_RIGHT:
            painter.drawRect(0, self.size*2//3, self.size, self.size//3)
            painter.drawRect(self.size*2//3, 0, self.size//3, self.size)
        elif self.corner == Corner.BOTTOM_LEFT:
            painter.drawRect(0, self.size*2//3, self.size, self.size//3)
            painter.drawRect(0, 0, self.size//3, self.size)

class EnhancedEditMode:
    """Спрощений EditMode"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.elements = []
        self.component_palette = {}
        
    def create_edit_ui(self):
        pass
        
    def add_element(self, element_type):
        pass

class LCARSConstructor(QMainWindow):
    """Покращений конструктор LCARS з новими компонентами"""
    
    def __init__(self, faction="22nd"):
        super().__init__()
        self.faction = faction
        self.setWindowTitle(f"LCARS Enhanced Constructor - {faction.upper()} Century")
        self.setGeometry(100, 100, 1400, 900)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Використовуємо покращений EditMode
        self.edit_mode = EnhancedEditMode(self.central_widget)
        
        # Налаштування палітри компонентів
        self.setup_enhanced_palette()
        
        self.edit_mode.create_edit_ui()
        self.add_enhanced_demo_elements()
        self.setup_enhanced_style()
        self.create_enhanced_menu()
        
    def setup_enhanced_palette(self):
        """Налаштування розширеної палітри компонентів"""
        self.edit_mode.component_palette = {
            # Оригінальні компоненти
            'panel': lambda parent=None: self.get_styled_widget('panel', parent=parent),
            'button': lambda parent=None: self.get_styled_widget('button', 'BUTTON', parent=parent),
            'mini': lambda parent=None: self.get_styled_widget('mini', 'MINI', parent=parent),
            'text': lambda parent=None: self.get_styled_widget('text', 'TEXT LABEL', parent=parent),
            'rect': lambda parent=None: self.get_styled_widget('rect', parent=parent),
            'square': lambda parent=None: self.get_styled_widget('square', parent=parent),
            'circle': lambda parent=None: self.get_styled_widget('circle', parent=parent),
            'triangle': lambda parent=None: self.get_styled_widget('triangle', parent=parent),
            'line_h': lambda parent=None: self.get_styled_widget('line_h', parent=parent),
            'line_v': lambda parent=None: self.get_styled_widget('line_v', parent=parent),
            
            # Нові LCARSToolkit-натхненні компоненти
            'stump_tl': lambda parent=None: LCARSStump(Corner.TOP_LEFT, parent),
            'stump_tr': lambda parent=None: LCARSStump(Corner.TOP_RIGHT, parent),
            'stump_bl': lambda parent=None: LCARSStump(Corner.BOTTOM_LEFT, parent),
            'stump_br': lambda parent=None: LCARSStump(Corner.BOTTOM_RIGHT, parent),
            'elbo_tl': lambda parent=None: LCARSElbo(Corner.TOP_LEFT, 60, parent),
            'elbo_tr': lambda parent=None: LCARSElbo(Corner.TOP_RIGHT, 60, parent),
            'elbo_bl': lambda parent=None: LCARSElbo(Corner.BOTTOM_LEFT, 60, parent),
            'elbo_br': lambda parent=None: LCARSElbo(Corner.BOTTOM_RIGHT, 60, parent),
            'enhanced_button': lambda parent=None: LCARSEnhancedButton("ENHANCED", parent),
        }
        
    def get_styled_widget(self, widget_type, text="", parent=None, faction="22nd"):
        """Створює віджет з правильним дизайном"""
        if True:
            if widget_type == 'panel':
                from lcars.themes.eras.PCARSPanel import PCARS22Panel
                return PCARS22Panel(parent=parent)
            elif widget_type == 'button':
                from lcars.themes.eras.pcars22_components import PCARS22Button
                return PCARS22Button(number='00-0001', label=text, width=120, height=40, parent=parent)
            elif widget_type == 'mini':
                from lcars.themes.eras.pcars22_components import PCARS22MiniButton
                return PCARS22MiniButton(label=text, size=70, color_index=0, parent=parent)
            elif widget_type == 'text':
                return TextLabel(text, parent=parent)
            elif widget_type == 'rect':
                return Rect(100, 60, QColor("#FF9900"), parent=parent)
            elif widget_type == 'square':
                return Square(60, QColor("#FF9900"), parent=parent)
            elif widget_type == 'circle':
                return Circle(30, QColor("#FF9900"), parent=parent)
            elif widget_type == 'triangle':
                return Triangle(40, QColor("#FF9900"), parent=parent)
            elif widget_type == 'line_h':
                return Line(200, 4, QColor("#FFFFFF"), 'horizontal', parent=parent)
            elif widget_type == 'line_v':
                return Line(100, 4, QColor("#FFFFFF"), 'vertical', parent=parent)
            else:
                return QLabel(widget_type, parent=parent)
        if False: # Removed except block
            print(f"Error creating widget {widget_type}: {e}")
            return QLabel(widget_type, parent=parent)
            
    def add_enhanced_demo_elements(self):
        """Додати демонстраційні елементи з новими компонентами"""
        # Оригінальні елементи
        panel = self.get_styled_widget('panel', parent=self.central_widget)
        panel.move(200, 50)
        self.edit_mode.elements.append({'type': 'panel', 'widget': panel, 'geom': [200, 50, 200, 150]})
        
        button = self.get_styled_widget('button', 'MAIN', parent=self.central_widget)
        button.move(450, 80)
        self.edit_mode.elements.append({'type': 'button', 'widget': button, 'geom': [450, 80, 120, 40]})
        
        # Нові компоненти
        stump_tl = LCARSStump(Corner.TOP_LEFT, self.central_widget)
        stump_tl.move(50, 50)
        self.edit_mode.elements.append({'type': 'stump_tl', 'widget': stump_tl, 'geom': [50, 50, 40, 40]})
        
        stump_tr = LCARSStump(Corner.TOP_RIGHT, self.central_widget)
        stump_tr.move(400, 50)
        self.edit_mode.elements.append({'type': 'stump_tr', 'widget': stump_tr, 'geom': [400, 50, 40, 40]})
        
        elbo_bl = LCARSElbo(Corner.BOTTOM_LEFT, 80, self.central_widget)
        elbo_bl.move(50, 400)
        self.edit_mode.elements.append({'type': 'elbo_bl', 'widget': elbo_bl, 'geom': [50, 400, 80, 80]})
        
        enhanced_btn = LCARSEnhancedButton("ENHANCED", self.central_widget)
        enhanced_btn.move(600, 200)
        self.edit_mode.elements.append({'type': 'enhanced_button', 'widget': enhanced_btn, 'geom': [600, 200, 150, 40]})
        
        # Додати ще кілька елементів для демонстрації
        for i in range(3):
            stump = LCARSStump(Corner.BOTTOM_LEFT + i, self.central_widget)
            stump.move(200 + i * 100, 300)
            stump.set_illumination(Illumination.FLASHING if i == 1 else Illumination.ON)
            self.edit_mode.elements.append({'type': f'stump_{i}', 'widget': stump, 'geom': [200 + i * 100, 300, 40, 40]})
            
    def setup_enhanced_style(self):
        """Налаштування стилю вікна"""
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
            }
            QWidget {
                background: #000000;
            }
        """)
        
    def create_enhanced_menu(self):
        """Створити меню з додатковими опціями"""
        menubar = self.menuBar()
        
        # Меню файлу
        file_menu = menubar.addMenu('File')
        
        # Меню компонентів
        components_menu = menubar.addMenu('Components')
        
        # Меню налаштувань
        settings_menu = menubar.addMenu('Settings')

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    constructor = LCARSConstructor("22nd")
    constructor.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
