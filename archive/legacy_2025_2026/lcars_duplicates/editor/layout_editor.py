"""
LCARS Layout Editor - Interactive drag-and-drop interface designer
Based on archive/22nd.py but integrated with main framework
"""
import json
import sys
import os

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                            QVBoxLayout, QLabel, QMainWindow, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QResizeEvent, QPainterPath, QMouseEvent

# Import main framework components
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.pcars22_components import PCARS22Button, PCARS22MiniButton
from lcars.themes.eras.PCARSPanel import PCARS22Panel

class EditablePCARSButton(PCARS22Button):
    """Extended PCARS button with drag and resize capabilities"""
    
    def __init__(self, number='00-0000', label='NAME', width=200, height=64, 
                 color=None, bar_color=None, border_color=None, border=1, parent=None):
        super().__init__(number, label, width, height, color, bar_color, border_color, border, parent)
        self.set_flags()
        self._resize_margin = 8
        self._resize_cursor = None
        
    def set_flags(self):
        """Enable mouse tracking and cursor for editing"""
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        
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
            new_pos = self._original_pos + delta
            self.move(new_pos.toPoint())
            self.parent().update_layout()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """End drag operation"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)

class EditablePCARSPanel(PCARS22Panel):
    """Extended PCARS panel with drag capabilities"""
    
    def __init__(self, parent=None, label="WARP FIELD ANL", circle_color="#1A3AFF"):
        super().__init__(parent, label, circle_color)
        self.set_flags()
        
    def set_flags(self):
        """Enable mouse tracking and cursor for editing"""
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        
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
            new_pos = self._original_pos + delta
            self.move(new_pos.toPoint())
            self.parent().update_layout()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """End drag operation"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)

class LCARSLayoutEditor(QMainWindow):
    """Main editor window with drag-and-drop functionality"""
    
    def __init__(self):
        super().__init__()
        self.elements = []
        self._drag = None
        self._resize = None
        self._drag_offset = (0, 0)
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
        
        self.add_mini_btn = QPushButton("Add Mini Button")
        self.add_mini_btn.clicked.connect(self.add_mini_button)
        control_layout.addWidget(self.add_mini_btn)
        
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
        
        # Enable mouse tracking for canvas
        self.canvas.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        self.canvas.setMouseTracking(True)
        
    def add_button(self):
        """Add a new editable button to canvas"""
        palette = get_palette_by_name("22nd")
        button = EditablePCARSButton(
            number=f"00-{len(self.elements):04d}",
            label=f"BUTTON {len(self.elements)+1}",
            width=200,
            height=80,
            color=palette.get('button_colors', ['#3399FF'])[0],
            bar_color=palette.get('panel_color', '#CCCCCC'),
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
        """Add a new editable panel to canvas"""
        palette = get_palette_by_name("22nd")
        panel = EditablePCARSPanel(
            parent=self.canvas,
            label=f"PANEL {len(self.elements)+1}",
            circle_color=palette.get('accent1', '#1A3AFF')
        )
        panel.setGeometry(100 + (len(self.elements) * 40), 100 + (len(self.elements) * 30), 300, 200)
        panel.show()
        self.elements.append({
            'type': 'panel',
            'widget': panel,
            'geom': [panel.x(), panel.y(), panel.width(), panel.height()]
        })
        self.status_label.setText(f"Added panel {len(self.elements)}")
        
    def add_mini_button(self):
        """Add a new mini button to canvas"""
        palette = get_palette_by_name("22nd")
        mini = EditablePCARSButton(
            number=f"00-{len(self.elements):04d}",
            label=f"MINI {len(self.elements)+1}",
            width=100,
            height=40,
            color=palette.get('button_colors', ['#3399FF'])[0],
            bar_color=palette.get('panel_color', '#CCCCCC'),
            parent=self.canvas
        )
        mini.setGeometry(50 + (len(self.elements) * 25), 50 + (len(self.elements) * 15), 100, 40)
        mini.show()
        self.elements.append({
            'type': 'mini_button',
            'widget': mini,
            'geom': [mini.x(), mini.y(), mini.width(), mini.height()]
        })
        self.status_label.setText(f"Added mini button {len(self.elements)}")
        
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
            with open('lcars_layout_editor.json', 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, ensure_ascii=False, indent=2)
            self.status_label.setText(f"Layout saved: {len(layout_data)} elements")
            QMessageBox.information(self, "Success", "Layout saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save layout: {str(e)}")
            
    def load_layout(self):
        """Load layout from JSON file"""
        try:
            with open('lcars_layout_editor.json', 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            # Clear existing elements
            self.clear_layout()
            
            # Create elements from saved data
            for item in layout_data:
                props = item.get('properties', {})
                geom = item['geom']
                
                if item['type'] == 'button':
                    widget = EditablePCARSButton(
                        number=props.get('number', '00-0000'),
                        label=props.get('label', 'BUTTON'),
                        color=props.get('color', '#3399FF'),
                        bar_color=props.get('bar_color', '#CCCCCC'),
                        parent=self.canvas
                    )
                elif item['type'] == 'panel':
                    widget = EditablePCARSPanel(
                        parent=self.canvas,
                        label=props.get('label', 'PANEL'),
                        circle_color=props.get('circle_color', '#1A3AFF')
                    )
                elif item['type'] == 'mini_button':
                    widget = EditablePCARSButton(
                        number=props.get('number', '00-0000'),
                        label=props.get('label', 'MINI'),
                        color=props.get('color', '#3399FF'),
                        bar_color=props.get('bar_color', '#CCCCCC'),
                        parent=self.canvas
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
    editor = LCARSLayoutEditor()
    editor.show()
    sys.exit(app.exec())
