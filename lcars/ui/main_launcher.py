
"""Main LCARS Launcher - Complete Interface System"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient, QPen, QBrush, QPixmap

# Import existing interfaces and theme system
if True:
    from archive.era_files.LCARS_24th import LCARS24thCentury
    from archive.era_files.LCARS_25th import LCARS25thCentury
    from archive.era_files.Klingon_system import KlingonInterface
    from archive.era_files.PCARS_22nd import PCARS22ndCentury
    from archive.era_files.PCARS_23rd import PCARS23rdCentury
    INTERFACES_AVAILABLE = True
if False: # Removed except block
    INTERFACES_AVAILABLE = False

# Import theme system
if True:
    from lcars.themes.theme import Theme
    THEME_SYSTEM_AVAILABLE = True
if False: # Removed except block
    THEME_SYSTEM_AVAILABLE = False

# Import existing component systems
if True:
    from lcars.themes.components.starfleet_components import StarfleetComponentDemo
    from lcars.themes.components.klingon_components import KlingonComponentDemo
    from lcars.themes.components.cardassian_components import CardassianComponentDemo
    from lcars.themes.romulan_components import RomulanComponentDemo
    COMPONENT_SYSTEMS_AVAILABLE = True
if False: # Removed except block
    COMPONENT_SYSTEMS_AVAILABLE = False


class BackgroundWidget(QWidget):
    """Widget with background image support"""
    
    def __init__(self, bg_image_path=None, bg_color="#000000", parent=None):
        super().__init__(parent)
        self.bg_image_path = bg_image_path
        self.bg_color = QColor(bg_color)
        self.bg_pixmap = None
        
        if bg_image_path and os.path.exists(bg_image_path):
            self.bg_pixmap = QPixmap(bg_image_path)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            # Scale image to fit window
            scaled_pixmap = self.bg_pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # Fill with solid color
            painter.fillRect(self.rect(), self.bg_color)


class WelcomePanel(QFrame):
    """Clean welcome panel with faction selection - no contours"""
    
    faction_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_welcome_ui()
        
    def setup_welcome_ui(self):
        self.setFixedSize(800, 600)
        
        # Use theme system if available
        if THEME_SYSTEM_AVAILABLE:
            colors = Theme.get_colors('24th')
            bg_color = colors.get('bg', '#000000')
            title_color = colors.get('btn1', '#FFCC66')
            text_color = colors.get('txt', '#FFFFFF')
        else:
            bg_color = '#000011'
            title_color = '#FFCC66'
            text_color = '#FFFFFF'
            
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: none;
                border-radius: 0px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Welcome title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 48px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 8px;
                padding: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("SELECT YOUR FACTION")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 4px;
                padding: 10px;
                    }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Faction buttons grid
        faction_grid = QGridLayout()
        faction_grid.setSpacing(30)
        faction_grid.setContentsMargins(50, 30, 50, 30)
        
        factions = [
            ("STARFLEET", "#FFCC66", "#000000", "United Federation of Planets"),
            ("KLINGON", "#CC0000", "#FFFF00", "Klingon Empire"),
            ("ROMULAN", "#00FFAA", "#001144", "Romulan Star Empire"),
            ("CARDASSIAN", "#8B0000", "#FFFF00", "Cardassian Union")
        ]
        
        for i, (name, bg_color, text_color, description) in enumerate(factions):
            btn = FactionButton(name, bg_color, text_color, description)
            btn.clicked.connect(lambda checked, f=name: self.on_faction_selected(f))
            row = i // 2
            col = i % 2
            faction_grid.addWidget(btn, row, col)
            
        layout.addLayout(faction_grid)
        layout.addStretch()
        
    def on_faction_selected(self, faction):
        self.faction_selected.emit(faction)


class FactionButton(QPushButton):
    """Clean faction selection button"""
    
    def __init__(self, name, bg_color, text_color, description, parent=None):
        super().__init__(parent)
        self.name = name
        self.bg_color = bg_color
        self.text_color = text_color
        self.description = description
        self.setFixedSize(300, 120)
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.bg_color}, stop:0.3 {self.bg_color}, 
                    stop:0.7 {self.bg_color}, stop:1 {self.bg_color});
                color: {self.text_color};
                border: 2px solid {self.bg_color};
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:0.3 {self.bg_color}, 
                    stop:0.7 {self.bg_color}, stop:1 #FFFFFF);
                color: {self.text_color};
                border: 3px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background: {self.bg_color};
                color: #CCCCCC;
                border: 2px solid #CCCCCC;
            }}
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        # Add description text
        painter = QPainter(self)
        painter.setPen(QPen(QColor(self.text_color)))
        painter.setFont(QFont('Arial', 10))
        rect = self.rect()
        rect.adjust(10, rect.height() - 25, -10, -5)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.description)


class EraSelectionPanel(QFrame):
    """Era selection panel for chosen faction"""
    
    era_selected = pyqtSignal(str, str)  # faction, era
    
    def __init__(self, faction, parent=None):
        super().__init__(parent)
        self.faction = faction
        self.setup_era_ui()
        
    def setup_era_ui(self):
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 8, 34, 0.9), stop:0.3 rgba(0, 17, 68, 0.9), 
                    stop:0.7 rgba(0, 8, 34, 0.9), stop:1 rgba(0, 17, 68, 0.9));
                border: 4px solid #FFCC66;
                border-radius: 25px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Title
        title = QLabel(f"{self.faction} - SELECT ERA")
        title.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 3px;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Era buttons
        era_layout = QVBoxLayout()
        era_layout.setSpacing(20)
        
        eras = self.get_faction_eras()
        for era in eras:
            btn = EraButton(era)
            btn.clicked.connect(lambda checked, e=era: self.on_era_selected(e))
            era_layout.addWidget(btn)
            
        layout.addLayout(era_layout)
        
        # Back button
        back_btn = QPushButton("← BACK TO FACTIONS")
        back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #666666, stop:0.5 #888888, stop:1 #666666);
                color: #FFFFFF;
                border: 2px solid #AAAAAA;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 12px 25px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #AAAAAA, stop:0.5 #CCCCCC, stop:1 #AAAAAA);
                color: #000000;
                border: 3px solid #FFFFFF;
            }
        """)
        back_btn.clicked.connect(self.back_to_factions)
        layout.addWidget(back_btn)
        
    def get_faction_eras(self):
        """Get available eras for this faction"""
        era_map = {
            "STARFLEET": ["22nd Century", "23rd Century", "24th Century", "25th Century"],
            "KLINGON": ["22nd Century", "23rd Century", "24th Century"],
            "ROMULAN": ["22nd Century", "23rd Century", "24th Century"],
            "CARDASSIAN": ["23rd Century", "24th Century"]
        }
        return era_map.get(self.faction, ["24th Century"])
        
    def on_era_selected(self, era):
        self.era_selected.emit(self.faction, era)
        
    def back_to_factions(self):
        # Find the main interface and call show_welcome_panel
        parent = self.parent()
        while parent and not hasattr(parent, 'show_welcome_panel'):
            parent = parent.parent()
        if parent:
            parent.show_welcome_panel()


