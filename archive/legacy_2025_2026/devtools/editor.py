"""
LCARS DevTools - Editor Module (prototype)

Базовий редактор форм/коду для інтеграції у LCARS Framework.
Може бути вкладкою у головному інтерфейсі або запускатися окремо.

TODO: Додати редактор Python-коду, редактор JSON-конфігів, редактор layout-файлів, менеджер плагінів.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel, 
                             QPushButton, QFileDialog, QHBoxLayout, QListWidget, QProgressBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
import os
import json
from pathlib import Path

# Add project root to path for lcars imports
project_root = str(Path(__file__).parent.parent)
import sys
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from lcars.core.vision import UIAnalyzer
except ImportError:
    UIAnalyzer = None

class LCARSDevEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS DevTools - Editor")
        self.setMinimumSize(1000, 700)
        
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Python code editor (prototype)
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("# Тут буде редактор Python-коду...")
        self.tabs.addTab(self.code_editor, "Python-код")

        # Tab 2: JSON editor (prototype)
        self.json_editor = QTextEdit()
        self.json_editor.setPlaceholderText("{\n  \"example\": true\n}")
        self.tabs.addTab(self.json_editor, "JSON-конфіг")

        # Tab 3: Constructor (New Integrated Tool)
        self.constructor_tab = QWidget()
        self._setup_constructor_tab()
        self.tabs.addTab(self.constructor_tab, "Constructor")

        # Tab 4: Layout editor (placeholder)
        self.layout_editor = QLabel("Редактор layout-файлів (у розробці)")
        self.layout_editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(self.layout_editor, "Layout")

        # Tab 5: Plugin manager (placeholder)
        self.plugin_manager = QLabel("Менеджер плагінів (у розробці)")
        self.plugin_manager.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(self.plugin_manager, "Плагіни")

    def _setup_constructor_tab(self):
        layout = QHBoxLayout(self.constructor_tab)
        
        # Left Panel: Controls
        ctrl_panel = QWidget()
        ctrl_layout = QVBoxLayout(ctrl_panel)
        ctrl_panel.setFixedWidth(300)
        
        ctrl_layout.addWidget(QLabel("<b>Interface Constructor</b>"))
        ctrl_layout.addWidget(QLabel("Select an image to analyze and convert into a working LCARS interface."))
        
        self.btn_load_img = QPushButton("Load Background Image")
        self.btn_load_img.clicked.connect(self._load_image)
        ctrl_layout.addWidget(self.btn_load_img)
        
        self.lbl_img_path = QLabel("No image selected")
        self.lbl_img_path.setWordWrap(True)
        ctrl_layout.addWidget(self.lbl_img_path)
        
        self.btn_analyze = QPushButton("Analyze Geometry")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self._run_analysis)
        ctrl_layout.addWidget(self.btn_analyze)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        ctrl_layout.addWidget(self.progress)
        
        self.results_list = QListWidget()
        ctrl_layout.addWidget(QLabel("Detected Elements:"))
        ctrl_layout.addWidget(self.results_list)
        
        self.btn_save_layout = QPushButton("Apply to Framework")
        self.btn_save_layout.setEnabled(False)
        self.btn_save_layout.clicked.connect(self._save_layout)
        ctrl_layout.addWidget(self.btn_save_layout)
        
        ctrl_layout.addStretch()
        
        # Right Panel: Preview
        self.preview_area = QLabel("Preview Area")
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setStyleSheet("background-color: black; border: 1px solid #336699;")
        
        layout.addWidget(ctrl_panel)
        layout.addWidget(self.preview_area, 1)

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "resources/", "Images (*.png *.jpg *.webp)")
        if path:
            self.lbl_img_path.setText(path)
            self.selected_image = path
            self.btn_analyze.setEnabled(True)
            
            pixmap = QPixmap(path)
            self.preview_area.setPixmap(pixmap.scaled(self.preview_area.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def _run_analysis(self):
        if not UIAnalyzer:
            self.results_list.addItem("Error: UIAnalyzer not found")
            return
            
        self.results_list.clear()
        self.results_list.addItem("Running computer analysis...")
        
        results = UIAnalyzer.analyze_background(self.selected_image)
        self.analysis_results = results
        
        if results:
            self.results_list.addItem(f"Size: {results['image_size']}")
            self.results_list.addItem(f"Faction buttons: {len(results['faction_buttons'])}")
            self.results_list.addItem(f"Top buttons: {len(results['top_buttons'])}")
            self.results_list.addItem(f"Eras: {len(results['era_left']) + len(results['era_right'])}")
            self.btn_save_layout.setEnabled(True)
        else:
            self.results_list.addItem("Analysis failed.")

    def _save_layout(self):
        if not hasattr(self, 'analysis_results'):
            return
            
        target_path = os.path.join("config", "generated_layout.json")
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=4)
        
        self.results_list.addItem(f"SUCCESS: Layout saved to {target_path}")
        self.results_list.addItem("Framework will hot-reload configuration.")

# Для інтеграції: додати вкладку LCARSDevEditor у головний QTabWidget або запускати окремо
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    win = LCARSDevEditor()
    win.show()
    sys.exit(app.exec())
