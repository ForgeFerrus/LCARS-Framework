"""
Onboard Computer Widget - Autonomous project management interface
Embedded directly into LCARS Central Command
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QComboBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from pathlib import Path
from lcars.core.autonomous_builder import AutonomousBuildOrchestrator, BuildDiagnostics
from lcars.core.project_manager import ProjectManager
import logging

logger = logging.getLogger(__name__)

class OnboardComputerWidget(QWidget):
    """
    Self-contained widget for autonomous project management
    Replaces the separate System Monitor window
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_manager = ProjectManager(Path.cwd())
        self.current_builder = None
        self.setup_ui()
        self.apply_lcars_style()
    
    def setup_ui(self):
        """Build the widget interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("◢ ONBOARD COMPUTER")
        header.setFont(QFont("Swis721 BT", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Project Selection
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("PROJECT:"))
        
        self.project_combo = QComboBox()
        self.populate_projects()
        project_layout.addWidget(self.project_combo, 1)
        
        layout.addLayout(project_layout)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.build_btn = QPushButton("◢ BUILD")
        self.build_btn.clicked.connect(self.start_build)
        button_layout.addWidget(self.build_btn)
        
        self.run_btn = QPushButton("▶ RUN")
        self.run_btn.setEnabled(False)
        button_layout.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("◼ STOP")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_build)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setFont(QFont("Swis721 BT", 10))
        layout.addWidget(self.status_label)
        
        # Log Output
        log_label = QLabel("BUILD LOG:")
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        self.log_output.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_output)
        
        # Diagnostics
        self.diagnostics_label = QLabel("")
        self.diagnostics_label.setWordWrap(True)
        layout.addWidget(self.diagnostics_label)
    
    def apply_lcars_style(self):
        """Apply LCARS styling to the widget"""
        self.setStyleSheet("""
            OnboardComputerWidget {
                background-color: #0A0A0A;
                border: 1px solid #37A6D1;
                border-radius: 8px;
            }
            QLabel {
                color: #37A6D1;
                background: transparent;
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
            QComboBox {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: 1px solid #37A6D1;
                border-radius: 4px;
                padding: 4px;
            }
            QTextEdit {
                background-color: #000;
                color: #00FF00;
                border: 1px solid #37A6D1;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #37A6D1;
                border-radius: 4px;
                background-color: #0A0A0A;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #FF9900;
                border-radius: 3px;
            }
        """)
    
    def populate_projects(self):
        """Load discovered projects into dropdown"""
        self.project_combo.clear()
        for project_name in self.project_manager.projects.keys():
            self.project_combo.addItem(project_name)
        
        if not self.project_manager.projects:
            self.project_combo.addItem("No projects found")
            self.build_btn.setEnabled(False)
    
    def start_build(self):
        """Initiate autonomous build process"""
        project_name = self.project_combo.currentText()
        if project_name not in self.project_manager.projects:
            return
        
        project = self.project_manager.projects[project_name]
        
        # Disable controls
        self.build_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("BUILDING...")
        
        # Create and start builder
        self.current_builder = AutonomousBuildOrchestrator(project.path)
        self.current_builder.log_signal.connect(self.append_log)
        self.current_builder.progress_signal.connect(self.update_progress)
        self.current_builder.finished_signal.connect(self.build_finished)
        self.current_builder.start()
    
    def stop_build(self):
        """Terminate the build process"""
        if self.current_builder:
            self.current_builder.terminate()
            self.current_builder.wait()
            self.status_label.setText("BUILD STOPPED")
            self.build_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    @pyqtSlot(str)
    def append_log(self, message: str):
        """Add message to build log"""
        self.log_output.append(message)
        # Auto-scroll to bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    @pyqtSlot(int, str)
    def update_progress(self, percentage: int, status: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(status.upper())
    
    @pyqtSlot(BuildDiagnostics)
    def build_finished(self, diagnostics: BuildDiagnostics):
        """Handle build completion"""
        self.build_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100 if diagnostics.success else 0)
        
        if diagnostics.success:
            self.status_label.setText("✓ BUILD SUCCESSFUL")
            self.run_btn.setEnabled(True)
            self.diagnostics_label.setText("")
        else:
            self.status_label.setText("◣ BUILD FAILED")
            self.run_btn.setEnabled(False)
            
            # Display diagnostics
            diag_text = []
            if diagnostics.errors:
                diag_text.append(f"ERRORS: {len(diagnostics.errors)}")
            if diagnostics.warnings:
                diag_text.append(f"WARNINGS: {len(diagnostics.warnings)}")
            if diagnostics.suggestions:
                diag_text.append("SUGGESTIONS:")
                for suggestion in diagnostics.suggestions[:3]:  # Show top 3
                    diag_text.append(f"  • {suggestion}")
            
            self.diagnostics_label.setText("\n".join(diag_text))
