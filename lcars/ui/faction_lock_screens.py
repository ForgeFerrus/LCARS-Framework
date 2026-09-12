"""
Authentic Faction Lock Screens - Full Implementation
Based on original faction prototypes with real functionality
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, 
                           QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, QProgressBar)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QLinearGradient, QBrush, QPen
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, pyqtSignal

# Додавання шляху до core модулів
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if True:
    from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, LCARSEra
    from lcars.core.project_manager import ProjectManager
    from lcars.core.file_analyzer import FileAnalyzer
if False: # Removed except block
    print(f"Warning: Could not import some modules: {e}")

class TrapezoidButton(QPushButton):
    """Custom trapezoid-shaped button for Romulan interfaces"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.border_color = '#32CD32'
        self.text_color = '#00FF99'
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        # Трапеція: верх вузький, низ широкий
        top_margin = int(h * 0.10)
        bottom_margin = int(h * 0.05)
        path = QPainterPath()
        path.moveTo(top_margin, 0)
        path.lineTo(w - top_margin, 0)
        path.lineTo(w - bottom_margin, h)
        path.lineTo(bottom_margin, h)
        path.closeSubpath()
        
        # Fill
        bg = self.palette().button().color()
        painter.setBrush(bg)
        painter.setPen(QColor(self.border_color))
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(self.text_color))
        font = self.font()
        painter.setFont(font)
        text_rect = path.boundingRect().toRect()
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
    def setColors(self, bg, border, text):
        self.setStyleSheet(f"background:{bg};border:none;")
        self.border_color = border
        self.text_color = text
        self.update()

