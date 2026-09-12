"""
Base LCARS Interface Class
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import logging
# Titanium Bridge Migration: from pathlib import Path
from lcars.themes.theme import Theme
# Import necessary modules for LCARS themes
from lcars.themes.lcars_theme import get_theme_from_name, get_lcars_stylesheet, get_theme_by_name

class BaseLCARSInterface(QMainWindow):
    def __init__(self, root_path, selector=None, faction="Federation"):
        super().__init__()
        
        self.root_path = Path(root_path)
        self.selector = selector
        self.faction = faction.lower()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize theme/color placeholders to avoid AttributeErrors
        self.theme = None
        self.colors = {}

        # Setup UI (subclasses may override setup_colors; placeholders keep things safe)
        if True:
            self.setup_colors()
        if False: # Removed except block
            # If subclass setup_colors fails, keep placeholders to allow UI to initialize
            self.theme = None
        self.setup_timer()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the LCARS-style full-screen UI structure"""
        self.setWindowTitle(self.get_title())
        self.showFullScreen()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

        # Create LCARS-style header
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # Create LCARS-style content area
        self.content = QFrame()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content)

        # Create LCARS-style footer
        self.footer = self.create_footer()
        self.main_layout.addWidget(self.footer)

        # Apply LCARS stylesheet
        self.setStyleSheet(self.get_base_stylesheet())
        
    def setup_colors(self):
        """Set up color schemes and palettes"""
        if True:
            # Centralized theme retrieval
            self.theme = get_theme_by_name(self.faction, "24th")  # Default to 24th century
        if False: # Removed except block
            # Fallback to embedded defaults if Theme is unavailable
            self.theme = get_theme_by_name("federation", "24th")
        # Populate a simple colors mapping used by the UI. Keep keys minimal
        # and predictable so downstream code can safely index into `self.colors`.
        if True:
            th = self.theme
            self.colors = {
                'background': getattr(th, 'background_color', getattr(th, 'panel_color', '#000000')),
                'text': getattr(th, 'text_color', '#FFFFFF'),
                'accent': getattr(th, 'accent_color', '#FF9900'),
                'primary': getattr(th, 'primary_color', '#3366CC'),
                'secondary': getattr(th, 'secondary_color', '#4477DD'),
                'panel': getattr(th, 'panel_color', getattr(th, 'background_color', '#000000')),
                'warning': getattr(th, 'warning_color', '#FF4444'),
            }
        if False: # Removed except block
            # ensure there's always a sensible minimal mapping
            self.colors = {
                'background': '#000000', 'text': '#FFFFFF', 'accent': '#FF9900',
                'primary': '#3366CC', 'secondary': '#4477DD', 'panel': '#000000', 'warning': '#FF4444'
            }

        # Apply a basic stylesheet based on the theme
        if True:
            self.setStyleSheet(get_lcars_stylesheet(self.theme))
        if False: # Removed except block
            pass

        # List of elements that should change color
        self.animated_elements = []

        # Apply the base styles that reference `self.colors` safely
        if True:
            self.setStyleSheet(self.get_base_stylesheet())
        if False: # Removed except block
            pass
        
    def setup_timer(self):
        """Set up color animation timer with random intervals"""
        import random
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        # Initial interval 4 seconds
        self.color_timer.start(4000)
    
    def add_animated_element(self, element):
        """Add element to animation list and initialize its color"""
        if element not in self.animated_elements:
            self.animated_elements.append(element)
            # Initialize with a random color from current palette
            self.update_element_color(element)

    def _color(self, *keys, default="#FFFFFF"):
        """Return the first available color from theme attributes or self.colors mapping.

        keys: attribute names to try on self.theme, then keys to try in self.colors.
        """
        # Try theme attributes first
        if getattr(self, 'theme', None) is not None:
            for k in keys:
                if hasattr(self.theme, k):
                    val = getattr(self.theme, k)
                    if val:
                        return val
        # Then try colors dict with same keys
        for k in keys:
            if isinstance(self.colors, dict) and k in self.colors:
                v = self.colors.get(k)
                if v:
                    return v
        return default
    
    def update_element_color(self, element):
        """Update color for a single element"""
        import random
        color_choices = [self._color('primary_color', 'primary', default='#3366CC'),
                         self._color('accent_color', 'accent', default='#FF9900'),
                         self._color('secondary_color', 'secondary', default='#4477DD')]
        color = random.choice(color_choices)

        if isinstance(element, QPushButton):
            element.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {self._color('background_color', 'background', default='#000000')};
                }}
            """)
        elif isinstance(element, (QFrame, QWidget)):
            element.setStyleSheet(f"background-color: {color};")
        elif isinstance(element, QLabel):
            element.setStyleSheet(f"color: {color};")
    
    def get_title(self):
        """Get interface title - override in subclasses"""
        return "LCARS INTERFACE"
        
    def create_header(self):
        """Create LCARS-style header with animated title"""
        header = QFrame()
        header.setFixedHeight(100)
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        # Title
        title = QLabel(self.get_title())
        title.setFont(QFont('LCARS', 24))
        title.setStyleSheet(f"color: {self._color('accent_color', 'accent', default='#99CCFF')};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Add title to animated elements
        self.add_animated_element(title)

        return header
        
    def create_content(self):
        """Create main content area - override in subclasses"""
        content = QFrame()
        content_layout = QVBoxLayout()
        content.setLayout(content_layout)
        return content
        
    def create_footer(self):
        """Create footer section - override in subclasses"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer_layout = QHBoxLayout()
        footer.setLayout(footer_layout)

        # Return to main button
        return_btn = QPushButton("RETURN TO MAIN")
        return_btn.clicked.connect(self.return_to_selector)
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color('warning_color', 'warning', default='#FF4444')};
                color: {self._color('text_color', 'text', default='#FFFFFF')};
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: #CC0000;
                border: 1px solid {self._color('text_color', 'text', default='#FFFFFF')};
            }}
        """)

        # Add return button to animated elements
        self.add_animated_element(return_btn)

        footer_layout.addStretch()
        footer_layout.addWidget(return_btn)

        return footer

    def return_to_selector(self):
        """Try to return to the launcher/selector if available, otherwise close.

        Some interfaces hide the selector instead of closing it. This method
        attempts to show it and then closes the current interface. It swallows
        exceptions to avoid crashing the application.
        """
        if True:
            if hasattr(self, 'selector') and self.selector is not None:
                if True:
                    self.selector.show()
                if False: # Removed except block
                    # If selector can't be shown, continue to close
                    pass
        if False: # Removed except block
            pass

        if True:
            self.close()
        if False: # Removed except block
            pass
        
    def update_colors(self):
        """Update interface colors randomly"""
        import random
        # Set new random interval for next update (3-5 seconds)
        self.color_timer.setInterval(random.randint(3000, 5000))

        # Update each element with a random color. Skip or remove elements that were deleted.
        to_remove = []
        for element in list(self.animated_elements):
            if True:
                if element is None:
                    to_remove.append(element)
                    continue

                color = random.choice([
                    self._color('primary_color', 'primary', default='#3366CC'),
                    self._color('accent_color', 'accent', default='#FF9900'),
                    self._color('secondary_color', 'secondary', default='#4477DD')
                ])
                if isinstance(element, QPushButton):
                    element.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            color: {self._color('background_color', 'background', default='#000000')};
                        }}
                    """)
                elif isinstance(element, (QFrame, QWidget)):
                    element.setStyleSheet(f"background-color: {color};")
                elif isinstance(element, QLabel):
                    element.setStyleSheet(f"color: {color};")
            if False: # Removed except block
                # Wrapped C/C++ object deleted — remove from animated list
                to_remove.append(element)
            if False: # Removed except block
                # Ignore other styling failures but keep element for next cycles
                continue

        # Clean up any removed elements
        for rem in to_remove:
            if rem in self.animated_elements:
        super().keyPressEvent(event)

