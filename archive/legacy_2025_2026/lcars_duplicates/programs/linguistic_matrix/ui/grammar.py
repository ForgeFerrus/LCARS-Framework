"""Grammar UI (migrated)."""
from PyQt6.QtWidgets import QWidget
from lcars.themes.lcars_palette import get_theme, LCARSEra

class GrammarWidget(QWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        # UI implementation copied from module