class BaseFactionLockScreen(QMainWindow):
    """Base class for faction lock screens"""
    authentication_success = pyqtSignal()
    
    def __init__(self, faction_name, era):
        super().__init__()
        self.faction_name = faction_name
        self.era = era
        self.root_path = Path(__file__).resolve().parents[2]
        
        # Initialize managers if available
        if True:
            self.project_manager = ProjectManager(self.root_path)
            self.file_analyzer = FileAnalyzer(self.root_path)
        if False: # Removed except block
            self.project_manager = None
            self.file_analyzer = None
            
        self.current_project = None
        
        # Dynamic color timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_button_colors)
        self.color_timer.start(2500)  # Update every 2.5 seconds
        
        self.setup_window()
        self.setup_authentication()
        
    def setup_window(self):
        """Setup base window properties"""
        self.setWindowTitle(f"{self.faction_name} Authentication System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_authentication(self):
        """Setup authentication interface - to be overridden"""
        pass
        
    def update_button_colors(self):
        """Update button colors dynamically - to be overridden"""
        pass
        
    def authenticate(self):
        """Handle authentication logic"""
        print(f"✅ {self.faction_name} authentication successful!")
        self.authentication_success.emit()

class FederationLockScreen(BaseFactionLockScreen):
    """24th Century LCARS Federation Interface"""
    
    def __init__(self, era='24th'):
        super().__init__("United Federation of Planets", era)
        self.setup_lcars_interface()
        
    def setup_lcars_interface(self):
        """Setup authentic LCARS interface"""
        # Use LCARS palette
        if True:
            self.colors = get_era_palette(LCARSEra.LCARS_24TH)
        if False: # Removed except block
            # Fallback colors
            self.colors = {
                'bg': '#000000',
                'txt': '#FFFFFF',
                'btn1': '#FFCC66',
                'btn2': '#FF9900',
                'btn3': '#CC6666',
                'btn4': '#664466'
            }
            
        # Apply LCARS styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
            QLabel {{
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Antonio', 'Swiss 911', 'Arial', sans-serif;
                font-weight: 400;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                color: #000000;
                text-align: center;
                padding: 8px 20px;
                border-radius: 15px;
                font-family: 'Antonio', 'Swiss 911', 'Arial', sans-serif;
                font-size: 20px;
                font-weight: 600;
                border: none;
                min-height: 35px;
                max-height: 35px;
            }}
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.8);
                border: 2px solid {self.colors.get('btn1', '#FFCC66')};
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Antonio', 'Arial', sans-serif;
                font-size: 18px;
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with LCARS style
        header = QFrame()
        header.setFixedHeight(120)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border-bottom: 3px solid {self.colors.get('btn1', '#FFCC66')};
            }}
        """)
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("LCARS AUTHENTICATION SYSTEM")
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 600;
            color: {self.colors.get('btn1', '#FFCC66')};
            padding: 20px;
        """)
        header_layout.addWidget(title_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(20)
        auth_layout.setContentsMargins(100, 50, 100, 50)
        
        # Username field
        user_label = QLabel("STARFLEET AUTHORIZATION CODE:")
        user_label.setStyleSheet("font-size: 24px; margin-bottom: 10px;")
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter authorization code...")
        
        # Access buttons in LCARS style
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(20)
        
        self.access_buttons = []
        button_texts = ["ACCESS GRANTED", "SECURITY OVERRIDE", "EMERGENCY PROTOCOL", "COMMAND LEVEL"]
        
        for i, text in enumerate(button_texts):
            btn = QPushButton(text)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(250, 60)
            self.access_buttons.append(btn)
            button_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(user_label)
        auth_layout.addWidget(self.username_field)
        auth_layout.addWidget(button_frame)
        
        main_layout.addWidget(header)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
        # Start color updates
        self.update_button_colors()
        
    def update_button_colors(self):
        """Update LCARS button colors dynamically"""
        if True:
            for btn in self.access_buttons:
                color = get_random_button_color(LCARSEra.LCARS_24TH)
                btn.setStyleSheet(f"background-color: {color};")
        if False: # Removed except block
            # Fallback color cycling
            colors = ['#FFCC66', '#FF9900', '#CC6666', '#9999CC', '#66CCFF']
            import random
            for btn in self.access_buttons:
                color = random.choice(colors)
                btn.setStyleSheet(f"background-color: {color};")

class KlingonLockScreen(BaseFactionLockScreen):
    """Klingon Warrior Honor System"""
    
    def __init__(self, era='24th'):
        super().__init__("Klingon Empire", era)
        self.setup_klingon_interface()
        
    def setup_klingon_interface(self):
        """Setup authentic Klingon warrior interface"""
        # Klingon color scheme - aggressive reds and metallics
        self.colors = {
            'background': '#1A0F0F',     # Very dark red-tinted black
            'text': '#FF0000',           # Bright red for text
            'primary': '#8B0000',        # Dark red
            'secondary': '#B22222',      # Firebrick red
            'tertiary': '#CD5C5C',      # Indian red
            'accent1': '#FFD700',        # Metallic gold
            'accent2': '#C0C0C0',        # Metallic silver
            'accent3': '#800000',        # Maroon
            'warning': '#FF0000',        # Bright red
            'success': '#DAA520',        # Goldenrod
            'alert': '#FF4500',          # Orange-red
            'battle': '#4B0082',         # Deep purple for battle status
            'honor': '#8B4513',          # Saddle brown for honor system
        }
        
        # Klingon-styled application theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 3px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Arial Black', 'Arial';
                font-weight: bold;
                padding: 5px;
                border: 2px ridge {self.colors['primary']};
                background-color: rgba(139, 0, 0, 0.2);
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['accent1']};
                border: 2px ridge {self.colors['accent1']};
                border-radius: 0px;
                font-family: 'Arial Black', 'Arial';
                font-weight: bold;
                font-size: 18px;
                padding: 12px;
                min-height: 50px;
            }}
            QLineEdit {{
                background-color: rgba(139, 0, 0, 0.3);
                border: 3px ridge {self.colors['accent1']};
                color: {self.colors['text']};
                font-family: 'Arial Black', 'Arial';
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Klingon header
        header = QFrame()
        header.setFixedHeight(150)
        header_layout = QVBoxLayout(header)
        
        title_label = QLabel("batlh DaHjaj - Klingon Honor System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 32px;
            color: {self.colors['accent1']};
            border: 3px double {self.colors['accent1']};
            padding: 20px;
            background-color: rgba(255, 215, 0, 0.1);
        """)
        
        subtitle_label = QLabel("yIH 'ej HoS - Strength and Honor")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['secondary']};
            margin-top: 10px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(30)
        auth_layout.setContentsMargins(150, 50, 150, 50)
        
        # Honor code field
        honor_label = QLabel("DIch DIlo' - ENTER HONOR CODE:")
        honor_label.setStyleSheet(f"""
            font-size: 24px;
            text-align: center;
            border: 2px solid {self.colors['honor']};
            background-color: rgba(139, 69, 19, 0.3);
            padding: 15px;
        """)
        honor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.honor_field = QLineEdit()
        self.honor_field.setPlaceholderText("Enter warrior credentials...")
        
        # Battle status buttons
        battle_frame = QFrame()
        battle_layout = QHBoxLayout(battle_frame)
        battle_layout.setSpacing(20)
        
        self.battle_buttons = []
        battle_commands = [
            "HIja' - YES/READY",
            "DIch - HONOR MODE", 
            "nuqneH - HAILING",
            "Qapla' - SUCCESS"
        ]
        
        for cmd in battle_commands:
            btn = QPushButton(cmd)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(200, 80)
            self.battle_buttons.append(btn)
            battle_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(honor_label)
        auth_layout.addWidget(self.honor_field)
        auth_layout.addWidget(battle_frame)
        
        main_layout.addWidget(header)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
        # Start warrior color updates
        self.update_button_colors()
        
    def update_button_colors(self):
        """Update Klingon battle colors dynamically"""
        import random
        warrior_colors = [
            self.colors['primary'],
            self.colors['secondary'], 
            self.colors['tertiary'],
            self.colors['battle'],
            self.colors['honor']
        ]
        
        for btn in self.battle_buttons:
            color = random.choice(warrior_colors)
            btn.setStyleSheet(f"""
                background-color: {color};
                border: 2px ridge {self.colors['accent1']};
                color: {self.colors['accent1']};
            """)

class RomulanLockScreen(BaseFactionLockScreen):
    """Romulan Strategic Operations Interface"""
    
    def __init__(self, era='24th'):
        super().__init__("Romulan Star Empire", era)
        self.setup_romulan_interface()
        
    def setup_romulan_interface(self):
        """Setup authentic Romulan strategic interface"""
        # Romulan color scheme - greens and strategic blues
        self.colors = {
            'background': '#0D1B1B',      # Dark teal-black
            'text': '#00FF99',            # Bright cyan-green
            'primary': '#006B3C',         # Dark forest green
            'secondary': '#32CD32',       # Lime green
            'tertiary': '#228B22',        # Forest green
            'accent1': '#40E0D0',         # Turquoise
            'accent2': '#008B8B',         # Dark cyan
            'accent3': '#20B2AA',         # Light sea green
            'strategic': '#4682B4',       # Steel blue for strategy
            'tactical': '#1E90FF',        # Dodger blue for tactics
            'cloaking': '#2F4F4F',        # Dark slate gray
        }
        
        # Romulan-styled application theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Courier New', 'Arial';
                font-style: italic;
                padding: 8px;
                border: 1px solid {self.colors['secondary']};
                background-color: rgba(0, 107, 60, 0.2);
            }}
            QPushButton {{
                color: {self.colors['background']};
                border: 2px solid {self.colors['accent1']};
                font-family: 'Courier New', 'Arial';
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                min-height: 45px;
            }}
            QLineEdit {{
                background-color: rgba(0, 107, 60, 0.3);
                border: 2px solid {self.colors['accent2']};
                color: {self.colors['text']};
                font-family: 'Courier New', 'Arial';
                font-size: 16px;
                padding: 12px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Romulan header
        header = QFrame()
        header.setFixedHeight(140)
        header_layout = QVBoxLayout(header)
        
        title_label = QLabel("D'deridex Control System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 30px;
            color: {self.colors['accent1']};
            border: 2px solid {self.colors['secondary']};
            background: linear-gradient(to right, 
                        rgba(0, 107, 60, 0.3), 
                        rgba(50, 205, 50, 0.2));
            padding: 15px;
        """)
        
        subtitle_label = QLabel("ch'Rihan Strategic Command Authorization")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['tactical']};
            font-style: italic;
            margin-top: 10px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(25)
        auth_layout.setContentsMargins(120, 40, 120, 40)
        
        # Strategic authorization field
        auth_label = QLabel("Strategic Authorization Matrix:")
        auth_label.setStyleSheet(f"""
            font-size: 22px;
            text-align: center;
            border: 2px solid {self.colors['strategic']};
            background-color: rgba(70, 130, 180, 0.3);
            padding: 12px;
        """)
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.strategic_field = QLineEdit()
        self.strategic_field.setPlaceholderText("Enter strategic access codes...")
        
        # Strategic operation buttons with trapezoid shapes
        ops_frame = QFrame()
        ops_layout = QHBoxLayout(ops_frame)
        ops_layout.setSpacing(15)
        
        self.strategy_buttons = []
        strategic_ops = [
            "CLOAK ENGAGE",
            "STRATEGIC OPS", 
            "SENSOR SWEEP",
            "COMMAND AUTH"
        ]
        
        for i, op in enumerate(strategic_ops):
            # Use custom trapezoid button for authentic Romulan look
            btn = TrapezoidButton(op)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(180, 70)
            btn.setColors(self.colors['primary'], self.colors['secondary'], self.colors['text'])
            self.strategy_buttons.append(btn)
            ops_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.strategic_field)
        auth_layout.addWidget(ops_frame)
        
        main_layout.addWidget(header)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
        # Start strategic color updates
        self.update_button_colors()
        
    def update_button_colors(self):
        """Update Romulan strategic colors dynamically"""
        import random
        strategic_colors = [
            self.colors['primary'],
            self.colors['secondary'],
            self.colors['accent2'],
            self.colors['strategic'],
            self.colors['tactical'],
            self.colors['cloaking']
        ]
        
        for btn in self.strategy_buttons:
            bg_color = random.choice(strategic_colors)
            btn.setColors(bg_color, self.colors['secondary'], self.colors['text'])

