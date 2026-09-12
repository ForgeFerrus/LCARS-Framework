"""
Universal Edit Mode Manager - can be attached to any interface
Provides drag & drop, resize, property editing functionality
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor
from lcars.themes.eras.pcars22_components import get_base_components
from lcars.themes.eras.pcars23_components import get_23rd_components


class EditModeManager:
    """Universal edit mode manager for any QWidget interface"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.enabled = False
        self.elements = []
        self.selected = None
        self._drag = None
        self._resize = None
        self._drag_offset = (0, 0)
        self._resize_offset = (0, 0)
        
        # Component palette for adding new elements
        self.component_palette = get_base_components()
        
        # Create edit mode UI
        self.create_edit_ui()
        
        # Install event filters
        self.parent.installEventFilter(self)
        
    def create_edit_ui(self):
        """Create edit mode toggle button and toolbar"""
        # Edit mode toggle button
        self.edit_btn = QPushButton("EDIT MODE", self.parent)
        self.edit_btn.setGeometry(10, 10, 120, 32)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                color: #FFF;
                border: 2px solid #666;
                border-radius: 6px;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        
        # Edit toolbar (initially hidden)
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
        
        # Toolbar layout
        toolbar_layout = QVBoxLayout(self.toolbar)
        
        # Component palette buttons
        self.palette_buttons = {}
        for idx, key in enumerate(self.component_palette):
            btn = QPushButton(key.upper(), self.toolbar)
            btn.setGeometry(10, 10 + idx * 35, 130, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: #3399FF;
                    color: #FFF;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #55AAFF;
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self.add_element(k))
            self.palette_buttons[key] = btn
            toolbar_layout.addWidget(btn)
        
        # Action buttons
        copy_btn = QPushButton("COPY", self.toolbar)
        copy_btn.setGeometry(10, 350, 130, 25)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: #FF9900;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        copy_btn.clicked.connect(self.copy_selected)
        toolbar_layout.addWidget(copy_btn)
        
        delete_btn = QPushButton("DELETE", self.toolbar)
        delete_btn.setGeometry(10, 380, 130, 25)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #CC0000;
                color: #FFF;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected)
        toolbar_layout.addWidget(delete_btn)
        
    def toggle_edit_mode(self):
        """Toggle edit mode on/off"""
        self.enabled = not self.enabled
        if self.enabled:
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: #FF6600;
                    color: #FFF;
                    border: 2px solid #FFAA00;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 4px;
                }
            """)
            self.edit_btn.setText("EDIT ON")
            self.toolbar.show()
            self.parent.update()
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
            self.edit_btn.setText("EDIT MODE")
            self.toolbar.hide()
            self.selected = None
            self.parent.update()
    
    def add_element(self, element_type):
        """Add new element to parent widget"""
        if not self.enabled:
            return
            
        if element_type in self.component_palette:
            # Create element at center of parent
            widget = self.component_palette[element_type](parent=self.parent)
            w, h = widget.width(), widget.height()
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
    
    def copy_selected(self):
        """Copy selected element"""
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
        """Delete selected element"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        el['widget'].deleteLater()
        del self.elements[self.selected]
        self.selected = None
        self.parent.update()
    
    def update_layout(self):
        """Update all element positions"""
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])
    
    def eventFilter(self, obj, event):
        """Handle mouse events for drag/resize"""
        if not self.enabled or obj != self.parent:
            return super().eventFilter(obj, event) if hasattr(super(), 'eventFilter') else False
            
        event_type = event.type()
        
        if event_type == event.Type.MouseButtonPress:
            return self.mouse_press_event(event)
        elif event_type == event.Type.MouseMove:
            return self.mouse_move_event(event)
        elif event_type == event.Type.MouseButtonRelease:
            return self.mouse_release_event(event)
        elif event_type == event.Type.KeyPress:
            return self.key_press_event(event)
        elif event_type == event.Type.Paint:
            self.paint_event(event)
            
        return super().eventFilter(obj, event) if hasattr(super(), 'eventFilter') else False
    
    def mouse_press_event(self, event):
        """Handle mouse press"""
        if not self.enabled:
            return False
            
        px, py = int(event.pos().x()), int(event.pos().y())
        margin = 8
        
        self.selected = None
        
        # Check elements in reverse order (top to bottom)
        for idx, el in enumerate(reversed(self.elements)):
            x, y, w, h = el['geom']
            actual_idx = len(self.elements) - 1 - idx
            
            # Check resize corner
            if x + w - margin <= px <= x + w and y + h - margin <= py <= y + h:
                self._resize = actual_idx
                self._resize_offset = (x + w - px, y + h - py)
                self.selected = actual_idx
                self.parent.update()
                return True
                
            # Check element body
            if x <= px <= x + w and y <= py <= y + h:
                self._drag = actual_idx
                self._drag_offset = (px - x, py - y)
                self.selected = actual_idx
                self.parent.update()
                return True
        
        self.parent.update()
        return False
    
    def mouse_move_event(self, event):
        """Handle mouse move"""
        if not self.enabled:
            return False
            
        px, py = int(event.pos().x()), int(event.pos().y())
        
        if self._resize is not None:
            x, y, w, h = self.elements[self._resize]['geom']
            dx, dy = self._resize_offset
            new_w = max(16, px - x + dx)
            new_h = max(16, py - y + dy)
            self.elements[self._resize]['geom'] = [x, y, new_w, new_h]
            self.update_layout()
            return True
        elif self._drag is not None:
            x, y, w, h = self.elements[self._drag]['geom']
            dx, dy = self._drag_offset
            self.elements[self._drag]['geom'] = [px - dx, py - dy, w, h]
            self.update_layout()
            return True
            
        return False
    
    def mouse_release_event(self, event):
        """Handle mouse release"""
        if not self.enabled:
            return False
            
        self._drag = None
        self._resize = None
        return False
    
    def key_press_event(self, event):
        """Handle key press"""
        if not self.enabled:
            return False
            
        if event.key() == Qt.Key.Key_Delete and self.selected is not None:
            self.delete_selected()
            return True
        elif event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.copy_selected()
            return True
            
        return False
    
    def paint_event(self, event):
        """Draw selection overlay"""
        if not self.enabled or self.selected is None:
            return
            
        el = self.elements[self.selected]
        x, y, w, h = el['geom']
        
        painter = QPainter(self.parent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw selection rectangle
        pen = QPen(QColor('#FFD700'), 3, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(x - 2, y - 2, w + 4, h + 4)
        
        # Draw resize handle
        painter.setPen(QPen(QColor('#FF6600'), 2))
        painter.setBrush(QColor('#FF6600'))
        painter.drawRect(x + w - 8, y + h - 8, 8, 8)
