"""
Simple EditMode - working version
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
from PyQt6.QtCore import Qt, QObject
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDialog, QLineEdit, QMenu
from PyQt6.QtGui import QPainter, QPen, QColor, QAction
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import math

class EditMode(QObject):
    """Simple edit mode for LCARS constructor"""
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent = parent_widget
        self.enabled = False
        self.elements = []
        self.selected = None
        self._drag = None
        self._drag_offset = (0, 0)
        
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
        print(f"EditMode toggled: {self.enabled}")
        if self.enabled:
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: #090;
                    color: #FFF;
                    border: 2px solid #0F0;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 4px;
                }
            """)
            self.toolbar.show()
            print("Toolbar показано")
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
            return False
            
        event_type = event.type()
        
        if event_type == event.Type.MouseButtonPress:
            return self.mouse_press_event(event)
        elif event_type == event.Type.MouseMove:
            return self.mouse_move_event(event)
        elif event_type == event.Type.MouseButtonRelease:
            return self.mouse_release_event(event)
            
        return False
    
    def mouse_press_event(self, event):
        """Handle mouse press"""
        if not self.enabled:
            return False
        
        px, py = int(event.pos().x()), int(event.pos().y())
        print(f"Mouse press at: {px}, {py}")
        margin = 8
        
        # Check elements in reverse order (top to bottom)
        for idx, el in enumerate(reversed(self.elements)):
            x, y, w, h = el['geom']
            actual_idx = len(self.elements) - 1 - idx
            
            print(f"Checking element {actual_idx}: {el['type']} at ({x}, {y}, {w}, {h})")
            
            # Check element body
            if x <= px <= x + w and y <= py <= y + h:
                self._drag = actual_idx
                self._drag_offset = (px - x, py - y)
                self.selected = actual_idx
                print(f"Selected element {actual_idx} for drag")
                self.parent.update()
                return True
        
        self.selected = None
        self.parent.update()
        return False
    
    def mouse_move_event(self, event):
        """Handle mouse move"""
        if not self.enabled or self._drag is None:
            return False
        
        px, py = int(event.pos().x()), int(event.pos().y())
        
        # Update element position
        el = self.elements[self._drag]
        x, y, w, h = el['geom']
        new_x = px - self._drag_offset[0]
        new_y = py - self._drag_offset[1]
        el['geom'] = [new_x, new_y, w, h]
        
        self.update_layout()
        self.parent.update()
        return True
    
    def mouse_release_event(self, event):
        """Handle mouse release"""
        if not self.enabled:
            return False
        
        self._drag = None
        return False
