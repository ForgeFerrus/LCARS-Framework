"""
Simple LCARS Layout Editor - Interactive drag-and-drop interface designer
Based on archive/22nd.py but simplified
"""
import json
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                            QVBoxLayout, QLabel, QMainWindow, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QResizeEvent, QPainterPath, QMouseEvent

class SimpleLCARSButton(QPushButton):
    """Simple LCARS button with drag capabilities"""
    
    def __init__(self, number='00-0000', label='NAME', color='#3399FF', 
                 bar_color='#CCCCCC', border_color='#222', parent=None):
        super().__init__(parent)
        self._number = number
        self._label = label
        self._color = color
        self._bar_color = bar_color
        self._border_color = border_color
        self.set_flags()
        
    def set_flags(self):
        """Enable mouse tracking and cursor for editing"""
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setMinimumSize(100, 60)
        self.setStyleSheet("background: transparent; border: none;")
        
    def mousePressEvent(self, event: QMouseEvent):
        """Start drag operation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position()
            self._original_pos = self.pos()
            self.raise_()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle drag movement"""
        if hasattr(self, '_drag_start') and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._drag_start
            new_pos = self._original_pos + delta.toPoint()
            self.move(new_pos.toPoint())
            if self.parent():
                self.parent().update_layout()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """End drag operation"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Custom LCARS button painting"""
        w, h = self.width(), self.height()
        bar_h = int(h * 0.28)
        square_size = int(h * 0.38)
        circle_d = int(square_size * 0.62)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Main rectangle
        pen_width = 2
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._color))
        painter.drawRect(0, 0, w, h-bar_h)
        
        # Gray bar at bottom
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(0, h-bar_h, w, bar_h)
        
        # Square in top-right corner
        sq_x = w - square_size - pen_width
        sq_y = pen_width
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(sq_x, sq_y, square_size, square_size)
        
        # White circle in square
        circ_x = sq_x + (square_size - circle_d)//2
        circ_y = sq_y + (square_size - circle_d)//2
        painter.setPen(QPen(QColor(self._bar_color), pen_width))
        painter.setBrush(QColor('#FFF'))
        painter.drawEllipse(circ_x, circ_y, circle_d, circle_d)
        
        # Number in center
        painter.setPen(QPen(QColor('#111'), 2))
        font = QFont('Arial', max(10, int((h-bar_h)*0.32)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int((h-bar_h)*0.18), w, int((h-bar_h)*0.32), 
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._number)
        
        # Label in gray bar
        font.setPointSize(max(8, int(bar_h*0.5)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, h-bar_h, w, bar_h, 
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._label)

class SimpleLCARSPanel(QWidget):
    """Simple LCARS panel with drag capabilities"""
    
    def __init__(self, parent=None, label="PANEL", circle_color="#1A3AFF"):
        super().__init__(parent)
        self.label = label
        self.circle_color = circle_color
        self.set_flags()
        self.setMinimumSize(200, 150)
        
    def set_flags(self):
        """Enable mouse tracking and cursor for editing"""
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setStyleSheet("background: transparent;")
        
    def mousePressEvent(self, event: QMouseEvent):
        """Start drag operation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position()
            self._original_pos = self.pos()
            self.raise_()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle drag movement"""
        if hasattr(self, '_drag_start') and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._drag_start
            new_pos = self._original_pos + delta.toPoint()
            self.move(new_pos.toPoint())
            if self.parent():
                self.parent().update_layout()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """End drag operation"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Custom LCARS panel painting"""
        w, h = self.width(), self.height()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Main panel background
        painter.setPen(QPen(QColor('#BFC2C4'), 6))
        painter.setBrush(QColor('#000000'))
        painter.drawRect(0, 0, w, h)
        
        # Circle indicator
        circle_size = min(w, h) * 0.3
        painter.setPen(QPen(QColor(self.circle_color), 4))
        painter.setBrush(QColor(self.circle_color))
        painter.drawEllipse(int(w*0.1), int(h*0.1), int(circle_size), int(circle_size))
        
        # Label
        painter.setPen(QPen(QColor('#FFFFFF'), 2))
        font = QFont('Arial', max(12, int(h*0.15)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int(h*0.6), w, int(h*0.3), 
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self.label)

class SimpleLCARSEditor(QMainWindow):
    """Simple LCARS editor with drag-and-drop functionality"""
    
    def __init__(self):
        super().__init__()
        self.elements = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the editor interface"""
        self.setWindowTitle("LCARS Layout Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Canvas area
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background-color: #000000;")
        self.canvas.setMinimumSize(800, 600)
        main_layout.addWidget(self.canvas, 3)
        
        # Control panel
        control_panel = QWidget()
        control_panel.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, 1)
        
        # Add element buttons
        self.add_button_btn = QPushButton("Add Button")
        self.add_button_btn.clicked.connect(self.add_button)
        control_layout.addWidget(self.add_button_btn)
        
        self.add_panel_btn = QPushButton("Add Panel")
        self.add_panel_btn.clicked.connect(self.add_panel)
        control_layout.addWidget(self.add_panel_btn)
        
        # Save/Load buttons
        self.save_btn = QPushButton("Save Layout")
        self.save_btn.clicked.connect(self.save_layout)
        control_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("Load Layout")
        self.load_btn.clicked.connect(self.load_layout)
        control_layout.addWidget(self.load_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_layout)
        control_layout.addWidget(self.clear_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
    def add_button(self):
        """Add a new button to canvas"""
        button = SimpleLCARSButton(
            number=f"00-{len(self.elements):04d}",
            label=f"BUTTON {len(self.elements)+1}",
            color="#3399FF",
            bar_color="#CCCCCC",
            parent=self.canvas
        )
        button.setGeometry(50 + (len(self.elements) * 30), 50 + (len(self.elements) * 20), 200, 80)
        button.show()
        self.elements.append({
            'type': 'button',
            'widget': button,
            'geom': [button.x(), button.y(), button.width(), button.height()]
        })
        self.status_label.setText(f"Added button {len(self.elements)}")
        
    def add_panel(self):
        """Add a new panel to canvas"""
        panel = SimpleLCARSPanel(
            parent=self.canvas,
            label=f"PANEL {len(self.elements)+1}",
            circle_color="#1A3AFF"
        )
        panel.setGeometry(100 + (len(self.elements) * 40), 100 + (len(self.elements) * 30), 300, 200)
        panel.show()
        self.elements.append({
            'type': 'panel',
            'widget': panel,
            'geom': [panel.x(), panel.y(), panel.width(), panel.height()]
        })
        self.status_label.setText(f"Added panel {len(self.elements)}")
        
    def update_layout(self):
        """Update element positions in layout data"""
        for element in self.elements:
            widget = element['widget']
            element['geom'] = [widget.x(), widget.y(), widget.width(), widget.height()]
            
    def save_layout(self):
        """Save current layout to JSON file"""
        layout_data = []
        for element in self.elements:
            widget = element['widget']
            layout_data.append({
                'type': element['type'],
                'geom': [widget.x(), widget.y(), widget.width(), widget.height()],
                'properties': {
                    'number': getattr(widget, '_number', ''),
                    'label': getattr(widget, '_label', ''),
                    'color': getattr(widget, '_color', '#3399FF'),
                    'bar_color': getattr(widget, '_bar_color', '#CCCCCC'),
                    'circle_color': getattr(widget, 'circle_color', '#1A3AFF')
                }
            })
        
        try:
            with open('lcars_simple_layout.json', 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, ensure_ascii=False, indent=2)
            self.status_label.setText(f"Layout saved: {len(layout_data)} elements")
            QMessageBox.information(self, "Success", "Layout saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save layout: {str(e)}")
            
    def load_layout(self):
        """Load layout from JSON file"""
        try:
            with open('lcars_simple_layout.json', 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            # Clear existing elements
            self.clear_layout()
            
            # Create elements from saved data
            for item in layout_data:
                props = item.get('properties', {})
                geom = item['geom']
                
                if item['type'] == 'button':
                    widget = SimpleLCARSButton(
                        number=props.get('number', '00-0000'),
                        label=props.get('label', 'BUTTON'),
                        color=props.get('color', '#3399FF'),
                        bar_color=props.get('bar_color', '#CCCCCC'),
                        parent=self.canvas
                    )
                elif item['type'] == 'panel':
                    widget = SimpleLCARSPanel(
                        parent=self.canvas,
                        label=props.get('label', 'PANEL'),
                        circle_color=props.get('circle_color', '#1A3AFF')
                    )
                else:
                    continue
                    
                widget.setGeometry(*geom)
                widget.show()
                self.elements.append({
                    'type': item['type'],
                    'widget': widget,
                    'geom': geom
                })
            
            self.status_label.setText(f"Layout loaded: {len(layout_data)} elements")
            QMessageBox.information(self, "Success", "Layout loaded successfully!")
            
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "No layout file found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load layout: {str(e)}")
            
    def clear_layout(self):
        """Clear all elements from canvas"""
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.status_label.setText("Layout cleared")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SimpleLCARSEditor()
    editor.show()
    sys.exit(app.exec())