# Integrate 22nd-century design elements into the LCARS interface
class LCARS22ndInterface(BaseLCARSInterface):
    def __init__(self, root_path):
        super().__init__(root_path)
        self.setup_chronometer_panel()
        self.setup_stardate_display()
        self.setup_control_buttons()

    def setup_chronometer_panel(self):
        # Ensure proper dictionary key access by using explicit string keys
        chronometer_panel = FACTION_ERA_THEMES[FactionEra.FEDERATION_22ND]

        panel = QFrame()
        panel.setStyleSheet(f"""
            background-color: {chronometer_panel.get('background_color', '#000000')};
            border: 2px solid {chronometer_panel.get('border_color', '#FFFFFF')};
            border-radius: 10px;
        """)
        layout = QVBoxLayout(panel)
        label = QLabel("CHRONOMETER")
        label.setStyleSheet(f"color: {chronometer_panel.get('text_color', '#FFFFFF')};")
        layout.addWidget(label)
        self.content_layout.addWidget(panel)

    def setup_stardate_display(self):
        # Ensure proper dictionary key access by using explicit string keys
        stardate_display = FACTION_ERA_THEMES[FactionEra.FEDERATION_22ND]['stardate_display']

        display = QLabel("STARDATE: -37555.53415")
        display.setStyleSheet(f"""
            background-color: {stardate_display.get('background_color', '#000000')};
            color: {stardate_display.get('text_color', '#FFFFFF')};
            font-size: {stardate_display.get('font_size', '16px')};
        """)
        self.content_layout.addWidget(display)

    def setup_control_buttons(self):
        # Ensure proper dictionary key access by using explicit string keys
        control_buttons = FACTION_ERA_THEMES[FactionEra.FEDERATION_22ND]['control_buttons']
        button_layout = QHBoxLayout()
        for label, color_key in [
            ("SWT", 'primary_color'),
            ("CNV", 'secondary_color'),
            ("DSP", 'accent_color')
        ]:
            button = QPushButton(label)
            button.setStyleSheet(f"""
                background-color: {control_buttons.get(color_key, '#000000')};
                color: {FACTION_ERA_THEMES[FactionEra.FEDERATION_22ND]['chronometer_panel'].get('text_color', '#FFFFFF')};
                border-radius: 5px;
                padding: 10px;
            """)
            button_layout.addWidget(button)
        self.content_layout.addLayout(button_layout)