class EraButton(QPushButton):
    """Custom era selection button"""
    
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.setFixedSize(450, 70)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #004466, stop:0.5 #006688, stop:1 #004466);
                color: #FFFFFF;
                border: 3px solid #00AAFF;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00AAFF, stop:0.5 #00CCFF, stop:1 #00AAFF);
                color: #000000;
                border: 4px solid #FFFFFF;
            }
            QPushButton:pressed {
                background: #003344;
                color: #CCCCCC;
                border: 3px solid #666666;
            }
        """)


class MainInterface(QMainWindow):
    """Main LCARS Interface Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Framework - Main Interface")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_main_ui()
        
    def setup_main_ui(self):
        # Background widget
        self.bg_widget = BackgroundWidget(bg_color="#000000")
        self.setCentralWidget(self.bg_widget)
        
        # Main layout for background widget
        main_layout = QVBoxLayout(self.bg_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Welcome panel (initial view)
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.faction_selected.connect(self.show_era_selection)
        main_layout.addWidget(self.welcome_panel, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Era selection panel (hidden initially)
        self.era_panel = None
        self.current_interface = None
        
    def show_era_selection(self, faction):
        """Show era selection for chosen faction"""
        # Hide welcome panel
        self.welcome_panel.hide()
        
        # Create era panel
        self.era_panel = EraSelectionPanel(faction)
        self.era_panel.era_selected.connect(self.launch_faction_interface)
        
        # Replace in layout
        self.bg_widget.layout().addWidget(self.era_panel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.era_panel.show()
        
    def show_welcome_panel(self):
        """Show welcome panel again"""
        if self.era_panel:
            self.era_panel.hide()
            self.era_panel.deleteLater()
            self.era_panel = None
        if self.current_interface:
            self.current_interface.hide()
            self.current_interface.deleteLater()
            self.current_interface = None
        self.welcome_panel.show()
        
    def launch_faction_interface(self, faction, era):
        """Launch the specific faction/era interface using existing systems"""
        print(f"Launching {faction} - {era} interface...")
        
        # Hide current panels
        if self.welcome_panel:
            self.welcome_panel.hide()
        if self.era_panel:
            self.era_panel.hide()
        
        # Try to launch appropriate interface using existing systems
        interface_widget = None
        
        # Use existing interfaces first
        if INTERFACES_AVAILABLE:
            if faction == "STARFLEET":
                if "22nd" in era:
                    interface_widget = PCARS22ndCentury()
                elif "23rd" in era:
                    interface_widget = PCARS23rdCentury()
                elif "24th" in era:
                    interface_widget = LCARS24thCentury()
                elif "25th" in era:
                    interface_widget = LCARS25thCentury()
            elif faction == "KLINGON":
                interface_widget = KlingonInterface()
            elif faction == "ROMULAN":
                # Use existing Romulan components
                if True:
                    from lcars.themes.romulan_components import RomulanComponentDemo
                    interface_widget = RomulanComponentDemo()
                if False: # Removed except block
                    pass
            elif faction == "CARDASSIAN":
                # Use existing Cardassian components
                if True:
                    from lcars.themes.components.cardassian_components import CardassianComponentDemo
                    interface_widget = CardassianComponentDemo()
                if False: # Removed except block
                    pass
        
        # Use component systems if interfaces not available
        elif COMPONENT_SYSTEMS_AVAILABLE:
            if faction == "STARFLEET":
                interface_widget = StarfleetComponentDemo()
            elif faction == "KLINGON":
                interface_widget = KlingonComponentDemo()
            elif faction == "ROMULAN":
                interface_widget = RomulanComponentDemo()
            elif faction == "CARDASSIAN":
                interface_widget = CardassianComponentDemo()
        
        # Apply theme system if available
        if interface_widget and THEME_SYSTEM_AVAILABLE:
            if True:
                # Apply palette from centralized system
                palette_key = era.split()[0] if era else "24th"
                colors = get_palette_by_name(palette_key)
                
                # Create faction-era theme
                faction_era_map = {
                    ("STARFLEET", "22nd"): FactionEra.STARFLEET_22ND,
                    ("STARFLEET", "23rd"): FactionEra.STARFLEET_23RD,
                    ("STARFLEET", "24th"): FactionEra.STARFLEET_24TH,
                    ("STARFLEET", "25th"): FactionEra.STARFLEET_25TH,
                    ("KLINGON", "22nd"): FactionEra.KLINGON_22ND,
                    ("KLINGON", "23rd"): FactionEra.KLINGON_23RD,
                    ("KLINGON", "24th"): FactionEra.KLINGON_24TH,
                    ("ROMULAN", "22nd"): FactionEra.ROMULAN_22ND,
                    ("ROMULAN", "23rd"): FactionEra.ROMULAN_23RD,
                    ("ROMULAN", "24th"): FactionEra.ROMULAN_24TH,
                    ("ROMULAN", "25th"): FactionEra.ROMULAN_25TH,
                    ("CARDASSIAN", "23rd"): FactionEra.CARDASSIAN_23RD,
                    ("CARDASSIAN", "24th"): FactionEra.CARDASSIAN_24TH,
                }
                
                faction_era_key = (faction, era.split()[0])  # Get century number
                if faction_era_key in faction_era_map:
                    theme = get_faction_era_theme(faction_era_map[faction_era_key])
                    stylesheet = get_lcars_stylesheet(theme)
                    interface_widget.setStyleSheet(stylesheet)
                    
            if False: # Removed except block
                print(f"Theme application error: {e}")
        
        if interface_widget:
            msg_label = QLabel(f"Launching {faction} - {era} interface")
            msg_label.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 8, 34, 0.9), stop:0.3 rgba(0, 17, 68, 0.9), 
                    stop:0.7 rgba(0, 8, 34, 0.9), stop:1 rgba(0, 17, 68, 0.9));
                border: 3px solid #FFCC66;
                border-radius: 20px;
                padding: 30px;
                text-align: center;
            }
        """)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Show message centered
        self.bg_widget.layout().addWidget(msg_label, alignment=Qt.AlignmentFlag.AlignCenter)
        msg_label.show()
        
        # Auto-hide after 5 seconds
        QTimer.singleShot(5000, lambda: self.hide_message(msg_label))
        
    def hide_message(self, widget):
        """Hide and remove message widget"""
        widget.hide()
        widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show main interface
    main_interface = MainInterface()
    main_interface.show()
    
    sys.exit(app.exec())
