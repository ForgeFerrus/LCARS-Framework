import os
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, 
                            QWidget, QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor

class GUILauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS GUI Launcher")
        self.setMinimumSize(800, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000033;
                color: #FFCC00;
            }
            QListWidget {
                background-color: #000033;
                color: #FFCC00;
                border: 2px solid #FFCC00;
                font-size: 16px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #FFCC00;
            }
            QListWidget::item:selected {
                background-color: #FFCC00;
                color: #000033;
            }
            QPushButton {
                background-color: #000033;
                color: #FFCC00;
                border: 2px solid #FFCC00;
                padding: 10px 20px;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #FFCC00;
                color: #000033;
            }
            QLabel {
                color: #FFCC00;
                font-size: 16px;
                padding: 10px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Title
        title = QLabel("LCARS GUI Launcher - Select a GUI to run")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # List of GUIs
        self.gui_list = QListWidget()
        self.gui_list.itemDoubleClicked.connect(self.run_selected_gui)
        layout.addWidget(self.gui_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Selected GUI")
        self.run_button.clicked.connect(self.run_selected_gui)
        
        refresh_button = QPushButton("Refresh List")
        refresh_button.clicked.connect(self.populate_gui_list)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Populate the list
        self.populate_gui_list()
    
    def populate_gui_list(self):
        """Scan for Python files that might contain GUIs"""
        self.gui_list.clear()
        self.statusBar().showMessage("Scanning for GUI files...")
        
        # Look for Python files in the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        gui_files = []
        
        for root, _, files in os.walk(project_dir):
            # Skip certain directories
            if any(skip in root for skip in ['__pycache__', '.git', '.vscode', '.idea', 'venv', 'env']):
                continue
                
            for file in files:
                if file.endswith('.py') and not file.startswith('_'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_dir)
                    gui_files.append(rel_path)
        
        # Add files to the list
        for file in sorted(gui_files):
            self.gui_list.addItem(file)
        
        self.statusBar().showMessage(f"Found {len(gui_files)} Python files")
    
    def run_selected_gui(self):
        """Run the selected GUI file"""
        selected_items = self.gui_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a GUI to run")
            return
            
        file_name = selected_items[0].text()
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        
        self.statusBar().showMessage(f"Running: {file_name}")
        
        try:
            # Use subprocess to run the GUI in a separate process
            subprocess.Popen([sys.executable, file_path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.statusBar().showMessage(f"Launched: {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run {file_name}:\n{str(e)}")
            self.statusBar().showMessage(f"Error running {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the launcher
    launcher = GUILauncher()
    launcher.show()
    
    sys.exit(app.exec())
