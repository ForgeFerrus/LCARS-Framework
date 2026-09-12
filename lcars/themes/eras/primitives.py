# === Універсальні примітиви ===
from PyQt6.QtWidgets import QLabel, QWidget, QPushButton
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from lcars.themes.lcars_palette import get_palette_by_name

class Rect(QWidget):
	def __init__(self, width=100, height=40, color="#FFFFFF", border_color="#222", border=2, parent=None):
		super().__init__(parent)
		self.setFixedSize(width, height)
		self.color = color
		self.border_color = border_color
		self.border = border
	
	def setColor(self, color):
		self.color = color
		self.update()
	
	def paintEvent(self, a0):
		from PyQt6.QtGui import QPainter, QPen
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.setPen(QPen(QColor(self.border_color), self.border))
		p.setBrush(QColor(self.color))
		p.drawRect(self.border//2, self.border//2, self.width()-self.border, self.height()-self.border)

class Square(Rect):
	def __init__(self, size=40, color="#FFFFFF", border_color="#222", border=2, parent=None):
		super().__init__(width=size, height=size, color=color, border_color=border_color, border=border, parent=parent)

class Circle(QWidget):
	def __init__(self, diameter=40, color="#FFFFFF", border_color="#222", border=2, parent=None):
		super().__init__(parent)
		self.setFixedSize(diameter, diameter)
		self.color = color
		self.border_color = border_color
		self.border = border
	
	def setColor(self, color):
		self.color = color
		self.update()
	
	def paintEvent(self, a0):
		from PyQt6.QtGui import QPainter, QPen
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.setPen(QPen(QColor(self.border_color), self.border))
		p.setBrush(QColor(self.color))
		d = min(self.width(), self.height()) - self.border
		p.drawEllipse((self.width()-d)//2, (self.height()-d)//2, d, d)

class Triangle(QWidget):
	def __init__(self, width=50, height=50, color="#FFFFFF", border_color="#222", border=2, parent=None):
		super().__init__(parent)
		self.setFixedSize(width, height)
		self.color = color
		self.border_color = border_color
		self.border = border
	
	def setColor(self, color):
		self.color = color
		self.update()
	
	def paintEvent(self, a0):
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.setPen(QPen(QColor(self.border_color), self.border))
		p.setBrush(QColor(self.color))
		points = QPolygonF([
			QPointF(self.width()/2, 0),
			QPointF(0, self.height()),
			QPointF(self.width(), self.height())
		])
		p.drawPolygon(points)

class Trapezoid(QWidget):
	def __init__(self, width=80, height=50, color="#FFFFFF", border_color="#222", border=2, parent=None):
		super().__init__(parent)
		self.setFixedSize(width, height)
		self.color = color
		self.border_color = border_color
		self.border = border
	def paintEvent(self, a0):
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.setPen(QPen(QColor(self.border_color), self.border))
		p.setBrush(QColor(self.color))
		points = QPolygonF([
			QPointF(self.width()*0.2, 0),
			QPointF(self.width()*0.8, 0),
			QPointF(self.width(), self.height()),
			QPointF(0, self.height())
		])
		p.drawPolygon(points)

class Line(QWidget):
	def __init__(self, length=100, thickness=4, color="#222", orientation="h", parent=None):
		super().__init__(parent)
		if orientation == "h":
			self.setFixedSize(length, thickness)
		else:
			self.setFixedSize(thickness, length)
		self.color = color
		self.orientation = orientation
	def paintEvent(self, a0):
		from PyQt6.QtGui import QPainter, QPen
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.setPen(QPen(QColor(self.color), self.height() if self.orientation=="h" else self.width()))
		if self.orientation == "h":
			p.drawLine(0, self.height()//2, self.width(), self.height()//2)
		else:
			p.drawLine(self.width()//2, 0, self.width()//2, self.height())

class LCARSButton(QPushButton):
	def __init__(self, text="", color="#FFE600", text_color="#000000", parent=None):
		super().__init__(text, parent)
		self.color = color
		self.text_color = text_color
		self.setup_style()
	def setup_style(self):
		self.setStyleSheet(f"""
			QPushButton {{
				background-color: {self.color};
				color: {self.text_color};
				padding: 8px 16px;
				font-weight: bold;
				font-size: 12px;
				font-family: 'Arial', sans-serif;
				text-transform: uppercase;
			}}
			QPushButton:hover {{
				background-color: #FFFF00;
			}}
			QPushButton:pressed {{
				background-color: #CCCC00;
			}}
		""")

# текстовий примітив з фіксованим шрифтом
class TextLabel(QLabel):
	def __init__(self, text="", font="Arial", size=14, color="#000000", parent=None):
		super().__init__(text, parent)
		self.setFont(QFont(font, size))
		self.setStyleSheet(f"color: {color}; background: transparent;")
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)

# --- Фабрика базових примітивів ---
def get_base_primitives():
	return {
		'rect': lambda parent=None: Rect(parent=parent),
		'square': lambda parent=None: Square(parent=parent),
		'circle': lambda parent=None: Circle(parent=parent),
		'triangle': lambda parent=None: Triangle(parent=parent),
		'trapezoid': lambda parent=None: Trapezoid(parent=parent),
		'line_h': lambda parent=None: Line(orientation="h", parent=parent),
		'line_v': lambda parent=None: Line(orientation="v", parent=parent),
		'button': lambda text="", parent=None: LCARSButton(text, parent=parent),
		'label': lambda text="", parent=None: TextLabel(text, parent=parent),
	}
# --- Фабрика розширених примітивів ---
def get_advanced_primitives():
	return {
		'label': lambda text="", parent=None: create_label(text, parent),
	}
def create_label(text, parent=None):
	label = QLabel(text, parent)
	label.setAlignment(Qt.AlignmentFlag.AlignCenter)
	label.setFont(QFont("Arial", 14))
	return label

# --- Комбіновані примітиви ---
def get_combined_primitives():
	return {
		'rect_with_label': lambda text="", parent=None: create_rect_with_label(text, parent),
	}
def create_rect_with_label(text, parent=None):
	rect = Rect(parent=parent)
	label = QLabel(text, rect)
	label.setAlignment(Qt.AlignmentFlag.AlignCenter)
	label.setFont(QFont("Arial", 14))
	label.setGeometry(0, 0, rect.width(), rect.height())
	return rect
# --- Всі примітиви разом ---
def get_all_primitives():
	primitives = {}
	primitives.update(get_base_primitives())
	primitives.update(get_advanced_primitives())
	primitives.update(get_combined_primitives())
	return primitives
# Отримати всі примітиви
all_primitives = get_all_primitives()
def get_primitives():
	return all_primitives