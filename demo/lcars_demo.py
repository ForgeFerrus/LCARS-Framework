"""
Автентична LCARS-система — демонстрація в стилі Star Trek

Файл містить демонстрацію використання базових компонентів LCARS Framework.
Коментарі й docstring'и тут виконані українською для зручності розробника.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
# Ensure repository root is on sys.path so the `lcars` package can be imported
repo_root = project_root.parent
sys.path.insert(0, str(repo_root))

from PyQt6.QtWidgets import QApplication

# Import base framework components
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.interface import Screen, Segment, Header, DataBlock
from lcars.base.default import Palette, RandomButtonColor, FontStyle
from lcars.base.desktop import LCARSDesktop
from lcars.themes.lcars_palette import LCARSEra, get_theme, setup_lcars_font
from lcars.themes.theme import FactionEra

# Register LCARS fonts (best-effort)
try:
    setup_lcars_font()
except (ImportError, OSError, FileNotFoundError):
    # Fonts are optional for the demo; ignore common filesystem/import errors
    pass

class DemoLCARSDesktop(LCARSDesktop):
    """Демонстраційний десктоп LCARS на базі фреймворку.

    Розширює базовий LCARSDesktop для створення демонстраційного інтерфейсу
    з використанням канонічних компонентів фреймворку.
    """
    def __init__(self, faction="FEDERATION", era="25th"):
        super().__init__()
        self.faction = faction
        self.era = era
        
        # Convert era string to enum if possible
        era_map = {
            "22nd": LCARSEra.COMS_22ND,
            "23rd": LCARSEra.PCARS_23RD,
            "24th": LCARSEra.LCARS_24TH,
            "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH,
        }
        self.era_enum = era_map.get(era, LCARSEra.LCARS_25TH)
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era}")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Apply theme styling
        self.apply_theme_styling()
        
    def apply_theme_styling(self):
        """Застосувати стилі теми до десктопу."""
        try:
            theme = get_theme(self.era_enum)
            bg_color = theme.get('background', '#000000')
            self.widget.setStyleSheet(f"background-color: {bg_color}; border: none;")
        except Exception:
            # Fallback to default black background
            self.widget.setStyleSheet("background-color: #000000; border: none;")
    
    def BuildLeftNavigation(self):
        """Перевизначення навігації з використанням базових компонентів."""
        # Викликаємо батьківський метод для базової структури
        super().BuildLeftNavigation()
        
        # Додаємо специфічні для демо кнопки
        demo_buttons = [
            ("TACTICAL", self.show_tactical),
            ("SCIENCE", self.show_science),
            ("ENGINEERING", self.show_engineering),
        ]
        
        for name, callback in demo_buttons:
            btn = LCARSButton(
                Text=name,
                Type="soft-left",
                Color=RandomButtonColor("accent", f"Demo{name}"),
                Parent=self.LeftColumn.widget
            )
            btn.Clicked.Connect(callback)
            self.LeftLayout.addWidget(btn.widget)
    
    def BuildRightShell(self):
        """Перевизначення правої панелі з демонстраційним контентом."""
        super().BuildRightShell()
        
        # Оновлюємо заголовок для демонстрації
        if hasattr(self, 'TopStatus'):
            self.TopStatus.SetText(f"LCARS DEMO - {self.faction} {self.era}")
    
    def show_tactical(self):
        """Показати тактичну панель."""
        self.ModeStatus.SetText("MODE // TACTICAL")
        self.Select("TACTICAL")
    
    def show_science(self):
        """Показати наукову панель."""
        self.ModeStatus.SetText("MODE // SCIENCE")
        self.Select("SCIENCE")
    
    def show_engineering(self):
        """Показати інженерну панель."""
        self.ModeStatus.SetText("MODE // ENGINEERING")
        self.Select("ENGINEERING")

def main():
    # Delegate to the unified demo launcher which implements
    # the full sequential initialization path. This keeps the
    # demo UI centralized and ensures palette/font algorithms
    # are used consistently.
    from demo import demo_launcher
    # Preserve any CLI args (support `--auto` for automatic demo)
    demo_launcher.main()

if __name__ == "__main__":
    main()