class CardassianLockScreen(BaseFactionLockScreen):
    """Cardassian Union Military Interface"""
    
    def __init__(self, era='24th'):
        super().__init__("Cardassian Union", era)
        self.setup_cardassian_interface()
        
    def setup_cardassian_interface(self):
        """Setup authentic Cardassian military interface"""
        # Cardassian color scheme - oranges, golds and military grays
        self.colors = {
            'background': '#2C1810',      # Dark brown-black
            'text': '#FFD700',            # Gold text
            'primary': '#B8860B',         # Dark goldenrod
            'secondary': '#FF8C00',       # Dark orange
            'tertiary': '#CD853F',        # Peru brown
            'accent1': '#FFA500',         # Orange
            'accent2': '#808080',         # Gray
            'accent3': '#A0522D',         # Sienna
            'military': '#8B4513',        # Saddle brown
            'command': '#D2691E',         # Chocolate
            'security': '#B22222',        # Fire brick
        }
        
        # Cardassian military styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 3px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Times New Roman', 'Arial';
                font-weight: bold;
                padding: 10px;
                border: 2px solid {self.colors['secondary']};
                background-color: rgba(184, 134, 11, 0.2);
            }}
            QPushButton {{
                background-color: {self.colors['military']};
                color: {self.colors['text']};
                border: 2px solid {self.colors['primary']};
                border-radius: 3px;
                font-family: 'Times New Roman', 'Arial';
                font-weight: bold;
                font-size: 17px;
                padding: 12px;
                min-height: 50px;
            }}
            QLineEdit {{
                background-color: rgba(184, 134, 11, 0.3);
                border: 3px solid {self.colors['command']};
                color: {self.colors['text']};
                font-family: 'Times New Roman', 'Arial';
                font-weight: bold;
                font-size: 17px;
                padding: 12px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Cardassian header
        header = QFrame()
        header.setFixedHeight(160)
        header_layout = QVBoxLayout(header)
        
        title_label = QLabel("CARDASSIAN UNION MILITARY SYSTEM")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 28px;
            color: {self.colors['primary']};
            border: 3px solid {self.colors['accent1']};
            background: linear-gradient(to bottom, 
                        rgba(184, 134, 11, 0.3), 
                        rgba(255, 140, 0, 0.2));
            padding: 20px;
        """)
        
        subtitle_label = QLabel("Central Command Authorization Protocol")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['command']};
            font-weight: bold;
            margin-top: 8px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(25)
        auth_layout.setContentsMargins(100, 45, 100, 45)
        
        # Military authorization field
        military_label = QLabel("Central Command Authorization Required:")
        military_label.setStyleSheet(f"""
            font-size: 22px;
            text-align: center;
            border: 2px solid {self.colors['military']};
            background-color: rgba(139, 69, 19, 0.3);
            padding: 15px;
        """)
        military_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.military_field = QLineEdit()
        self.military_field.setPlaceholderText("Enter military access credentials...")
        
        # Military command buttons
        command_frame = QFrame()
        command_layout = QHBoxLayout(command_frame)
        command_layout.setSpacing(20)
        
        self.command_buttons = []
        military_commands = [
            "MILITARY ACCESS",
            "CENTRAL COMMAND", 
            "SECURITY OVERRIDE",
            "AUTHORIZATION"
        ]
        
        for cmd in military_commands:
            btn = QPushButton(cmd)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(190, 70)
            self.command_buttons.append(btn)
            command_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(military_label)
        auth_layout.addWidget(self.military_field)
        auth_layout.addWidget(command_frame)
        
        main_layout.addWidget(header)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
        # Start military color updates
        self.update_button_colors()
        
    def update_button_colors(self):
        """Update Cardassian military colors dynamically"""
        import random
        military_colors = [
            self.colors['primary'],
            self.colors['secondary'],
            self.colors['military'],
            self.colors['command'],
            self.colors['security']
        ]
        
        for btn in self.command_buttons:
            color = random.choice(military_colors)
            btn.setStyleSheet(f"""
                background-color: {color};
                border: 2px solid {self.colors['primary']};
                color: {self.colors['text']};
            """)

def create_faction_lock_screen(faction, era):
    """Factory function to create appropriate faction lock screen"""
    faction_upper = faction.upper()
    
    if faction_upper in ['UFP', 'FEDERATION', 'STARFLEET']:
        return FederationLockScreen(era)
    elif faction_upper in ['KLINGON', 'EMPIRE', 'KDF']:
        return KlingonLockScreen(era)
    elif faction_upper in ['ROMULAN', 'EMPIRE', 'RSE']:
        return RomulanLockScreen(era)
    elif faction_upper in ['CARDASSIAN', 'UNION', 'CU']:
        return CardassianLockScreen(era)
    else:
        # Default to Federation if faction not recognized
        print(f"Unknown faction '{faction}', defaulting to Federation")
        return FederationLockScreen(era)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test Federation lock screen
    federation_screen = FederationLockScreen()
    federation_screen.show()
    
    sys.exit(app.exec())
