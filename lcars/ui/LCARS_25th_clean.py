"""
LCARS Interface - 25th Century Edition (Clean Version)
Simple, clean LCARS interface with working buttons and color animation
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QListWidget, QTabWidget, QLineEdit, QDialog, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color

class LoginDialog(QDialog):
    """LCARS Login System"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS AUTHORIZATION")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("LCARS ACCESS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFAA00;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("LOGIN")
        login_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

class LCARS25thCenturyClean(QMainWindow):
    """Clean 25th Century LCARS Interface"""
    
    def __init__(self):
        super().__init__()
        
        # Show login first
        if not self.show_login():
            self.close()
            return
        
        # Set up window
        self.setWindowTitle("LCARS Framework")
        self.showFullScreen()
        
        # Color animation variables
        self.color_timer = QTimer(self)
        self.color_change_interval = 3000  # 3 seconds
        
        # Star date timer
        self.star_date_timer = QTimer(self)
        
        # Set up colors
        self.setup_colors()
        
        # Create interface
        self.create_interface()
        
        # Start color animation
        self.start_color_animation()
        
        # Start star date updates
        self.start_star_date_updates()
        
        # Show window
        self.show()
        
    def show_login(self):
        """Show login dialog"""
        login = LoginDialog(self)
        return login.exec() == QDialog.DialogCode.Accepted
        
    def calculate_star_date(self):
        """Calculate Star Trek star date"""
        current = QDateTime.currentDateTime()
        year = current.date().year()
        day_of_year = current.date().dayOfYear()
        
        # Star date calculation: 1000 * (year - 2323) + (day_of_year - 1) * 1000 / 365
        star_date = 1000 * (year - 2323) + (day_of_year - 1) * 1000 / 365
        return f"STARDATE {star_date:.1f}"
        
    def start_star_date_updates(self):
        """Start star date updates"""
        self.update_star_date()
        self.star_date_timer.timeout.connect(self.update_star_date)
        self.star_date_timer.start(1000)  # Update every second
        
    def setup_colors(self):
        """Set up LCARS colors"""
        self.era = LCARSEra.LCARS_25TH
        palette = get_era_palette(self.era)
        self.colors = palette.copy()
        self.font_family = "Orbitron, Arial"
        
    def create_interface(self):
        """Create clean LCARS interface"""
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        self.create_left_panel(main_layout)
        
        # Right content area
        self.create_content_area(main_layout)
        
        # Apply initial stylesheet
        self.update_colors()
        
    def create_left_panel(self, main_layout):
        """Create left navigation panel"""
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Status header
        status = QLabel("LCARS 25TH")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['background']};
                background: {self.colors['alert_colors'][0]};
                font-size: 18px;
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 20px;
                border-radius: 8px;
            }}
        """)
        left_layout.addWidget(status)
        
        # Navigation buttons
        nav_buttons = [
            ("PROJECTS", self.show_projects),
            ("SIMULATION", self.show_simulation), 
            ("ANALYSIS", self.show_analysis),
            ("SETTINGS", self.show_settings)
        ]
        
        for text, slot in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setFixedHeight(50)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        # Return button
        return_btn = QPushButton("RETURN TO MAIN")
        return_btn.clicked.connect(self.close)
        return_btn.setFixedHeight(60)
        left_layout.addWidget(return_btn)
        
        main_layout.addWidget(left_panel)
        
    def create_content_area(self, main_layout):
        """Create main content area"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Header with star date and time
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title = QLabel("LCARS FRAMEWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                font-size: 32px;
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 20px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
            }}
        """)
        
        # Date and time panel
        datetime_panel = QWidget()
        datetime_layout = QVBoxLayout(datetime_panel)
        
        self.star_date_label = QLabel()
        self.star_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.star_date_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['alert_colors'][0]};
                font-size: 16px;
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 5px;
            }}
        """)
        
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['button_colors'][0]};
                font-size: 18px;
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 5px;
            }}
        """)
        
        datetime_layout.addWidget(self.star_date_label)
        datetime_layout.addWidget(self.time_label)
        
        header_layout.addWidget(title)
        header_layout.addWidget(datetime_panel)
        
        content_layout.addWidget(header_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.setup_tabs()
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content_widget)
        
    def update_star_date(self):
        """Update star date and time display"""
        self.star_date_label.setText(self.calculate_star_date())
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)
        
    def setup_tabs(self):
        """Set up content tabs"""
        # Projects tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        
        project_list = QListWidget()
        project_list.addItems(["Project Alpha", "Project Beta", "Project Gamma"])
        projects_layout.addWidget(project_list)
        
        self.tabs.addTab(projects_tab, "PROJECTS")
        
        # Simulation tab
        sim_tab = QWidget()
        sim_layout = QVBoxLayout(sim_tab)
        
        sim_label = QLabel("Simulation Control")
        sim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sim_layout.addWidget(sim_label)
        
        self.tabs.addTab(sim_tab, "SIMULATION")
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        analysis_label = QLabel("Data Analysis")
        analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_layout.addWidget(analysis_label)
        
        self.tabs.addTab(analysis_tab, "ANALYSIS")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_label = QLabel("System Settings")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(settings_label)
        
        self.tabs.addTab(settings_tab, "SETTINGS")
        
    def start_color_animation(self):
        """Start color animation"""
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(self.color_change_interval)
        
    def update_colors(self):
        """Update colors with animation - each element gets random color"""
        # Get different random colors for each element type
        button_primary = get_random_button_color(self.era)
        button_secondary = get_random_button_color(self.era)
        button_accent = get_random_button_color(self.era)
        tab_primary = get_random_button_color(self.era)
        tab_secondary = get_random_button_color(self.era)
        list_primary = get_random_button_color(self.era)
        
        # Apply stylesheet with different random colors
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {self.colors['background']};
                border: none;
            }}
            QWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QPushButton {{
                background: {button_primary};
                color: {self.colors['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
            QPushButton:hover {{
                background: {button_secondary};
                color: {self.colors['background']};
            }}
            QPushButton:pressed {{
                background: {button_accent};
            }}
            QListWidget {{
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid {self.colors['panel_border']};
                border-radius: 8px;
                color: {self.colors['text']};
                padding: 8px;
                font-family: '{self.font_family}';
            }}
            QListWidget::item {{
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background: {list_primary};
                color: {self.colors['background']};
            }}
            QTabWidget::pane {{
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid {self.colors['panel_border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QTabBar::tab {{
                background: {tab_secondary};
                color: {self.colors['text']};
                padding: 12px 24px;
                border: 1px solid {self.colors['panel_border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
            QTabBar::tab:selected {{
                background: {tab_primary};
                color: {self.colors['background']};
            }}
        """)
        
    def show_projects(self):
        """Show projects tab"""
        self.tabs.setCurrentIndex(0)
        
    def show_simulation(self):
        """Show simulation tab"""
        self.tabs.setCurrentIndex(1)
        
    def show_analysis(self):
        """Show analysis tab"""
        self.tabs.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings tab"""
        self.tabs.setCurrentIndex(3)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LCARS25thCenturyClean()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
